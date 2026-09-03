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

# ============================================================================
# Utility functions for logistic regression
# ============================================================================

def sigmoid(z):
    """Stable sigmoid function"""
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))

def compute_brier_score(y_true, y_pred_prob):
    """Compute Brier score: mean squared error between predictions and labels"""
    return np.mean((y_pred_prob - y_true) ** 2)

def fit_logistic_regression(X_train, y_train, lambda_reg=0.0, learning_rate=0.1, n_iterations=200):
    """
    Fit logistic regression using full-batch gradient descent.
    
    Update rule:
    w -= learning_rate * (grad_w / n + lambda * w)
    b -= learning_rate * (grad_b / n)
    
    Logits are clipped to [-30, 30]
    """
    n, d = X_train.shape
    w = np.zeros(d)
    b = 0.0
    
    for iteration in range(n_iterations):
        # Forward pass
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)  # Clip logits
        pred = sigmoid(logits)
        
        # Compute gradients
        error = pred - y_train
        grad_w = X_train.T @ error
        grad_b = np.sum(error)
        
        # Update weights
        w = w - learning_rate * (grad_w / n + lambda_reg * w)
        b = b - learning_rate * (grad_b / n)
    
    return w, b

def predict_logistic(X_test, w, b):
    """Predict probabilities using fitted model"""
    logits = X_test @ w + b
    logits = np.clip(logits, -30, 30)
    return sigmoid(logits)

# ============================================================================
# Create 5-fold contiguous blocks
# ============================================================================

def create_folds_contiguous(n_samples, n_folds=5):
    """Create contiguous folds: fold k = rows k, k+5, k+10, ..."""
    folds = [[] for _ in range(n_folds)]
    for i in range(n_samples):
        fold_id = i % n_folds
        folds[fold_id].append(i)
    return folds

folds = create_folds_contiguous(n_samples, n_folds=5)
print(f"Fold sizes: {[len(f) for f in folds]}")

# ============================================================================
# Question 1: Find best lambda and improvement over baseline
# ============================================================================

lambda_values = [0.0, 0.01, 0.1, 1.0, 10.0]
brier_scores_per_lambda = {lam: [] for lam in lambda_values}

print("\n=== Question 1: Lambda tuning ===")

for lam in lambda_values:
    print(f"Lambda = {lam}")
    for fold_id in range(5):
        # Get train and test indices
        test_indices = np.array(folds[fold_id])
        train_indices = np.concatenate([folds[i] for i in range(5) if i != fold_id])
        
        X_train, y_train = X[train_indices], y[train_indices]
        X_test, y_test = X[test_indices], y[test_indices]
        
        # Fit model
        w, b = fit_logistic_regression(X_train, y_train, lambda_reg=lam, learning_rate=0.1, n_iterations=200)
        
        # Predict and compute Brier score on test set
        y_pred = predict_logistic(X_test, w, b)
        brier = compute_brier_score(y_test, y_pred)
        brier_scores_per_lambda[lam].append(brier)
        print(f"  Fold {fold_id}: Brier = {brier:.6f}")
    
    avg_brier = np.mean(brier_scores_per_lambda[lam])
    print(f"  Average Brier: {avg_brier:.6f}")

# Find best lambda
avg_briers = {lam: np.mean(brier_scores_per_lambda[lam]) for lam in lambda_values}
best_lambda = min(avg_briers, key=avg_briers.get)
best_brier = avg_briers[best_lambda]
baseline_brier = avg_briers[0.0]
improvement = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda}")
print(f"Best Brier: {best_brier:.6f}")
print(f"Baseline (lambda=0) Brier: {baseline_brier:.6f}")
print(f"Improvement: {improvement:.6f}")

# ============================================================================
# Question 2: Interaction terms and paired t-test
# ============================================================================

print("\n=== Question 2: Interaction terms ===")

# Add interaction features
interaction_features = np.zeros((n_samples, 4))
interaction_features[:, 0] = X[:, 0] * X[:, 1]  # x0*x1
interaction_features[:, 1] = X[:, 1] * X[:, 2]  # x1*x2
interaction_features[:, 2] = X[:, 2] * X[:, 3]  # x2*x3
interaction_features[:, 3] = X[:, 0] * X[:, 3]  # x0*x3

# Fit models with lambda=0.1
lambda_tuning = 0.1
brier_raw = []
brier_interaction = []

