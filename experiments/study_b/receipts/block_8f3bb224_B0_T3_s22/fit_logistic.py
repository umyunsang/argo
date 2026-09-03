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

# Create contiguous fold indices
fold_size = n_samples // n_folds
fold_indices = []
for k in range(n_folds):
    start = k * fold_size
    end = start + fold_size
    fold_indices.append(np.arange(start, end))

print(f"Data shape: X={X.shape}, y={y.shape}")
print(f"Fold sizes: {[len(idx) for idx in fold_indices]}")

def sigmoid(x):
    """Sigmoid with clipping to avoid overflow"""
    x = np.clip(x, -30, 30)
    return 1.0 / (1.0 + np.exp(-x))

def logit(x):
    """Logit with clipping"""
    return np.clip(x, -30, 30)

def brier_score(y_true, y_pred):
    """Brier score: mean squared error between true and predicted probabilities"""
    return np.mean((y_true - y_pred) ** 2)

def fit_logistic(X_train, y_train, lambda_reg, n_iterations=200, learning_rate=0.1):
    """Fit logistic regression with specified hyperparameters"""
    n_features = X_train.shape[1]
    n_samples = X_train.shape[0]
    
    # Initialize weights and bias at 0
    w = np.zeros(n_features)
    b = 0.0
    
    for iteration in range(n_iterations):
        # Forward pass
        logits = np.dot(X_train, w) + b
        logits = np.clip(logits, -30, 30)
        y_pred = sigmoid(logits)
        
        # Compute gradients
        error = y_pred - y_train
        grad_w = np.dot(X_train.T, error)
        grad_b = np.sum(error)
        
        # Update parameters
        # w -= 0.1 * (grad_w / n + lambda * w)
        # b -= 0.1 * (grad_b / n)
        w = w - learning_rate * (grad_w / n_samples + lambda_reg * w)
        b = b - learning_rate * (grad_b / n_samples)
    
    return w, b

def predict_logistic(X, w, b):
    """Predict probabilities"""
    logits = np.dot(X, w) + b
    logits = np.clip(logits, -30, 30)
    return sigmoid(logits)

# ============================================
# Question 1: Find best lambda
# ============================================
print("\n" + "="*60)
print("Question 1: Finding best lambda")
print("="*60)

lambda_values = [0.0, 0.01, 0.1, 1.0, 10.0]
brier_scores_per_lambda = {lam: [] for lam in lambda_values}

for lam in lambda_values:
    print(f"\nLambda = {lam}")
    fold_brier_scores = []
    
    for fold_idx, test_indices in enumerate(fold_indices):
        # Create train/test split
        train_indices = np.concatenate([fold_indices[i] for i in range(n_folds) if i != fold_idx])
        
        X_train = X[train_indices]
        y_train = y[train_indices]
        X_test = X[test_indices]
        y_test = y[test_indices]
        
        # Fit model
        w, b = fit_logistic(X_train, y_train, lam)
        
        # Predict on test set
        y_pred = predict_logistic(X_test, w, b)
        
        # Compute Brier score
        brier = brier_score(y_test, y_pred)
        fold_brier_scores.append(brier)
        print(f"  Fold {fold_idx}: Brier = {brier:.6f}")
    
    mean_brier = np.mean(fold_brier_scores)
    brier_scores_per_lambda[lam] = fold_brier_scores
    print(f"  Mean Brier: {mean_brier:.6f}")

# Find best lambda
mean_briers = {lam: np.mean(brier_scores_per_lambda[lam]) for lam in lambda_values}
best_lambda = min(mean_briers, key=mean_briers.get)
baseline_brier = mean_briers[0.0]
best_brier = mean_briers[best_lambda]
improvement = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda}")
print(f"Baseline Brier (lambda=0): {baseline_brier:.6f}")
print(f"Best Brier (lambda={best_lambda}): {best_brier:.6f}")
print(f"Improvement: {improvement:.6f}")

# ============================================
# Question 2: Interaction features
# ============================================
print("\n" + "="*60)
print("Question 2: Interaction features")
print("="*60)

# Add interaction features: x0*x1, x1*x2, x2*x3, x0*x3
X_with_interactions = np.concatenate([
    X,
    X[:, 0:1] * X[:, 1:2],  # x0 * x1
    X[:, 1:2] * X[:, 2:3],  # x1 * x2
    X[:, 2:3] * X[:, 3:4],  # x2 * x3
    X[:, 0:1] * X[:, 3:4],  # x0 * x3
], axis=1)

print(f"Original features: {X.shape[1]}")
print(f"Features with interactions: {X_with_interactions.shape[1]}")

# Fit both models with lambda=0.1
lambda_val = 0.1
raw_brier_scores = []
interaction_brier_scores = []

