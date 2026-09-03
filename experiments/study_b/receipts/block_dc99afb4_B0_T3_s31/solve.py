import json
import numpy as np
from scipy.stats import ttest_rel

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'])
y = np.array(data['y']).astype(float)

n_samples = X.shape[0]
n_features = X.shape[1]

print(f"Data shape: {X.shape}, y shape: {y.shape}")

# Task 1: Find best lambda and improvement
# 5-fold CV with contiguous blocks
lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
n_folds = 5
fold_size = n_samples // n_folds

def sigmoid(z):
    return 1 / (1 + np.exp(-np.clip(z, -30, 30)))

def brier_score(y_true, y_pred):
    return np.mean((y_true - y_pred) ** 2)

def fit_logistic(X_train, y_train, lambda_reg, learning_rate=0.1, iterations=200):
    """Fit logistic regression with specified conventions"""
    n = X_train.shape[0]
    d = X_train.shape[1]
    
    w = np.zeros(d)
    b = 0.0
    
    for iteration in range(iterations):
        # Forward pass
        z = X_train @ w + b
        z = np.clip(z, -30, 30)  # Clip logits
        y_pred = sigmoid(z)
        
        # Gradient computation (binary cross-entropy loss)
        error = y_pred - y_train
        grad_w = X_train.T @ error / n
        grad_b = np.mean(error)
        
        # Update (full-batch gradient descent)
        w = w - learning_rate * (grad_w + lambda_reg * w)
        b = b - learning_rate * grad_b
    
    return w, b

def predict_logistic(X_test, w, b):
    """Make predictions"""
    z = X_test @ w + b
    z = np.clip(z, -30, 30)
    return sigmoid(z)

# Evaluate all lambdas with 5-fold CV
cv_scores = {lam: [] for lam in lambdas}

for fold_idx in range(n_folds):
    # Create fold split: fold k is the k-th consecutive slice
    test_start = fold_idx * fold_size
    test_end = test_start + fold_size
    
    X_test_fold = X[test_start:test_end]
    y_test_fold = y[test_start:test_end]
    
    X_train_fold = np.vstack([X[:test_start], X[test_end:]])
    y_train_fold = np.hstack([y[:test_start], y[test_end:]])
    
    for lam in lambdas:
        w, b = fit_logistic(X_train_fold, y_train_fold, lam)
        y_pred = predict_logistic(X_test_fold, w, b)
        brier = brier_score(y_test_fold, y_pred)
        cv_scores[lam].append(brier)

# Calculate mean CV scores
mean_cv_scores = {lam: np.mean(cv_scores[lam]) for lam in lambdas}
print("\nMean CV Brier scores:")
for lam in lambdas:
    print(f"  lambda={lam}: {mean_cv_scores[lam]:.6f}")

# Find best lambda
best_lambda = min(mean_cv_scores, key=mean_cv_scores.get)
improvement = mean_cv_scores[0.0] - mean_cv_scores[best_lambda]

print(f"\nBest lambda: {best_lambda}")
print(f"Improvement over baseline (lambda=0): {improvement:.6f}")

# Task 2: Interaction features and paired t-test
# Add products: x0*x1, x1*x2, x2*x3, x0*x3
X_interaction = X.copy()
X_interaction = np.hstack([
    X_interaction,
    (X[:, 0] * X[:, 1]).reshape(-1, 1),  # x0*x1
    (X[:, 1] * X[:, 2]).reshape(-1, 1),  # x1*x2
    (X[:, 2] * X[:, 3]).reshape(-1, 1),  # x2*x3
    (X[:, 0] * X[:, 3]).reshape(-1, 1),  # x0*x3
])

print(f"\nX_interaction shape: {X_interaction.shape}")

# Evaluate both models with lambda=0.1
lambda_interaction = 0.1
brier_raw_folds = []
brier_interaction_folds = []

