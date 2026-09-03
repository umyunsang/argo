import json
import numpy as np
from scipy import stats

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'], dtype=np.float64)
y = np.array(data['y'], dtype=np.int32)

n_samples, n_features = X.shape
print(f"Data shape: {n_samples} samples, {n_features} features")

def sigmoid(z):
    """Sigmoid function with clipping to avoid overflow"""
    z = np.clip(z, -30, 30)
    return 1.0 / (1.0 + np.exp(-z))

def compute_brier_score(y_true, y_pred_proba):
    """Compute Brier score: mean((pred - y)^2)"""
    return np.mean((y_pred_proba - y_true) ** 2)

def fit_logistic(X, y, lambda_reg=0.0, n_iter=200, learning_rate=0.1):
    """
    Fit logistic regression with specified constraints.
    Returns weights, bias, and training history.
    """
    n_samples, n_features = X.shape
    
    # Initialize weights and bias at 0
    w = np.zeros(n_features, dtype=np.float64)
    b = 0.0
    
    history = []
    
    # Gradient descent for n_iter iterations
    for iteration in range(n_iter):
        # Compute logits (clipped)
        logits = np.dot(X, w) + b
        logits = np.clip(logits, -30, 30)
        
        # Compute predictions
        y_pred = sigmoid(logits)
        
        # Compute gradients (cross-entropy loss)
        # grad_w = X.T @ (y_pred - y) / n + lambda * w
        # grad_b = (y_pred - y).sum() / n
        error = y_pred - y
        grad_w = np.dot(X.T, error) / n_samples + lambda_reg * w
        grad_b = np.sum(error) / n_samples
        
        # Update weights and bias
        w = w - learning_rate * grad_w
        b = b - learning_rate * grad_b
        
        # Compute Brier score for monitoring
        brier = compute_brier_score(y, y_pred)
        history.append(brier)
    
    return w, b, history

def predict_logistic(X, w, b):
    """Predict probabilities"""
    logits = np.dot(X, w) + b
    logits = np.clip(logits, -30, 30)
    return sigmoid(logits)

# ============ Task 1: Find best lambda ============
print("\n" + "="*60)
print("Task 1: Find best lambda from [0.0, 0.01, 0.1, 1.0, 10.0]")
print("="*60)

lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
n_folds = 5
fold_size = n_samples // n_folds

# 5-fold cross-validation
cv_scores = {lam: [] for lam in lambdas}

for fold_idx in range(n_folds):
    # Create fold indices: fold k = k-th consecutive slice
    test_start = fold_idx * fold_size
    test_end = test_start + fold_size
    
    test_indices = list(range(test_start, test_end))
    train_indices = list(range(0, test_start)) + list(range(test_end, n_samples))
    
    X_train, X_test = X[train_indices], X[test_indices]
    y_train, y_test = y[train_indices], y[test_indices]
    
    print(f"\nFold {fold_idx}: train={len(train_indices)}, test={len(test_indices)}")
    
    for lam in lambdas:
        w, b, _ = fit_logistic(X_train, y_train, lambda_reg=lam)
        y_pred = predict_logistic(X_test, w, b)
        brier = compute_brier_score(y_test, y_pred)
        cv_scores[lam].append(brier)
        print(f"  lambda={lam}: Brier={brier:.6f}")

# Compute mean CV scores
print("\nMean CV Brier scores:")
mean_cv_scores = {}
for lam in lambdas:
    mean_score = np.mean(cv_scores[lam])
    mean_cv_scores[lam] = mean_score
    print(f"  lambda={lam}: {mean_score:.6f}")

# Find best lambda
best_lambda = min(lambdas, key=lambda lam: mean_cv_scores[lam])
best_cv_score = mean_cv_scores[best_lambda]
baseline_score = mean_cv_scores[0.0]
improvement = baseline_score - best_cv_score

print(f"\nBest lambda: {best_lambda}")
print(f"Best CV Brier: {best_cv_score:.6f}")
print(f"Baseline (lambda=0.0) Brier: {baseline_score:.6f}")
print(f"Improvement: {improvement:.6f}")

# ============ Task 2: Interaction features and paired t-test ============
print("\n" + "="*60)
print("Task 2: Add interaction features and run paired t-test")
print("="*60)

# Add interaction features: x0*x1, x1*x2, x2*x3, x0*x3
X_with_interactions = np.column_stack([
    X,
    X[:, 0] * X[:, 1],  # x0*x1
    X[:, 1] * X[:, 2],  # x1*x2
    X[:, 2] * X[:, 3],  # x2*x3
    X[:, 0] * X[:, 3],  # x0*x3
])

print(f"Original X shape: {X.shape}")
print(f"X with interactions shape: {X_with_interactions.shape}")

raw_brier_per_fold = []
interaction_brier_per_fold = []
lambda_test = 0.1

