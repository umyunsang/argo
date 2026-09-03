import json
import numpy as np
from scipy import stats

# Load data
with open('data.json') as f:
    data = json.load(f)

X = np.array(data['X'])
y = np.array(data['y'])

n_samples = X.shape[0]
n_features = X.shape[1]

print(f"Data shape: {n_samples} samples, {n_features} features")

# Helper functions
def sigmoid(z):
    z = np.clip(z, -30, 30)
    return 1 / (1 + np.exp(-z))

def brier_score(y_true, y_pred_probs):
    """Compute Brier score: mean squared error between predictions and ground truth"""
    return np.mean((y_pred_probs - y_true) ** 2)

def fit_logistic_regression(X, y, lambda_reg=0.0, max_iter=200, learning_rate=0.1):
    """
    Fit logistic regression with full-batch gradient descent.
    w -= 0.1 * (grad_w / n + lambda * w); b -= 0.1 * (grad_b / n)
    """
    n, d = X.shape
    w = np.zeros(d)
    b = 0.0
    
    for iteration in range(max_iter):
        # Forward pass
        logits = X @ w + b
        logits = np.clip(logits, -30, 30)
        probs = sigmoid(logits)
        
        # Gradient computation
        error = probs - y
        grad_w = X.T @ error / n
        grad_b = np.mean(error)
        
        # Update with L2 regularization
        w -= learning_rate * (grad_w + lambda_reg * w)
        b -= learning_rate * grad_b
    
    return w, b

def predict_proba(X, w, b):
    """Get predicted probabilities"""
    logits = X @ w + b
    logits = np.clip(logits, -30, 30)
    return sigmoid(logits)

# ============================================================================
# Task 1: Find best lambda for L2 regularization
# ============================================================================
print("\n" + "="*70)
print("TASK 1: L2 Regularization (Brier Score)")
print("="*70)

lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
n_folds = 5
fold_size = n_samples // n_folds

brier_scores_per_lambda = {}
brier_per_fold_per_lambda = {}

for lam in lambdas:
    fold_briers = []
    
    for fold_idx in range(n_folds):
        # Create fold indices: fold k = rows k, k+5, k+10, ...
        test_indices = np.arange(fold_idx, n_samples, n_folds)
        train_indices = np.array([i for i in range(n_samples) if i not in test_indices])
        
        # Split data
        X_train, X_test = X[train_indices], X[test_indices]
        y_train, y_test = y[train_indices], y[test_indices]
        
        # Fit model
        w, b = fit_logistic_regression(X_train, y_train, lambda_reg=lam, 
                                       max_iter=200, learning_rate=0.1)
        
        # Evaluate on test fold
        y_pred_probs = predict_proba(X_test, w, b)
        fold_brier = brier_score(y_test, y_pred_probs)
        fold_briers.append(fold_brier)
    
    avg_brier = np.mean(fold_briers)
    brier_scores_per_lambda[lam] = avg_brier
    brier_per_fold_per_lambda[lam] = fold_briers
    print(f"Lambda {lam:5.2f}: avg Brier = {avg_brier:.6f}, folds = {[f'{b:.6f}' for b in fold_briers]}")

# Find best lambda
best_lambda = min(brier_scores_per_lambda, key=brier_scores_per_lambda.get)
best_brier = brier_scores_per_lambda[best_lambda]
baseline_brier = brier_scores_per_lambda[0.0]
improvement = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda}")
print(f"Best Brier score: {best_brier:.6f}")
print(f"Baseline (lambda=0) Brier: {baseline_brier:.6f}")
print(f"Improvement: {improvement:.6f}")

# ============================================================================
# Task 2: Paired t-test with interaction terms
# ============================================================================
print("\n" + "="*70)
print("TASK 2: Interaction Terms & Paired t-test")
print("="*70)

# Create interaction features: x0*x1, x1*x2, x2*x3, x0*x3
X_with_interactions = X.copy()
X_with_interactions = np.hstack([
    X_with_interactions,
    (X[:, 0:1] * X[:, 1:2]),  # x0*x1
    (X[:, 1:2] * X[:, 2:3]),  # x1*x2
    (X[:, 2:3] * X[:, 3:4]),  # x2*x3
    (X[:, 0:1] * X[:, 3:4])   # x0*x3
])

print(f"Original features: {X.shape[1]}")
print(f"Features with interactions: {X_with_interactions.shape[1]}")

# Fit both representations with lambda=0.1 on 5 folds
lambda_interaction = 0.1
fold_briers_raw = []
fold_briers_interaction = []

