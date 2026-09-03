import json
import numpy as np
from scipy import stats

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'], dtype=np.float32)
y = np.array(data['y'], dtype=np.int32)

n_samples, n_features = X.shape
print(f"Data shape: {n_samples} samples, {n_features} features")

# ============================================================================
# Helper functions for logistic regression
# ============================================================================

def sigmoid(z):
    """Sigmoid with clipping"""
    z = np.clip(z, -30, 30)
    return 1 / (1 + np.exp(-z))

def brier_score(y_true, y_pred):
    """Calculate Brier score"""
    return np.mean((y_pred - y_true) ** 2)

def fit_logistic(X_train, y_train, lambda_reg=0.0, learning_rate=0.1, iterations=200):
    """
    Fit logistic regression with full-batch gradient descent.
    """
    n = X_train.shape[0]
    d = X_train.shape[1]
    
    # Initialize weights and bias
    w = np.zeros(d, dtype=np.float32)
    b = 0.0
    
    for _ in range(iterations):
        # Compute logits
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)
        
        # Compute predictions
        y_pred = sigmoid(logits)
        
        # Compute gradients
        errors = y_pred - y_train
        grad_w = X_train.T @ errors
        grad_b = np.sum(errors)
        
        # Update weights with L2 regularization
        w = w - learning_rate * (grad_w / n + lambda_reg * w)
        b = b - learning_rate * (grad_b / n)
    
    return w, b

def predict(X, w, b):
    """Make predictions"""
    logits = X @ w + b
    logits = np.clip(logits, -30, 30)
    return sigmoid(logits)

# ============================================================================
# Task 1: Find best lambda with 5-fold cross-validation
# ============================================================================

lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
fold_size = n_samples // 5

results = {}

for lambda_val in lambdas:
    fold_briers = []
    
    for fold_idx in range(5):
        # Create fold split (contiguous blocks)
        test_indices = np.arange(fold_idx, n_samples, 5)
        train_indices = np.array([i for i in range(n_samples) if i not in test_indices])
        
        X_train, y_train = X[train_indices], y[train_indices]
        X_test, y_test = X[test_indices], y[test_indices]
        
        # Fit model
        w, b = fit_logistic(X_train, y_train, lambda_reg=lambda_val)
        
        # Evaluate
        y_pred = predict(X_test, w, b)
        brier = brier_score(y_test, y_pred)
        fold_briers.append(brier)
    
    results[lambda_val] = {
        'fold_briers': fold_briers,
        'mean_brier': np.mean(fold_briers)
    }
    print(f"Lambda {lambda_val}: mean Brier = {np.mean(fold_briers):.6f}, folds = {[f'{b:.6f}' for b in fold_briers]}")

# Find best lambda
best_lambda = min(results.keys(), key=lambda l: results[l]['mean_brier'])
baseline_brier = results[0.0]['mean_brier']
best_brier = results[best_lambda]['mean_brier']
improvement = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda}, Improvement: {improvement:.6f}")

# ============================================================================
# Task 2: Test interaction features
# ============================================================================

# Add interaction features
X_interactions = X.copy()
X_interactions = np.column_stack([
    X_interactions,
    X[:, 0] * X[:, 1],  # x0*x1
    X[:, 1] * X[:, 2],  # x1*x2
    X[:, 2] * X[:, 3],  # x2*x3
    X[:, 0] * X[:, 3],  # x0*x3
])

fold_briers_raw = []
fold_briers_interaction = []

for fold_idx in range(5):
    test_indices = np.arange(fold_idx, n_samples, 5)
    train_indices = np.array([i for i in range(n_samples) if i not in test_indices])
    
    # Raw features
    X_train_raw, y_train = X[train_indices], y[train_indices]
    X_test_raw, y_test = X[test_indices], y[test_indices]
    w_raw, b_raw = fit_logistic(X_train_raw, y_train, lambda_reg=0.1)
    y_pred_raw = predict(X_test_raw, w_raw, b_raw)
    brier_raw = brier_score(y_test, y_pred_raw)
    fold_briers_raw.append(brier_raw)
    
    # With interactions
    X_train_int, y_train = X_interactions[train_indices], y[train_indices]
    X_test_int, y_test = X_interactions[test_indices], y[test_indices]
    w_int, b_int = fit_logistic(X_train_int, y_train, lambda_reg=0.1)
    y_pred_int = predict(X_test_int, w_int, b_int)
    brier_int = brier_score(y_test, y_pred_int)
    fold_briers_interaction.append(brier_int)

# Paired t-test: raw minus interaction
fold_diffs = np.array(fold_briers_raw) - np.array(fold_briers_interaction)
paired_t_stat, _ = stats.ttest_rel(fold_briers_raw, fold_briers_interaction)
interaction_helps = paired_t_stat > 2.0

print(f"\nFold Brier scores (raw): {fold_briers_raw}")
print(f"Fold Brier scores (interaction): {fold_briers_interaction}")
print(f"Paired t-stat: {paired_t_stat:.6f}")
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# ============================================================================
# Task 3: Compression - find best configuration
# ============================================================================

# Fit dense model on all rows with lambda=0.1
w_dense, b_dense = fit_logistic(X, y, lambda_reg=0.1)
y_pred_dense = predict(X, w_dense, b_dense)
dense_brier = brier_score(y, y_pred_dense)

print(f"\nDense model Brier score (in-sample): {dense_brier:.6f}")

sparsity_levels = [20, 40, 60]
bit_levels = [8, 4]

best_config = None
best_retention = 0

for sparsity in sparsity_levels:
    for bits in bit_levels:
        # Apply sparsity (zero smallest magnitude weights)
        w_sparse = w_dense.copy()
        k = round(sparsity / 100.0 * len(w_dense))
        
        # Find k smallest absolute values
        abs_w = np.abs(w_sparse)
        threshold_idx = np.argsort(abs_w)[:k]
        w_sparse[threshold_idx] = 0
        
        # Apply quantization (only to non-zero weights)
        w_quantized = w_sparse.copy()
        mask = w_sparse != 0
        
        if np.any(mask):
            w_min = np.min(w_sparse[mask])
            w_max = np.max(w_sparse[mask])
            
            if w_min != w_max:
                # Map to 2^bits levels
                levels = np.linspace(w_min, w_max, 2**bits)
                for i in np.where(mask)[0]:
                    # Find nearest level
                    idx = np.argmin(np.abs(levels - w_sparse[i]))
                    w_quantized[i] = levels[idx]
        
        # Evaluate compressed model
        y_pred_compressed = predict(X, w_quantized, b_dense)
        compressed_brier = brier_score(y, y_pred_compressed)
        
        # Retention = dense / compressed
        if compressed_brier > 0:
            retention = dense_brier / compressed_brier
        else:
            retention = float('inf')
        
        config_name = f"sparsity{sparsity}_bits{bits}"
        print(f"{config_name}: Brier={compressed_brier:.6f}, Retention={retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = config_name

print(f"\nBest compression config: {best_config}")

# ============================================================================
# Write answers
# ============================================================================

answers = {
    "best_lambda": best_lambda,
    "improvement_over_baseline": improvement,
    "paired_t_stat": float(paired_t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("\nAnswers written to answers.json")
print(json.dumps(answers, indent=2))
