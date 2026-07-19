#!/usr/bin/env python3
"""Analyze subject-level BCI robustness results and build a dashboard.

The script expects benchmark CSV outputs produced by the runner and creates
subject risk cards, montage-rescue metrics, paired statistics, and an
interactive HTML dashboard.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import beta
from statsmodels.stats.multitest import multipletests


def exact_binom_ci(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    if n <= 0:
        return (np.nan, np.nan)
    lo = 0.0 if k == 0 else beta.ppf(alpha / 2, k, n - k + 1)
    hi = 1.0 if k == n else beta.ppf(1 - alpha / 2, k + 1, n - k)
    return float(lo), float(hi)


def bootstrap_ci(x: np.ndarray, n_resamples: int = 5000, seed: int = 42) -> tuple[float, float]:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    if x.size < 2:
        return np.nan, np.nan
    res = stats.bootstrap((x,), np.mean, n_resamples=n_resamples, random_state=seed, method='BCa')
    return float(res.confidence_interval.low), float(res.confidence_interval.high)


def load_wide(results_dir: Path, prefix: str, use_cached: bool = False, write_cache: bool = True) -> pd.DataFrame:
    """Load or build a subject-wide table from the current subject summary.

    By default this rebuilds from `{prefix}_subject_summary.csv` so reruns that
    update checkpoints/results cannot silently reuse an older wide CSV. Set
    `use_cached=True` only when intentionally reusing a previously generated
    `{prefix}_subject_wide.csv`.
    """
    wide_path = results_dir / f'{prefix}_subject_wide.csv'
    if use_cached and wide_path.exists():
        return pd.read_csv(wide_path)
    subj_path = results_dir / f'{prefix}_subject_summary.csv'
    if not subj_path.exists():
        if wide_path.exists():
            raise FileNotFoundError(f'Missing current subject summary: {subj_path}. Use --use-cached-wide to read {wide_path}.')
        raise FileNotFoundError(f'Missing {wide_path} and {subj_path}')
    subj = pd.read_csv(subj_path)
    clean = subj[(subj.stressor == 'clean') & (subj.montage == 'all_channels')][['subject','roc_auc','balanced_accuracy']].rename(columns={'roc_auc':'clean_auc','balanced_accuracy':'clean_bal'})
    wide = clean.copy()
    for frac in sorted(subj.loc[subj.stressor == 'channel_dropout', 'dropout_fraction'].dropna().unique()):
        d = subj[(subj.stressor == 'channel_dropout') & (subj.dropout_fraction == frac)][['subject','roc_auc','balanced_accuracy']].rename(columns={'roc_auc':f'auc_dropout_{frac:g}','balanced_accuracy':f'bal_dropout_{frac:g}'})
        wide = wide.merge(d, on='subject', how='left')
    for montage in sorted(subj.loc[subj.stressor == 'reduced_montage', 'montage'].dropna().unique()):
        d = subj[(subj.stressor == 'reduced_montage') & (subj.montage == montage)][['subject','roc_auc','balanced_accuracy']].rename(columns={'roc_auc':f'auc_{montage}','balanced_accuracy':f'bal_{montage}'})
        wide = wide.merge(d, on='subject', how='left')
    if write_cache:
        wide.to_csv(wide_path, index=False)
    return wide


def risk_cards(wide: pd.DataFrame, clean_thr: float, fail_thr: float) -> pd.DataFrame:
    dropout_cols = sorted([c for c in wide.columns if c.startswith('auc_dropout_')], key=lambda s: float(s.split('_')[-1]))
    rows = []
    for _, r in wide.iterrows():
        deltas = {c: r[c] - r['clean_auc'] for c in dropout_cols if pd.notna(r[c])}
        worst_col = min(deltas, key=deltas.get) if deltas else None
        worst_delta = deltas[worst_col] if worst_col else np.nan
        # AUC at 50% dropout if present, otherwise worst observed dropout AUC.
        auc50_col = next((c for c in dropout_cols if abs(float(c.split('_')[-1]) - 0.5) < 1e-9), None)
        auc50 = r[auc50_col] if auc50_col else (min([r[c] for c in dropout_cols]) if dropout_cols else np.nan)
        clean_working = bool(r['clean_auc'] >= clean_thr)
        dropout_failure = bool(clean_working and auc50 < fail_thr)
        rescue_candidates = [c for c in ['auc_motor_core','auc_motor_extended'] if c in wide.columns and pd.notna(r.get(c, np.nan))]
        best_montage_col = max(rescue_candidates, key=lambda c: r[c]) if rescue_candidates else None
        best_montage_auc = r[best_montage_col] if best_montage_col else np.nan
        best_montage_gain = best_montage_auc - r['clean_auc'] if best_montage_col else np.nan
        if clean_working and auc50 < fail_thr:
            risk_level = 'high_drop_failure'
        elif clean_working and worst_delta <= -0.20:
            risk_level = 'moderate_fragility'
        elif r['clean_auc'] < clean_thr:
            risk_level = 'low_clean_performance'
        else:
            risk_level = 'stable_in_dev_run'
        rows.append({
            'subject': int(r['subject']),
            'clean_auc': r['clean_auc'],
            'auc_at_50pct_dropout': auc50,
            'worst_dropout_delta_auc': worst_delta,
            'clean_working': clean_working,
            'dropout_failure_at_50pct': dropout_failure,
            'best_montage': best_montage_col.replace('auc_', '') if best_montage_col else None,
            'best_montage_auc': best_montage_auc,
            'best_montage_gain_vs_clean': best_montage_gain,
            'risk_level': risk_level,
        })
    return pd.DataFrame(rows).sort_values(['risk_level','subject']).reset_index(drop=True)


def paired_stats(wide: pd.DataFrame) -> pd.DataFrame:
    rows = []
    cond_cols = [c for c in wide.columns if c.startswith('auc_dropout_') or c in ['auc_motor_core','auc_motor_extended']]
    for c in cond_cols:
        d = wide[[c, 'clean_auc']].dropna()
        diff = d[c] - d['clean_auc']
        n = len(diff)
        if n < 2:
            continue
        shapiro_p = stats.shapiro(diff).pvalue if 3 <= n <= 5000 else np.nan
        t = stats.ttest_rel(d[c], d['clean_auc'])
        try:
            w = stats.wilcoxon(diff, zero_method='wilcox')
            w_stat, w_p = float(w.statistic), float(w.pvalue)
        except ValueError:
            w_stat, w_p = np.nan, np.nan
        ci_low, ci_high = bootstrap_ci(diff.to_numpy())
        dz = diff.mean() / diff.std(ddof=1) if diff.std(ddof=1) > 0 else np.nan
        label = c.replace('auc_', '')
        rows.append({
            'condition': label,
            'n_subjects': n,
            'mean_auc': d[c].mean(),
            'clean_mean_auc': d['clean_auc'].mean(),
            'delta_auc_vs_clean': diff.mean(),
            'delta_ci_low': ci_low,
            'delta_ci_high': ci_high,
            'shapiro_p': shapiro_p,
            'paired_t_stat': float(t.statistic),
            'paired_t_p': float(t.pvalue),
            'wilcoxon_stat': w_stat,
            'wilcoxon_p': w_p,
            'cohens_dz': dz,
        })
    out = pd.DataFrame(rows)
    if not out.empty:
        out['paired_t_p_fdr_bh'] = multipletests(out['paired_t_p'], method='fdr_bh')[1]
    return out


def failure_rates(wide: pd.DataFrame, clean_thr: float, fail_thr: float) -> pd.DataFrame:
    rows = []
    clean_working = wide['clean_auc'] >= clean_thr
    n = int(clean_working.sum())
    for c in sorted([c for c in wide.columns if c.startswith('auc_dropout_')], key=lambda s: float(s.split('_')[-1])):
        frac = float(c.split('_')[-1])
        k = int((clean_working & (wide[c] < fail_thr)).sum())
        lo, hi = exact_binom_ci(k, n)
        rows.append({'dropout_fraction': frac, 'clean_working_subjects': n, 'failures': k, 'failure_rate': k/n if n else np.nan, 'failure_rate_ci_low': lo, 'failure_rate_ci_high': hi})
    return pd.DataFrame(rows)


def write_dashboard(wide: pd.DataFrame, cards: pd.DataFrame, paired: pd.DataFrame, failure: pd.DataFrame, out_path: Path) -> None:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots

    dropout_cols = sorted([c for c in wide.columns if c.startswith('auc_dropout_')], key=lambda s: float(s.split('_')[-1]))
    x = [0] + [float(c.split('_')[-1]) * 100 for c in dropout_cols]
    fig1 = go.Figure()
    for _, r in wide.iterrows():
        y = [r['clean_auc']] + [r[c] for c in dropout_cols]
        fig1.add_trace(go.Scatter(x=x, y=y, mode='lines+markers', name=f"S{int(r['subject'])}", opacity=0.65))
    fig1.add_hline(y=0.60, line_dash='dot', line_color='firebrick', annotation_text='failure threshold AUC=0.60')
    fig1.add_hline(y=0.50, line_dash='dash', line_color='gray', annotation_text='chance')
    fig1.update_layout(title='Individual dropout degradation curves', xaxis_title='Test-time channel dropout (%)', yaxis_title='ROC-AUC', height=520)

    fig2 = px.bar(cards.sort_values('worst_dropout_delta_auc'), x='subject', y='worst_dropout_delta_auc', color='risk_level', title='Worst subject-level AUC drop under channel dropout')
    fig2.update_layout(yaxis_title='Worst ΔROC-AUC vs clean')

    montage_cols = [c for c in ['auc_motor_core','auc_motor_extended'] if c in wide.columns]
    if montage_cols:
        long = wide.melt(id_vars=['subject','clean_auc'], value_vars=montage_cols, var_name='montage', value_name='auc')
        long['montage'] = long['montage'].str.replace('auc_', '', regex=False)
        long['gain_vs_clean'] = long['auc'] - long['clean_auc']
        fig3 = px.scatter(long, x='clean_auc', y='auc', color='montage', text='subject', title='Reduced montage as a possible intervention/rescue')
        fig3.add_shape(type='line', x0=0.35, y0=0.35, x1=1.0, y1=1.0, line=dict(color='gray', dash='dash'))
        fig3.update_layout(xaxis_title='Clean all-channel ROC-AUC', yaxis_title='Reduced-montage ROC-AUC', height=500)
    else:
        fig3 = go.Figure()

    html = f"""
