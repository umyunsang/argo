import json
import numpy as np
from scipy import stats

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'])
y = np.array(data['y'])

n_samples = X.shape[0]
n_features = X.shape[1]

print(f"Data shape: {X.shape}, labels: {y.shape}")

# ============================================================================
# Helper functions for logistic regression
# ============================================================================

def sigmoid(z):
    """Sigmoid with clipping to [-30, 30]"""
    z = np.clip(z, -30, 30)
    return 1 / (1 + np.exp(-z))

def compute_brier_score(y_true, y_pred):
    """Compute Brier score: mean squared error of predicted probabilities"""
    return np.mean((y_pred - y_true) ** 2)

def fit_logistic(X_train, y_train, lambda_reg, num_iterations=200, learning_rate=0.1):
    """
    Fit logistic regression with full-batch gradient descent.
    """
    n = X_train.shape[0]
    d = X_train.shape[1]
    
    # Initialize weights and bias to zero
    w = np.zeros(d)
    b = 0.0
    
    for iteration in range(num_iterations):
        # Compute logits and clip them
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)
        
        # Compute predictions (sigmoid)
        y_pred = sigmoid(logits)
        
        # Compute gradients
        errors = y_pred - y_train
        grad_w = X_train.T @ errors / n
        grad_b = np.sum(errors) / n
        
        # Update with L2 regularization
        w = w - learning_rate * (grad_w + lambda_reg * w)
        b = b - learning_rate * grad_b
    
    return w, b

def predict_proba(X, w, b):
    """Predict probabilities"""
    logits = X @ w + b
    logits = np.clip(logits, -30, 30)
    return sigmoid(logits)

# ============================================================================
# Task 1: Find best lambda for L2 regularization
# ============================================================================

lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
fold_size = n_samples // 5

print("\n=== Task 1: L2 Regularization ===")
print(f"Fold size: {fold_size}")

brier_scores_by_lambda = {}

for lambda_val in lambdas:
    fold_briers = []
    
    for fold_idx in range(5):
        # Create contiguous fold
        test_idx = np.arange(fold_idx, n_samples, 5)
        train_idx = np.setdiff1d(np.arange(n_samples), test_idx)
        
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Fit model
        w, b = fit_logistic(X_train, y_train, lambda_val)
        
        # Evaluate
        y_pred = predict_proba(X_test, w, b)
        brier = compute_brier_score(y_test, y_pred)
        fold_briers.append(brier)
    
    mean_brier = np.mean(fold_briers)
    brier_scores_by_lambda[lambda_val] = fold_briers
    print(f"Lambda {lambda_val}: Brier scores per fold = {fold_briers}, Mean = {mean_brier:.6f}")

# Find best lambda
best_lambda = min(lambdas, key=lambda x: np.mean(brier_scores_by_lambda[x]))
best_brier = np.mean(brier_scores_by_lambda[best_lambda])
baseline_brier = np.mean(brier_scores_by_lambda[0.0])
improvement = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda}")
print(f"Best Brier (mean): {best_brier:.6f}")
print(f"Baseline Brier (lambda=0): {baseline_brier:.6f}")
print(f"Improvement: {improvement:.6f}")

# ============================================================================
# Task 2: Paired t-test with interaction features
# ============================================================================

print("\n=== Task 2: Interaction Features ===")

lambda_test = 0.1

# Create interaction features: x0*x1, x1*x2, x2*x3, x0*x3
X_interaction = X.copy()
X_interaction = np.hstack([
    X_interaction,
    X[:, 0:1] * X[:, 1:2],  # x0*x1
    X[:, 1:2] * X[:, 2:3],  # x1*x2
    X[:, 2:3] * X[:, 3:4],  # x2*x3
    X[:, 0:1] * X[:, 3:4],  # x0*x3
])

print(f"Original features: {X.shape[1]}")
print(f"Features with interaction: {X_interaction.shape[1]}")

# Run 5-fold cross-validation on both representations
fold_briers_raw = []
fold_briers_interaction = []