for fold_id in range(5):
    test_indices = np.array(folds[fold_id])
    train_indices = np.concatenate([folds[i] for i in range(5) if i != fold_id])
    
    # Raw features
    X_train_raw, y_train = X[train_indices], y[train_indices]
    X_test_raw, y_test = X[test_indices], y[test_indices]
    
    w_raw, b_raw = fit_logistic_regression(X_train_raw, y_train, lambda_reg=lambda_tuning)
    y_pred_raw = predict_logistic(X_test_raw, w_raw, b_raw)
    brier_raw.append(compute_brier_score(y_test, y_pred_raw))
    
    # Raw + interaction features
    X_train_int = np.hstack([X_train_raw, interaction_features[train_indices]])
    X_test_int = np.hstack([X_test_raw, interaction_features[test_indices]])
    
    w_int, b_int = fit_logistic_regression(X_train_int, y_train, lambda_reg=lambda_tuning)
    y_pred_int = predict_logistic(X_test_int, w_int, b_int)
    brier_interaction.append(compute_brier_score(y_test, y_pred_int))
    
    print(f"Fold {fold_id}: Raw Brier = {brier_raw[-1]:.6f}, Interaction Brier = {brier_interaction[-1]:.6f}")

brier_raw = np.array(brier_raw)
brier_interaction = np.array(brier_interaction)

# Paired t-test: raw minus interaction
differences = brier_raw - brier_interaction
t_stat, p_value = stats.ttest_rel(brier_raw, brier_interaction)

print(f"\nPaired t-test results:")
print(f"  Differences: {differences}")
print(f"  t-statistic: {t_stat:.6f}")
print(f"  p-value: {p_value:.6f}")

# interaction_helps is true only if t > 2.0
interaction_helps = t_stat > 2.0

print(f"  interaction_helps (t > 2.0): {interaction_helps}")

# ============================================================================
# Question 3: Compression (sparsity and quantization)
# ============================================================================

print("\n=== Question 3: Compression ===")

# Fit dense model once on all data with lambda=0.1
w_dense, b_dense = fit_logistic_regression(X, y, lambda_reg=0.1)
y_pred_dense = predict_logistic(X, w_dense, b_dense)
brier_dense = compute_brier_score(y, y_pred_dense)

print(f"Dense model Brier (in-sample): {brier_dense:.6f}")

sparsity_percents = [20, 40, 60]
bits_options = [4, 8]

best_retention = 0.0
best_config = None

for sparsity_percent in sparsity_percents:
    for bits in bits_options:
        # Apply sparsity
        w_sparse = w_dense.copy()
        k = round(sparsity_percent / 100.0 * len(w_dense))
        
        # Zero out smallest magnitude weights
        if k > 0:
            threshold_idx = np.argsort(np.abs(w_sparse))[: k]
            w_sparse[threshold_idx] = 0.0
        
        # Apply quantization (on non-zero weights)
        w_quantized = w_sparse.copy()
        non_zero_mask = w_sparse != 0
        if np.any(non_zero_mask):
            non_zero_weights = w_sparse[non_zero_mask]
            min_w = np.min(non_zero_weights)
            max_w = np.max(non_zero_weights)
            
            if max_w > min_w:
                # Map to 2^bits levels
                n_levels = 2 ** bits
                quantized = np.round((non_zero_weights - min_w) / (max_w - min_w) * (n_levels - 1))
                w_quantized[non_zero_mask] = min_w + quantized / (n_levels - 1) * (max_w - min_w)
        
        # Compute in-sample Brier with compressed model
        logits_compressed = X @ w_quantized + b_dense
        logits_compressed = np.clip(logits_compressed, -30, 30)
        y_pred_compressed = sigmoid(logits_compressed)
        brier_compressed = compute_brier_score(y, y_pred_compressed)
        
        retention = brier_dense / brier_compressed if brier_compressed > 0 else 0
        
        print(f"Sparsity {sparsity_percent}%, Bits {bits}: Brier = {brier_compressed:.6f}, Retention = {retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = (sparsity_percent, bits)

print(f"\nBest config: sparsity={best_config[0]}%, bits={best_config[1]}")
print(f"Best retention: {best_retention:.6f}")

# ============================================================================
# Save answers
# ============================================================================

answers = {
    "best_lambda": float(best_lambda),
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": f"sparsity{best_config[0]}_bits{best_config[1]}"
}

print("\n=== Final Answers ===")
print(json.dumps(answers, indent=2))

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("\nAnswers saved to answers.json")
