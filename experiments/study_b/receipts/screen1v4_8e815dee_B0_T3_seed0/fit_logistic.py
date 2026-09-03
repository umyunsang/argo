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
print(f"Data shape: X={X.shape}, y={y.shape}")

# ============================================================================
# QUESTION 1: Best Lambda and Improvement Over Baseline
# ============================================================================

def sigmoid(z):
    """Sigmoid with clipping to [-30, 30] for stability"""
    z = np.clip(z, -30, 30)
    return 1.0 / (1.0 + np.exp(-z))

def brier_score(y_true, y_pred_proba):
    """Brier score: mean squared error between predicted probabilities and true labels"""
    return np.mean((y_pred_proba - y_true) ** 2)

def fit_logistic_gd(X_train, y_train, lambda_reg=0.0, lr=0.1, iterations=200):
    """
    Fit logistic regression using full-batch gradient descent.
    - weights and bias start at 0
    - Update: w -= lr * (grad_w / n + lambda * w); b -= lr * (grad_b / n)
    """
    n = X_train.shape[0]
    d = X_train.shape[1]
    
    w = np.zeros(d)
    b = 0.0
    
    for _ in range(iterations):
        # Forward pass
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)
        y_pred = sigmoid(logits)
        
        # Gradient computation
        error = y_pred - y_train
        grad_w = X_train.T @ error / n
        grad_b = np.sum(error) / n
        
        # Update
        w -= lr * (grad_w + lambda_reg * w)
        b -= lr * grad_b
    
    return w, b

def evaluate_model(X_test, y_test, w, b):
    """Evaluate model on test set using Brier score"""
    logits = X_test @ w + b
    logits = np.clip(logits, -30, 30)
    y_pred = sigmoid(logits)
    return brier_score(y_test, y_pred)

# 5-fold cross-validation with contiguous blocks
def cross_validate(X, y, lambda_val, n_folds=5):
    """5-fold CV with contiguous blocks"""
    n = len(y)
    fold_size = n // n_folds
    brier_scores = []
    
    for fold_idx in range(n_folds):
        # Create train/test split: fold_idx-th contiguous block is test
        test_start = fold_idx * fold_size
        test_end = test_start + fold_size if fold_idx < n_folds - 1 else n
        
        test_indices = np.arange(test_start, test_end)
        train_indices = np.concatenate([
            np.arange(0, test_start),
            np.arange(test_end, n)
        ])
        
        X_train, y_train = X[train_indices], y[train_indices]
        X_test, y_test = X[test_indices], y[test_indices]
        
        # Fit model
        w, b = fit_logistic_gd(X_train, y_train, lambda_reg=lambda_val, lr=0.1, iterations=200)
        
        # Evaluate
        brier = evaluate_model(X_test, y_test, w, b)
        brier_scores.append(brier)
    
    return np.mean(brier_scores)

# Try different lambda values
lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
cv_scores = {}

print("\nQuestion 1: Lambda selection")
for lam in lambdas:
    score = cross_validate(X, y, lam)
    cv_scores[lam] = score
    print(f"  Lambda {lam}: Brier score = {score:.6f}")

# Find best lambda
best_lambda = min(cv_scores, key=cv_scores.get)
baseline_brier = cv_scores[0.0]  # Lambda = 0 is baseline
best_brier = cv_scores[best_lambda]
improvement = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda}")
print(f"Baseline Brier (lambda=0): {baseline_brier:.6f}")
print(f"Best Brier: {best_brier:.6f}")
print(f"Improvement over baseline: {improvement:.6f}")

# ============================================================================
# QUESTION 2: Interaction Features and Paired T-Test
# ============================================================================

print("\n\nQuestion 2: Interaction features")

# Add interaction features: x0*x1, x1*x2, x2*x3, x0*x3
X_with_interactions = np.column_stack([
    X,
    X[:, 0] * X[:, 1],  # x0*x1
    X[:, 1] * X[:, 2],  # x1*x2
    X[:, 2] * X[:, 3],  # x2*x3
    X[:, 0] * X[:, 3],  # x0*x3
])

print(f"Original X shape: {X.shape}")
print(f"X with interactions shape: {X_with_interactions.shape}")

# 5-fold CV for both models with lambda=0.1
lambda_val = 0.1
n_folds = 5
n = len(y)
fold_size = n // n_folds

raw_briers = []
interaction_briers = []

