import json
import numpy as np
from scipy import stats

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'], dtype=np.float64)
y = np.array(data['y'], dtype=np.float64)

n_samples = X.shape[0]
n_features = X.shape[1]

print(f"Data shape: {X.shape}, Labels: {y.shape}")

# Helper functions for logistic regression
def sigmoid(z):
    return 1 / (1 + np.exp(-np.clip(z, -30, 30)))

def fit_logistic(X_train, y_train, lambda_reg=0.0, lr=0.1, iterations=200):
    """Fit logistic regression with full-batch gradient descent"""
    n, d = X_train.shape
    w = np.zeros(d)
    b = 0.0
    
    for _ in range(iterations):
        # Forward pass
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)
        probs = sigmoid(logits)
        
        # Gradients
        error = probs - y_train
        grad_w = X_train.T @ error / n
        grad_b = np.sum(error) / n
        
        # Update with L2 regularization
        w = w - lr * (grad_w + lambda_reg * w)
        b = b - lr * grad_b
    
    return w, b

def predict_proba(X_test, w, b):
    """Get predicted probabilities"""
    logits = X_test @ w + b
    logits = np.clip(logits, -30, 30)
    return sigmoid(logits)

def brier_score(y_true, y_pred_proba):
    """Compute Brier score"""
    return np.mean((y_pred_proba - y_true) ** 2)

# =============================================================================
# PART 1: Find best lambda
# =============================================================================
print("\n=== PART 1: Finding best lambda ===")

lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
n_folds = 5
fold_size = n_samples // n_folds

# Store CV scores
cv_scores = {lam: [] for lam in lambdas}

# 5-fold CV with contiguous blocks
for fold_idx in range(n_folds):
    # Create fold split: fold k is the k-th consecutive slice
    test_indices = np.arange(fold_idx, n_samples, n_folds)
    train_indices = np.setdiff1d(np.arange(n_samples), test_indices)
    
    X_train, X_test = X[train_indices], X[test_indices]
    y_train, y_test = y[train_indices], y[test_indices]
    
    for lam in lambdas:
        w, b = fit_logistic(X_train, y_train, lambda_reg=lam)
        y_pred = predict_proba(X_test, w, b)
        brier = brier_score(y_test, y_pred)
        cv_scores[lam].append(brier)

# Calculate mean CV scores
mean_cv_scores = {lam: np.mean(cv_scores[lam]) for lam in lambdas}
print("Mean CV Brier scores:")
for lam, score in mean_cv_scores.items():
    print(f"  lambda={lam}: {score:.6f}")

# Find best lambda
best_lambda = min(mean_cv_scores, key=mean_cv_scores.get)
best_cv_score = mean_cv_scores[best_lambda]
baseline_score = mean_cv_scores[0.0]
improvement = baseline_score - best_cv_score

print(f"\nBest lambda: {best_lambda}")
print(f"Best CV Brier: {best_cv_score:.6f}")
print(f"Baseline (lambda=0): {baseline_score:.6f}")
print(f"Improvement: {improvement:.6f}")

# =============================================================================
# PART 2: Interaction features and paired t-test
# =============================================================================
print("\n=== PART 2: Interaction features and paired t-test ===")

# Create interaction features
X_interaction = X.copy()
# Add products: x0*x1, x1*x2, x2*x3, x0*x3
X_interaction = np.hstack([X_interaction, 
                           (X[:, 0] * X[:, 1]).reshape(-1, 1),
                           (X[:, 1] * X[:, 2]).reshape(-1, 1),
                           (X[:, 2] * X[:, 3]).reshape(-1, 1),
                           (X[:, 0] * X[:, 3]).reshape(-1, 1)])

print(f"X_interaction shape: {X_interaction.shape}")

# Run paired t-test across 5 folds
brier_raw = []
brier_interaction = []