<!doctype html>
<html><head><meta charset='utf-8'><title>BCI robustness dashboard</title>
<style>body{{font-family:Arial, sans-serif; max-width:1200px; margin:30px auto; line-height:1.35}} table{{border-collapse:collapse; font-size:13px}} th,td{{border:1px solid #ccc; padding:4px 6px}} th{{background:#e8f1f8}} .note{{background:#fff8e1; padding:10px; border-left:4px solid #f0b400}}</style></head>
<body>
<h1>Intervention-Robust EEG Benchmark dashboard</h1>
<h2>Subject risk cards</h2>
{cards.round(4).to_html(index=False)}
<h2>Failure-rate estimates</h2>
{failure.round(4).to_html(index=False)}
<h2>Paired statistics vs clean all-channel baseline</h2>
{paired.round(4).to_html(index=False)}
<h2>Individual degradation</h2>
{fig1.to_html(include_plotlyjs='cdn', full_html=False)}
<h2>Worst dropout loss by subject</h2>
{fig2.to_html(include_plotlyjs=False, full_html=False)}
<h2>Reduced montage as intervention</h2>
{fig3.to_html(include_plotlyjs=False, full_html=False)}
</body></html>
"""
    out_path.write_text(html, encoding='utf-8')


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('--results-dir', type=Path, default=Path('results'))
    ap.add_argument('--prefix', default='PhysionetMI_PhysionetMI_all_riemann_lr')
    ap.add_argument('--clean-working-threshold', type=float, default=0.60)
    ap.add_argument('--failure-threshold', type=float, default=0.60)
    ap.add_argument('--reports-dir', type=Path, default=Path('reports'))
    ap.add_argument('--use-cached-wide', action='store_true', help='Reuse existing {prefix}_subject_wide.csv instead of rebuilding from the current subject summary.')
    args = ap.parse_args()
    args.reports_dir.mkdir(parents=True, exist_ok=True)
    wide = load_wide(args.results_dir, args.prefix, use_cached=args.use_cached_wide)
    cards = risk_cards(wide, args.clean_working_threshold, args.failure_threshold)
    paired = paired_stats(wide)
    failure = failure_rates(wide, args.clean_working_threshold, args.failure_threshold)
    cards.to_csv(args.results_dir / f'{args.prefix}_subject_risk_cards.csv', index=False)
    paired.to_csv(args.results_dir / f'{args.prefix}_paired_stats_next.csv', index=False)
    failure.to_csv(args.results_dir / f'{args.prefix}_failure_rates_next.csv', index=False)
    summary = {
        'n_subjects': int(wide['subject'].nunique()),
        'clean_working_threshold': args.clean_working_threshold,
        'failure_threshold': args.failure_threshold,
        'n_clean_working': int((wide['clean_auc'] >= args.clean_working_threshold).sum()),
        'n_high_drop_failure': int((cards['risk_level'] == 'high_drop_failure').sum()),
        'mean_clean_auc': float(wide['clean_auc'].mean()),
        'mean_auc_50pct_dropout': float(wide['auc_dropout_0.5'].mean()) if 'auc_dropout_0.5' in wide.columns else np.nan,
    }
    (args.results_dir / f'{args.prefix}_next_summary.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    write_dashboard(wide, cards, paired, failure, args.reports_dir / f'{args.prefix}_interactive_dashboard.html')
    print(json.dumps(summary, indent=2))
    print('Wrote risk cards, paired stats, failure rates, and dashboard.')


if __name__ == '__main__':
    main()
