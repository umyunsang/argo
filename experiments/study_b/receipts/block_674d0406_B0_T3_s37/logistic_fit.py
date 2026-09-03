import json
import numpy as np
from scipy import stats

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'])
y = np.array(data['y']).astype(float)

n_samples = X.shape[0]
n_features = X.shape[1]
n_folds = 5

print(f"Data shape: X={X.shape}, y={y.shape}")
print(f"Sample count: {n_samples}, Features: {n_features}")

# ============================================================================
# Task 1: Find best lambda using 5-fold CV with Brier score
# ============================================================================

def sigmoid(z):
    """Sigmoid with clipping."""
    z = np.clip(z, -30, 30)
    return 1.0 / (1.0 + np.exp(-z))

def brier_score(y_true, y_pred):
    """Brier score: mean squared error."""
    return np.mean((y_pred - y_true) ** 2)

def fit_logistic_regression(X_train, y_train, lambda_reg=0.0, learning_rate=0.1, n_iter=200):
    """
    Full-batch gradient descent for logistic regression.
    w and b start at 0.
    Update: w -= lr * (grad_w / n + lambda * w)
            b -= lr * (grad_b / n)
    """
    n = X_train.shape[0]
    d = X_train.shape[1]
    
    w = np.zeros(d)
    b = 0.0
    
    for _ in range(n_iter):
        # Forward pass
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)
        probs = sigmoid(logits)
        
        # Gradient
        error = probs - y_train
        grad_w = X_train.T @ error
        grad_b = np.sum(error)
        
        # Update
        w -= learning_rate * (grad_w / n + lambda_reg * w)
        b -= learning_rate * (grad_b / n)
    
    return w, b

def predict_logistic(X_test, w, b):
    """Predict probabilities."""
    logits = X_test @ w + b
    logits = np.clip(logits, -30, 30)
    return sigmoid(logits)

# 5-fold CV with different lambdas
lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
cv_results = {}

for lambda_reg in lambdas:
    fold_scores = []
    
    for fold_idx in range(n_folds):
        # Create contiguous folds
        fold_size = n_samples // n_folds
        test_start = fold_idx * fold_size
        test_end = (fold_idx + 1) * fold_size
        
        # Handle last fold
        if fold_idx == n_folds - 1:
            test_end = n_samples
        
        test_idx = np.arange(test_start, test_end)
        train_idx = np.concatenate([np.arange(0, test_start), np.arange(test_end, n_samples)])
        
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Fit model
        w, b = fit_logistic_regression(X_train, y_train, lambda_reg=lambda_reg)
        
        # Evaluate
        y_pred = predict_logistic(X_test, w, b)
        brier = brier_score(y_test, y_pred)
        fold_scores.append(brier)
    
    mean_score = np.mean(fold_scores)
    cv_results[lambda_reg] = {
        'mean_brier': mean_score,
        'fold_scores': fold_scores
    }
    print(f"Lambda={lambda_reg}: Mean Brier={mean_score:.6f}, Fold scores={fold_scores}")

# Find best lambda
best_lambda = min(lambdas, key=lambda l: cv_results[l]['mean_brier'])
best_brier = cv_results[best_lambda]['mean_brier']
baseline_brier = cv_results[0.0]['mean_brier']
improvement = baseline_brier - best_brier

print(f"\nTask 1 Results:")
print(f"Best lambda: {best_lambda}")
print(f"Best Brier: {best_brier:.6f}")
print(f"Baseline (lambda=0) Brier: {baseline_brier:.6f}")
print(f"Improvement: {improvement:.6f}")

# ============================================================================
# Task 2: Interaction features with lambda=0.1
# ============================================================================

print(f"\nTask 2: Testing interaction features with lambda=0.1")

# Create interaction features
X_with_interactions = X.copy()
# Add x0*x1, x1*x2, x2*x3, x0*x3
x01 = X[:, 0] * X[:, 1]
x12 = X[:, 1] * X[:, 2]
x23 = X[:, 2] * X[:, 3]
x03 = X[:, 0] * X[:, 3]

X_interactions = np.column_stack([X_with_interactions, x01, x12, x23, x03])
print(f"X_interactions shape: {X_interactions.shape}")

# 5-fold CV for both representations
lambda_test = 0.1
raw_brier_scores = []
interaction_brier_scores = []