for fold_idx in range(5):
    test_idx = np.arange(fold_idx, n_samples, 5)
    train_idx = np.setdiff1d(np.arange(n_samples), test_idx)
    
    # Raw representation
    X_train_raw = X[train_idx]
    X_test_raw = X[test_idx]
    y_train = y[train_idx]
    y_test = y[test_idx]
    
    w_raw, b_raw = fit_logistic(X_train_raw, y_train, lambda_test)
    y_pred_raw = predict_proba(X_test_raw, w_raw, b_raw)
    brier_raw = compute_brier_score(y_test, y_pred_raw)
    fold_briers_raw.append(brier_raw)
    
    # Interaction representation
    X_train_int = X_interaction[train_idx]
    X_test_int = X_interaction[test_idx]
    
    w_int, b_int = fit_logistic(X_train_int, y_train, lambda_test)
    y_pred_int = predict_proba(X_test_int, w_int, b_int)
    brier_int = compute_brier_score(y_test, y_pred_int)
    fold_briers_interaction.append(brier_int)

print(f"Raw Brier per fold: {fold_briers_raw}")
print(f"Interaction Brier per fold: {fold_briers_interaction}")

# Paired t-test: raw - interaction (to see if interaction helps)
# We want to test if interaction reduces Brier (makes it negative when subtracting)
differences = np.array(fold_briers_raw) - np.array(fold_briers_interaction)
print(f"Differences (raw - interaction): {differences}")

# Paired t-test
t_stat, p_value = stats.ttest_rel(fold_briers_raw, fold_briers_interaction)
print(f"Paired t-test: t-statistic = {t_stat:.6f}, p-value = {p_value:.6f}")

interaction_helps = t_stat > 2.0
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# ============================================================================
# Task 3: Compression - sparsity and quantization
# ============================================================================

print("\n=== Task 3: Compression ===")

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic(X, y, 0.1)

# Evaluate on training data (in-sample)
y_pred_dense = predict_proba(X, w_dense, b_dense)
brier_dense = compute_brier_score(y, y_pred_dense)
print(f"Dense model Brier (in-sample): {brier_dense:.6f}")

sparsities = [20, 40, 60]
bits_list = [8, 4]

results = []

for sparsity in sparsities:
    for bits in bits_list:
        # Apply sparsity
        k = round(sparsity / 100.0 * n_features)
        
        # Zero out smallest magnitude weights
        w_sparse = w_dense.copy()
        threshold_idx = np.argsort(np.abs(w_sparse))[:-k] if k > 0 else np.arange(n_features)
        w_sparse[threshold_idx] = 0
        
        # Apply quantization to non-zero weights
        nonzero_mask = w_sparse != 0
        if np.any(nonzero_mask):
            w_min = np.min(w_sparse[nonzero_mask])
            w_max = np.max(w_sparse[nonzero_mask])
            
            if w_min == w_max:
                # All non-zero weights are the same
                w_quant = w_sparse.copy()
            else:
                # Map to 2^bits levels
                w_normalized = (w_sparse[nonzero_mask] - w_min) / (w_max - w_min)
                n_levels = 2 ** bits
                w_quantized = np.round(w_normalized * (n_levels - 1)) / (n_levels - 1)
                w_quant = w_sparse.copy()
                w_quant[nonzero_mask] = w_min + w_quantized * (w_max - w_min)
        else:
            w_quant = w_sparse.copy()
        
        # Evaluate
        y_pred_quant = predict_proba(X, w_quant, b_dense)
        brier_quant = compute_brier_score(y, y_pred_quant)
        
        retention = brier_dense / brier_quant if brier_quant > 0 else float('inf')
        
        config_name = f"sparsity{sparsity}_bits{bits}"
        results.append({
            'config': config_name,
            'sparsity': sparsity,
            'bits': bits,
            'brier': brier_quant,
            'retention': retention,
            'k_zeros': n_features - k
        })
        
        print(f"Config {config_name}: Brier={brier_quant:.6f}, Retention={retention:.6f}, Non-zero weights={n_features - k}")

# Find best config (highest retention)
best_config = max(results, key=lambda x: x['retention'])
print(f"\nBest config: {best_config['config']} with retention {best_config['retention']:.6f}")

# ============================================================================
# Write answers to JSON
# ============================================================================

answers = {
    "best_lambda": float(best_lambda),
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config['config']
}

print("\n=== Final Answers ===")
print(json.dumps(answers, indent=2))

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("\nAnswers written to answers.json")
