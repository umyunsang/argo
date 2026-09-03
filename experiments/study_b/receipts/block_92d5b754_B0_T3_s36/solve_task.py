import json
import numpy as np
from scipy import stats

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'])
y = np.array(data['y'])

print(f"Data shape: X {X.shape}, y {y.shape}")

# ============================================================================
# Helper functions for logistic regression with specific training conventions
# ============================================================================

def sigmoid(logits):
    """Sigmoid function with numerical stability"""
    return 1 / (1 + np.exp(-np.clip(logits, -30, 30)))

def logistic_loss_and_grad(X, y, w, b, lambda_reg):
    """Calculate logistic loss and gradients"""
    n = X.shape[0]
    logits = np.clip(X @ w + b, -30, 30)
    probs = sigmoid(logits)
    
    # Binary cross-entropy loss
    eps = 1e-15
    loss = -np.mean(y * np.log(probs + eps) + (1 - y) * np.log(1 - probs + eps))
    loss += (lambda_reg / 2) * np.mean(w ** 2)  # L2 regularization
    
    # Gradients
    error = probs - y
    grad_w = X.T @ error / n + lambda_reg * w
    grad_b = np.mean(error)
    
    return loss, grad_w, grad_b

def fit_logistic(X_train, y_train, lambda_reg, iterations=200, lr=0.1):
    """
    Fit logistic regression with full-batch gradient descent
    - 200 iterations, learning rate 0.1
    - Weights and bias start at 0
    - Logits clipped to [-30, 30]
    """
    n_features = X_train.shape[0]
    d = X_train.shape[1]
    
    w = np.zeros(d)
    b = 0.0
    
    for _ in range(iterations):
        loss, grad_w, grad_b = logistic_loss_and_grad(X_train, y_train, w, b, lambda_reg)
        
        # Update: w -= 0.1 * (grad_w / n + lambda * w); b -= 0.1 * (grad_b / n)
        # Note: grad_w already includes lambda * w, and grad_b is already (grad_b / n)
        w -= lr * grad_w
        b -= lr * grad_b
    
    return w, b

def predict_proba(X, w, b):
    """Predict probability of class 1"""
    logits = np.clip(X @ w + b, -30, 30)
    return sigmoid(logits)

def brier_score(y_true, y_pred_proba):
    """Calculate Brier score"""
    return np.mean((y_true - y_pred_proba) ** 2)

# ============================================================================
# Task 1: Find best lambda and improvement over baseline
# ============================================================================

def create_folds(X, y, n_folds=5):
    """Create 5 contiguous blocks (no shuffle)"""
    n = len(y)
    fold_size = n // n_folds
    folds = []
    
    for k in range(n_folds):
        test_indices = list(range(k, n, n_folds))
        train_indices = [i for i in range(n) if i not in test_indices]
        folds.append((train_indices, test_indices))
    
    return folds

lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
folds = create_folds(X, y, n_folds=5)

print("\n" + "="*60)
print("Task 1: Finding best lambda")
print("="*60)

best_lambda = None
best_brier = float('inf')
brier_scores_by_lambda = {}

for lam in lambdas:
    brier_scores = []
    
    for train_idx, test_idx in folds:
        X_train = X[train_idx]
        y_train = y[train_idx]
        X_test = X[test_idx]
        y_test = y[test_idx]
        
        w, b = fit_logistic(X_train, y_train, lam)
        y_pred_proba = predict_proba(X_test, w, b)
        brier = brier_score(y_test, y_pred_proba)
        brier_scores.append(brier)
    
    mean_brier = np.mean(brier_scores)
    brier_scores_by_lambda[lam] = mean_brier
    print(f"Lambda {lam:6.2f}: mean Brier = {mean_brier:.6f}, fold scores: {[f'{b:.6f}' for b in brier_scores]}")
    
    if mean_brier < best_brier:
        best_brier = mean_brier
        best_lambda = lam

# Calculate improvement over baseline (lambda=0)
baseline_brier = brier_scores_by_lambda[0.0]
improvement_over_baseline = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda}")
print(f"Baseline Brier (lambda=0): {baseline_brier:.6f}")
print(f"Best Brier: {best_brier:.6f}")
print(f"Improvement: {improvement_over_baseline:.6f}")

# ============================================================================
# Task 2: Paired t-test with interaction features
# ============================================================================

print("\n" + "="*60)
print("Task 2: Interaction features and paired t-test")
print("="*60)

# Add interaction features
X_with_interactions = np.hstack([
    X,
    (X[:, 0] * X[:, 1]).reshape(-1, 1),  # x0*x1
    (X[:, 1] * X[:, 2]).reshape(-1, 1),  # x1*x2
    (X[:, 2] * X[:, 3]).reshape(-1, 1),  # x2*x3
    (X[:, 0] * X[:, 3]).reshape(-1, 1),  # x0*x3
])

print(f"Original features: {X.shape[1]}")
print(f"Features with interactions: {X_with_interactions.shape[1]}")

