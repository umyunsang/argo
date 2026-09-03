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

def sigmoid(z):
    """Sigmoid function with clipping to [-30, 30]"""
    z = np.clip(z, -30, 30)
    return 1 / (1 + np.exp(-z))

def brier_score(y_true, y_pred_proba):
    """Calculate Brier score"""
    return np.mean((y_pred_proba - y_true) ** 2)

def fit_logistic(X_train, y_train, lambda_reg=0.0, n_iter=200, lr=0.1):
    """
    Fit logistic regression using full-batch gradient descent.
    
    w -= 0.1 * (grad_w / n + lambda * w)
    b -= 0.1 * (grad_b / n)
    """
    n = len(y_train)
    d = X_train.shape[1]
    
    # Initialize weights and bias
    w = np.zeros(d)
    b = 0.0
    
    for iteration in range(n_iter):
        # Forward pass
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)
        y_pred = sigmoid(logits)
        
        # Gradients
        error = y_pred - y_train
        grad_w = X_train.T @ error
        grad_b = np.sum(error)
        
        # Update
        w -= lr * (grad_w / n + lambda_reg * w)
        b -= lr * (grad_b / n)
    
    return w, b

def predict_proba(X_test, w, b):
    """Predict probability"""
    logits = X_test @ w + b
    logits = np.clip(logits, -30, 30)
    return sigmoid(logits)

# Create 5 contiguous folds
fold_size = n_samples // 5
folds = []
for k in range(5):
    start_idx = k * fold_size
    end_idx = (k + 1) * fold_size if k < 4 else n_samples
    fold_indices = list(range(start_idx, end_idx))
    folds.append(fold_indices)

print(f"Fold sizes: {[len(f) for f in folds]}")

# ========== Question 1: Best lambda and improvement ==========
print("\n=== Question 1: Lambda Selection ===")
lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
brier_scores_per_lambda = {lam: [] for lam in lambdas}

for lam in lambdas:
    fold_briers = []
    for fold_idx in range(5):
        # Get test fold
        test_indices = folds[fold_idx]
        train_indices = []
        for j in range(5):
            if j != fold_idx:
                train_indices.extend(folds[j])
        
        X_train = X[train_indices]
        y_train = y[train_indices]
        X_test = X[test_indices]
        y_test = y[test_indices]
        
        # Fit and evaluate
        w, b = fit_logistic(X_train, y_train, lambda_reg=lam)
        y_pred = predict_proba(X_test, w, b)
        brier = brier_score(y_test, y_pred)
        fold_briers.append(brier)
    
    mean_brier = np.mean(fold_briers)
    brier_scores_per_lambda[lam] = fold_briers
    print(f"Lambda {lam}: mean Brier = {mean_brier:.6f}, fold scores = {[f'{b:.6f}' for b in fold_briers]}")

# Find best lambda
best_lambda = min(lambdas, key=lambda lam: np.mean(brier_scores_per_lambda[lam]))
baseline_brier = np.mean(brier_scores_per_lambda[0.0])
best_brier = np.mean(brier_scores_per_lambda[best_lambda])
improvement = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda}")
print(f"Baseline (lambda=0) Brier: {baseline_brier:.6f}")
print(f"Best Brier: {best_brier:.6f}")
print(f"Improvement: {improvement:.6f}")

# ========== Question 2: Interaction terms ==========
print("\n=== Question 2: Interaction Terms ===")

def add_interaction_features(X):
    """Add interaction terms: x0*x1, x1*x2, x2*x3, x0*x3"""
    X_interaction = X.copy()
    X_interaction = np.column_stack([
        X_interaction,
        X[:, 0] * X[:, 1],  # x0*x1
        X[:, 1] * X[:, 2],  # x1*x2
        X[:, 2] * X[:, 3],  # x2*x3
        X[:, 0] * X[:, 3]   # x0*x3
    ])
    return X_interaction

# Fit with raw features and interaction features, lambda=0.1
raw_briers = []
interaction_briers = []
paired_diffs = []

