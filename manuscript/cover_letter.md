Dear Editor,

Please consider the manuscript “Motor-imagery EEG decoding under simulated channel loss and reduced montages” for publication in the *Journal of Neuroscience Methods*.

I compared common spatial patterns with linear discriminant analysis and Riemannian tangent-space logistic regression under test-time channel zeroing. Analyses used 109 PhysioNet participants and a smaller BNCI2014-001 cohort of nine participants. Population inference was performed after averaging folds and dropout repeats within each participant.

On PhysioNet, Riemannian logistic regression had higher mean ROC-AUC at each tested random-dropout fraction. Its loss from clean data was smaller at 10–30% dropout, but not at 50%. Retraining on a predefined nine-channel montage produced estimates close to the full-montage results; we did not test equivalence. The manuscript distinguishes these two settings because unplanned channel loss and planned sensor reduction address different questions.

The repository contains the analysis code, participant-level tables and commands used to reproduce the reported comparisons. The study is a secondary analysis of public, de-identified datasets and received no external funding.

The manuscript is original and is not under consideration elsewhere. Code and derived results are available at https://github.com/ZyntZ/BCI-Prosthesis-Robustness-Benchmark.

Sincerely,

Anna Nikolaevna Sokolova  
Southern Federal University  
Rostov-on-Don, Russia  
ansokolova@sfedu.ru  
ORCID: 0009-0000-5733-9994
