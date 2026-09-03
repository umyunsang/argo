import json
import numpy as np
from scipy import stats

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'])
y = np.array(data['y'])

n_samples = len(X)
n_features = len(X[0])

print(f"Data shape: X={X.shape}, y={y.shape}")

# Helper function: logistic regression fit with specified parameters
def fit_logistic_regression(X_train, y_train, X_val, y_val, lambda_val=0.0, n_iterations=200, learning_rate=0.1):
    """
    Fit logistic regression with full-batch gradient descent
    """
    n = len(X_train)
    d = X_train.shape[1]  # Use the actual number of features from input
    
    # Initialize weights and bias at 0
    w = np.zeros(d)
    b = 0.0
    
    # Training loop
    for _ in range(n_iterations):
        # Forward pass
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)
        
        # Sigmoid
        probs = 1.0 / (1.0 + np.exp(-logits))
        
        # Gradients
        errors = probs - y_train
        grad_w = X_train.T @ errors / n
        grad_b = np.mean(errors)
        
        # Update with L2 regularization
        w = w - learning_rate * (grad_w + lambda_val * w)
        b = b - learning_rate * grad_b
    
    # Predictions on validation set
    logits_val = X_val @ w + b
    logits_val = np.clip(logits_val, -30, 30)
    probs_val = 1.0 / (1.0 + np.exp(-logits_val))
    
    # Brier score = mean squared error
    brier = np.mean((probs_val - y_val) ** 2)
    
    return w, b, brier

# Create 5-fold cross-validation with contiguous blocks
n_samples = len(X)
fold_size = n_samples // 5

brier_scores = {lambda_val: [] for lambda_val in [0.0, 0.01, 0.1, 1.0, 10.0]}

for fold_idx in range(5):
    # Create fold boundaries
    val_start = fold_idx * fold_size
    if fold_idx == 4:
        val_end = n_samples
    else:
        val_end = (fold_idx + 1) * fold_size
    
    # Split data
    val_indices = list(range(val_start, val_end))
    train_indices = list(range(0, val_start)) + list(range(val_end, n_samples))
    
    X_train = X[train_indices]
    y_train = y[train_indices]
    X_val = X[val_indices]
    y_val = y[val_indices]
    
    # Test different lambda values
    for lambda_val in [0.0, 0.01, 0.1, 1.0, 10.0]:
        _, _, brier = fit_logistic_regression(X_train, y_train, X_val, y_val, lambda_val=lambda_val)
        brier_scores[lambda_val].append(brier)

# Q1: Find best lambda and improvement
mean_brier = {lam: np.mean(scores) for lam, scores in brier_scores.items()}
best_lambda = min(mean_brier, key=mean_brier.get)
improvement = mean_brier[0.0] - mean_brier[best_lambda]

print(f"\nQuestion 1:")
print(f"Mean Brier scores: {mean_brier}")
print(f"Best lambda: {best_lambda}")
print(f"Improvement over baseline: {improvement:.6f}")

# Q2: Test with interaction terms
# Add interaction features: x0*x1, x1*x2, x2*x3, x0*x3

X_with_interactions = np.hstack([
    X,
    (X[:, 0] * X[:, 1]).reshape(-1, 1),  # x0*x1
    (X[:, 1] * X[:, 2]).reshape(-1, 1),  # x1*x2
    (X[:, 2] * X[:, 3]).reshape(-1, 1),  # x2*x3
    (X[:, 0] * X[:, 3]).reshape(-1, 1),  # x0*x3
])

brier_raw = []
brier_interaction = []

for fold_idx in range(5):
    # Create fold boundaries
    val_start = fold_idx * fold_size
    if fold_idx == 4:
        val_end = n_samples
    else:
        val_end = (fold_idx + 1) * fold_size
    
    # Split data
    val_indices = list(range(val_start, val_end))
    train_indices = list(range(0, val_start)) + list(range(val_end, n_samples))
    
    # Raw features (lambda=0.1)
    X_train = X[train_indices]
    y_train = y[train_indices]
    X_val = X[val_indices]
    y_val = y[val_indices]
    
    _, _, brier_raw_fold = fit_logistic_regression(X_train, y_train, X_val, y_val, lambda_val=0.1)
    brier_raw.append(brier_raw_fold)
    
    # With interactions (lambda=0.1)
    X_train_int = X_with_interactions[train_indices]
    X_val_int = X_with_interactions[val_indices]
    
    _, _, brier_int_fold = fit_logistic_regression(X_train_int, y_train, X_val_int, y_val, lambda_val=0.1)
    brier_interaction.append(brier_int_fold)

