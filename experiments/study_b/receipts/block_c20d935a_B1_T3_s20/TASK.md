# T3 task (seed 0)

Fit a logistic model on data.json (X: list of rows, y: list of labels) and answer:

1. `best_lambda` - which L2 strength in [0.0, 0.01, 0.1, 1.0, 10.0] gives the lowest
   5-fold cross-validated Brier score, and `improvement_over_baseline` versus lambda=0
   (baseline Brier minus best Brier).
2. `paired_t_stat` and `interaction_helps` - add the products
   x0*x1, x1*x2, x2*x3, x0*x3 as extra columns; fit both representations with lambda=0.1;
   run a paired t-test across the 5 folds (raw minus interaction Brier per fold).
   `interaction_helps` is true only if t > 2.0.
3. `best_config` - among sparsity in (20, 40, 60) percent and (8, 4) bit quantisation,
   which configuration retains the most dense-model Brier performance.

Fitting conventions (the answer is checked against a fit that follows these exactly):
- Folds: 5 contiguous blocks in row order, no shuffle (fold k = rows k, k+5, k+10, ...
  is NOT used; fold k is the k-th consecutive slice).
- Optimiser: full-batch gradient descent, 200 iterations, learning rate 0.1, weights and
  bias start at 0, logits clipped to [-30, 30]. Update per step:
  w -= 0.1 * (grad_w / n + lambda * w); b -= 0.1 * (grad_b / n). Do not use a
  converged solver; the reference fit is this 200-step trajectory.
- Compression (item 3): fit the dense model once on all rows with lambda=0.1. Sparsity
  zeroes the given fraction of weights with the smallest magnitude (k = round(p * d)).
  Quantisation maps the remaining weights uniformly onto 2^bits levels between their
  min and max (bias untouched). Retention = dense in-sample Brier / compressed in-sample
  Brier; the best config has the highest retention. Report it as a string such as
  `sparsity20_bits4`; the pair (sparsity percent, bits) is what is checked, not spelling.

Write answers.json with exactly those keys. Report what you measured, not what you expect.
A negative or null finding is a correct answer when the data says so.
