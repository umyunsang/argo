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

def sigmoid(z):
    """Sigmoid function"""
    return 1.0 / (1.0 + np.exp(-np.clip(z, -500, 500)))

def brier_score(y_true, y_pred):
    """Compute Brier score"""
    return np.mean((y_pred - y_true) ** 2)

def create_folds(n, n_splits=5):
    """Create contiguous folds: fold k contains indices k, k+n_splits, k+2*n_splits, ..."""
    folds = []
    for fold_idx in range(n_splits):
        test_indices = list(range(fold_idx, n, n_splits))
        train_indices = [i for i in range(n) if i not in test_indices]
        folds.append((train_indices, test_indices))
    return folds

def fit_logistic_regression(X_train, y_train, lambda_reg=0.0, n_iter=200, lr=0.1):
    """
    Fit logistic regression with full-batch gradient descent.
    Updates per step: w -= lr * (grad_w / n + lambda * w); b -= lr * (grad_b / n)
    """
    n, d = X_train.shape
    w = np.zeros(d)
    b = 0.0
    
    for iteration in range(n_iter):
        # Compute logits and clip them
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)
        
        # Compute predictions (probabilities)
        preds = sigmoid(logits)
        
        # Compute gradients
        residual = preds - y_train
        grad_w = X_train.T @ residual
        grad_b = np.sum(residual)
        
        # Update weights
        w = w - lr * (grad_w / n + lambda_reg * w)
        b = b - lr * (grad_b / n)
    
    return w, b

def predict(X, w, b):
    """Predict probabilities"""
    logits = X @ w + b
    logits = np.clip(logits, -30, 30)
    return sigmoid(logits)

# Task 1: Find best lambda
print("\n=== Task 1: Find best lambda ===")
lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
folds = create_folds(n_samples, n_splits=5)

cv_scores = {lam: [] for lam in lambdas}

for fold_idx, (train_idx, test_idx) in enumerate(folds):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    for lam in lambdas:
        w, b = fit_logistic_regression(X_train, y_train, lambda_reg=lam, n_iter=200, lr=0.1)
        y_pred = predict(X_test, w, b)
        brier = brier_score(y_test, y_pred)
        cv_scores[lam].append(brier)
        print(f"Fold {fold_idx}, lambda={lam}: Brier={brier:.6f}")

# Compute mean CV scores
mean_cv_scores = {lam: np.mean(cv_scores[lam]) for lam in lambdas}
print(f"\nMean CV Brier scores: {mean_cv_scores}")

best_lambda = min(lambdas, key=lambda x: mean_cv_scores[x])
baseline_brier = mean_cv_scores[0.0]
best_brier = mean_cv_scores[best_lambda]
improvement = baseline_brier - best_brier

print(f"Best lambda: {best_lambda}")
print(f"Baseline (lambda=0) Brier: {baseline_brier:.6f}")
print(f"Best Brier: {best_brier:.6f}")
print(f"Improvement: {improvement:.6f}")

# Task 2: Interaction features
print("\n=== Task 2: Interaction features ===")

# Add interaction features: x0*x1, x1*x2, x2*x3, x0*x3
X_with_interactions = np.hstack([
    X,
    X[:, 0:1] * X[:, 1:2],  # x0*x1
    X[:, 1:2] * X[:, 2:3],  # x1*x2
    X[:, 2:3] * X[:, 3:4],  # x2*x3
    X[:, 0:1] * X[:, 3:4],  # x0*x3
])

print(f"Original features: {X.shape[1]}, With interactions: {X_with_interactions.shape[1]}")

# Fit both models with lambda=0.1 on each fold and collect Brier scores
raw_briers = []
interaction_briers = []

