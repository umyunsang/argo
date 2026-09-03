import json
import numpy as np
from scipy import stats

# Load data
with open('data.json') as f:
    data = json.load(f)

X = np.array(data['X'], dtype=np.float64)
y = np.array(data['y'], dtype=np.float64)

n_samples, n_features = X.shape
print(f"Data shape: {n_samples} samples, {n_features} features")

# Create 5 contiguous folds (consecutive slices, not interleaved)
def create_folds(X, y, n_folds=5):
    """Create contiguous folds - each fold is a consecutive slice"""
    fold_size = n_samples // n_folds
    folds = []
    for k in range(n_folds):
        start_idx = k * fold_size
        end_idx = start_idx + fold_size
        test_indices = list(range(start_idx, end_idx))
        train_indices = [i for i in range(n_samples) if i not in test_indices]
        folds.append((train_indices, test_indices))
    return folds

# Logistic regression implementation
def sigmoid(z):
    """Sigmoid function with clipping"""
    z = np.clip(z, -30, 30)
    return 1 / (1 + np.exp(-z))

def brier_score(y_true, y_pred_proba):
    """Compute Brier score"""
    return np.mean((y_pred_proba - y_true) ** 2)

def fit_logistic(X_train, y_train, X_test, y_test, lambda_reg=0.0, n_iter=200, lr=0.1):
    """Fit logistic regression with full-batch gradient descent"""
    n_train = X_train.shape[0]
    n_feats = X_train.shape[1]
    
    # Initialize weights and bias
    w = np.zeros(n_feats)
    b = 0.0
    
    # Training loop
    for iteration in range(n_iter):
        # Forward pass
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)
        y_pred = sigmoid(logits)
        
        # Compute gradients
        error = y_pred - y_train
        grad_w = X_train.T @ error / n_train
        grad_b = np.mean(error)
        
        # Update with L2 regularization
        w = w - lr * (grad_w + lambda_reg * w)
        b = b - lr * grad_b
    
    # Predict on test
    logits_test = X_test @ w + b
    logits_test = np.clip(logits_test, -30, 30)
    y_pred_test = sigmoid(logits_test)
    
    # Also predict on train
    logits_train = X_train @ w + b
    logits_train = np.clip(logits_train, -30, 30)
    y_pred_train = sigmoid(logits_train)
    
    return y_pred_test, y_pred_train, w, b

# ===== Task 1: Find best lambda =====
lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
folds = create_folds(X, y, n_folds=5)

cv_scores = {lam: [] for lam in lambdas}

for lam in lambdas:
    for train_idx, test_idx in folds:
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        y_pred_test, _, _, _ = fit_logistic(X_train, y_train, X_test, y_test, 
                                             lambda_reg=lam, n_iter=200, lr=0.1)
        
        brier = brier_score(y_test, y_pred_test)
        cv_scores[lam].append(brier)

# Find best lambda
mean_scores = {lam: np.mean(cv_scores[lam]) for lam in lambdas}
best_lambda = min(lambdas, key=lambda x: mean_scores[x])
baseline_score = mean_scores[0.0]
best_score = mean_scores[best_lambda]
improvement = baseline_score - best_score

print(f"\n=== Task 1: Lambda Selection ===")
print(f"Mean CV Brier scores by lambda:")
for lam in lambdas:
    print(f"  lambda={lam}: {mean_scores[lam]:.6f}")
print(f"Best lambda: {best_lambda}")
print(f"Baseline (lambda=0): {baseline_score:.6f}")
print(f"Best score: {best_score:.6f}")
print(f"Improvement: {improvement:.6f}")

# ===== Task 2: Test interaction features =====
# Add interaction columns
X_with_interaction = np.concatenate([
    X,
    X[:, 0:1] * X[:, 1:2],  # x0*x1
    X[:, 1:2] * X[:, 2:3],  # x1*x2
    X[:, 2:3] * X[:, 3:4],  # x2*x3
    X[:, 0:1] * X[:, 3:4],  # x0*x3
], axis=1)

print(f"\n=== Task 2: Interaction Features ===")
print(f"Original features: {n_features}")
print(f"With interactions: {X_with_interaction.shape[1]}")

# Fit both on all folds and compute paired differences
raw_brier_scores = []
interaction_brier_scores = []

