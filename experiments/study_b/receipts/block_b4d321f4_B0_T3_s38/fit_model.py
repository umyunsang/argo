import json
import numpy as np
from scipy import stats

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'], dtype=np.float64)
y = np.array(data['y'], dtype=np.float64)

n_samples, n_features = X.shape
print(f"Data shape: {n_samples} samples, {n_features} features")

# Helper function to compute sigmoid with clipping
def sigmoid_clipped(z, clip_value=30):
    z = np.clip(z, -clip_value, clip_value)
    return 1 / (1 + np.exp(-z))

# Logistic regression with gradient descent
def fit_logistic(X_train, y_train, lambda_reg=0.0, n_iterations=200, learning_rate=0.1):
    """Fit logistic regression using full-batch gradient descent."""
    n = X_train.shape[0]
    d = X_train.shape[1]
    
    w = np.zeros(d, dtype=np.float64)
    b = 0.0
    
    for iteration in range(n_iterations):
        # Forward pass
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)
        probs = sigmoid_clipped(logits, clip_value=30)
        
        # Gradient computation
        errors = probs - y_train
        grad_w = (X_train.T @ errors) / n
        grad_b = np.sum(errors) / n
        
        # Update with L2 regularization
        w = w - learning_rate * (grad_w + lambda_reg * w)
        b = b - learning_rate * grad_b
    
    return w, b

def predict_proba(X, w, b):
    """Predict probability."""
    logits = X @ w + b
    logits = np.clip(logits, -30, 30)
    return sigmoid_clipped(logits, clip_value=30)

def brier_score(y_true, y_pred_proba):
    """Compute Brier score."""
    return np.mean((y_pred_proba - y_true) ** 2)

# Task 1: Find best lambda with cross-validation
print("\n=== Task 1: Finding best lambda ===")
lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
n_folds = 5
fold_size = n_samples // n_folds

# Dictionary to store CV scores for each lambda
cv_scores = {lam: [] for lam in lambdas}

for lam in lambdas:
    for fold_idx in range(n_folds):
        # Create fold: k-th consecutive slice
        test_indices = np.arange(fold_idx, n_samples, n_folds)
        train_indices = np.setdiff1d(np.arange(n_samples), test_indices)
        
        X_train, y_train = X[train_indices], y[train_indices]
        X_test, y_test = X[test_indices], y[test_indices]
        
        # Fit and evaluate
        w, b = fit_logistic(X_train, y_train, lambda_reg=lam)
        y_pred = predict_proba(X_test, w, b)
        score = brier_score(y_test, y_pred)
        cv_scores[lam].append(score)

# Compute mean CV scores
mean_cv_scores = {lam: np.mean(cv_scores[lam]) for lam in lambdas}
best_lambda = min(mean_cv_scores, key=mean_cv_scores.get)
baseline_brier = mean_cv_scores[0.0]
best_brier = mean_cv_scores[best_lambda]
improvement = baseline_brier - best_brier

print(f"Mean CV Brier scores: {mean_cv_scores}")
print(f"Best lambda: {best_lambda}")
print(f"Baseline (lambda=0): {baseline_brier:.6f}")
print(f"Best Brier: {best_brier:.6f}")
print(f"Improvement: {improvement:.6f}")

# Task 2: Interaction features and paired t-test
print("\n=== Task 2: Interaction features ===")
# Add interaction features: x0*x1, x1*x2, x2*x3, x0*x3
X_interactions = X.copy()
X_interactions = np.column_stack([
    X_interactions,
    X[:, 0] * X[:, 1],  # x0*x1
    X[:, 1] * X[:, 2],  # x1*x2
    X[:, 2] * X[:, 3],  # x2*x3
    X[:, 0] * X[:, 3]   # x0*x3
])

# Fit both models with lambda=0.1 and collect Brier scores per fold
raw_briers = []
interaction_briers = []