for fold_idx, (train_idx, test_idx) in enumerate(folds):
    # Raw model
    X_train_raw = X[train_idx]
    X_test_raw = X[test_idx]
    y_train = y[train_idx]
    y_test = y[test_idx]
    
    w_raw, b_raw = fit_logistic_regression(X_train_raw, y_train, lambda_reg=0.1, n_iter=200, lr=0.1)
    y_pred_raw = predict(X_test_raw, w_raw, b_raw)
    brier_raw = brier_score(y_test, y_pred_raw)
    raw_briers.append(brier_raw)
    
    # Interaction model
    X_train_inter = X_with_interactions[train_idx]
    X_test_inter = X_with_interactions[test_idx]
    
    w_inter, b_inter = fit_logistic_regression(X_train_inter, y_train, lambda_reg=0.1, n_iter=200, lr=0.1)
    y_pred_inter = predict(X_test_inter, w_inter, b_inter)
    brier_inter = brier_score(y_test, y_pred_inter)
    interaction_briers.append(brier_inter)
    
    print(f"Fold {fold_idx}: Raw Brier={brier_raw:.6f}, Interaction Brier={brier_inter:.6f}")

# Paired t-test: raw minus interaction
raw_briers = np.array(raw_briers)
interaction_briers = np.array(interaction_briers)
differences = raw_briers - interaction_briers

t_stat, p_value = stats.ttest_rel(raw_briers, interaction_briers)
print(f"\nRaw Briers: {raw_briers}")
print(f"Interaction Briers: {interaction_briers}")
print(f"Differences (raw - interaction): {differences}")
print(f"Paired t-statistic: {t_stat:.6f}")
print(f"P-value: {p_value:.6f}")

interaction_helps = t_stat > 2.0
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# Task 3: Compression
print("\n=== Task 3: Compression ===")

# Fit dense model on all rows with lambda=0.1
w_dense, b_dense = fit_logistic_regression(X, y, lambda_reg=0.1, n_iter=200, lr=0.1)
y_pred_dense = predict(X, w_dense, b_dense)
dense_brier = brier_score(y, y_pred_dense)

print(f"Dense model (lambda=0.1) Brier on full data: {dense_brier:.6f}")

# Test all configurations
sparsities = [20, 40, 60]  # percent
bits_options = [8, 4]

retention_results = {}

for sparsity_pct in sparsities:
    for bits in bits_options:
        # Apply sparsity: zero out smallest magnitude weights
        w_compressed = w_dense.copy()
        n_weights = len(w_compressed)
        k = round(sparsity_pct / 100.0 * n_weights)  # number of weights to zero
        
        # Find indices of smallest magnitude weights
        magnitudes = np.abs(w_compressed)
        threshold_idx = np.argsort(magnitudes)[:k]
        w_compressed[threshold_idx] = 0
        
        # Apply quantization: map remaining weights to 2^bits levels
        w_nonzero = w_compressed[w_compressed != 0]
        
        if len(w_nonzero) > 0:
            w_min = np.min(w_nonzero)
            w_max = np.max(w_nonzero)
            
            if w_max > w_min:
                # Map to 2^bits levels
                levels = 2 ** bits
                w_quantized = w_compressed.copy()
                w_q_nonzero = w_quantized[w_quantized != 0]
                
                # Quantize non-zero weights
                quantized = np.round((w_q_nonzero - w_min) / (w_max - w_min) * (levels - 1))
                w_q_nonzero_reconstructed = w_min + quantized / (levels - 1) * (w_max - w_min)
                w_quantized[w_quantized != 0] = w_q_nonzero_reconstructed
                
                # Compute Brier score
                y_pred_compressed = predict(X, w_quantized, b_dense)
                compressed_brier = brier_score(y, y_pred_compressed)
                retention = dense_brier / compressed_brier
            else:
                retention = 1.0
        else:
            retention = 1.0
        
        config_name = f"sparsity{sparsity_pct}_bits{bits}"
        retention_results[config_name] = retention
        print(f"{config_name}: Retention = {retention:.6f}")

best_config = max(retention_results.keys(), key=lambda x: retention_results[x])
print(f"\nBest configuration (highest retention): {best_config}")
print(f"Retention: {retention_results[best_config]:.6f}")

# Write answers
answers = {
    "best_lambda": best_lambda,
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

print("\n=== Final Answers ===")
print(json.dumps(answers, indent=2))

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)
