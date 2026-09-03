import json
import numpy as np
from scipy import stats

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'], dtype=np.float64)
y = np.array(data['y'], dtype=np.float64)

n_samples = X.shape[0]
n_features = X.shape[1]
n_folds = 5

print(f"Data shape: {X.shape}, labels shape: {y.shape}")

# Helper function to compute Brier score
def brier_score(y_true, y_pred_proba):
    """Brier score: mean squared error of probability predictions"""
    return np.mean((y_pred_proba - y_true) ** 2)

# Helper function to sigmoid
def sigmoid(z):
    """Sigmoid with clipping to prevent overflow"""
    z = np.clip(z, -30, 30)
    return 1.0 / (1.0 + np.exp(-z))

# Helper function to fit logistic model
def fit_logistic(X_train, y_train, lambda_reg=0.0, learning_rate=0.1, n_iterations=200):
    """
    Fit logistic regression using full-batch gradient descent
    """
    n_samples, n_features = X_train.shape
    w = np.zeros(n_features)
    b = 0.0
    
    for iteration in range(n_iterations):
        # Forward pass
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)
        proba = sigmoid(logits)
        
        # Gradient computation
        residuals = proba - y_train
        grad_w = X_train.T @ residuals / n_samples
        grad_b = np.mean(residuals)
        
        # Update
        w = w - learning_rate * (grad_w + lambda_reg * w)
        b = b - learning_rate * grad_b
    
    return w, b

# Helper function to predict
def predict_proba(X, w, b):
    """Compute predicted probabilities"""
    logits = X @ w + b
    logits = np.clip(logits, -30, 30)
    return sigmoid(logits)

# Create folds: 5 contiguous blocks in row order
fold_size = n_samples // n_folds
folds = []
for k in range(n_folds):
    start_idx = k * fold_size
    if k == n_folds - 1:
        end_idx = n_samples
    else:
        end_idx = (k + 1) * fold_size
    fold_indices = np.arange(start_idx, end_idx)
    folds.append(fold_indices)

print(f"Fold sizes: {[len(f) for f in folds]}")

# ============================================
# Question 1: Best lambda and improvement
# ============================================
print("\n" + "="*50)
print("Question 1: Best Lambda and Improvement")
print("="*50)

lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
brier_scores_per_lambda = {lam: [] for lam in lambdas}

for lam in lambdas:
    for fold_idx in range(n_folds):
        # Get train and test indices
        test_indices = folds[fold_idx]
        train_indices = np.concatenate([folds[i] for i in range(n_folds) if i != fold_idx])
        
        X_train = X[train_indices]
        y_train = y[train_indices]
        X_test = X[test_indices]
        y_test = y[test_indices]
        
        # Fit model
        w, b = fit_logistic(X_train, y_train, lambda_reg=lam)
        
        # Evaluate on test set
        y_pred_proba = predict_proba(X_test, w, b)
        brier = brier_score(y_test, y_pred_proba)
        brier_scores_per_lambda[lam].append(brier)

# Compute mean Brier score for each lambda
mean_brier_scores = {lam: np.mean(brier_scores_per_lambda[lam]) for lam in lambdas}
print("\nMean Brier scores by lambda:")
for lam in lambdas:
    print(f"  lambda={lam}: {mean_brier_scores[lam]:.6f}")

best_lambda = min(mean_brier_scores, key=mean_brier_scores.get)
baseline_brier = mean_brier_scores[0.0]
best_brier = mean_brier_scores[best_lambda]
improvement = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda}")
print(f"Baseline (lambda=0) Brier: {baseline_brier:.6f}")
print(f"Best Brier: {best_brier:.6f}")
print(f"Improvement: {improvement:.6f}")

# ============================================
# Question 2: Interaction terms analysis
# ============================================
print("\n" + "="*50)
print("Question 2: Interaction Terms")
print("="*50)

# Add interaction features: x0*x1, x1*x2, x2*x3, x0*x3
X_with_interactions = np.hstack([
    X,
    (X[:, 0:1] * X[:, 1:2]),
    (X[:, 1:2] * X[:, 2:3]),
    (X[:, 2:3] * X[:, 3:4]),
    (X[:, 0:1] * X[:, 3:4])
])

print(f"Original features: {n_features}")
print(f"With interactions: {X_with_interactions.shape[1]}")

# Fit both models on all 5 folds with lambda=0.1
lambda_interaction = 0.1
brier_raw_per_fold = []
brier_interaction_per_fold = []

