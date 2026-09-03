import json
import numpy as np
from scipy import stats

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'], dtype=np.float64)
y = np.array(data['y'], dtype=np.float64)

n_samples, n_features = X.shape
n_folds = 5
fold_size = n_samples // n_folds

def create_folds(X, y, n_folds):
    """Create contiguous folds without shuffling."""
    folds = []
    fold_size = len(X) // n_folds
    for k in range(n_folds):
        start_idx = k * fold_size
        if k == n_folds - 1:
            end_idx = len(X)
        else:
            end_idx = (k + 1) * fold_size
        
        test_idx = np.arange(start_idx, end_idx)
        train_idx = np.concatenate([np.arange(0, start_idx), np.arange(end_idx, len(X))])
        
        folds.append({
            'train_idx': train_idx,
            'test_idx': test_idx
        })
    return folds

def sigmoid(z):
    """Sigmoid with clipping to prevent overflow."""
    z = np.clip(z, -30, 30)
    return 1.0 / (1.0 + np.exp(-z))

def brier_score(y_true, y_pred):
    """Compute Brier score."""
    return np.mean((y_true - y_pred) ** 2)

def fit_logistic_regression(X, y, lambda_reg, n_iter=200, lr=0.1):
    """Fit logistic regression with gradient descent."""
    n_samples, n_features = X.shape
    w = np.zeros(n_features)
    b = 0.0
    
    for iteration in range(n_iter):
        # Forward pass
        logits = X @ w + b
        logits = np.clip(logits, -30, 30)
        probs = sigmoid(logits)
        
        # Backward pass (gradient computation)
        errors = probs - y
        grad_w = X.T @ errors / n_samples + lambda_reg * w
        grad_b = np.sum(errors) / n_samples
        
        # Update
        w -= lr * grad_w
        b -= lr * grad_b
    
    return w, b

def predict_proba(X, w, b):
    """Predict probability."""
    logits = X @ w + b
    logits = np.clip(logits, -30, 30)
    return sigmoid(logits)

# ============================================================
# Question 1: Find best lambda
# ============================================================
lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
folds = create_folds(X, y, n_folds)

brier_scores_per_lambda = {}
for lam in lambdas:
    brier_scores = []
    for fold in folds:
        train_idx = fold['train_idx']
        test_idx = fold['test_idx']
        
        X_train, y_train = X[train_idx], y[train_idx]
        X_test, y_test = X[test_idx], y[test_idx]
        
        w, b = fit_logistic_regression(X_train, y_train, lam)
        y_pred = predict_proba(X_test, w, b)
        brier = brier_score(y_test, y_pred)
        brier_scores.append(brier)
    
    brier_scores_per_lambda[lam] = brier_scores

# Find best lambda
mean_brier_scores = {lam: np.mean(scores) for lam, scores in brier_scores_per_lambda.items()}
best_lambda = min(mean_brier_scores, key=mean_brier_scores.get)
best_brier = mean_brier_scores[best_lambda]
baseline_brier = mean_brier_scores[0.0]
improvement = baseline_brier - best_brier

print(f"Question 1:")
print(f"  Best lambda: {best_lambda}")
print(f"  Mean Brier scores per lambda: {mean_brier_scores}")
print(f"  Best Brier: {best_brier}")
print(f"  Baseline Brier (lambda=0): {baseline_brier}")
print(f"  Improvement: {improvement}")
print()

# ============================================================
# Question 2: Interaction features and paired t-test
# ============================================================

# Create interaction features
X_with_interactions = np.column_stack([
    X,
    X[:, 0] * X[:, 1],  # x0 * x1
    X[:, 1] * X[:, 2],  # x1 * x2
    X[:, 2] * X[:, 3],  # x2 * x3
    X[:, 0] * X[:, 3]   # x0 * x3
])

lambda_test = 0.1
raw_brier_scores = []
interaction_brier_scores = []

