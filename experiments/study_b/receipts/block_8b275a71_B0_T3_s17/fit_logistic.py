import json
import numpy as np
from scipy import stats

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'])
y = np.array(data['y'])

n_samples, n_features = X.shape
print(f"Data shape: X={X.shape}, y={y.shape}")

# Helper functions
def sigmoid(z):
    """Sigmoid function with clipping to avoid numerical issues"""
    z = np.clip(z, -30, 30)
    return 1 / (1 + np.exp(-z))

def brier_score(y_true, y_pred):
    """Calculate Brier score"""
    return np.mean((y_pred - y_true) ** 2)

def create_folds(n, n_folds=5):
    """Create contiguous folds without shuffle"""
    fold_size = n // n_folds
    folds = []
    for i in range(n_folds):
        test_idx = list(range(i, n, n_folds))
        train_idx = [j for j in range(n) if j not in test_idx]
        folds.append((train_idx, test_idx))
    return folds

def fit_logistic(X_train, y_train, X_test, y_test, lam=0.0, n_iter=200, lr=0.1):
    """
    Fit logistic regression with full-batch gradient descent.
    Returns weights, bias, and test Brier score.
    """
    n_train = len(X_train)
    n_features = X_train.shape[1]
    
    # Initialize weights and bias at 0
    w = np.zeros(n_features)
    b = 0.0
    
    # Full-batch gradient descent
    for iteration in range(n_iter):
        # Forward pass
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)
        y_pred = sigmoid(logits)
        
        # Compute gradients
        error = y_pred - y_train
        grad_w = X_train.T @ error / n_train
        grad_b = np.sum(error) / n_train
        
        # Update with L2 regularization
        w -= lr * (grad_w + lam * w)
        b -= lr * grad_b
    
    # Test predictions
    logits_test = X_test @ w + b
    logits_test = np.clip(logits_test, -30, 30)
    y_pred_test = sigmoid(logits_test)
    
    test_brier = brier_score(y_test, y_pred_test)
    
    return w, b, test_brier, y_pred_test

# Create folds
folds = create_folds(n_samples, n_folds=5)
print(f"Created {len(folds)} folds")

# ===== QUESTION 1: Best lambda and improvement =====
print("\n" + "="*60)
print("QUESTION 1: Best Lambda and Improvement")
print("="*60)

lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
brier_scores = {lam: [] for lam in lambdas}

for train_idx, test_idx in folds:
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    for lam in lambdas:
        w, b, test_brier, _ = fit_logistic(X_train, y_train, X_test, y_test, lam=lam)
        brier_scores[lam].append(test_brier)

# Calculate average Brier scores
avg_brier = {lam: np.mean(brier_scores[lam]) for lam in lambdas}
print(f"\nAverage Brier scores per lambda:")
for lam, score in avg_brier.items():
    print(f"  lambda={lam}: {score:.6f}")

# Find best lambda
best_lambda = min(avg_brier, key=avg_brier.get)
best_brier = avg_brier[best_lambda]
baseline_brier = avg_brier[0.0]
improvement = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda}")
print(f"Best Brier score: {best_brier:.6f}")
print(f"Baseline Brier (lambda=0): {baseline_brier:.6f}")
print(f"Improvement: {improvement:.6f}")

# ===== QUESTION 2: Interaction terms and paired t-test =====
print("\n" + "="*60)
print("QUESTION 2: Interaction Terms and Paired T-Test")
print("="*60)

# Add interaction terms: x0*x1, x1*x2, x2*x3, x0*x3
X_interaction = np.hstack([
    X,
    (X[:, 0] * X[:, 1]).reshape(-1, 1),
    (X[:, 1] * X[:, 2]).reshape(-1, 1),
    (X[:, 2] * X[:, 3]).reshape(-1, 1),
    (X[:, 0] * X[:, 3]).reshape(-1, 1)
])

print(f"Original features: {X.shape[1]}")
print(f"With interactions: {X_interaction.shape[1]}")

# Fit both models on each fold with lambda=0.1
raw_brier_scores = []
interaction_brier_scores = []

for train_idx, test_idx in folds:
    # Raw model
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    w, b, test_brier_raw, _ = fit_logistic(X_train, y_train, X_test, y_test, lam=0.1)
    raw_brier_scores.append(test_brier_raw)
    
    # Interaction model
    X_train_int, X_test_int = X_interaction[train_idx], X_interaction[test_idx]
    w, b, test_brier_int, _ = fit_logistic(X_train_int, y_train, X_test_int, y_test, lam=0.1)
    interaction_brier_scores.append(test_brier_int)

