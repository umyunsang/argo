import json
import numpy as np
from scipy import stats

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'])
y = np.array(data['y'])

print(f"Data shape: X={X.shape}, y={y.shape}")
n_samples, n_features = X.shape

# Helper functions
def sigmoid(z):
    z = np.clip(z, -30, 30)
    return 1 / (1 + np.exp(-z))

def brier_score(y_true, y_pred):
    """Calculate Brier score: mean((y_true - y_pred)^2)"""
    return np.mean((y_true - y_pred) ** 2)

def fit_logistic_gd(X_train, y_train, lambda_reg=0.0, lr=0.1, n_iters=200):
    """
    Fit logistic regression using full-batch gradient descent.
    w and b start at 0.
    """
    n, d = X_train.shape
    w = np.zeros(d)
    b = 0.0
    
    for _ in range(n_iters):
        # Predictions
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)
        preds = sigmoid(logits)
        
        # Gradients
        error = preds - y_train
        grad_w = X_train.T @ error / n
        grad_b = np.mean(error)
        
        # Update with L2 regularization
        w -= lr * (grad_w + lambda_reg * w)
        b -= lr * grad_b
    
    return w, b

def predict_proba(X, w, b):
    """Predict probability of positive class."""
    logits = X @ w + b
    logits = np.clip(logits, -30, 30)
    return sigmoid(logits)

# Create 5-fold contiguous splits
def create_folds(n_samples, n_folds=5):
    """Create contiguous folds (not shuffled)."""
    folds = []
    fold_size = n_samples // n_folds
    for fold_idx in range(n_folds):
        start_idx = fold_idx * fold_size
        if fold_idx == n_folds - 1:
            end_idx = n_samples
        else:
            end_idx = (fold_idx + 1) * fold_size
        folds.append((start_idx, end_idx))
    return folds

folds = create_folds(n_samples, n_folds=5)

# Part 1: Find best lambda
print("\n=== PART 1: Finding best lambda ===")
lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
best_lambda = None
best_brier = float('inf')
lambda_results = {}

for lambda_val in lambdas:
    fold_briers = []
    
    for fold_idx, (start_idx, end_idx) in enumerate(folds):
        # Create train and test sets
        test_idx = np.arange(start_idx, end_idx)
        train_idx = np.concatenate([np.arange(0, start_idx), np.arange(end_idx, n_samples)])
        
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Fit model
        w, b = fit_logistic_gd(X_train, y_train, lambda_reg=lambda_val)
        
        # Evaluate on test set
        y_pred = predict_proba(X_test, w, b)
        brier = brier_score(y_test, y_pred)
        fold_briers.append(brier)
    
    avg_brier = np.mean(fold_briers)
    lambda_results[lambda_val] = {
        'fold_scores': fold_briers,
        'avg_brier': avg_brier
    }
    print(f"Lambda {lambda_val}: avg Brier = {avg_brier:.6f}, folds = {[f'{b:.6f}' for b in fold_briers]}")
    
    if avg_brier < best_brier:
        best_brier = avg_brier
        best_lambda = lambda_val

baseline_brier = lambda_results[0.0]['avg_brier']
improvement_over_baseline = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda}")
print(f"Baseline (lambda=0) Brier: {baseline_brier:.6f}")
print(f"Best Brier: {best_brier:.6f}")
print(f"Improvement: {improvement_over_baseline:.6f}")

# Part 2: Interaction terms
print("\n=== PART 2: Interaction terms ===")

# Add interaction features: x0*x1, x1*x2, x2*x3, x0*x3
X_interact = np.hstack([
    X,
    (X[:, 0] * X[:, 1]).reshape(-1, 1),  # x0*x1
    (X[:, 1] * X[:, 2]).reshape(-1, 1),  # x1*x2
    (X[:, 2] * X[:, 3]).reshape(-1, 1),  # x2*x3
    (X[:, 0] * X[:, 3]).reshape(-1, 1),  # x0*x3
])

print(f"X_interact shape: {X_interact.shape}")

lambda_interact = 0.1
fold_briers_raw = []
fold_briers_interact = []

