import json
import numpy as np
from scipy import stats

# Load data
with open('data.json') as f:
    data = json.load(f)

X = np.array(data['X'])
y = np.array(data['y'], dtype=np.float32)
n_samples = X.shape[0]
n_features = X.shape[1]

print(f"Data shape: {X.shape}, labels shape: {y.shape}")

# Define logistic model fitting function
def fit_logistic_gd(X, y, lambda_reg=0.0, learning_rate=0.1, iterations=200):
    """
    Fit logistic regression using full-batch gradient descent.
    """
    n = X.shape[0]
    d = X.shape[1]
    
    # Initialize weights and bias at 0
    w = np.zeros(d)
    b = 0.0
    
    for i in range(iterations):
        # Compute logits (clipped to [-30, 30])
        logits = X @ w + b
        logits = np.clip(logits, -30, 30)
        
        # Sigmoid
        probs = 1.0 / (1.0 + np.exp(-logits))
        
        # Gradients
        grad_w = X.T @ (probs - y) / n
        grad_b = np.sum(probs - y) / n
        
        # Update
        w = w - learning_rate * (grad_w + lambda_reg * w)
        b = b - learning_rate * grad_b
    
    return w, b

def predict_proba(X, w, b):
    """Predict probabilities for class 1."""
    logits = X @ w + b
    logits = np.clip(logits, -30, 30)
    probs = 1.0 / (1.0 + np.exp(-logits))
    return probs

def brier_score(y_true, y_pred_proba):
    """Compute Brier score (mean squared error of probabilities)."""
    return np.mean((y_pred_proba - y_true) ** 2)

# ============ Question 1: Best Lambda ============
print("\n=== Question 1: Finding best lambda ===")
lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
fold_size = n_samples // 5

brier_scores_per_lambda = {lam: [] for lam in lambdas}

for fold_idx in range(5):
    # Create contiguous fold (fold k = rows k, k+5, k+10, ...)
    test_indices = np.arange(fold_idx, n_samples, 5)
    train_indices = np.setdiff1d(np.arange(n_samples), test_indices)
    
    X_train = X[train_indices]
    y_train = y[train_indices]
    X_test = X[test_indices]
    y_test = y[test_indices]
    
    print(f"Fold {fold_idx}: train size = {len(train_indices)}, test size = {len(test_indices)}")
    
    for lam in lambdas:
        w, b = fit_logistic_gd(X_train, y_train, lambda_reg=lam, learning_rate=0.1, iterations=200)
        y_pred_proba = predict_proba(X_test, w, b)
        brier = brier_score(y_test, y_pred_proba)
        brier_scores_per_lambda[lam].append(brier)

# Compute mean Brier scores for each lambda
mean_brier_per_lambda = {lam: np.mean(brier_scores_per_lambda[lam]) for lam in lambdas}
print("\nMean Brier scores per lambda:")
for lam in lambdas:
    print(f"  lambda={lam}: {mean_brier_per_lambda[lam]:.6f}")

# Find best lambda
best_lambda = min(lambdas, key=lambda lam: mean_brier_per_lambda[lam])
baseline_brier = mean_brier_per_lambda[0.0]
best_brier = mean_brier_per_lambda[best_lambda]
improvement = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda}")
print(f"Baseline Brier (lambda=0): {baseline_brier:.6f}")
print(f"Best Brier: {best_brier:.6f}")
print(f"Improvement over baseline: {improvement:.6f}")

# ============ Question 2: Interaction terms ============
print("\n=== Question 2: Interaction terms ===")

# Create interaction features
X_with_interactions = np.hstack([
    X,
    (X[:, 0] * X[:, 1]).reshape(-1, 1),  # x0*x1
    (X[:, 1] * X[:, 2]).reshape(-1, 1),  # x1*x2
    (X[:, 2] * X[:, 3]).reshape(-1, 1),  # x2*x3
    (X[:, 0] * X[:, 3]).reshape(-1, 1),  # x0*x3
])

print(f"X_with_interactions shape: {X_with_interactions.shape}")

# Fit models with lambda=0.1 on both representations across folds
brier_raw_per_fold = []
brier_interaction_per_fold = []

