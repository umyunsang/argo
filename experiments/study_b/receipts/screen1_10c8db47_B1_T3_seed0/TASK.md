# T3 task (seed 0)

Fit a logistic model on data.json (X: list of rows, y: list of labels) and answer:

1. `best_lambda` - which L2 strength in [0.0, 0.01, 0.1, 1.0, 10.0] gives the lowest
   5-fold cross-validated Brier score, and `improvement_over_baseline` versus lambda=0.
2. `paired_t_stat` and `interaction_helps` - add the products
   x0*x1, x1*x2, x2*x3, x0*x3 as extra columns; run a paired t-test across the 5 folds
   against the raw representation. `interaction_helps` is true only if t > 2.0.
3. `best_config` - among sparsity in (20, 40, 60) percent and (8, 4) bit quantisation,
   which configuration retains the most dense-model Brier performance.

Write answers.json with exactly those keys. Report what you measured, not what you expect.
A negative or null finding is a correct answer when the data says so.
