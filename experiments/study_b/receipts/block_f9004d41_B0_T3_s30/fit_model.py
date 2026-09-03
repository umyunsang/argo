import json
import numpy as np
from scipy import stats

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'])
y = np.array(data['y'])

n_samples, n_features = X.shape
print(f"Data shape: {n_samples} samples, {n_features} features")

# Helper function for logistic regression
def sigmoid(z):
    """Numerically stable sigmoid"""
    z = np.clip(z, -500, 500)
    return 1.0 / (1.0 + np.exp(-z))

def fit_logistic_regression(X_train, y_train, lambda_reg=0.0, iterations=200, learning_rate=0.1):
    """
    Fit logistic regression with full-batch gradient descent
    - Weights and bias start at 0
    - Logits clipped to [-30, 30]
    - Update: w -= lr * (grad_w / n + lambda * w); b -= lr * (grad_b / n)
    """
    n_samples, n_features = X_train.shape
    w = np.zeros(n_features)
    b = 0.0
    
    for iteration in range(iterations):
        # Forward pass
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)
        y_pred = sigmoid(logits)
        
        # Compute gradients
        error = y_pred - y_train
        grad_w = X_train.T @ error / n_samples
        grad_b = np.sum(error) / n_samples
        
        # Update weights (with L2 regularization)
        w -= learning_rate * (grad_w + lambda_reg * w)
        b -= learning_rate * grad_b
    
    return w, b

def predict_proba(X_test, w, b):
    """Predict probability"""
    logits = X_test @ w + b
    logits = np.clip(logits, -30, 30)
    return sigmoid(logits)

def brier_score(y_true, y_pred):
    """Compute Brier score (mean squared error)"""
    return np.mean((y_pred - y_true) ** 2)

# 5-fold cross-validation with contiguous blocks
def cross_validate(X, y, lambda_reg=0.0, iterations=200, learning_rate=0.1):
    """
    5-fold cross-validation with contiguous blocks
    Fold k = k-th consecutive slice
    """
    n_samples = X.shape[0]
    fold_size = n_samples // 5
    
    brier_scores = []
    
    for fold_idx in range(5):
        # Create fold indices (contiguous blocks)
        test_start = fold_idx * fold_size
        test_end = test_start + fold_size if fold_idx < 4 else n_samples
        
        test_indices = np.arange(test_start, test_end)
        train_indices = np.concatenate([
            np.arange(0, test_start),
            np.arange(test_end, n_samples)
        ])
        
        X_train, X_test = X[train_indices], X[test_indices]
        y_train, y_test = y[train_indices], y[test_indices]
        
        # Fit model
        w, b = fit_logistic_regression(X_train, y_train, lambda_reg, iterations, learning_rate)
        
        # Predict
        y_pred = predict_proba(X_test, w, b)
        
        # Compute Brier score
        bs = brier_score(y_test, y_pred)
        brier_scores.append(bs)
    
    return np.array(brier_scores)

print("\n=== Question 1: Best Lambda and Improvement ===")
lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
lambda_results = {}

for lam in lambdas:
    bs = cross_validate(X, y, lambda_reg=lam)
    mean_bs = np.mean(bs)
    lambda_results[lam] = bs
    print(f"Lambda={lam}: Brier scores={bs}, Mean={mean_bs:.6f}")

# Find best lambda
best_idx = np.argmin([np.mean(lambda_results[lam]) for lam in lambdas])
best_lambda = lambdas[best_idx]
best_brier = np.mean(lambda_results[best_lambda])
baseline_brier = np.mean(lambda_results[0.0])
improvement = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda}")
print(f"Best Brier score: {best_brier:.6f}")
print(f"Baseline (lambda=0) Brier score: {baseline_brier:.6f}")
print(f"Improvement: {improvement:.6f}")

