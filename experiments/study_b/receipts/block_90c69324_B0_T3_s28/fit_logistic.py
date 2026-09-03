import json
import numpy as np
from scipy.special import expit
from scipy.stats import ttest_rel
import copy

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'], dtype=np.float64)
y = np.array(data['y'], dtype=np.float64)

n_samples, n_features = X.shape
print(f"Data shape: {n_samples} samples, {n_features} features")

def sigmoid(z):
    """Sigmoid with clipping to prevent overflow"""
    z = np.clip(z, -30, 30)
    return expit(z)

def logistic_loss_and_grad(X, y, w, b, lambda_reg):
    """Compute Brier score and gradients"""
    logits = X @ w + b
    logits = np.clip(logits, -30, 30)
    probs = sigmoid(logits)
    
    # Brier score
    brier = np.mean((probs - y) ** 2)
    
    # Gradient of Brier loss
    errors = probs - y  # (n,)
    grad_w = (2.0 / len(y)) * (X.T @ errors) + 2 * lambda_reg * w
    grad_b = (2.0 / len(y)) * np.sum(errors)
    
    return brier, grad_w, grad_b

def fit_logistic(X, y, lambda_reg=0.0, max_iter=200, lr=0.1):
    """Full-batch gradient descent for logistic regression"""
    w = np.zeros(X.shape[1])
    b = 0.0
    n = len(y)
    
    for iteration in range(max_iter):
        brier, grad_w, grad_b = logistic_loss_and_grad(X, y, w, b, lambda_reg)
        
        # Update weights: w -= lr * (grad_w / n + lambda * w)
        w -= lr * (grad_w / n + lambda_reg * w)
        # Update bias: b -= lr * (grad_b / n)
        b -= lr * (grad_b / n)
    
    return w, b

def evaluate(X, y, w, b):
    """Evaluate Brier score"""
    logits = X @ w + b
    logits = np.clip(logits, -30, 30)
    probs = sigmoid(logits)
    brier = np.mean((probs - y) ** 2)
    return brier

# Create 5 contiguous folds
n_per_fold = n_samples // 5
print(f"\nFold size: {n_per_fold} samples per fold")

# Q1: Find best lambda using 5-fold CV
lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
results_q1 = {}

for lam in lambdas:
    brier_scores = []
    for fold_idx in range(5):
        # Define fold boundaries
        test_indices = list(range(fold_idx, n_samples, 5))
        train_indices = [i for i in range(n_samples) if i not in test_indices]
        
        X_train = X[train_indices]
        y_train = y[train_indices]
        X_test = X[test_indices]
        y_test = y[test_indices]
        
        # Fit model
        w, b = fit_logistic(X_train, y_train, lambda_reg=lam)
        
        # Evaluate on test fold
        brier = evaluate(X_test, y_test, w, b)
        brier_scores.append(brier)
    
    mean_brier = np.mean(brier_scores)
    results_q1[lam] = mean_brier
    print(f"Lambda {lam}: mean Brier = {mean_brier:.6f}, fold scores = {[f'{b:.6f}' for b in brier_scores]}")

# Find best lambda
best_lambda = min(results_q1, key=results_q1.get)
best_brier = results_q1[best_lambda]
baseline_brier = results_q1[0.0]  # lambda=0 is baseline
improvement = baseline_brier - best_brier

print(f"\n=== Q1 Results ===")
print(f"Best lambda: {best_lambda}")
print(f"Best Brier: {best_brier:.6f}")
print(f"Baseline Brier (lambda=0): {baseline_brier:.6f}")
print(f"Improvement: {improvement:.6f}")

# Q2: Test interaction terms
print(f"\n=== Q2: Interaction Terms ===")

# Create feature matrix with interaction terms
def add_interactions(X):
    """Add interaction terms: x0*x1, x1*x2, x2*x3, x0*x3"""
    X_with_inter = np.column_stack([
        X,
        X[:, 0] * X[:, 1],  # x0*x1
        X[:, 1] * X[:, 2],  # x1*x2
        X[:, 2] * X[:, 3],  # x2*x3
        X[:, 0] * X[:, 3]   # x0*x3
    ])
    return X_with_inter

