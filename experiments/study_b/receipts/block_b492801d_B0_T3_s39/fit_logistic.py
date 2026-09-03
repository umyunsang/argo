#!/usr/bin/env python3
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
print(f"Data shape: {n_samples} samples, {n_features} features")

# Helper function to clip logits
def clip_logits(logits, min_val=-30, max_val=30):
    return np.clip(logits, min_val, max_val)

# Sigmoid function
def sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))

# Brier score
def brier_score(y_true, y_pred_proba):
    return np.mean((y_true - y_pred_proba) ** 2)

# Fit logistic regression with full-batch gradient descent
def fit_logistic_gd(X, y, lambda_reg=0.0, n_iters=200, lr=0.1):
    n_samples, n_features = X.shape
    
    # Initialize weights and bias at 0
    w = np.zeros(n_features)
    b = 0.0
    
    for iteration in range(n_iters):
        # Forward pass
        logits = X @ w + b
        logits = clip_logits(logits)
        y_pred = sigmoid(logits)
        
        # Compute gradients
        error = y_pred - y
        grad_w = X.T @ error
        grad_b = np.sum(error)
        
        # Update with L2 regularization
        w = w - lr * (grad_w / n_samples + lambda_reg * w)
        b = b - lr * (grad_b / n_samples)
    
    return w, b

# Cross-validation split (5 contiguous blocks)
def get_cv_splits(n_samples, n_folds=5):
    fold_size = n_samples // n_folds
    splits = []
    for fold_idx in range(n_folds):
        test_indices = []
        for i in range(n_samples):
            if i % n_folds == fold_idx:
                test_indices.append(i)
        train_indices = [i for i in range(n_samples) if i not in test_indices]
        splits.append((np.array(train_indices), np.array(test_indices)))
    return splits

splits = get_cv_splits(n_samples, n_folds=5)
print(f"CV splits created: {len(splits)} folds")

# ============================================
# QUESTION 1: Best lambda and improvement
# ============================================
print("\n=== QUESTION 1: Lambda tuning ===")
lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
cv_brier_scores = {lam: [] for lam in lambdas}

for lam in lambdas:
    for train_idx, test_idx in splits:
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        w, b = fit_logistic_gd(X_train, y_train, lambda_reg=lam, n_iters=200, lr=0.1)
        
        logits_test = X_test @ w + b
        logits_test = clip_logits(logits_test)
        y_pred_proba = sigmoid(logits_test)
        
        brier = brier_score(y_test, y_pred_proba)
        cv_brier_scores[lam].append(brier)

# Compute mean CV Brier score for each lambda
mean_cv_brier = {lam: np.mean(cv_brier_scores[lam]) for lam in lambdas}
print("Mean CV Brier scores:")
for lam, score in mean_cv_brier.items():
    print(f"  lambda={lam}: {score:.6f}")

best_lambda = min(mean_cv_brier, key=mean_cv_brier.get)
improvement = mean_cv_brier[0.0] - mean_cv_brier[best_lambda]
print(f"Best lambda: {best_lambda}")
print(f"Improvement over baseline (lambda=0): {improvement:.6f}")

# ============================================
# QUESTION 2: Interaction features
# ============================================
print("\n=== QUESTION 2: Interaction features ===")

# Create interaction features
X_with_interactions = np.copy(X)
n_features_original = X.shape[1]

# Add products: x0*x1, x1*x2, x2*x3, x0*x3
interaction_1 = X[:, 0] * X[:, 1]
interaction_2 = X[:, 1] * X[:, 2]
interaction_3 = X[:, 2] * X[:, 3]
interaction_4 = X[:, 0] * X[:, 3]

X_with_interactions = np.column_stack([X_with_interactions, interaction_1, interaction_2, interaction_3, interaction_4])
print(f"X shape after adding interactions: {X_with_interactions.shape}")

# Fit both models with lambda=0.1 and collect Brier scores per fold
lambda_fixed = 0.1
brier_raw_per_fold = []
brier_interaction_per_fold = []