for fold_idx in range(n_folds):
    test_start = fold_idx * fold_size
    test_end = test_start + fold_size
    
    test_indices = list(range(test_start, test_end))
    train_indices = list(range(0, test_start)) + list(range(test_end, n_samples))
    
    # Raw features
    X_train_raw, X_test_raw = X[train_indices], X[test_indices]
    y_train, y_test = y[train_indices], y[test_indices]
    w_raw, b_raw, _ = fit_logistic(X_train_raw, y_train, lambda_reg=lambda_test)
    y_pred_raw = predict_logistic(X_test_raw, w_raw, b_raw)
    brier_raw = compute_brier_score(y_test, y_pred_raw)
    raw_brier_per_fold.append(brier_raw)
    
    # With interaction features
    X_train_int, X_test_int = X_with_interactions[train_indices], X_with_interactions[test_indices]
    w_int, b_int, _ = fit_logistic(X_train_int, y_train, lambda_reg=lambda_test)
    y_pred_int = predict_logistic(X_test_int, w_int, b_int)
    brier_int = compute_brier_score(y_test, y_pred_int)
    interaction_brier_per_fold.append(brier_int)
    
    print(f"Fold {fold_idx}: Raw Brier={brier_raw:.6f}, Interaction Brier={brier_int:.6f}")

# Paired t-test: raw - interaction per fold
differences = np.array(raw_brier_per_fold) - np.array(interaction_brier_per_fold)
t_stat, p_value = stats.ttest_rel(raw_brier_per_fold, interaction_brier_per_fold)

print(f"\nPaired t-test results (raw vs interaction):")
print(f"Differences per fold: {differences}")
print(f"t-statistic: {t_stat:.6f}")
print(f"p-value: {p_value:.6f}")

interaction_helps = t_stat > 2.0
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# ============ Task 3: Compression - Sparsity and Quantization ============
print("\n" + "="*60)
print("Task 3: Find best compression config")
print("="*60)

# Fit dense model on all data with lambda=0.1
w_dense, b_dense, _ = fit_logistic(X, y, lambda_reg=0.1)

# Compute dense in-sample Brier
y_pred_dense = predict_logistic(X, w_dense, b_dense)
brier_dense = compute_brier_score(y, y_pred_dense)
print(f"Dense model in-sample Brier: {brier_dense:.6f}")

sparsity_levels = [20, 40, 60]  # percentage
bit_levels = [8, 4]

best_retention = -1
best_config = None

for sparsity_pct in sparsity_levels:
    for bits in bit_levels:
        # Apply sparsity: zero out smallest magnitude weights
        w_sparse = w_dense.copy()
        k = round(sparsity_pct / 100.0 * len(w_dense))
        if k > 0:
            # Find indices of k smallest magnitude weights
            threshold_idx = np.argsort(np.abs(w_sparse))[k-1]
            threshold_val = np.abs(w_sparse[threshold_idx])
            # Zero out weights with magnitude <= threshold
            w_sparse[np.abs(w_sparse) <= threshold_val] = 0
            # Keep exactly k weights zeroed (in case of ties)
            n_zeroed = np.sum(w_sparse == 0)
            if n_zeroed > k:
                # Too many tied at threshold, keep only k of them
                zero_indices = np.where(w_sparse == 0)[0]
                zero_indices_to_restore = zero_indices[:n_zeroed - k]
                w_sparse[zero_indices_to_restore] = w_dense[zero_indices_to_restore]
        
        # Apply quantization: map remaining weights to 2^bits levels
        nonzero_mask = w_sparse != 0
        if np.any(nonzero_mask):
            nonzero_weights = w_sparse[nonzero_mask]
            w_min, w_max = np.min(nonzero_weights), np.max(nonzero_weights)
            
            if w_max > w_min:
                # Map to 2^bits levels between min and max
                n_levels = 2 ** bits
                # Quantize: (w - min) / (max - min) * (n_levels - 1), then inverse
                quantized = np.round((nonzero_weights - w_min) / (w_max - w_min) * (n_levels - 1))
                w_sparse[nonzero_mask] = w_min + quantized * (w_max - w_min) / (n_levels - 1)
        
        # Compute in-sample Brier with compressed model
        y_pred_comp = predict_logistic(X, w_sparse, b_dense)
        brier_comp = compute_brier_score(y, y_pred_comp)
        
        # Retention = dense_brier / compressed_brier
        retention = brier_dense / brier_comp if brier_comp > 0 else 0
        
        config_name = f"sparsity{sparsity_pct}_bits{bits}"
        print(f"{config_name}: Brier={brier_comp:.6f}, Retention={retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = config_name

print(f"\nBest compression config: {best_config}")
print(f"Best retention: {best_retention:.6f}")

# ============ Write answers ============
answers = {
    "best_lambda": float(best_lambda),
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

print("\n" + "="*60)
print("Final Answers:")
print("="*60)
for key, val in answers.items():
    print(f"{key}: {val}")

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("\nAnswers saved to answers.json")
