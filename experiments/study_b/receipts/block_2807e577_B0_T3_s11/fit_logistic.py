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
    """Sigmoid function with clipping to avoid overflow"""
    z = np.clip(z, -30, 30)
    return 1.0 / (1.0 + np.exp(-z))

def logistic_fit(X_train, y_train, lambda_reg=0.0, learning_rate=0.1, n_iter=200):
    """
    Fit logistic regression using full-batch gradient descent
    """
    n_samples, n_features = X_train.shape
    
    # Initialize weights and bias
    w = np.zeros(n_features)
    b = 0.0
    
    for _ in range(n_iter):
        # Forward pass
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)
        probs = sigmoid(logits)
        
        # Compute gradients
        errors = probs - y_train
        grad_w = X_train.T @ errors / n_samples
        grad_b = np.mean(errors)
        
        # Update weights and bias
        w -= learning_rate * (grad_w + lambda_reg * w)
        b -= learning_rate * grad_b
    
    return w, b

def predict_proba(X, w, b):
    """Predict class probabilities"""
    logits = X @ w + b
    logits = np.clip(logits, -30, 30)
    return sigmoid(logits)

def brier_score(y_true, y_pred_proba):
    """Compute Brier score (mean squared error between predictions and labels)"""
    return np.mean((y_pred_proba - y_true) ** 2)

# ===== Task 1: Find best lambda =====
print("\n=== Task 1: Best lambda for L2 regularization ===")

lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
n_folds = 5

# Create 5-fold cross-validation folds (contiguous blocks)
fold_size = n_samples // n_folds
folds = []
for k in range(n_folds):
    start = k * fold_size
    end = start + fold_size if k < n_folds - 1 else n_samples
    folds.append((start, end))

print(f"Fold splits: {folds}")

cv_scores = {lam: [] for lam in lambdas}
all_test_pred = {lam: [] for lam in lambdas}

for lam in lambdas:
    print(f"\nLambda = {lam}")
    fold_scores = []
    
    for fold_idx, (test_start, test_end) in enumerate(folds):
        # Create train and test sets
        test_indices = np.arange(test_start, test_end)
        train_indices = np.concatenate([np.arange(0, test_start), np.arange(test_end, n_samples)])
        
        X_train, y_train = X[train_indices], y[train_indices]
        X_test, y_test = X[test_indices], y[test_indices]
        
        # Fit model
        w, b = logistic_fit(X_train, y_train, lambda_reg=lam)
        
        # Predict on test set
        y_pred_proba = predict_proba(X_test, w, b)
        
        # Compute Brier score
        score = brier_score(y_test, y_pred_proba)
        fold_scores.append(score)
        cv_scores[lam].append(score)
        
        print(f"  Fold {fold_idx}: {score:.6f}")
    
    mean_cv_score = np.mean(fold_scores)
    print(f"  Mean CV score: {mean_cv_score:.6f}")

# Find best lambda
best_lambda = min(lambdas, key=lambda lam: np.mean(cv_scores[lam]))
best_cv_score = np.mean(cv_scores[best_lambda])
baseline_cv_score = np.mean(cv_scores[0.0])
improvement = baseline_cv_score - best_cv_score

print(f"\nBest lambda: {best_lambda}")
print(f"Best CV score: {best_cv_score:.6f}")
print(f"Baseline (lambda=0) score: {baseline_cv_score:.6f}")
print(f"Improvement: {improvement:.6f}")

# ===== Task 2: Interaction features and paired t-test =====
print("\n=== Task 2: Interaction features ===")

# Create interaction features
X_with_interaction = np.column_stack([
    X,
    X[:, 0] * X[:, 1],  # x0 * x1
    X[:, 1] * X[:, 2],  # x1 * x2
    X[:, 2] * X[:, 3],  # x2 * x3
    X[:, 0] * X[:, 3],  # x0 * x3
])

print(f"Original features: {X.shape[1]}")
print(f"Features with interaction: {X_with_interaction.shape[1]}")

# Fit models with and without interaction on each fold
brier_scores_raw = []
brier_scores_interaction = []
paired_diffs = []