for fold_idx in range(n_folds):
    test_indices = np.arange(fold_idx, n_samples, n_folds)
    train_indices = np.setdiff1d(np.arange(n_samples), test_indices)
    
    # Raw model
    X_train_raw, y_train = X[train_indices], y[train_indices]
    X_test_raw, y_test = X[test_indices], y[test_indices]
    
    w_raw, b_raw = fit_logistic(X_train_raw, y_train, lambda_reg=0.1)
    y_pred_raw = predict_proba(X_test_raw, w_raw, b_raw)
    brier_raw = brier_score(y_test, y_pred_raw)
    raw_briers.append(brier_raw)
    
    # Interaction model
    X_train_int, y_train = X_interactions[train_indices], y[train_indices]
    X_test_int, y_test = X_interactions[test_indices], y[test_indices]
    
    w_int, b_int = fit_logistic(X_train_int, y_train, lambda_reg=0.1)
    y_pred_int = predict_proba(X_test_int, w_int, b_int)
    brier_int = brier_score(y_test, y_pred_int)
    interaction_briers.append(brier_int)

# Paired t-test
raw_briers = np.array(raw_briers)
interaction_briers = np.array(interaction_briers)
differences = raw_briers - interaction_briers

t_stat, p_value = stats.ttest_rel(raw_briers, interaction_briers)
print(f"Raw model Briers: {raw_briers}")
print(f"Interaction model Briers: {interaction_briers}")
print(f"Differences (raw - interaction): {differences}")
print(f"Paired t-statistic: {t_stat:.6f}")
print(f"P-value: {p_value:.6f}")
interaction_helps = t_stat > 2.0
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# Task 3: Compression - find best configuration
print("\n=== Task 3: Compression ===")
# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic(X, y, lambda_reg=0.1)
y_pred_dense = predict_proba(X, w_dense, b_dense)
dense_brier = brier_score(y, y_pred_dense)

print(f"Dense model in-sample Brier: {dense_brier:.6f}")

sparsity_levels = [20, 40, 60]
bits_levels = [8, 4]

best_retention = 0
best_config = None
results = []

for sparsity_pct in sparsity_levels:
    for bits in bits_levels:
        # Apply sparsity: zero out smallest magnitude weights
        k = round(sparsity_pct / 100.0 * len(w_dense))
        w_sparse = w_dense.copy()
        threshold_idx = np.argsort(np.abs(w_sparse))[: k]
        w_sparse[threshold_idx] = 0
        
        # Apply quantization to non-zero weights
        non_zero_mask = w_sparse != 0
        if np.sum(non_zero_mask) > 0:
            w_min = np.min(w_sparse[non_zero_mask])
            w_max = np.max(w_sparse[non_zero_mask])
            
            if w_min == w_max:
                # All non-zero weights are the same
                w_quantized = w_sparse.copy()
            else:
                # Map to 2^bits levels
                n_levels = 2 ** bits
                w_norm = (w_sparse[non_zero_mask] - w_min) / (w_max - w_min)
                w_quantized = w_sparse.copy()
                w_quantized[non_zero_mask] = np.round(w_norm * (n_levels - 1)) / (n_levels - 1) * (w_max - w_min) + w_min
        else:
            w_quantized = w_sparse.copy()
        
        # Compute compressed model Brier on full data
        y_pred_compressed = predict_proba(X, w_quantized, b_dense)
        compressed_brier = brier_score(y, y_pred_compressed)
        
        # Retention = dense_brier / compressed_brier (higher is better)
        retention = dense_brier / compressed_brier if compressed_brier > 0 else 0
        
        config_name = f"sparsity{sparsity_pct}_bits{bits}"
        results.append((config_name, sparsity_pct, bits, retention, dense_brier, compressed_brier))
        
        if retention > best_retention:
            best_retention = retention
            best_config = config_name
        
        print(f"{config_name}: retention={retention:.6f} (dense={dense_brier:.6f}, compressed={compressed_brier:.6f})")

print(f"\nBest compression config: {best_config}")
print(f"Best retention: {best_retention:.6f}")

# Write answers
answers = {
    "best_lambda": best_lambda,
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("\n=== Answers written to answers.json ===")
print(json.dumps(answers, indent=2))