X_inter = add_interactions(X)
lambda_q2 = 0.1

# Fit both models on each fold and collect Brier scores
brier_raw_folds = []
brier_inter_folds = []

for fold_idx in range(5):
    test_indices = list(range(fold_idx, n_samples, 5))
    train_indices = [i for i in range(n_samples) if i not in test_indices]
    
    # Raw model
    X_train = X[train_indices]
    y_train = y[train_indices]
    X_test = X[test_indices]
    y_test = y[test_indices]
    
    w_raw, b_raw = fit_logistic(X_train, y_train, lambda_reg=lambda_q2)
    brier_raw = evaluate(X_test, y_test, w_raw, b_raw)
    
    # Interaction model
    X_train_inter = X_inter[train_indices]
    X_test_inter = X_inter[test_indices]
    
    w_inter, b_inter = fit_logistic(X_train_inter, y_train, lambda_reg=lambda_q2)
    brier_inter = evaluate(X_test_inter, y_test, w_inter, b_inter)
    
    brier_raw_folds.append(brier_raw)
    brier_inter_folds.append(brier_inter)
    
    print(f"Fold {fold_idx}: Raw={brier_raw:.6f}, Interaction={brier_inter:.6f}")

# Paired t-test: raw - interaction (if positive, raw is worse)
differences = np.array(brier_raw_folds) - np.array(brier_inter_folds)
print(f"Differences (raw - inter): {differences}")

# t-test: testing if mean difference != 0
t_stat, p_val = ttest_rel(brier_raw_folds, brier_inter_folds)
print(f"Paired t-statistic: {t_stat:.6f}")
print(f"P-value: {p_val:.6f}")

interaction_helps = t_stat > 2.0
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# Q3: Compression test
print(f"\n=== Q3: Compression ===")

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic(X, y, lambda_reg=0.1)
brier_dense = evaluate(X, y, w_dense, b_dense)
print(f"Dense model Brier: {brier_dense:.6f}")

sparsity_levels = [20, 40, 60]  # percent
bit_levels = [8, 4]

best_retention = 0
best_config = None

for sparsity_pct in sparsity_levels:
    for bits in bit_levels:
        # Apply sparsity: zero out smallest magnitude weights
        w_comp = w_dense.copy()
        k = int(np.round(sparsity_pct / 100.0 * len(w_dense)))
        # Find indices of k smallest magnitude weights
        smallest_indices = np.argsort(np.abs(w_comp))[:k]
        w_comp[smallest_indices] = 0
        
        # Apply quantization: map remaining weights to 2^bits levels
        non_zero_mask = w_comp != 0
        if np.any(non_zero_mask):
            w_nz = w_comp[non_zero_mask]
            w_min = np.min(w_nz)
            w_max = np.max(w_nz)
            
            if w_max > w_min:
                # Map to [0, 2^bits - 1]
                levels = 2 ** bits - 1
                w_normalized = (w_nz - w_min) / (w_max - w_min)
                w_quantized = np.round(w_normalized * levels) / levels * (w_max - w_min) + w_min
                w_comp[non_zero_mask] = w_quantized
        
        # Evaluate compressed model
        brier_comp = evaluate(X, y, w_comp, b_dense)
        retention = brier_dense / brier_comp if brier_comp > 0 else 0
        
        print(f"Sparsity {sparsity_pct}%, bits {bits}: Brier={brier_comp:.6f}, Retention={retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = f"sparsity{sparsity_pct}_bits{bits}"

print(f"\nBest config: {best_config} with retention {best_retention:.6f}")

# Save results
results = {
    "best_lambda": best_lambda,
    "improvement_over_baseline": improvement,
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

print(f"\n=== Final Results ===")
print(json.dumps(results, indent=2))

with open('answers.json', 'w') as f:
    json.dump(results, f, indent=2)