print(f"\nRaw model Brier scores per fold: {raw_brier_scores}")
print(f"Interaction model Brier scores per fold: {interaction_brier_scores}")

# Paired t-test
differences = np.array(raw_brier_scores) - np.array(interaction_brier_scores)
print(f"Differences (raw - interaction): {differences}")

# t-test (one-sample test on differences)
t_stat, p_value = stats.ttest_1samp(differences, 0)
print(f"\nPaired t-test:")
print(f"  t-statistic: {t_stat:.6f}")
print(f"  p-value: {p_value:.6f}")

interaction_helps = t_stat > 2.0
print(f"  Interaction helps (t > 2.0): {interaction_helps}")

# ===== QUESTION 3: Best compression config =====
print("\n" + "="*60)
print("QUESTION 3: Best Compression Configuration")
print("="*60)

# Fit dense model on all data with lambda=0.1
w_dense, b_dense, _, _ = fit_logistic(X, y, X, y, lam=0.1, n_iter=200, lr=0.1)

# Get dense model predictions for Brier score
logits_dense = X @ w_dense + b_dense
logits_dense = np.clip(logits_dense, -30, 30)
y_pred_dense = sigmoid(logits_dense)
dense_brier = brier_score(y, y_pred_dense)

print(f"Dense model Brier score (in-sample): {dense_brier:.6f}")

# Try all compression configs
sparsity_levels = [20, 40, 60]
bit_levels = [8, 4]
best_retention = -1
best_config_str = None

for sparsity_pct in sparsity_levels:
    for bits in bit_levels:
        # Apply sparsity
        w_sparse = w_dense.copy()
        k_zero = round(sparsity_pct / 100.0 * len(w_sparse))
        threshold = np.partition(np.abs(w_sparse), k_zero-1)[k_zero-1]
        w_sparse[np.abs(w_sparse) < threshold] = 0
        
        # Handle ties: if multiple values equal threshold, zero smallest magnitude first
        if np.sum(np.abs(w_sparse) == threshold) > 1:
            mask_threshold = np.abs(w_sparse) == threshold
            num_to_zero = k_zero - np.sum(w_sparse == 0)
            if num_to_zero > 0:
                indices_threshold = np.where(mask_threshold)[0]
                indices_to_zero = indices_threshold[:num_to_zero]
                w_sparse[indices_to_zero] = 0
        
        # Apply quantization to non-zero weights
        w_quantized = w_sparse.copy()
        nonzero_mask = w_sparse != 0
        if np.any(nonzero_mask):
            w_min = np.min(w_sparse[nonzero_mask])
            w_max = np.max(w_sparse[nonzero_mask])
            
            if w_min == w_max:
                # All remaining weights are equal
                w_quantized[nonzero_mask] = w_min
            else:
                # Map to 2^bits levels
                num_levels = 2 ** bits
                w_normalized = (w_sparse[nonzero_mask] - w_min) / (w_max - w_min)
                w_quantized[nonzero_mask] = np.round(w_normalized * (num_levels - 1)) / (num_levels - 1) * (w_max - w_min) + w_min
        
        # Evaluate compressed model
        logits_compressed = X @ w_quantized + b_dense
        logits_compressed = np.clip(logits_compressed, -30, 30)
        y_pred_compressed = sigmoid(logits_compressed)
        compressed_brier = brier_score(y, y_pred_compressed)
        
        # Calculate retention
        retention = dense_brier / compressed_brier if compressed_brier > 0 else 0
        
        config_str = f"sparsity{sparsity_pct}_bits{bits}"
        print(f"{config_str}: dense_brier={dense_brier:.6f}, compressed_brier={compressed_brier:.6f}, retention={retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config_str = config_str

print(f"\nBest compression config: {best_config_str}")
print(f"Best retention: {best_retention:.6f}")

# ===== Output results =====
results = {
    "best_lambda": best_lambda,
    "improvement_over_baseline": improvement,
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config_str
}

print("\n" + "="*60)
print("FINAL RESULTS")
print("="*60)
print(json.dumps(results, indent=2))

with open('answers.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to answers.json")
