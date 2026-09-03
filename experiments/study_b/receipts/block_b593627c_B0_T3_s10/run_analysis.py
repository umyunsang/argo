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

# === Helper functions ===

def sigmoid(z):
    """Sigmoid function with clipping"""
    z = np.clip(z, -30, 30)
    return 1 / (1 + np.exp(-z))

def brier_score(y_true, y_pred):
    """Brier score: mean((y_pred - y_true)^2)"""
    return np.mean((y_pred - y_true) ** 2)

def fit_logistic_gd(X_train, y_train, lambda_reg=0.0, iterations=200, lr=0.1):
    """
    Fit logistic regression using full-batch gradient descent.
    
    Update rule:
    w -= lr * (grad_w / n + lambda * w)
    b -= lr * (grad_b / n)
    """
    n = X_train.shape[0]
    d = X_train.shape[1]
    
    # Initialize weights and bias
    w = np.zeros(d)
    b = 0.0
    
    for iteration in range(iterations):
        # Compute logits and predictions
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)
        y_pred = sigmoid(logits)
        
        # Compute gradients
        error = y_pred - y_train
        grad_w = X_train.T @ error / n
        grad_b = np.sum(error) / n
        
        # Update weights with L2 regularization
        w = w - lr * (grad_w + lambda_reg * w)
        b = b - lr * grad_b
    
    return w, b

def predict(X, w, b):
    """Predict probabilities"""
    logits = X @ w + b
    logits = np.clip(logits, -30, 30)
    return sigmoid(logits)

# === PART 1: Find best lambda via 5-fold CV ===

lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
fold_size = n_samples // 5

cv_results = {}

for lam in lambdas:
    fold_scores = []
    
    for fold_idx in range(5):
        # Create fold: contiguous blocks in row order
        # fold k is the k-th consecutive slice (rows k, k+5, k+10, ...)
        test_indices = np.arange(fold_idx, n_samples, 5)
        train_indices = np.setdiff1d(np.arange(n_samples), test_indices)
        
        X_train, X_test = X[train_indices], X[test_indices]
        y_train, y_test = y[train_indices], y[test_indices]
        
        # Fit model
        w, b = fit_logistic_gd(X_train, y_train, lambda_reg=lam, iterations=200, lr=0.1)
        
        # Evaluate
        y_pred = predict(X_test, w, b)
        score = brier_score(y_test, y_pred)
        fold_scores.append(score)
    
    mean_score = np.mean(fold_scores)
    cv_results[lam] = mean_score
    print(f"Lambda {lam}: CV Brier = {mean_score:.6f} (folds: {[f'{s:.6f}' for s in fold_scores]})")

# Find best lambda
best_lambda = min(cv_results, key=cv_results.get)
best_brier = cv_results[best_lambda]
baseline_brier = cv_results[0.0]
improvement = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda} with Brier = {best_brier:.6f}")
print(f"Baseline (lambda=0): {baseline_brier:.6f}")
print(f"Improvement: {improvement:.6f}")

# === PART 2: Test interaction features ===

# Add interaction features: x0*x1, x1*x2, x2*x3, x0*x3
X_base = X.copy()
X_interact = np.column_stack([
    X[:, 0] * X[:, 1],  # x0*x1
    X[:, 1] * X[:, 2],  # x1*x2
    X[:, 2] * X[:, 3],  # x2*x3
    X[:, 0] * X[:, 3],  # x0*x3
])
X_with_interact = np.column_stack([X_base, X_interact])

print(f"\nBase features: {X_base.shape[1]}")
print(f"Interaction features: {X_interact.shape[1]}")
print(f"Combined features: {X_with_interact.shape[1]}")

lambda_interact = 0.1

# 5-fold CV for both models
base_fold_briers = []
interact_fold_briers = []