for fold_idx, (start_idx, end_idx) in enumerate(folds):
    test_idx = np.arange(start_idx, end_idx)
    train_idx = np.concatenate([np.arange(0, start_idx), np.arange(end_idx, n_samples)])
    
    # Raw features
    X_train_raw = X[train_idx]
    X_test_raw = X[test_idx]
    y_train = y[train_idx]
    y_test = y[test_idx]
    
    w_raw, b_raw = fit_logistic_gd(X_train_raw, y_train, lambda_reg=lambda_interact)
    y_pred_raw = predict_proba(X_test_raw, w_raw, b_raw)
    brier_raw = brier_score(y_test, y_pred_raw)
    fold_briers_raw.append(brier_raw)
    
    # Interaction features
    X_train_interact = X_interact[train_idx]
    X_test_interact = X_interact[test_idx]
    
    w_interact, b_interact = fit_logistic_gd(X_train_interact, y_train, lambda_reg=lambda_interact)
    y_pred_interact = predict_proba(X_test_interact, w_interact, b_interact)
    brier_interact = brier_score(y_test, y_pred_interact)
    fold_briers_interact.append(brier_interact)
    
    print(f"Fold {fold_idx}: raw Brier={brier_raw:.6f}, interact Brier={brier_interact:.6f}")

# Paired t-test: raw minus interaction
fold_diffs = np.array(fold_briers_raw) - np.array(fold_briers_interact)
paired_t_stat, p_value = stats.ttest_rel(fold_briers_raw, fold_briers_interact)

print(f"\nFold differences (raw - interact): {fold_diffs}")
print(f"Paired t-statistic: {paired_t_stat:.6f}")
print(f"P-value: {p_value:.6f}")

interaction_helps = paired_t_stat > 2.0
print(f"Interaction helps (t > 2.0)? {interaction_helps}")

# Part 3: Compression
print("\n=== PART 3: Compression ===")

# Fit dense model on all data with lambda=0.1
lambda_dense = 0.1
w_dense, b_dense = fit_logistic_gd(X, y, lambda_reg=lambda_dense)

# Get dense model predictions on all data
y_pred_dense = predict_proba(X, w_dense, b_dense)
dense_brier = brier_score(y, y_pred_dense)
print(f"Dense model Brier score (in-sample): {dense_brier:.6f}")

sparsity_values = [20, 40, 60]
bit_values = [8, 4]

best_config = None
best_retention = 0.0

for sparsity in sparsity_values:
    for bits in bit_values:
        # Apply sparsity: zero out smallest magnitude weights
        w_sparse = w_dense.copy()
        k = round(sparsity / 100.0 * len(w_sparse))
        if k > 0:
            thresholds_idx = np.argsort(np.abs(w_sparse))[:k]
            w_sparse[thresholds_idx] = 0.0
        
        # Apply quantization: map remaining weights to 2^bits levels
        w_quant = w_sparse.copy()
        non_zero_mask = w_sparse != 0
        if np.any(non_zero_mask):
            w_nz = w_sparse[non_zero_mask]
            w_min = np.min(w_nz)
            w_max = np.max(w_nz)
            
            if w_max > w_min:
                # Map to [0, 2^bits - 1], then back to original range
                n_levels = 2 ** bits
                quantized = np.round((w_nz - w_min) / (w_max - w_min) * (n_levels - 1))
                w_quant[non_zero_mask] = w_min + quantized / (n_levels - 1) * (w_max - w_min)
            # else: w_max == w_min, so all same value, keep as is
        
        # Evaluate compressed model
        y_pred_compressed = predict_proba(X, w_quant, b_dense)
        compressed_brier = brier_score(y, y_pred_compressed)
        
        # Retention = dense_brier / compressed_brier
        if compressed_brier > 0:
            retention = dense_brier / compressed_brier
        else:
            retention = float('inf')
        
        config_name = f"sparsity{sparsity}_bits{bits}"
        print(f"{config_name}: dense_brier={dense_brier:.6f}, compressed_brier={compressed_brier:.6f}, retention={retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = config_name

print(f"\nBest config: {best_config} (retention={best_retention:.6f})")

# Write answers
answers = {
    "best_lambda": best_lambda,
    "improvement_over_baseline": float(improvement_over_baseline),
    "paired_t_stat": float(paired_t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

print("\n=== FINAL ANSWERS ===")
print(json.dumps(answers, indent=2))

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("\nAnswers saved to answers.json")