for fold_idx in range(n_folds):
    fold_size = n_samples // n_folds
    test_start = fold_idx * fold_size
    test_end = (fold_idx + 1) * fold_size
    
    if fold_idx == n_folds - 1:
        test_end = n_samples
    
    test_idx = np.arange(test_start, test_end)
    train_idx = np.concatenate([np.arange(0, test_start), np.arange(test_end, n_samples)])
    
    # Raw model
    X_train_raw, X_test_raw = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    w_raw, b_raw = fit_logistic_regression(X_train_raw, y_train, lambda_reg=lambda_test)
    y_pred_raw = predict_logistic(X_test_raw, w_raw, b_raw)
    brier_raw = brier_score(y_test, y_pred_raw)
    raw_brier_scores.append(brier_raw)
    
    # Interaction model
    X_train_int, X_test_int = X_interactions[train_idx], X_interactions[test_idx]
    w_int, b_int = fit_logistic_regression(X_train_int, y_train, lambda_reg=lambda_test)
    y_pred_int = predict_logistic(X_test_int, w_int, b_int)
    brier_int = brier_score(y_test, y_pred_int)
    interaction_brier_scores.append(brier_int)

raw_brier_scores = np.array(raw_brier_scores)
interaction_brier_scores = np.array(interaction_brier_scores)

# Paired t-test: raw minus interaction
differences = raw_brier_scores - interaction_brier_scores
t_stat, p_value = stats.ttest_rel(raw_brier_scores, interaction_brier_scores)

interaction_helps = t_stat > 2.0

print(f"Raw Brier scores per fold: {raw_brier_scores}")
print(f"Interaction Brier scores per fold: {interaction_brier_scores}")
print(f"Differences (raw - interaction): {differences}")
print(f"Paired t-test statistic: {t_stat:.6f}")
print(f"P-value: {p_value:.6f}")
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# ============================================================================
# Task 3: Compression with different sparsity and bits
# ============================================================================

print(f"\nTask 3: Compression configurations")

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic_regression(X, y, lambda_reg=0.1)
y_pred_dense = predict_logistic(X, w_dense, b_dense)
dense_brier = brier_score(y, y_pred_dense)

print(f"Dense model Brier (in-sample): {dense_brier:.6f}")

sparsity_percents = [20, 40, 60]
bits_list = [8, 4]
best_retention = 0
best_config = None

for sparsity_pct in sparsity_percents:
    for bits in bits_list:
        # Apply sparsity
        w_sparse = w_dense.copy()
        k = round(sparsity_pct * len(w_sparse) / 100)
        # Zero smallest magnitude weights
        magnitude_idx = np.argsort(np.abs(w_sparse))
        w_sparse[magnitude_idx[:k]] = 0
        
        # Apply quantization to non-zero weights
        nonzero_mask = w_sparse != 0
        if np.sum(nonzero_mask) > 0:
            w_min = np.min(w_sparse[nonzero_mask])
            w_max = np.max(w_sparse[nonzero_mask])
            if w_max > w_min:
                # Map to 2^bits levels
                n_levels = 2 ** bits
                w_quantized = np.zeros_like(w_sparse)
                w_quantized[nonzero_mask] = np.round(
                    (w_sparse[nonzero_mask] - w_min) / (w_max - w_min) * (n_levels - 1)
                ) / (n_levels - 1) * (w_max - w_min) + w_min
            else:
                w_quantized = w_sparse
        else:
            w_quantized = w_sparse
        
        # Evaluate compressed model
        y_pred_compressed = predict_logistic(X, w_quantized, b_dense)
        compressed_brier = brier_score(y, y_pred_compressed)
        
        # Retention = dense_brier / compressed_brier
        retention = dense_brier / compressed_brier if compressed_brier > 0 else 0
        
        config_name = f"sparsity{sparsity_pct}_bits{bits}"
        print(f"{config_name}: Compressed Brier={compressed_brier:.6f}, Retention={retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = config_name

print(f"\nBest compression config: {best_config}")
print(f"Best retention: {best_retention:.6f}")

# ============================================================================
# Write results
# ============================================================================

results = {
    "best_lambda": float(best_lambda),
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": str(best_config)
}

with open('answers.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n" + "="*60)
print("FINAL RESULTS")
print("="*60)
print(json.dumps(results, indent=2))