for fold_idx in range(5):
    test_indices = folds[fold_idx]
    train_indices = []
    for j in range(5):
        if j != fold_idx:
            train_indices.extend(folds[j])
    
    X_train = X[train_indices]
    y_train = y[train_indices]
    X_test = X[test_indices]
    y_test = y[test_indices]
    
    # Raw model
    w_raw, b_raw = fit_logistic(X_train, y_train, lambda_reg=0.1)
    y_pred_raw = predict_proba(X_test, w_raw, b_raw)
    brier_raw = brier_score(y_test, y_pred_raw)
    raw_briers.append(brier_raw)
    
    # Interaction model
    X_train_int = add_interaction_features(X_train)
    X_test_int = add_interaction_features(X_test)
    w_int, b_int = fit_logistic(X_train_int, y_train, lambda_reg=0.1)
    y_pred_int = predict_proba(X_test_int, w_int, b_int)
    brier_int = brier_score(y_test, y_pred_int)
    interaction_briers.append(brier_int)
    
    # Paired difference
    paired_diffs.append(brier_raw - brier_int)
    
    print(f"Fold {fold_idx}: Raw Brier = {brier_raw:.6f}, Interaction Brier = {brier_int:.6f}, Diff = {paired_diffs[-1]:.6f}")

# Paired t-test
paired_diffs = np.array(paired_diffs)
t_stat = np.mean(paired_diffs) / (np.std(paired_diffs, ddof=1) / np.sqrt(len(paired_diffs)))
interaction_helps = t_stat > 2.0

print(f"\nPaired t-test statistic: {t_stat:.6f}")
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# ========== Question 3: Compression and sparsity ==========
print("\n=== Question 3: Compression ===")

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic(X, y, lambda_reg=0.1)
y_pred_dense = predict_proba(X, w_dense, b_dense)
brier_dense = brier_score(y, y_pred_dense)
print(f"Dense model in-sample Brier: {brier_dense:.6f}")

sparsity_levels = [20, 40, 60]
bit_levels = [8, 4]
best_retention = -1
best_config = None

results = []
for sparsity in sparsity_levels:
    for bits in bit_levels:
        # Apply sparsity
        w_sparse = w_dense.copy()
        k = round(sparsity / 100.0 * len(w_sparse))
        if k > 0:
            # Zero out k smallest magnitude weights
            abs_w = np.abs(w_sparse)
            threshold_idx = np.argsort(abs_w)[:k]
            w_sparse[threshold_idx] = 0
        
        # Apply quantization
        w_quant = w_sparse.copy()
        nonzero_mask = w_quant != 0
        if np.any(nonzero_mask):
            w_min = np.min(w_quant[nonzero_mask])
            w_max = np.max(w_quant[nonzero_mask])
            if w_max > w_min:
                # Map to 2^bits levels
                levels = 2 ** bits
                w_quant[nonzero_mask] = np.round((w_quant[nonzero_mask] - w_min) / (w_max - w_min) * (levels - 1))
                w_quant[nonzero_mask] = (w_quant[nonzero_mask] / (levels - 1)) * (w_max - w_min) + w_min
        
        # Evaluate
        y_pred_comp = predict_proba(X, w_quant, b_dense)
        brier_comp = brier_score(y, y_pred_comp)
        retention = brier_dense / brier_comp
        
        config = f"sparsity{sparsity}_bits{bits}"
        results.append((sparsity, bits, brier_comp, retention, config))
        print(f"{config}: Brier = {brier_comp:.6f}, Retention = {retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = config

print(f"\nBest compression config: {best_config} (Retention = {best_retention:.6f})")

# ========== Save results ==========
results_dict = {
    "best_lambda": best_lambda,
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

print("\n=== Final Answers ===")
for key, value in results_dict.items():
    print(f"{key}: {value}")

with open('answers.json', 'w') as f:
    json.dump(results_dict, f, indent=2)

print("\nResults saved to answers.json")