for fold_idx in range(n_folds):
    test_indices = np.arange(fold_idx, n_samples, n_folds)
    train_indices = np.array([i for i in range(n_samples) if i not in test_indices])
    
    X_train, X_test = X[train_indices], X[test_indices]
    X_train_int, X_test_int = X_with_interactions[train_indices], X_with_interactions[test_indices]
    y_train, y_test = y[train_indices], y[test_indices]
    
    # Raw features
    w_raw, b_raw = fit_logistic_regression(X_train, y_train, lambda_reg=lambda_interaction,
                                           max_iter=200, learning_rate=0.1)
    y_pred_raw = predict_proba(X_test, w_raw, b_raw)
    brier_raw = brier_score(y_test, y_pred_raw)
    fold_briers_raw.append(brier_raw)
    
    # With interactions
    w_int, b_int = fit_logistic_regression(X_train_int, y_train, lambda_reg=lambda_interaction,
                                           max_iter=200, learning_rate=0.1)
    y_pred_int = predict_proba(X_test_int, w_int, b_int)
    brier_int = brier_score(y_test, y_pred_int)
    fold_briers_interaction.append(brier_int)
    
    print(f"Fold {fold_idx}: Raw Brier = {brier_raw:.6f}, Interaction Brier = {brier_int:.6f}, Diff = {brier_raw - brier_int:.6f}")

fold_briers_raw = np.array(fold_briers_raw)
fold_briers_interaction = np.array(fold_briers_interaction)

# Paired t-test: raw minus interaction
differences = fold_briers_raw - fold_briers_interaction
t_stat, p_value = stats.ttest_rel(fold_briers_raw, fold_briers_interaction)

print(f"\nPaired t-test results:")
print(f"Differences (raw - interaction): {differences}")
print(f"Mean difference: {np.mean(differences):.6f}")
print(f"t-statistic: {t_stat:.6f}")
print(f"p-value: {p_value:.6f}")

interaction_helps = t_stat > 2.0
print(f"interaction_helps (t > 2.0): {interaction_helps}")

# ============================================================================
# Task 3: Compression - sparsity and quantization
# ============================================================================
print("\n" + "="*70)
print("TASK 3: Model Compression")
print("="*70)

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic_regression(X, y, lambda_reg=0.1, max_iter=200, learning_rate=0.1)
y_pred_dense = predict_proba(X, w_dense, b_dense)
brier_dense = brier_score(y, y_pred_dense)

print(f"Dense model Brier (on all data): {brier_dense:.6f}")

sparsities = [20, 40, 60]  # percent
bits_options = [8, 4]

best_retention = 0
best_config = None
results = []

for sparsity_pct in sparsities:
    for bits in bits_options:
        # Apply sparsity: zero out smallest magnitude weights
        w_sparse = w_dense.copy()
        k = round((sparsity_pct / 100.0) * len(w_dense))
        if k > 0:
            # Find k smallest magnitude indices
            indices_to_zero = np.argsort(np.abs(w_sparse))[:k]
            w_sparse[indices_to_zero] = 0
        
        # Apply quantization to non-zero weights
        # Map to 2^bits levels between min and max
        non_zero_mask = w_sparse != 0
        if np.any(non_zero_mask):
            w_min = np.min(w_sparse[non_zero_mask])
            w_max = np.max(w_sparse[non_zero_mask])
            
            if w_min != w_max:
                n_levels = 2 ** bits
                # Map to [0, n_levels-1] then back to [w_min, w_max]
                w_quantized = w_sparse.copy()
                w_quantized[non_zero_mask] = (w_sparse[non_zero_mask] - w_min) / (w_max - w_min)
                w_quantized[non_zero_mask] = np.round(w_quantized[non_zero_mask] * (n_levels - 1)) / (n_levels - 1)
                w_quantized[non_zero_mask] = w_quantized[non_zero_mask] * (w_max - w_min) + w_min
            else:
                w_quantized = w_sparse.copy()
        else:
            w_quantized = w_sparse.copy()
        
        # Evaluate compressed model
        y_pred_compressed = predict_proba(X, w_quantized, b_dense)
        brier_compressed = brier_score(y, y_pred_compressed)
        
        # Retention = dense Brier / compressed Brier
        retention = brier_dense / brier_compressed if brier_compressed > 0 else float('inf')
        
        config_str = f"sparsity{sparsity_pct}_bits{bits}"
        results.append({
            'config': config_str,
            'sparsity': sparsity_pct,
            'bits': bits,
            'dense_brier': brier_dense,
            'compressed_brier': brier_compressed,
            'retention': retention
        })
        
        print(f"{config_str}: dense_brier={brier_dense:.6f}, compressed_brier={brier_compressed:.6f}, retention={retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = config_str

print(f"\nBest compression config: {best_config} with retention {best_retention:.6f}")

# ============================================================================
# Write results
# ============================================================================
output = {
    "best_lambda": best_lambda,
    "improvement_over_baseline": improvement,
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

print("\n" + "="*70)
print("FINAL ANSWERS")
print("="*70)
for key, value in output.items():
    print(f"{key}: {value}")

with open('answers.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nAnswers written to answers.json")