for fold_idx, (test_start, test_end) in enumerate(folds):
    test_indices = np.arange(test_start, test_end)
    train_indices = np.concatenate([np.arange(0, test_start), np.arange(test_end, n_samples)])
    
    # Raw model
    X_train_raw, y_train = X[train_indices], y[train_indices]
    X_test_raw, y_test = X[test_indices], y[test_indices]
    w_raw, b_raw = logistic_fit(X_train_raw, y_train, lambda_reg=0.1)
    y_pred_raw = predict_proba(X_test_raw, w_raw, b_raw)
    brier_raw = brier_score(y_test, y_pred_raw)
    
    # Interaction model
    X_train_inter = X_with_interaction[train_indices]
    X_test_inter = X_with_interaction[test_indices]
    w_inter, b_inter = logistic_fit(X_train_inter, y_train, lambda_reg=0.1)
    y_pred_inter = predict_proba(X_test_inter, w_inter, b_inter)
    brier_inter = brier_score(y_test, y_pred_inter)
    
    brier_scores_raw.append(brier_raw)
    brier_scores_interaction.append(brier_inter)
    paired_diffs.append(brier_raw - brier_inter)
    
    print(f"Fold {fold_idx}: Raw={brier_raw:.6f}, Interaction={brier_inter:.6f}, Diff={brier_raw - brier_inter:.6f}")

# Paired t-test
t_stat, p_val = stats.ttest_rel(brier_scores_raw, brier_scores_interaction)
print(f"\nPaired t-test:")
print(f"  t-statistic: {t_stat:.6f}")
print(f"  p-value: {p_val:.6f}")
print(f"  Mean diff (raw - interaction): {np.mean(paired_diffs):.6f}")

interaction_helps = t_stat > 2.0
print(f"  interaction_helps (t > 2.0): {interaction_helps}")

# ===== Task 3: Compression =====
print("\n=== Task 3: Model compression ===")

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = logistic_fit(X, y, lambda_reg=0.1)
y_pred_dense = predict_proba(X, w_dense, b_dense)
brier_dense = brier_score(y, y_pred_dense)

print(f"Dense model Brier score: {brier_dense:.6f}")

sparsity_levels = [20, 40, 60]
bit_levels = [8, 4]
best_retention = -1
best_config = None

for sparsity in sparsity_levels:
    for bits in bit_levels:
        # Apply sparsity: zero out smallest magnitude weights
        w_sparse = w_dense.copy()
        k = round(sparsity / 100.0 * len(w_sparse))
        
        # Find indices of k smallest magnitude weights
        abs_w = np.abs(w_sparse)
        threshold_idx = np.argsort(abs_w)[k]
        threshold = abs_w[threshold_idx]
        
        # Zero out weights with magnitude <= threshold
        w_sparse[np.abs(w_sparse) <= threshold] = 0
        
        # Apply quantization to remaining weights
        nonzero_mask = w_sparse != 0
        if np.any(nonzero_mask):
            w_min = np.min(w_sparse[nonzero_mask])
            w_max = np.max(w_sparse[nonzero_mask])
            
            if w_min != w_max:
                # Map to 2^bits levels
                n_levels = 2 ** bits
                w_sparse[nonzero_mask] = np.round((w_sparse[nonzero_mask] - w_min) / (w_max - w_min) * (n_levels - 1)) * (w_max - w_min) / (n_levels - 1) + w_min
        
        # Evaluate compressed model
        y_pred_compressed = predict_proba(X, w_sparse, b_dense)
        brier_compressed = brier_score(y, y_pred_compressed)
        
        # Calculate retention (inverse of degradation)
        retention = brier_dense / brier_compressed if brier_compressed > 0 else 0
        
        print(f"Sparsity {sparsity}%, Bits {bits}: Brier={brier_compressed:.6f}, Retention={retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = f"sparsity{sparsity}_bits{bits}"

print(f"\nBest config: {best_config} (retention={best_retention:.6f})")

# ===== Write results =====
results = {
    "best_lambda": float(best_lambda),
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

print("\n=== Final Results ===")
for key, val in results.items():
    print(f"{key}: {val}")

with open('answers.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults written to answers.json")