for fold_idx in range(5):
    test_indices = np.arange(fold_idx, n_samples, 5)
    train_indices = np.setdiff1d(np.arange(n_samples), test_indices)
    
    # Base model
    X_train_base, X_test_base = X_base[train_indices], X_base[test_indices]
    y_train, y_test = y[train_indices], y[test_indices]
    
    w_base, b_base = fit_logistic_gd(X_train_base, y_train, lambda_reg=lambda_interact, 
                                     iterations=200, lr=0.1)
    y_pred_base = predict(X_test_base, w_base, b_base)
    brier_base = brier_score(y_test, y_pred_base)
    base_fold_briers.append(brier_base)
    
    # Model with interactions
    X_train_interact, X_test_interact = X_with_interact[train_indices], X_with_interact[test_indices]
    
    w_interact, b_interact = fit_logistic_gd(X_train_interact, y_train, lambda_reg=lambda_interact,
                                             iterations=200, lr=0.1)
    y_pred_interact = predict(X_test_interact, w_interact, b_interact)
    brier_interact = brier_score(y_test, y_pred_interact)
    interact_fold_briers.append(brier_interact)
    
    print(f"Fold {fold_idx}: Base Brier = {brier_base:.6f}, Interact Brier = {brier_interact:.6f}")

# Paired t-test: raw minus interaction Brier per fold
diffs = np.array(base_fold_briers) - np.array(interact_fold_briers)
print(f"\nDifferences (base - interact): {diffs}")
print(f"Mean difference: {np.mean(diffs):.6f}")

t_stat, p_value = stats.ttest_rel(base_fold_briers, interact_fold_briers)
print(f"Paired t-test t-statistic: {t_stat:.6f}")
print(f"Paired t-test p-value: {p_value:.6f}")

interaction_helps = (t_stat > 2.0)
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# === PART 3: Compression (sparsity and quantization) ===

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic_gd(X_base, y, lambda_reg=0.1, iterations=200, lr=0.1)
y_pred_dense = predict(X_base, w_dense, b_dense)
dense_brier = brier_score(y, y_pred_dense)

print(f"\n=== COMPRESSION ANALYSIS ===")
print(f"Dense model in-sample Brier: {dense_brier:.6f}")

sparsities = [20, 40, 60]  # percentage
bits = [8, 4]

best_retention = -1.0
best_config = None

for sparsity_pct in sparsities:
    for bit_depth in bits:
        # Apply sparsity: zero out smallest magnitude weights
        w_sparse = w_dense.copy()
        k = round((sparsity_pct / 100.0) * len(w_dense))
        
        if k > 0:
            # Find indices of k smallest magnitude weights
            abs_w = np.abs(w_sparse)
            threshold_idx = np.argsort(abs_w)[:k]
            w_sparse[threshold_idx] = 0.0
        
        # Apply quantization: map remaining weights to 2^bits levels
        w_quant = w_sparse.copy()
        nonzero_mask = w_quant != 0
        
        if np.any(nonzero_mask):
            w_min = np.min(w_quant[nonzero_mask])
            w_max = np.max(w_quant[nonzero_mask])
            
            if w_min < w_max:
                # Quantize
                n_levels = 2 ** bit_depth
                w_quant[nonzero_mask] = np.round(
                    (w_quant[nonzero_mask] - w_min) / (w_max - w_min) * (n_levels - 1)
                ) / (n_levels - 1) * (w_max - w_min) + w_min
        
        # Evaluate compressed model
        y_pred_compressed = predict(X_base, w_quant, b_dense)
        compressed_brier = brier_score(y, y_pred_compressed)
        
        # Retention: dense Brier / compressed Brier
        if compressed_brier > 0:
            retention = dense_brier / compressed_brier
        else:
            retention = float('inf')
        
        config_name = f"sparsity{sparsity_pct}_bits{bit_depth}"
        print(f"{config_name}: compressed Brier = {compressed_brier:.6f}, retention = {retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = config_name

print(f"\nBest compression config: {best_config} with retention = {best_retention:.6f}")

# === Write answers ===

answers = {
    "best_lambda": best_lambda,
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("\n" + "="*50)
print("FINAL ANSWERS:")
print(json.dumps(answers, indent=2))
