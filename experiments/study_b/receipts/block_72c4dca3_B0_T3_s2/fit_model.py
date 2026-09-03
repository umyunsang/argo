import json
import numpy as np
from scipy import stats

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'])
y = np.array(data['y'])

n_samples = X.shape[0]
n_features = X.shape[1]

print(f"Data shape: X={X.shape}, y={y.shape}")

# ============================================================================
# TASK 1: Find best lambda with 5-fold CV
# ============================================================================

def logistic_loss_and_grad(X_batch, y_batch, w, b, lambda_reg):
    """Compute logistic loss and gradients."""
    logits = X_batch @ w + b
    # Clip logits to [-30, 30]
    logits = np.clip(logits, -30, 30)
    
    # Probability
    probs = 1.0 / (1.0 + np.exp(-logits))
    
    # Cross-entropy loss
    eps = 1e-15
    loss = -np.mean(y_batch * np.log(probs + eps) + (1 - y_batch) * np.log(1 - probs + eps))
    
    # L2 regularization
    loss += (lambda_reg / 2) * np.sum(w ** 2)
    
    # Gradients
    grad_w = (X_batch.T @ (probs - y_batch)) / len(y_batch) + lambda_reg * w
    grad_b = np.mean(probs - y_batch)
    
    return loss, grad_w, grad_b, probs

def fit_logistic_regression(X_train, y_train, lambda_reg=0.0, learning_rate=0.1, n_iters=200):
    """Fit logistic regression with full-batch gradient descent."""
    n_samples = X_train.shape[0]
    n_features = X_train.shape[1]
    
    # Initialize weights and bias at 0
    w = np.zeros(n_features)
    b = 0.0
    
    # Full-batch gradient descent
    for iteration in range(n_iters):
        loss, grad_w, grad_b, _ = logistic_loss_and_grad(X_train, y_train, w, b, lambda_reg)
        
        # Update weights and bias
        w -= learning_rate * (grad_w / n_samples + lambda_reg * w)
        b -= learning_rate * grad_b
    
    return w, b

def predict_proba(X, w, b):
    """Predict probabilities."""
    logits = X @ w + b
    logits = np.clip(logits, -30, 30)
    probs = 1.0 / (1.0 + np.exp(-logits))
    return probs

def brier_score(y_true, y_pred_proba):
    """Compute Brier score."""
    return np.mean((y_true - y_pred_proba) ** 2)

# Create 5 contiguous folds
fold_size = n_samples // 5
folds = []
for k in range(5):
    indices = np.arange(k, n_samples, 5)  # k, k+5, k+10, ...
    folds.append(indices)

print(f"\nFold sizes: {[len(f) for f in folds]}")

lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
cv_results = {}

for lam in lambdas:
    brier_scores = []
    for fold_idx in range(5):
        # Get train and test indices
        test_indices = folds[fold_idx]
        train_indices = np.concatenate([folds[i] for i in range(5) if i != fold_idx])
        
        X_train, y_train = X[train_indices], y[train_indices]
        X_test, y_test = X[test_indices], y[test_indices]
        
        # Fit model
        w, b = fit_logistic_regression(X_train, y_train, lambda_reg=lam, learning_rate=0.1, n_iters=200)
        
        # Evaluate on test fold
        y_pred_proba = predict_proba(X_test, w, b)
        brier = brier_score(y_test, y_pred_proba)
        brier_scores.append(brier)
    
    mean_brier = np.mean(brier_scores)
    cv_results[lam] = {
        'mean': mean_brier,
        'fold_scores': brier_scores
    }
    print(f"Lambda={lam}: mean Brier={mean_brier:.6f}, fold scores={brier_scores}")

# Find best lambda
best_lambda = min(cv_results.keys(), key=lambda l: cv_results[l]['mean'])
best_brier = cv_results[best_lambda]['mean']
baseline_brier = cv_results[0.0]['mean']
improvement = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda} with mean Brier={best_brier:.6f}")
print(f"Baseline (lambda=0) Brier: {baseline_brier:.6f}")
print(f"Improvement: {improvement:.6f}")

# ============================================================================
# TASK 2: Test interaction features with paired t-test
# ============================================================================

def add_interaction_features(X):
    """Add interaction features: x0*x1, x1*x2, x2*x3, x0*x3."""
    n_samples = X.shape[0]
    interactions = np.column_stack([
        X[:, 0] * X[:, 1],
        X[:, 1] * X[:, 2],
        X[:, 2] * X[:, 3],
        X[:, 0] * X[:, 3]
    ])
    return np.column_stack([X, interactions])

# Fit both representations with lambda=0.1 and run paired t-test
lambda_test = 0.1
brier_raw_folds = []
brier_interaction_folds = []