for fold_idx in range(n_folds):
    test_start = fold_idx * fold_size
    test_end = test_start + fold_size if fold_idx < n_folds - 1 else n
    
    test_indices = np.arange(test_start, test_end)
    train_indices = np.concatenate([
        np.arange(0, test_start),
        np.arange(test_end, n)
    ])
    
    X_train, y_train = X[train_indices], y[train_indices]
    X_test, y_test = X[test_indices], y[test_indices]
    
    # Raw model (no interactions)
    w_raw, b_raw = fit_logistic_gd(X_train, y_train, lambda_reg=lambda_val, lr=0.1, iterations=200)
    raw_brier = evaluate_model(X_test, y_test, w_raw, b_raw)
    raw_briers.append(raw_brier)
    
    # Interaction model
    X_train_int = np.column_stack([
        X_train,
        X_train[:, 0] * X_train[:, 1],
        X_train[:, 1] * X_train[:, 2],
        X_train[:, 2] * X_train[:, 3],
        X_train[:, 0] * X_train[:, 3],
    ])
    X_test_int = np.column_stack([
        X_test,
        X_test[:, 0] * X_test[:, 1],
        X_test[:, 1] * X_test[:, 2],
        X_test[:, 2] * X_test[:, 3],
        X_test[:, 0] * X_test[:, 3],
    ])
    
    w_int, b_int = fit_logistic_gd(X_train_int, y_train, lambda_reg=lambda_val, lr=0.1, iterations=200)
    interaction_brier = evaluate_model(X_test_int, y_test, w_int, b_int)
    interaction_briers.append(interaction_brier)

raw_briers = np.array(raw_briers)
interaction_briers = np.array(interaction_briers)

# Paired t-test: raw - interaction per fold
differences = raw_briers - interaction_briers
t_stat, p_value = stats.ttest_rel(raw_briers, interaction_briers)

print(f"Raw model Brier scores per fold: {raw_briers}")
print(f"Interaction model Brier scores per fold: {interaction_briers}")
print(f"Differences (raw - interaction): {differences}")
print(f"Paired t-statistic: {t_stat:.6f}")
print(f"P-value: {p_value:.6f}")

interaction_helps = t_stat > 2.0
print(f"Interaction helps (t > 2.0)? {interaction_helps}")

# ============================================================================
# QUESTION 3: Best Compression Configuration
# ============================================================================

print("\n\nQuestion 3: Compression configuration")

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic_gd(X, y, lambda_reg=0.1, lr=0.1, iterations=200)
dense_brier = evaluate_model(X, y, w_dense, b_dense)
print(f"Dense model Brier score (in-sample): {dense_brier:.6f}")

# Test different compression configs
sparsities = [20, 40, 60]  # percent
bits_list = [4, 8]

best_config = None
best_retention = 0

for sparsity in sparsities:
    for bits in bits_list:
        # Create compressed weights
        w_compressed = w_dense.copy()
        
        # Sparsity: zero out smallest magnitude weights
        k = round(sparsity / 100.0 * len(w_dense))
        threshold_idx = np.argsort(np.abs(w_compressed))[k]
        threshold = np.abs(w_compressed[threshold_idx])
        w_compressed[np.abs(w_compressed) < threshold] = 0
        
        # Remove the exact k smallest
        abs_w = np.abs(w_compressed)
        sorted_indices = np.argsort(abs_w)
        w_compressed[sorted_indices[:k]] = 0
        
        # Quantization: map remaining weights uniformly onto 2^bits levels
        non_zero_mask = w_compressed != 0
        if np.any(non_zero_mask):
            w_min = np.min(w_compressed[non_zero_mask])
            w_max = np.max(w_compressed[non_zero_mask])
            
            if w_min != w_max:
                # Map to [0, 2^bits - 1]
                q_levels = 2 ** bits
                w_quantized = w_compressed.copy()
                w_quantized[non_zero_mask] = np.round(
                    (w_compressed[non_zero_mask] - w_min) / (w_max - w_min) * (q_levels - 1)
                )
                # Map back to original range
                w_quantized[non_zero_mask] = (
                    w_quantized[non_zero_mask] / (q_levels - 1) * (w_max - w_min) + w_min
                )
            else:
                w_quantized = w_compressed.copy()
        else:
            w_quantized = w_compressed.copy()
        
        # Evaluate compressed model
        compressed_brier = evaluate_model(X, y, w_quantized, b_dense)
        
        # Retention = dense_brier / compressed_brier
        retention = dense_brier / compressed_brier if compressed_brier > 0 else 0
        
        config_name = f"sparsity{sparsity}_bits{bits}"
        print(f"{config_name}: Brier={compressed_brier:.6f}, Retention={retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = config_name

print(f"\nBest compression config: {best_config} (Retention: {best_retention:.6f})")

# ============================================================================
# Write answers to JSON
# ============================================================================

answers = {
    "best_lambda": float(best_lambda),
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": str(best_config)
}

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("\n" + "="*60)
print("FINAL ANSWERS:")
print("="*60)
print(json.dumps(answers, indent=2))
