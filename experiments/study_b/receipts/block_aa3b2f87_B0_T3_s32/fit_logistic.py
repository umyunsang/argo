import json
import numpy as np
from scipy.stats import ttest_rel
import warnings
warnings.filterwarnings('ignore')

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'], dtype=np.float64)
y = np.array(data['y'], dtype=np.float64)

n_samples, n_features = X.shape
print(f"Data shape: {n_samples} samples, {n_features} features")

# ============================================================================
# PART 1: Find best lambda
# ============================================================================

def sigmoid(z):
    """Numerically stable sigmoid"""
    z = np.clip(z, -30, 30)
    return 1 / (1 + np.exp(-z))

def brier_score(y_true, y_pred):
    """Brier score: mean squared error between predictions and labels"""
    return np.mean((y_pred - y_true) ** 2)

def fit_logistic(X_train, y_train, lambda_reg, n_iterations=200, lr=0.1):
    """
    Fit logistic regression with full-batch gradient descent
    w -= lr * (grad_w / n + lambda * w)
    b -= lr * (grad_b / n)
    """
    n_train = X_train.shape[0]
    n_feat = X_train.shape[1]
    
    # Initialize weights and bias
    w = np.zeros(n_feat)
    b = 0.0
    
    for iteration in range(n_iterations):
        # Forward pass
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)  # Clip logits
        pred = sigmoid(logits)
        
        # Backward pass
        diff = pred - y_train
        grad_w = X_train.T @ diff  # gradient for w
        grad_b = np.sum(diff)       # gradient for b
        
        # Update
        w -= lr * (grad_w / n_train + lambda_reg * w)
        b -= lr * (grad_b / n_train)
    
    return w, b

def predict_logistic(X_test, w, b):
    """Make predictions"""
    logits = X_test @ w + b
    logits = np.clip(logits, -30, 30)
    return sigmoid(logits)

# 5-fold CV with contiguous blocks (no shuffle)
n_folds = 5
fold_size = n_samples // n_folds
fold_indices = []
for k in range(n_folds):
    start_idx = k * fold_size
    end_idx = (k + 1) * fold_size if k < n_folds - 1 else n_samples
    fold_indices.append((start_idx, end_idx))

print(f"Fold indices: {fold_indices}")

lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
results_part1 = {}

for lam in lambdas:
    brier_scores = []
    
    for k in range(n_folds):
        # Get test fold
        test_start, test_end = fold_indices[k]
        test_idx = list(range(test_start, test_end))
        
        # Get train folds (all except fold k)
        train_idx = []
        for j in range(n_folds):
            if j != k:
                start, end = fold_indices[j]
                train_idx.extend(range(start, end))
        
        X_train, y_train = X[train_idx], y[train_idx]
        X_test, y_test = X[test_idx], y[test_idx]
        
        # Fit model
        w, b = fit_logistic(X_train, y_train, lambda_reg=lam, n_iterations=200, lr=0.1)
        
        # Evaluate on test set
        y_pred = predict_logistic(X_test, w, b)
        brier = brier_score(y_test, y_pred)
        brier_scores.append(brier)
    
    avg_brier = np.mean(brier_scores)
    results_part1[lam] = {
        'scores': brier_scores,
        'avg_brier': avg_brier
    }
    print(f"Lambda {lam}: avg Brier = {avg_brier:.6f}, fold scores: {[f'{s:.6f}' for s in brier_scores]}")

# Find best lambda
best_lambda = min(results_part1.keys(), key=lambda l: results_part1[l]['avg_brier'])
baseline_brier = results_part1[0.0]['avg_brier']
best_brier = results_part1[best_lambda]['avg_brier']
improvement = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda}")
print(f"Baseline (lambda=0.0) Brier: {baseline_brier:.6f}")
print(f"Best Brier: {best_brier:.6f}")
print(f"Improvement: {improvement:.6f}")

# ============================================================================
# PART 2: Interaction terms and paired t-test
# ============================================================================

# Add interaction terms: x0*x1, x1*x2, x2*x3, x0*x3
X_interaction = np.hstack([
    X,
    (X[:, 0] * X[:, 1]).reshape(-1, 1),  # x0*x1
    (X[:, 1] * X[:, 2]).reshape(-1, 1),  # x1*x2
    (X[:, 2] * X[:, 3]).reshape(-1, 1),  # x2*x3
    (X[:, 0] * X[:, 3]).reshape(-1, 1),  # x0*x3
])

print(f"\nInteraction feature shape: {X_interaction.shape}")