for fold_idx in range(5):
    test_indices = folds[fold_idx]
    train_indices = np.concatenate([folds[i] for i in range(5) if i != fold_idx])
    
    X_train, y_train = X[train_indices], y[train_indices]
    X_test, y_test = X[test_indices], y[test_indices]
    
    # Raw model
    w_raw, b_raw = fit_logistic_regression(X_train, y_train, lambda_reg=lambda_test, learning_rate=0.1, n_iters=200)
    y_pred_raw = predict_proba(X_test, w_raw, b_raw)
    brier_raw = brier_score(y_test, y_pred_raw)
    brier_raw_folds.append(brier_raw)
    
    # Interaction model
    X_train_inter = add_interaction_features(X_train)
    X_test_inter = add_interaction_features(X_test)
    w_inter, b_inter = fit_logistic_regression(X_train_inter, y_train, lambda_reg=lambda_test, learning_rate=0.1, n_iters=200)
    y_pred_inter = predict_proba(X_test_inter, w_inter, b_inter)
    brier_inter = brier_score(y_test, y_pred_inter)
    brier_interaction_folds.append(brier_inter)

print(f"\nInteraction features test (lambda={lambda_test}):")
print(f"Raw model Brier per fold: {brier_raw_folds}")
print(f"Interaction model Brier per fold: {brier_interaction_folds}")

# Paired t-test: raw minus interaction
differences = np.array(brier_raw_folds) - np.array(brier_interaction_folds)
t_stat, p_value = stats.ttest_rel(brier_raw_folds, brier_interaction_folds)

print(f"Differences (raw - interaction): {differences}")
print(f"Mean difference: {np.mean(differences):.6f}")
print(f"Paired t-statistic: {t_stat:.6f}")
print(f"P-value: {p_value:.6f}")

interaction_helps = t_stat > 2.0
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# ============================================================================
# TASK 3: Model compression (sparsity + quantization)
# ============================================================================

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic_regression(X, y, lambda_reg=0.1, learning_rate=0.1, n_iters=200)
y_pred_dense = predict_proba(X, w_dense, b_dense)
brier_dense = brier_score(y, y_pred_dense)

print(f"\nDense model (lambda=0.1) Brier on all data: {brier_dense:.6f}")

sparsity_levels = [20, 40, 60]
bit_levels = [8, 4]

best_retention = -1
best_config_str = None
retention_results = {}

for sparsity in sparsity_levels:
    for bits in bit_levels:
        # Apply sparsity: zero out smallest magnitude weights
        w_sparse = w_dense.copy()
        k = round((sparsity / 100) * len(w_dense))
        threshold_idx = np.argsort(np.abs(w_sparse))[k]
        threshold = np.abs(w_sparse)[threshold_idx]
        w_sparse[np.abs(w_sparse) <= threshold] = 0
        
        # Apply quantization to remaining weights
        w_quant = w_sparse.copy()
        nonzero_mask = w_sparse != 0
        if np.any(nonzero_mask):
            w_min = np.min(w_sparse[nonzero_mask])
            w_max = np.max(w_sparse[nonzero_mask])
            
            # Map to 2^bits levels
            n_levels = 2 ** bits
            if w_max > w_min:
                w_quant_norm = (w_sparse[nonzero_mask] - w_min) / (w_max - w_min)
                w_quant_levels = np.round(w_quant_norm * (n_levels - 1)) / (n_levels - 1)
                w_quant[nonzero_mask] = w_quant_levels * (w_max - w_min) + w_min
            else:
                w_quant[nonzero_mask] = w_min
        
        # Evaluate compressed model
        y_pred_compressed = predict_proba(X, w_quant, b_dense)
        brier_compressed = brier_score(y, y_pred_compressed)
        
        # Retention = dense Brier / compressed Brier
        retention = brier_dense / brier_compressed if brier_compressed > 0 else float('inf')
        
        config_str = f"sparsity{sparsity}_bits{bits}"
        retention_results[config_str] = {
            'retention': retention,
            'dense_brier': brier_dense,
            'compressed_brier': brier_compressed
        }
        
        print(f"Config {config_str}: dense_brier={brier_dense:.6f}, compressed_brier={brier_compressed:.6f}, retention={retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config_str = config_str

print(f"\nBest compression config: {best_config_str} with retention={best_retention:.6f}")

# ============================================================================
# Write answers to JSON
# ============================================================================

answers = {
    "best_lambda": best_lambda,
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config_str
}

print(f"\n{'='*60}")
print("FINAL ANSWERS:")
print(json.dumps(answers, indent=2))

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)