for train_idx, test_idx in folds:
    # Raw features
    X_train_raw, X_test_raw = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    y_pred_raw, _, _, _ = fit_logistic(X_train_raw, y_train, X_test_raw, y_test,
                                        lambda_reg=0.1, n_iter=200, lr=0.1)
    brier_raw = brier_score(y_test, y_pred_raw)
    raw_brier_scores.append(brier_raw)
    
    # With interactions
    X_train_int, X_test_int = X_with_interaction[train_idx], X_with_interaction[test_idx]
    y_pred_int, _, _, _ = fit_logistic(X_train_int, y_train, X_test_int, y_test,
                                        lambda_reg=0.1, n_iter=200, lr=0.1)
    brier_int = brier_score(y_test, y_pred_int)
    interaction_brier_scores.append(brier_int)

# Paired t-test: raw - interaction (higher raw score = worse)
# So we want the t-stat to be positive if interaction is better
differences = np.array(raw_brier_scores) - np.array(interaction_brier_scores)
paired_t_stat = stats.ttest_rel(raw_brier_scores, interaction_brier_scores).statistic
interaction_helps = paired_t_stat > 2.0

print(f"Raw Brier scores: {raw_brier_scores}")
print(f"Interaction Brier scores: {interaction_brier_scores}")
print(f"Differences (raw - interaction): {differences}")
print(f"Paired t-statistic: {paired_t_stat:.6f}")
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# ===== Task 3: Model compression =====
# Fit dense model on all data with lambda=0.1
_, _, w_dense, b_dense = fit_logistic(X, y, X, y, lambda_reg=0.1, n_iter=200, lr=0.1)

# Predict on full data to get dense Brier
logits_dense = X @ w_dense + b_dense
logits_dense = np.clip(logits_dense, -30, 30)
y_pred_dense = sigmoid(logits_dense)
brier_dense = brier_score(y, y_pred_dense)

print(f"\n=== Task 3: Model Compression ===")
print(f"Dense model Brier: {brier_dense:.6f}")

sparsity_levels = [20, 40, 60]
bit_depths = [8, 4]

best_retention = -1
best_config = None

for sparsity_pct in sparsity_levels:
    for bits in bit_depths:
        # Apply sparsity
        w_sparse = w_dense.copy()
        k = round(sparsity_pct / 100.0 * len(w_sparse))
        
        # Zero smallest magnitude weights
        indices_to_zero = np.argsort(np.abs(w_sparse))[:k]
        w_sparse[indices_to_zero] = 0
        
        # Apply quantization to remaining weights
        non_zero_mask = w_sparse != 0
        if np.any(non_zero_mask):
            w_min = np.min(w_sparse[non_zero_mask])
            w_max = np.max(w_sparse[non_zero_mask])
            
            if w_min == w_max:
                # All non-zero values are the same
                w_quantized = w_sparse
            else:
                # Map to 2^bits levels
                n_levels = 2 ** bits
                w_normalized = (w_sparse[non_zero_mask] - w_min) / (w_max - w_min)
                w_quantized_vals = np.round(w_normalized * (n_levels - 1)) / (n_levels - 1)
                w_quantized_vals = w_quantized_vals * (w_max - w_min) + w_min
                
                w_quantized = w_sparse.copy()
                w_quantized[non_zero_mask] = w_quantized_vals
        else:
            w_quantized = w_sparse
        
        # Predict with compressed model
        logits_compressed = X @ w_quantized + b_dense
        logits_compressed = np.clip(logits_compressed, -30, 30)
        y_pred_compressed = sigmoid(logits_compressed)
        brier_compressed = brier_score(y, y_pred_compressed)
        
        # Retention = dense / compressed
        retention = brier_dense / brier_compressed
        
        print(f"sparsity={sparsity_pct}%, bits={bits}: Brier={brier_compressed:.6f}, retention={retention:.4f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = (sparsity_pct, bits)

print(f"\nBest config: sparsity={best_config[0]}%, bits={best_config[1]}")
print(f"Best retention: {best_retention:.4f}")

# Format config as string
config_str = f"sparsity{best_config[0]}_bits{best_config[1]}"

# ===== Write answers =====
answers = {
    "best_lambda": float(best_lambda),
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(paired_t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": config_str
}

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print(f"\n=== Final Answers ===")
print(json.dumps(answers, indent=2))