for train_idx, test_idx in splits:
    # Raw features
    X_train_raw, X_test_raw = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    w_raw, b_raw = fit_logistic_gd(X_train_raw, y_train, lambda_reg=lambda_fixed, n_iters=200, lr=0.1)
    logits_test_raw = X_test_raw @ w_raw + b_raw
    logits_test_raw = clip_logits(logits_test_raw)
    y_pred_proba_raw = sigmoid(logits_test_raw)
    brier_raw = brier_score(y_test, y_pred_proba_raw)
    brier_raw_per_fold.append(brier_raw)
    
    # With interactions
    X_train_inter = X_with_interactions[train_idx]
    X_test_inter = X_with_interactions[test_idx]
    
    w_inter, b_inter = fit_logistic_gd(X_train_inter, y_train, lambda_reg=lambda_fixed, n_iters=200, lr=0.1)
    logits_test_inter = X_test_inter @ w_inter + b_inter
    logits_test_inter = clip_logits(logits_test_inter)
    y_pred_proba_inter = sigmoid(logits_test_inter)
    brier_inter = brier_score(y_test, y_pred_proba_inter)
    brier_interaction_per_fold.append(brier_inter)

brier_raw_per_fold = np.array(brier_raw_per_fold)
brier_interaction_per_fold = np.array(brier_interaction_per_fold)

print(f"Brier scores (raw) per fold: {brier_raw_per_fold}")
print(f"Brier scores (interaction) per fold: {brier_interaction_per_fold}")

# Paired t-test: H0 is that there's no difference
# We test if raw > interaction (i.e., raw is worse, so interaction helps)
differences = brier_raw_per_fold - brier_interaction_per_fold
print(f"Differences (raw - interaction): {differences}")

# One-sample t-test on differences
t_stat, p_value = stats.ttest_1samp(differences, 0)
print(f"Paired t-statistic: {t_stat:.6f}")
print(f"P-value: {p_value:.6f}")

# interaction_helps is True if t > 2.0
interaction_helps = t_stat > 2.0
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# ============================================
# QUESTION 3: Compression
# ============================================
print("\n=== QUESTION 3: Compression ===")

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic_gd(X, y, lambda_reg=0.1, n_iters=200, lr=0.1)

# Compute dense model in-sample Brier score
logits_dense = X @ w_dense + b_dense
logits_dense = clip_logits(logits_dense)
y_pred_proba_dense = sigmoid(logits_dense)
brier_dense = brier_score(y, y_pred_proba_dense)
print(f"Dense model Brier score: {brier_dense:.6f}")

# Test configurations
sparsity_levels = [20, 40, 60]  # percent
bit_levels = [8, 4]
best_retention = 0
best_config = None

for sparsity_pct in sparsity_levels:
    for bits in bit_levels:
        # Copy weights
        w_compressed = np.copy(w_dense)
        
        # Sparsity: zero out smallest magnitude weights
        k = round(sparsity_pct / 100.0 * len(w_compressed))
        if k > 0:
            threshold_idx = np.argsort(np.abs(w_compressed))[k]
            threshold = np.abs(w_compressed[threshold_idx])
            w_compressed[np.abs(w_compressed) < threshold] = 0
            # If there are ties, select exactly k smallest
            sorted_abs = np.sort(np.abs(w_compressed))
            if k < len(sorted_abs):
                threshold = sorted_abs[k]
                mask = np.abs(w_compressed) < threshold
                w_compressed[mask] = 0
        
        # Quantization: map non-zero weights to 2^bits levels
        non_zero_mask = w_compressed != 0
        if np.sum(non_zero_mask) > 0:
            w_nz = w_compressed[non_zero_mask]
            min_w = np.min(w_nz)
            max_w = np.max(w_nz)
            
            if min_w != max_w:
                # Map to [0, 2^bits - 1]
                n_levels = 2 ** bits
                w_quantized = np.round((w_nz - min_w) / (max_w - min_w) * (n_levels - 1))
                # Map back
                w_dequantized = min_w + w_quantized / (n_levels - 1) * (max_w - min_w)
                w_compressed[non_zero_mask] = w_dequantized
        
        # Compute compressed model in-sample Brier score
        logits_compressed = X @ w_compressed + b_dense  # bias untouched
        logits_compressed = clip_logits(logits_compressed)
        y_pred_proba_compressed = sigmoid(logits_compressed)
        brier_compressed = brier_score(y, y_pred_proba_compressed)
        
        # Retention = dense Brier / compressed Brier
        retention = brier_dense / brier_compressed if brier_compressed > 0 else float('inf')
        
        config_name = f"sparsity{sparsity_pct}_bits{bits}"
        print(f"{config_name}: Brier={brier_compressed:.6f}, Retention={retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = config_name

print(f"\nBest compression config: {best_config} (retention: {best_retention:.6f})")

# ============================================
# Save answers
# ============================================
answers = {
    "best_lambda": float(best_lambda),
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": str(best_config)
}

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("\n=== ANSWERS ===")
print(json.dumps(answers, indent=2))