for fold in folds:
    train_idx = fold['train_idx']
    test_idx = fold['test_idx']
    
    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]
    
    X_train_interactions = np.column_stack([
        X_train,
        X_train[:, 0] * X_train[:, 1],
        X_train[:, 1] * X_train[:, 2],
        X_train[:, 2] * X_train[:, 3],
        X_train[:, 0] * X_train[:, 3]
    ])
    
    X_test_interactions = np.column_stack([
        X_test,
        X_test[:, 0] * X_test[:, 1],
        X_test[:, 1] * X_test[:, 2],
        X_test[:, 2] * X_test[:, 3],
        X_test[:, 0] * X_test[:, 3]
    ])
    
    # Fit raw model
    w_raw, b_raw = fit_logistic_regression(X_train, y_train, lambda_test)
    y_pred_raw = predict_proba(X_test, w_raw, b_raw)
    brier_raw = brier_score(y_test, y_pred_raw)
    raw_brier_scores.append(brier_raw)
    
    # Fit model with interactions
    w_int, b_int = fit_logistic_regression(X_train_interactions, y_train, lambda_test)
    y_pred_int = predict_proba(X_test_interactions, w_int, b_int)
    brier_int = brier_score(y_test, y_pred_int)
    interaction_brier_scores.append(brier_int)

# Paired t-test
differences = np.array(raw_brier_scores) - np.array(interaction_brier_scores)
t_stat, p_value = stats.ttest_rel(raw_brier_scores, interaction_brier_scores)

interaction_helps = t_stat > 2.0

print(f"Question 2:")
print(f"  Raw Brier scores per fold: {raw_brier_scores}")
print(f"  Interaction Brier scores per fold: {interaction_brier_scores}")
print(f"  Differences (raw - interaction): {differences}")
print(f"  Paired t-statistic: {t_stat}")
print(f"  Interaction helps (t > 2.0): {interaction_helps}")
print()

# ============================================================
# Question 3: Compression (sparsity + quantization)
# ============================================================

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic_regression(X, y, 0.1)

# In-sample predictions for dense model
y_pred_dense = predict_proba(X, w_dense, b_dense)
dense_brier = brier_score(y, y_pred_dense)

# Test different compression configurations
sparsities = [20, 40, 60]  # percentages
bits_options = [8, 4]

best_config = None
best_retention = 0

config_results = {}

for sparsity_pct in sparsities:
    for bits in bits_options:
        # Apply sparsity
        k = round(sparsity_pct / 100.0 * n_features)
        w_sparse = w_dense.copy()
        
        # Zero out smallest magnitude weights
        threshold_idx = np.argsort(np.abs(w_sparse))[:-k if k > 0 else None]
        w_sparse[threshold_idx] = 0
        
        # Apply quantization to non-zero weights
        nonzero_mask = w_sparse != 0
        if np.any(nonzero_mask):
            w_nonzero = w_sparse[nonzero_mask]
            w_min = np.min(w_nonzero)
            w_max = np.max(w_nonzero)
            
            if w_min == w_max:
                # All same value, no quantization needed
                w_quantized = w_sparse.copy()
            else:
                # Map to 2^bits levels
                levels = np.linspace(w_min, w_max, 2**bits)
                w_quantized = w_sparse.copy()
                # Find nearest level for each non-zero weight
                nearest_levels = np.zeros_like(w_nonzero)
                for i, val in enumerate(w_nonzero):
                    nearest_levels[i] = levels[np.argmin(np.abs(levels - val))]
                w_quantized[nonzero_mask] = nearest_levels
        else:
            w_quantized = w_sparse.copy()
        
        # Evaluate compressed model
        y_pred_compressed = predict_proba(X, w_quantized, b_dense)
        compressed_brier = brier_score(y, y_pred_compressed)
        
        # Compute retention
        retention = dense_brier / compressed_brier if compressed_brier > 0 else 0
        
        config_name = f"sparsity{sparsity_pct}_bits{bits}"
        config_results[config_name] = {
            'retention': retention,
            'dense_brier': dense_brier,
            'compressed_brier': compressed_brier
        }
        
        if retention > best_retention:
            best_retention = retention
            best_config = config_name

print(f"Question 3:")
print(f"  Dense model Brier score (all data): {dense_brier}")
print(f"  Configuration results:")
for config_name, results in sorted(config_results.items()):
    print(f"    {config_name}: retention={results['retention']:.6f}, "
          f"compressed_brier={results['compressed_brier']:.6f}")
print(f"  Best config: {best_config}")
print(f"  Best retention: {best_retention}")
print()

# ============================================================
# Write answers
# ============================================================

answers = {
    "best_lambda": float(best_lambda),
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": str(best_config)
}

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("Answers written to answers.json:")
print(json.dumps(answers, indent=2))