# Fit both models on each fold and compute Brier scores
brier_raw_scores = []
brier_interaction_scores = []

for train_idx, test_idx in folds:
    # Raw model
    X_train_raw = X[train_idx]
    y_train = y[train_idx]
    X_test_raw = X[test_idx]
    y_test = y[test_idx]
    
    w_raw, b_raw = fit_logistic(X_train_raw, y_train, 0.1)
    y_pred_raw = predict_proba(X_test_raw, w_raw, b_raw)
    brier_raw = brier_score(y_test, y_pred_raw)
    brier_raw_scores.append(brier_raw)
    
    # Interaction model
    X_train_inter = X_with_interactions[train_idx]
    X_test_inter = X_with_interactions[test_idx]
    
    w_inter, b_inter = fit_logistic(X_train_inter, y_train, 0.1)
    y_pred_inter = predict_proba(X_test_inter, w_inter, b_inter)
    brier_inter = brier_score(y_test, y_pred_inter)
    brier_interaction_scores.append(brier_inter)

print(f"\nRaw model Brier scores: {[f'{b:.6f}' for b in brier_raw_scores]}")
print(f"Interaction model Brier scores: {[f'{b:.6f}' for b in brier_interaction_scores]}")

# Paired t-test: raw - interaction (positive means interaction helps)
differences = np.array(brier_raw_scores) - np.array(brier_interaction_scores)
print(f"Differences (raw - interaction): {[f'{d:.6f}' for d in differences]}")

t_stat, p_value = stats.ttest_rel(brier_raw_scores, brier_interaction_scores)
print(f"\nPaired t-statistic: {t_stat:.6f}")
print(f"P-value: {p_value:.6f}")

interaction_helps = t_stat > 2.0
print(f"t > 2.0: {interaction_helps}")

# ============================================================================
# Task 3: Compression configurations
# ============================================================================

print("\n" + "="*60)
print("Task 3: Compression configurations")
print("="*60)

# Fit dense model on all rows with lambda=0.1
w_dense, b_dense = fit_logistic(X, y, 0.1)
y_pred_dense = predict_proba(X, w_dense, b_dense)
dense_brier = brier_score(y, y_pred_dense)

print(f"Dense model Brier (in-sample): {dense_brier:.6f}")

# Test configurations: sparsity in (20, 40, 60) percent, bits in (8, 4)
sparsities = [20, 40, 60]
bits_list = [8, 4]

best_config = None
best_retention = 0

configs_results = []

for sparsity_pct in sparsities:
    for bits in bits_list:
        # Create sparse weights by zeroing smallest magnitude weights
        w_sparse = w_dense.copy()
        k = round((sparsity_pct / 100.0) * len(w_sparse))
        
        # Zero the k smallest magnitude weights
        abs_w = np.abs(w_sparse)
        threshold_idx = np.argsort(abs_w)[k]
        threshold = abs_w[threshold_idx]
        w_sparse[abs_w < threshold] = 0
        # If needed, zero more to get exactly k
        zero_count = np.sum(w_sparse == 0)
        if zero_count < k:
            idx_to_zero = np.argsort(abs_w)[:k]
            w_sparse[idx_to_zero] = 0
        
        # Quantize non-zero weights
        nonzero_mask = w_sparse != 0
        if np.any(nonzero_mask):
            w_min = w_sparse[nonzero_mask].min()
            w_max = w_sparse[nonzero_mask].max()
            
            if w_min == w_max:
                # All nonzero weights are the same
                w_quant = w_sparse.copy()
            else:
                # Map uniformly to 2^bits levels
                levels = np.linspace(w_min, w_max, 2**bits)
                w_temp = w_sparse.copy()
                for i in np.where(nonzero_mask)[0]:
                    # Find closest level
                    w_temp[i] = levels[np.argmin(np.abs(levels - w_sparse[i]))]
                w_quant = w_temp
        else:
            w_quant = w_sparse.copy()
        
        # Evaluate compressed model (bias untouched)
        y_pred_compressed = predict_proba(X, w_quant, b_dense)
        compressed_brier = brier_score(y, y_pred_compressed)
        
        # Retention = dense Brier / compressed Brier
        retention = dense_brier / compressed_brier if compressed_brier > 0 else float('inf')
        
        config_name = f"sparsity{sparsity_pct}_bits{bits}"
        configs_results.append((config_name, retention, dense_brier, compressed_brier))
        
        print(f"{config_name}: retention={retention:.6f}, dense={dense_brier:.6f}, compressed={compressed_brier:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = config_name

print(f"\nBest configuration: {best_config} (retention={best_retention:.6f})")

# ============================================================================
# Write answers
# ============================================================================

answers = {
    "best_lambda": best_lambda,
    "improvement_over_baseline": float(improvement_over_baseline),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("\n" + "="*60)
print("FINAL ANSWERS")
print("="*60)
print(json.dumps(answers, indent=2))