print("\n=== Question 2: Interaction Terms ===")
# Add interaction terms: x0*x1, x1*x2, x2*x3, x0*x3
X_with_interactions = np.column_stack([
    X,
    X[:, 0] * X[:, 1],  # x0*x1
    X[:, 1] * X[:, 2],  # x1*x2
    X[:, 2] * X[:, 3],  # x2*x3
    X[:, 0] * X[:, 3],  # x0*x3
])

print(f"Original X shape: {X.shape}")
print(f"X with interactions shape: {X_with_interactions.shape}")

# Fit both representations with lambda=0.1
bs_raw = cross_validate(X, y, lambda_reg=0.1)
bs_interaction = cross_validate(X_with_interactions, y, lambda_reg=0.1)

print(f"\nRaw representation Brier scores: {bs_raw}")
print(f"Interaction representation Brier scores: {bs_interaction}")

# Paired t-test: raw minus interaction
differences = bs_raw - bs_interaction
print(f"\nDifferences (raw - interaction): {differences}")

# Compute paired t-statistic
t_stat, p_value = stats.ttest_rel(bs_raw, bs_interaction)
print(f"Paired t-test: t={t_stat:.6f}, p-value={p_value:.6f}")

interaction_helps = t_stat > 2.0
print(f"Interaction helps (t > 2.0): {interaction_helps}")

print("\n=== Question 3: Compression ===")
# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic_regression(X, y, lambda_reg=0.1)

# Get in-sample predictions for dense model
y_pred_dense = predict_proba(X, w_dense, b_dense)
brier_dense = brier_score(y, y_pred_dense)
print(f"Dense model in-sample Brier score: {brier_dense:.6f}")

# Try all compression configurations
sparsities = [20, 40, 60]  # percentages
bits = [8, 4]

results = {}
for sparsity_pct in sparsities:
    for bit_depth in bits:
        # Apply sparsity: zero out k weights with smallest magnitude
        k = round(sparsity_pct / 100.0 * len(w_dense))
        w_sparse = w_dense.copy()
        
        # Find indices of k smallest magnitude weights
        abs_w = np.abs(w_sparse)
        threshold_idx = np.argsort(abs_w)[:k]
        w_sparse[threshold_idx] = 0.0
        
        # Apply quantization: map remaining weights uniformly to 2^bits levels
        w_quantized = w_sparse.copy()
        non_zero_mask = w_sparse != 0
        
        if np.any(non_zero_mask):
            w_min = np.min(w_sparse[non_zero_mask])
            w_max = np.max(w_sparse[non_zero_mask])
            
            if w_min < w_max:
                # Quantize to 2^bits levels
                n_levels = 2 ** bit_depth
                # Map to [0, n_levels-1]
                w_normalized = (w_sparse[non_zero_mask] - w_min) / (w_max - w_min)
                w_quantized[non_zero_mask] = np.round(w_normalized * (n_levels - 1)) / (n_levels - 1) * (w_max - w_min) + w_min
        
        # Evaluate compressed model on in-sample data
        y_pred_compressed = predict_proba(X, w_quantized, b_dense)
        brier_compressed = brier_score(y, y_pred_compressed)
        
        # Retention = dense Brier / compressed Brier
        retention = brier_dense / brier_compressed if brier_compressed > 0 else float('inf')
        
        config_name = f"sparsity{sparsity_pct}_bits{bit_depth}"
        results[config_name] = {
            'sparsity': sparsity_pct,
            'bits': bit_depth,
            'brier_compressed': brier_compressed,
            'retention': retention
        }
        
        print(f"{config_name}: Brier={brier_compressed:.6f}, Retention={retention:.6f}")

# Find best configuration
best_config_name = max(results.keys(), key=lambda k: results[k]['retention'])
print(f"\nBest configuration: {best_config_name}")
print(f"Retention: {results[best_config_name]['retention']:.6f}")

# Prepare final answers
answers = {
    "best_lambda": float(best_lambda),
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config_name
}

print("\n=== Final Answers ===")
print(json.dumps(answers, indent=2))

# Write to file
with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("\nAnswers written to answers.json")