# Paired t-test
brier_diff = np.array(brier_raw) - np.array(brier_interaction)
paired_t_stat = (np.mean(brier_diff) / (np.std(brier_diff, ddof=1) / np.sqrt(5)))
interaction_helps = paired_t_stat > 2.0

print(f"\nQuestion 2:")
print(f"Brier raw: {brier_raw}")
print(f"Brier interaction: {brier_interaction}")
print(f"Differences (raw - interaction): {brier_diff}")
print(f"Paired t-statistic: {paired_t_stat:.6f}")
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# Q3: Compression - fit on all data with lambda=0.1
print(f"\nQuestion 3:")
print(f"Fitting dense model on all data with lambda=0.1...")

# Fit dense model on all data
n = len(X)
d = n_features

w_dense = np.zeros(d)
b_dense = 0.0

for _ in range(200):
    logits = X @ w_dense + b_dense
    logits = np.clip(logits, -30, 30)
    probs = 1.0 / (1.0 + np.exp(-logits))
    
    errors = probs - y
    grad_w = X.T @ errors / n
    grad_b = np.mean(errors)
    
    w_dense = w_dense - 0.1 * (grad_w + 0.1 * w_dense)
    b_dense = b_dense - 0.1 * grad_b

# Compute dense Brier on all data
logits_dense = X @ w_dense + b_dense
logits_dense = np.clip(logits_dense, -30, 30)
probs_dense = 1.0 / (1.0 + np.exp(-logits_dense))
brier_dense = np.mean((probs_dense - y) ** 2)

print(f"Dense model Brier: {brier_dense:.6f}")

# Test all compression configurations
best_retention = -1
best_config = None

sparsity_levels = [20, 40, 60]
bit_levels = [8, 4]

for sparsity in sparsity_levels:
    for bits in bit_levels:
        # Sparsity: zero out smallest magnitude weights
        k = max(1, round(sparsity / 100.0 * d))
        w_sparse = w_dense.copy()
        
        # Get indices of smallest magnitude weights
        abs_w = np.abs(w_sparse)
        threshold_idx = np.argsort(abs_w)[: k]
        w_sparse[threshold_idx] = 0
        
        # Quantization on remaining weights
        w_compressed = w_sparse.copy()
        non_zero_mask = w_compressed != 0
        
        if np.any(non_zero_mask):
            w_min = np.min(w_compressed[non_zero_mask])
            w_max = np.max(w_compressed[non_zero_mask])
            
            if w_min != w_max:
                # Map to 2^bits levels
                n_levels = 2 ** bits
                quantized = np.zeros_like(w_compressed)
                
                # Quantize non-zero values
                for idx in np.where(non_zero_mask)[0]:
                    # Map to [0, n_levels-1]
                    level = round((w_compressed[idx] - w_min) / (w_max - w_min) * (n_levels - 1))
                    # Map back
                    quantized[idx] = w_min + level * (w_max - w_min) / (n_levels - 1)
                
                w_compressed = quantized
        
        # Compute Brier on all data with compressed model
        logits_compressed = X @ w_compressed + b_dense
        logits_compressed = np.clip(logits_compressed, -30, 30)
        probs_compressed = 1.0 / (1.0 + np.exp(-logits_compressed))
        brier_compressed = np.mean((probs_compressed - y) ** 2)
        
        # Retention = dense / compressed
        retention = brier_dense / brier_compressed if brier_compressed > 0 else 0
        
        print(f"Config sparsity{sparsity}_bits{bits}: retention={retention:.6f}, brier_compressed={brier_compressed:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = f"sparsity{sparsity}_bits{bits}"

print(f"Best compression config: {best_config} with retention {best_retention:.6f}")

# Write answers
answers = {
    "best_lambda": float(best_lambda),
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(paired_t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print(f"\nAnswers saved to answers.json")
print(json.dumps(answers, indent=2))