for fold_idx in range(n_folds):
    test_indices = folds[fold_idx]
    train_indices = np.concatenate([folds[i] for i in range(n_folds) if i != fold_idx])
    
    X_train_raw = X[train_indices]
    y_train = y[train_indices]
    X_test_raw = X[test_indices]
    y_test = y[test_indices]
    
    X_train_inter = X_with_interactions[train_indices]
    X_test_inter = X_with_interactions[test_indices]
    
    # Fit raw model
    w_raw, b_raw = fit_logistic(X_train_raw, y_train, lambda_reg=lambda_interaction)
    y_pred_raw = predict_proba(X_test_raw, w_raw, b_raw)
    brier_raw = brier_score(y_test, y_pred_raw)
    brier_raw_per_fold.append(brier_raw)
    
    # Fit interaction model
    w_inter, b_inter = fit_logistic(X_train_inter, y_train, lambda_reg=lambda_interaction)
    y_pred_inter = predict_proba(X_test_inter, w_inter, b_inter)
    brier_inter = brier_score(y_test, y_pred_inter)
    brier_interaction_per_fold.append(brier_inter)

print(f"\nBrier scores (raw model, lambda=0.1):")
print(f"  Per fold: {brier_raw_per_fold}")
print(f"  Mean: {np.mean(brier_raw_per_fold):.6f}")

print(f"\nBrier scores (interaction model, lambda=0.1):")
print(f"  Per fold: {brier_interaction_per_fold}")
print(f"  Mean: {np.mean(brier_interaction_per_fold):.6f}")

# Paired t-test
brier_raw_per_fold = np.array(brier_raw_per_fold)
brier_interaction_per_fold = np.array(brier_interaction_per_fold)
differences = brier_raw_per_fold - brier_interaction_per_fold

print(f"\nPer-fold differences (raw - interaction):")
print(f"  {differences}")

t_stat, p_value = stats.ttest_rel(brier_raw_per_fold, brier_interaction_per_fold)
print(f"\nPaired t-test (raw vs interaction):")
print(f"  t-statistic: {t_stat:.6f}")
print(f"  p-value: {p_value:.6f}")
print(f"  interaction_helps: {t_stat > 2.0}")

# ============================================
# Question 3: Compression (Sparsity + Quantization)
# ============================================
print("\n" + "="*50)
print("Question 3: Compression")
print("="*50)

# First, fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic(X, y, lambda_reg=0.1)
y_pred_dense = predict_proba(X, w_dense, b_dense)
brier_dense = brier_score(y, y_pred_dense)

print(f"Dense model Brier score (all data, lambda=0.1): {brier_dense:.6f}")

# Test all configurations
sparsity_levels = [20, 40, 60]  # percent
bit_widths = [8, 4]

results = {}

for sparsity in sparsity_levels:
    for bits in bit_widths:
        config_name = f"sparsity{sparsity}_bits{bits}"
        
        # Apply sparsity: zero smallest magnitude weights
        w_sparse = w_dense.copy()
        k = int(np.round(sparsity / 100.0 * len(w_dense)))
        if k > 0:
            threshold_idx = np.argsort(np.abs(w_sparse))[k]
            threshold = np.abs(w_sparse[threshold_idx])
            w_sparse[np.abs(w_sparse) <= threshold] = 0
        
        # Apply quantization to non-zero weights
        w_compressed = w_sparse.copy()
        non_zero_mask = w_sparse != 0
        if np.any(non_zero_mask):
            non_zero_weights = w_sparse[non_zero_mask]
            min_w = np.min(non_zero_weights)
            max_w = np.max(non_zero_weights)
            
            if min_w < max_w:  # Only quantize if there's variation
                # Map to 2^bits levels
                n_levels = 2 ** bits
                quantized = np.round((non_zero_weights - min_w) / (max_w - min_w) * (n_levels - 1))
                w_compressed[non_zero_mask] = min_w + quantized * (max_w - min_w) / (n_levels - 1)
        
        # Evaluate compressed model on all data (in-sample)
        y_pred_compressed = predict_proba(X, w_compressed, b_dense)
        brier_compressed = brier_score(y, y_pred_compressed)
        
        retention = brier_dense / brier_compressed
        
        results[config_name] = {
            'sparsity': sparsity,
            'bits': bits,
            'brier_compressed': brier_compressed,
            'retention': retention
        }
        
        print(f"\n{config_name}:")
        print(f"  Compressed Brier: {brier_compressed:.6f}")
        print(f"  Retention (dense/compressed): {retention:.6f}")

# Find best configuration
best_config = max(results, key=lambda x: results[x]['retention'])
print(f"\nBest configuration: {best_config}")
print(f"  Retention: {results[best_config]['retention']:.6f}")

# ============================================
# Prepare answers
# ============================================
answers = {
    "best_lambda": best_lambda,
    "improvement_over_baseline": improvement,
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(t_stat > 2.0),
    "best_config": best_config
}

print("\n" + "="*50)
print("FINAL ANSWERS")
print("="*50)
print(json.dumps(answers, indent=2))

# Write to file
with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("\nAnswers written to answers.json")