for fold_idx in range(n_folds):
    test_start = fold_idx * fold_size
    test_end = test_start + fold_size
    
    # Raw model
    X_train_raw = np.vstack([X[:test_start], X[test_end:]])
    y_train_fold = np.hstack([y[:test_start], y[test_end:]])
    X_test_raw = X[test_start:test_end]
    
    w_raw, b_raw = fit_logistic(X_train_raw, y_train_fold, lambda_interaction)
    y_pred_raw = predict_logistic(X_test_raw, w_raw, b_raw)
    brier_raw = brier_score(y[test_start:test_end], y_pred_raw)
    brier_raw_folds.append(brier_raw)
    
    # Interaction model
    X_train_inter = np.vstack([X_interaction[:test_start], X_interaction[test_end:]])
    X_test_inter = X_interaction[test_start:test_end]
    
    w_inter, b_inter = fit_logistic(X_train_inter, y_train_fold, lambda_interaction)
    y_pred_inter = predict_logistic(X_test_inter, w_inter, b_inter)
    brier_inter = brier_score(y[test_start:test_end], y_pred_inter)
    brier_interaction_folds.append(brier_inter)

print("\nRaw model Brier scores per fold:")
for i, b in enumerate(brier_raw_folds):
    print(f"  Fold {i}: {b:.6f}")

print("\nInteraction model Brier scores per fold:")
for i, b in enumerate(brier_interaction_folds):
    print(f"  Fold {i}: {b:.6f}")

# Paired t-test: raw minus interaction
differences = np.array(brier_raw_folds) - np.array(brier_interaction_folds)
print(f"\nDifferences (raw - interaction): {differences}")

t_stat, p_value = ttest_rel(brier_raw_folds, brier_interaction_folds)
print(f"Paired t-test t-statistic: {t_stat:.6f}")
print(f"P-value: {p_value:.6f}")

interaction_helps = t_stat > 2.0
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# Task 3: Compression - sparsity and quantization
# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic(X, y, 0.1)
y_pred_dense = predict_logistic(X, w_dense, b_dense)
brier_dense = brier_score(y, y_pred_dense)

print(f"\nDense model Brier score: {brier_dense:.6f}")

# Test all configurations
sparsity_levels = [20, 40, 60]
bit_levels = [8, 4]

best_config = None
best_retention = 0

for sparsity in sparsity_levels:
    for bits in bit_levels:
        # Apply sparsity: zero out smallest magnitude weights
        k = round((sparsity / 100.0) * len(w_dense))
        w_sparse = w_dense.copy()
        
        # Get indices of k smallest magnitude weights
        magnitude = np.abs(w_sparse)
        threshold_idx = np.argsort(magnitude)[: k]
        w_sparse[threshold_idx] = 0
        
        # Apply quantization to non-zero weights
        nonzero_mask = w_sparse != 0
        if np.any(nonzero_mask):
            w_nonzero = w_sparse[nonzero_mask]
            min_val = np.min(w_nonzero)
            max_val = np.max(w_nonzero)
            
            # Map to 2^bits levels
            n_levels = 2 ** bits
            if max_val > min_val:
                w_sparse[nonzero_mask] = np.round(
                    (w_nonzero - min_val) / (max_val - min_val) * (n_levels - 1)
                ) / (n_levels - 1) * (max_val - min_val) + min_val
        
        # Evaluate compressed model
        y_pred_compressed = predict_logistic(X, w_sparse, b_dense)
        brier_compressed = brier_score(y, y_pred_compressed)
        
        # Retention = dense Brier / compressed Brier
        retention = brier_dense / brier_compressed if brier_compressed > 0 else 0
        
        config_name = f"sparsity{sparsity}_bits{bits}"
        print(f"{config_name}: brier_compressed={brier_compressed:.6f}, retention={retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = config_name

print(f"\nBest config: {best_config} with retention: {best_retention:.6f}")

# Prepare answers
answers = {
    "best_lambda": float(best_lambda),
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

print("\n" + "=" * 50)
print("FINAL ANSWERS:")
print("=" * 50)
print(json.dumps(answers, indent=2))

# Write answers to file
with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("\nAnswers written to answers.json")