for fold_idx in range(n_folds):
    test_indices = np.arange(fold_idx, n_samples, n_folds)
    train_indices = np.setdiff1d(np.arange(n_samples), test_indices)
    
    # Raw features
    X_train_raw, X_test_raw = X[train_indices], X[test_indices]
    y_train, y_test = y[train_indices], y[test_indices]
    
    w_raw, b_raw = fit_logistic(X_train_raw, y_train, lambda_reg=0.1)
    y_pred_raw = predict_proba(X_test_raw, w_raw, b_raw)
    brier_raw.append(brier_score(y_test, y_pred_raw))
    
    # Interaction features
    X_train_inter, X_test_inter = X_interaction[train_indices], X_interaction[test_indices]
    w_inter, b_inter = fit_logistic(X_train_inter, y_train, lambda_reg=0.1)
    y_pred_inter = predict_proba(X_test_inter, w_inter, b_inter)
    brier_interaction.append(brier_score(y_test, y_pred_inter))

brier_raw = np.array(brier_raw)
brier_interaction = np.array(brier_interaction)

print(f"Brier scores (raw): {brier_raw}")
print(f"Brier scores (interaction): {brier_interaction}")

# Paired t-test: raw minus interaction
differences = brier_raw - brier_interaction
print(f"Differences (raw - interaction): {differences}")

# One-sample t-test
t_stat, p_value = stats.ttest_1samp(differences, 0)
print(f"Paired t-statistic: {t_stat:.6f}")
print(f"P-value: {p_value:.6f}")

interaction_helps = t_stat > 2.0
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# =============================================================================
# PART 3: Compression configurations
# =============================================================================
print("\n=== PART 3: Compression configurations ===")

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic(X, y, lambda_reg=0.1)
y_pred_dense = predict_proba(X, w_dense, b_dense)
dense_brier = brier_score(y, y_pred_dense)
print(f"Dense model in-sample Brier: {dense_brier:.6f}")

# Test compression configs
sparsity_levels = [20, 40, 60]  # percentages
bit_levels = [8, 4]

best_retention = -1
best_config = None
configs_results = []

for sparsity in sparsity_levels:
    for bits in bit_levels:
        # Apply sparsity: zero smallest magnitude weights
        w_sparse = w_dense.copy()
        k = max(1, round(sparsity / 100.0 * len(w_sparse)))
        threshold_idx = np.argsort(np.abs(w_sparse))[:(len(w_sparse) - k)]
        w_sparse[threshold_idx] = 0
        
        # Apply quantization to non-zero weights
        non_zero_mask = w_sparse != 0
        if np.any(non_zero_mask):
            w_min = np.min(w_sparse[non_zero_mask])
            w_max = np.max(w_sparse[non_zero_mask])
            
            if w_max > w_min:
                # Quantize to 2^bits levels
                levels = 2 ** bits
                w_quantized = w_sparse.copy()
                w_quantized[non_zero_mask] = np.round(
                    (w_sparse[non_zero_mask] - w_min) / (w_max - w_min) * (levels - 1)
                ) / (levels - 1) * (w_max - w_min) + w_min
            else:
                w_quantized = w_sparse
        else:
            w_quantized = w_sparse
        
        # Evaluate compressed model
        y_pred_compressed = predict_proba(X, w_quantized, b_dense)
        compressed_brier = brier_score(y, y_pred_compressed)
        
        # Retention = dense / compressed
        retention = dense_brier / (compressed_brier + 1e-10)
        
        config_name = f"sparsity{sparsity}_bits{bits}"
        configs_results.append((config_name, retention, compressed_brier))
        print(f"{config_name}: retention={retention:.6f}, compressed_brier={compressed_brier:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = config_name

print(f"\nBest compression config: {best_config}")
print(f"Best retention: {best_retention:.6f}")

# =============================================================================
# Write answers
# =============================================================================
answers = {
    "best_lambda": best_lambda,
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

print("\n=== FINAL ANSWERS ===")
print(json.dumps(answers, indent=2))

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("\nAnswers saved to answers.json")