# Fit both representations with lambda=0.1
lam = 0.1  # Use this variable for the loop
raw_brier_scores = []
interaction_brier_scores = []

for k in range(n_folds):
    test_start, test_end = fold_indices[k]
    test_idx = list(range(test_start, test_end))
    
    train_idx = []
    for j in range(n_folds):
        if j != k:
            start, end = fold_indices[j]
            train_idx.extend(range(start, end))
    
    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]
    X_train_int, X_test_int = X_interaction[train_idx], X_interaction[test_idx]
    
    # Fit raw model
    w_raw, b_raw = fit_logistic(X_train, y_train, lambda_reg=lam, n_iterations=200, lr=0.1)
    y_pred_raw = predict_logistic(X_test, w_raw, b_raw)
    brier_raw = brier_score(y_test, y_pred_raw)
    raw_brier_scores.append(brier_raw)
    
    # Fit interaction model
    w_int, b_int = fit_logistic(X_train_int, y_train, lambda_reg=lam, n_iterations=200, lr=0.1)
    y_pred_int = predict_logistic(X_test_int, w_int, b_int)
    brier_int = brier_score(y_test, y_pred_int)
    interaction_brier_scores.append(brier_int)

raw_brier_scores = np.array(raw_brier_scores)
interaction_brier_scores = np.array(interaction_brier_scores)

print(f"Raw model Brier (fold-wise): {raw_brier_scores}")
print(f"Interaction model Brier (fold-wise): {interaction_brier_scores}")

# Paired t-test: raw - interaction per fold
differences = raw_brier_scores - interaction_brier_scores
print(f"Differences (raw - interaction): {differences}")

t_stat, p_val = ttest_rel(raw_brier_scores, interaction_brier_scores)
print(f"Paired t-test t-statistic: {t_stat:.6f}")
print(f"p-value: {p_val:.6f}")

interaction_helps = t_stat > 2.0
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# ============================================================================
# PART 3: Model compression (sparsity and quantization)
# ============================================================================

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic(X, y, lambda_reg=0.1, n_iterations=200, lr=0.1)
y_pred_dense = predict_logistic(X, w_dense, b_dense)
dense_brier = brier_score(y, y_pred_dense)
print(f"\nDense model in-sample Brier: {dense_brier:.6f}")

sparsity_levels = [20, 40, 60]
bits_levels = [8, 4]
best_retention = -1
best_config = None

compression_results = {}

for sparsity_pct in sparsity_levels:
    for bits in bits_levels:
        # Apply sparsity
        w_sparse = w_dense.copy()
        k = round((sparsity_pct / 100.0) * len(w_dense))
        
        # Zero out k smallest magnitude weights
        if k > 0:
            thresholds = np.partition(np.abs(w_sparse), k-1)[k-1]
            mask = np.abs(w_sparse) < thresholds
            # Handle ties carefully - just zero out by smallest magnitude
            abs_sorted_indices = np.argsort(np.abs(w_sparse))
            w_sparse[abs_sorted_indices[:k]] = 0
        
        # Apply quantization to non-zero weights
        w_quantized = w_sparse.copy()
        nonzero_mask = w_sparse != 0
        if np.any(nonzero_mask):
            min_val = np.min(w_sparse[nonzero_mask])
            max_val = np.max(w_sparse[nonzero_mask])
            
            if max_val > min_val:
                # Map to [0, 2^bits - 1]
                levels = 2 ** bits
                # Quantize
                w_quantized[nonzero_mask] = np.round(
                    (w_sparse[nonzero_mask] - min_val) / (max_val - min_val) * (levels - 1)
                ) * (max_val - min_val) / (levels - 1) + min_val
        
        # Evaluate compressed model
        y_pred_compressed = predict_logistic(X, w_quantized, b_dense)
        compressed_brier = brier_score(y, y_pred_compressed)
        
        retention = dense_brier / compressed_brier if compressed_brier > 0 else 0
        
        config_name = f"sparsity{sparsity_pct}_bits{bits}"
        compression_results[config_name] = {
            'sparsity': sparsity_pct,
            'bits': bits,
            'dense_brier': dense_brier,
            'compressed_brier': compressed_brier,
            'retention': retention
        }
        
        print(f"{config_name}: dense_brier={dense_brier:.6f}, compressed_brier={compressed_brier:.6f}, retention={retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = config_name

print(f"\nBest compression config: {best_config} (retention={best_retention:.6f})")

# ============================================================================
# Save results
# ============================================================================

answers = {
    "best_lambda": best_lambda,
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

print(f"\n\nFinal Answers:")
print(json.dumps(answers, indent=2))

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("Answers saved to answers.json")