for fold_idx in range(5):
    test_indices = np.arange(fold_idx, n_samples, 5)
    train_indices = np.setdiff1d(np.arange(n_samples), test_indices)
    
    # Raw model
    X_train_raw = X[train_indices]
    y_train = y[train_indices]
    X_test_raw = X[test_indices]
    y_test = y[test_indices]
    
    w_raw, b_raw = fit_logistic_gd(X_train_raw, y_train, lambda_reg=0.1, learning_rate=0.1, iterations=200)
    y_pred_raw = predict_proba(X_test_raw, w_raw, b_raw)
    brier_raw = brier_score(y_test, y_pred_raw)
    brier_raw_per_fold.append(brier_raw)
    
    # Interaction model
    X_train_int = X_with_interactions[train_indices]
    X_test_int = X_with_interactions[test_indices]
    
    w_int, b_int = fit_logistic_gd(X_train_int, y_train, lambda_reg=0.1, learning_rate=0.1, iterations=200)
    y_pred_int = predict_proba(X_test_int, w_int, b_int)
    brier_int = brier_score(y_test, y_pred_int)
    brier_interaction_per_fold.append(brier_int)
    
    print(f"Fold {fold_idx}: Brier raw = {brier_raw:.6f}, Brier interaction = {brier_int:.6f}")

# Paired t-test (raw minus interaction)
differences = np.array(brier_raw_per_fold) - np.array(brier_interaction_per_fold)
print(f"\nDifferences (raw - interaction): {differences}")
print(f"Mean difference: {np.mean(differences):.6f}")

# Paired t-test
t_stat, p_val = stats.ttest_rel(brier_raw_per_fold, brier_interaction_per_fold)
print(f"Paired t-test statistic: {t_stat:.6f}")
print(f"P-value: {p_val:.6f}")

interaction_helps = t_stat > 2.0
print(f"t-stat > 2.0? {interaction_helps}")

# ============ Question 3: Best compression config ============
print("\n=== Question 3: Best compression configuration ===")

# Fit dense model on all rows with lambda=0.1
w_dense, b_dense = fit_logistic_gd(X, y, lambda_reg=0.1, learning_rate=0.1, iterations=200)
y_pred_dense = predict_proba(X, w_dense, b_dense)
brier_dense = brier_score(y, y_pred_dense)

print(f"Dense model Brier (in-sample): {brier_dense:.6f}")

sparsity_percents = [20, 40, 60]
bit_options = [8, 4]

best_retention = -1
best_config = None

for sparsity_pct in sparsity_percents:
    for bits in bit_options:
        # Make a copy of weights
        w_compressed = w_dense.copy()
        
        # Compute sparsity: k = round(sparsity_pct / 100 * d)
        k = round(sparsity_pct / 100.0 * len(w_compressed))
        
        # Zero out smallest magnitude weights
        abs_weights = np.abs(w_compressed)
        threshold = np.partition(abs_weights, k-1)[k-1] if k > 0 else np.inf
        w_compressed[abs_weights <= threshold] = 0
        
        # Handle ties: if we didn't zero enough, zero additional smallest
        n_zeros = np.sum(w_compressed == 0)
        if n_zeros < k:
            non_zero_mask = w_compressed != 0
            non_zero_abs = np.abs(w_compressed[non_zero_mask])
            new_threshold_idx = k - n_zeros - 1
            if new_threshold_idx >= 0 and new_threshold_idx < len(non_zero_abs):
                new_threshold = np.partition(non_zero_abs, new_threshold_idx)[new_threshold_idx]
                w_compressed[non_zero_mask & (np.abs(w_compressed) <= new_threshold)] = 0
        
        # Quantisation: map remaining weights uniformly onto 2^bits levels
        non_zero_mask = w_compressed != 0
        if np.any(non_zero_mask):
            w_nz = w_compressed[non_zero_mask]
            w_min = np.min(w_nz)
            w_max = np.max(w_nz)
            
            if w_max > w_min:
                # Map to levels 0, 1, ..., 2^bits - 1
                n_levels = 2 ** bits
                w_quantized = np.round((w_nz - w_min) / (w_max - w_min) * (n_levels - 1))
                # Map back
                w_compressed[non_zero_mask] = w_min + w_quantized / (n_levels - 1) * (w_max - w_min)
            # else: if w_max == w_min, all weights are equal, leave as is
        
        # Evaluate compressed model
        y_pred_compressed = predict_proba(X, w_compressed, b_dense)
        brier_compressed = brier_score(y, y_pred_compressed)
        
        retention = brier_dense / brier_compressed if brier_compressed > 0 else np.inf
        
        config_name = f"sparsity{sparsity_pct}_bits{bits}"
        print(f"{config_name}: Brier = {brier_compressed:.6f}, Retention = {retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = config_name

print(f"\nBest config: {best_config} with retention = {best_retention:.6f}")

# ============ Output answers ============
answers = {
    "best_lambda": best_lambda,
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

print("\n=== FINAL ANSWERS ===")
print(json.dumps(answers, indent=2))

# Write to file
with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)