for fold_idx, test_indices in enumerate(fold_indices):
    # Create train/test split
    train_indices = np.concatenate([fold_indices[i] for i in range(n_folds) if i != fold_idx])
    
    X_train = X[train_indices]
    y_train = y[train_indices]
    X_test = X[test_indices]
    y_test = y[test_indices]
    
    # Raw model
    w_raw, b_raw = fit_logistic(X_train, y_train, lambda_val)
    y_pred_raw = predict_logistic(X_test, w_raw, b_raw)
    brier_raw = brier_score(y_test, y_pred_raw)
    raw_brier_scores.append(brier_raw)
    
    # Interaction model
    X_train_int = X_with_interactions[train_indices]
    X_test_int = X_with_interactions[test_indices]
    
    w_int, b_int = fit_logistic(X_train_int, y_train, lambda_val)
    y_pred_int = predict_logistic(X_test_int, w_int, b_int)
    brier_int = brier_score(y_test, y_pred_int)
    interaction_brier_scores.append(brier_int)
    
    print(f"Fold {fold_idx}: Raw Brier={brier_raw:.6f}, Interaction Brier={brier_int:.6f}")

# Compute paired t-test
raw_brier_scores = np.array(raw_brier_scores)
interaction_brier_scores = np.array(interaction_brier_scores)
differences = raw_brier_scores - interaction_brier_scores  # raw - interaction

t_stat, p_value = stats.ttest_rel(raw_brier_scores, interaction_brier_scores)

print(f"\nPaired t-test results:")
print(f"  Raw Brier scores: {raw_brier_scores}")
print(f"  Interaction Brier scores: {interaction_brier_scores}")
print(f"  Differences (raw - interaction): {differences}")
print(f"  t-statistic: {t_stat:.6f}")
print(f"  p-value: {p_value:.6f}")

# Check if t > 2.0 (interaction helps)
interaction_helps = t_stat > 2.0
print(f"  t > 2.0? {interaction_helps}")

# ============================================
# Question 3: Compression (sparsity and quantization)
# ============================================
print("\n" + "="*60)
print("Question 3: Compression")
print("="*60)

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic(X, y, 0.1)

# Get dense model Brier score on full data
y_pred_dense = predict_logistic(X, w_dense, b_dense)
brier_dense = brier_score(y, y_pred_dense)
print(f"Dense model Brier (on full data): {brier_dense:.6f}")

# Test all compression configurations
sparsity_levels = [20, 40, 60]  # percent
bit_levels = [8, 4]

best_retention = 0.0
best_config = None
results = []

for sparsity_pct in sparsity_levels:
    for bits in bit_levels:
        # Apply sparsity
        w_sparse = w_dense.copy()
        
        # Number of weights to zero out
        k = int(np.round(sparsity_pct / 100.0 * len(w_sparse)))
        
        # Get indices of smallest magnitude weights
        abs_w = np.abs(w_sparse)
        threshold_idx = np.argsort(abs_w)[:k]
        w_sparse[threshold_idx] = 0.0
        
        # Apply quantization
        w_quant = w_sparse.copy()
        
        # Find min/max of non-zero weights
        non_zero_mask = w_quant != 0
        if np.any(non_zero_mask):
            w_nonzero = w_quant[non_zero_mask]
            w_min = np.min(w_nonzero)
            w_max = np.max(w_nonzero)
            
            # Map to 2^bits levels
            n_levels = 2 ** bits
            
            if w_max > w_min:
                # Quantize
                w_quant[non_zero_mask] = np.round((w_nonzero - w_min) / (w_max - w_min) * (n_levels - 1)) * (w_max - w_min) / (n_levels - 1) + w_min
            # else: if all non-zero weights are equal, they stay the same
        
        # Predict with compressed model
        y_pred_comp = predict_logistic(X, w_quant, b_dense)
        brier_comp = brier_score(y, y_pred_comp)
        
        # Compute retention
        retention = brier_dense / brier_comp if brier_comp > 0 else float('inf')
        
        config_name = f"sparsity{sparsity_pct}_bits{bits}"
        results.append({
            'config': config_name,
            'sparsity': sparsity_pct,
            'bits': bits,
            'brier': brier_comp,
            'retention': retention
        })
        
        print(f"{config_name:20s}: Brier={brier_comp:.6f}, Retention={retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = config_name

print(f"\nBest compression config: {best_config}")
print(f"Best retention: {best_retention:.6f}")

# ============================================
# Save answers
# ============================================
answers = {
    "best_lambda": best_lambda,
    "improvement_over_baseline": improvement,
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

print("\n" + "="*60)
print("FINAL ANSWERS")
print("="*60)
for key, value in answers.items():
    print(f"{key}: {value}")

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("\nAnswers saved to answers.json")
