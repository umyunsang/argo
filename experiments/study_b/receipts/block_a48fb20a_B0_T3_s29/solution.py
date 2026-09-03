import json
import numpy as np
from scipy import stats

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'], dtype=np.float64)
y = np.array(data['y'], dtype=np.float64)

n_samples, n_features = X.shape
print(f"Data shape: {n_samples} samples, {n_features} features")

# ============================================================================
# TASK 1: Find best lambda from [0.0, 0.01, 0.1, 1.0, 10.0]
# ============================================================================

def logistic_regression_cv(X, y, lambda_val, n_folds=5, n_iters=200, lr=0.1):
    """
    Logistic regression with 5-fold CV using contiguous blocks.
    Returns list of Brier scores for each fold.
    """
    n_samples = len(y)
    fold_size = n_samples // n_folds
    brier_scores = []
    
    for fold_idx in range(n_folds):
        # Create train and test split using contiguous blocks
        # fold k is the k-th consecutive slice
        test_indices = list(range(fold_idx, n_samples, n_folds))
        train_indices = [i for i in range(n_samples) if i not in test_indices]
        
        X_train = X[train_indices]
        y_train = y[train_indices]
        X_test = X[test_indices]
        y_test = y[test_indices]
        
        n_train = len(y_train)
        
        # Initialize weights and bias at 0
        w = np.zeros(n_features, dtype=np.float64)
        b = np.float64(0.0)
        
        # Full-batch gradient descent, 200 iterations
        for iteration in range(n_iters):
            # Compute logits
            logits = X_train @ w + b
            
            # Clip logits to [-30, 30]
            logits = np.clip(logits, -30, 30)
            
            # Compute probabilities using sigmoid
            probs = 1.0 / (1.0 + np.exp(-logits))
            
            # Compute gradients
            error = probs - y_train
            grad_w = X_train.T @ error / n_train + lambda_val * w
            grad_b = np.sum(error) / n_train
            
            # Update weights and bias
            w -= lr * grad_w
            b -= lr * grad_b
        
        # Evaluate on test set
        test_logits = X_test @ w + b
        test_logits = np.clip(test_logits, -30, 30)
        test_probs = 1.0 / (1.0 + np.exp(-test_logits))
        
        # Brier score: mean squared error between predicted probabilities and actual labels
        brier = np.mean((test_probs - y_test) ** 2)
        brier_scores.append(brier)
    
    return np.array(brier_scores)

lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
results_task1 = {}

for lambda_val in lambdas:
    brier_scores = logistic_regression_cv(X, y, lambda_val)
    mean_brier = np.mean(brier_scores)
    results_task1[lambda_val] = {
        'mean_brier': mean_brier,
        'brier_scores': brier_scores.tolist()
    }
    print(f"Lambda {lambda_val}: mean Brier = {mean_brier:.6f}, scores = {brier_scores}")

# Find best lambda
best_lambda = min(results_task1.keys(), key=lambda x: results_task1[x]['mean_brier'])
best_brier = results_task1[best_lambda]['mean_brier']
baseline_brier = results_task1[0.0]['mean_brier']
improvement = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda}, Brier: {best_brier:.6f}")
print(f"Baseline (lambda=0): {baseline_brier:.6f}")
print(f"Improvement: {improvement:.6f}")

# ============================================================================
# TASK 2: Interaction terms and paired t-test
# ============================================================================

# Add interaction features
X_interaction = X.copy()
X_interaction = np.column_stack([
    X_interaction,
    X[:, 0] * X[:, 1],  # x0 * x1
    X[:, 1] * X[:, 2],  # x1 * x2
    X[:, 2] * X[:, 3],  # x2 * x3
    X[:, 0] * X[:, 3]   # x0 * x3
])

print(f"\nInteraction features shape: {X_interaction.shape}")

def logistic_regression_cv_get_per_fold_brier(X, y, lambda_val=0.1, n_folds=5, n_iters=200, lr=0.1):
    """
    Returns per-fold Brier scores instead of averaged.
    """
    n_samples = len(y)
    brier_scores = []
    
    for fold_idx in range(n_folds):
        # Create train and test split using contiguous blocks
        test_indices = list(range(fold_idx, n_samples, n_folds))
        train_indices = [i for i in range(n_samples) if i not in test_indices]
        
        X_train = X[train_indices]
        y_train = y[train_indices]
        X_test = X[test_indices]
        y_test = y[test_indices]
        
        n_train = len(y_train)
        n_features = X_train.shape[1]
        
        # Initialize weights and bias at 0
        w = np.zeros(n_features, dtype=np.float64)
        b = np.float64(0.0)
        
        # Full-batch gradient descent, 200 iterations
        for iteration in range(n_iters):
            # Compute logits
            logits = X_train @ w + b
            
            # Clip logits to [-30, 30]
            logits = np.clip(logits, -30, 30)
            
            # Compute probabilities using sigmoid
            probs = 1.0 / (1.0 + np.exp(-logits))
            
            # Compute gradients
            error = probs - y_train
            grad_w = X_train.T @ error / n_train + lambda_val * w
            grad_b = np.sum(error) / n_train
            
            # Update weights and bias
            w -= lr * grad_w
            b -= lr * grad_b
        
        # Evaluate on test set
        test_logits = X_test @ w + b
        test_logits = np.clip(test_logits, -30, 30)
        test_probs = 1.0 / (1.0 + np.exp(-test_logits))
        
        # Brier score
        brier = np.mean((test_probs - y_test) ** 2)
        brier_scores.append(brier)
    
    return np.array(brier_scores)

# Get per-fold Brier scores for both representations
brier_raw = logistic_regression_cv_get_per_fold_brier(X, y, lambda_val=0.1)
brier_interaction = logistic_regression_cv_get_per_fold_brier(X_interaction, y, lambda_val=0.1)

print(f"\nBrier scores (raw): {brier_raw}")
print(f"Brier scores (interaction): {brier_interaction}")

# Paired t-test: raw minus interaction
differences = brier_raw - brier_interaction
print(f"Differences (raw - interaction): {differences}")

# Compute t-statistic
mean_diff = np.mean(differences)
std_diff = np.std(differences, ddof=1)
t_stat = mean_diff / (std_diff / np.sqrt(len(differences)))

print(f"Mean difference: {mean_diff:.6f}")
print(f"Std of differences: {std_diff:.6f}")
print(f"T-statistic: {t_stat:.6f}")

interaction_helps = t_stat > 2.0
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# ============================================================================
# TASK 3: Compression (sparsity and quantization)
# ============================================================================

# First, fit the dense model on all data with lambda=0.1
print("\n\n=== TASK 3: Compression ===")

def fit_logistic_full(X, y, lambda_val=0.1, n_iters=200, lr=0.1):
    """
    Fit logistic regression on full dataset.
    """
    n_samples, n_features = X.shape
    
    # Initialize weights and bias at 0
    w = np.zeros(n_features, dtype=np.float64)
    b = np.float64(0.0)
    
    # Full-batch gradient descent
    for iteration in range(n_iters):
        # Compute logits
        logits = X @ w + b
        
        # Clip logits to [-30, 30]
        logits = np.clip(logits, -30, 30)
        
        # Compute probabilities
        probs = 1.0 / (1.0 + np.exp(-logits))
        
        # Compute gradients
        error = probs - y
        grad_w = X.T @ error / n_samples + lambda_val * w
        grad_b = np.sum(error) / n_samples
        
        # Update
        w -= lr * grad_w
        b -= lr * grad_b
    
    return w, b

# Fit dense model on all data
w_dense, b_dense = fit_logistic_full(X, y, lambda_val=0.1)

# Compute dense model Brier score on full data
logits_dense = X @ w_dense + b_dense
logits_dense = np.clip(logits_dense, -30, 30)
probs_dense = 1.0 / (1.0 + np.exp(-logits_dense))
brier_dense = np.mean((probs_dense - y) ** 2)

print(f"Dense model Brier score: {brier_dense:.6f}")

# Test different configurations
sparsities = [20, 40, 60]  # percentages
bits_options = [8, 4]

best_retention = 0
best_config = None
results_compression = {}

for sparsity_pct in sparsities:
    for bits in bits_options:
        # Apply sparsity: zero smallest magnitude weights
        w_sparse = w_dense.copy()
        k = round(sparsity_pct / 100.0 * len(w_sparse))
        
        # Find indices of k smallest magnitude weights
        abs_w = np.abs(w_sparse)
        threshold_idx = np.argsort(abs_w)[:k]
        w_sparse[threshold_idx] = 0.0
        
        # Apply quantization to non-zero weights
        w_quant = w_sparse.copy()
        mask_nonzero = w_sparse != 0.0
        if np.any(mask_nonzero):
            nonzero_vals = w_sparse[mask_nonzero]
            w_min = np.min(nonzero_vals)
            w_max = np.max(nonzero_vals)
            
            if w_min < w_max:
                # Map to 2^bits levels
                levels = 2 ** bits
                normalized = (nonzero_vals - w_min) / (w_max - w_min)
                quantized = np.round(normalized * (levels - 1)) / (levels - 1) * (w_max - w_min) + w_min
                w_quant[mask_nonzero] = quantized
        
        # Evaluate compressed model on full data
        logits_comp = X @ w_quant + b_dense  # bias untouched
        logits_comp = np.clip(logits_comp, -30, 30)
        probs_comp = 1.0 / (1.0 + np.exp(-logits_comp))
        brier_comp = np.mean((probs_comp - y) ** 2)
        
        # Retention = dense Brier / compressed Brier
        retention = brier_dense / brier_comp if brier_comp > 0 else float('inf')
        
        config_name = f"sparsity{sparsity_pct}_bits{bits}"
        results_compression[config_name] = {
            'sparsity': sparsity_pct,
            'bits': bits,
            'brier_compressed': brier_comp,
            'retention': retention
        }
        
        print(f"Config {config_name}: compressed Brier={brier_comp:.6f}, retention={retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = config_name

print(f"\nBest compression config: {best_config} with retention {best_retention:.6f}")

# ============================================================================
# Save results
# ============================================================================

answers = {
    'best_lambda': float(best_lambda),
    'improvement_over_baseline': float(improvement),
    'paired_t_stat': float(t_stat),
    'interaction_helps': bool(interaction_helps),
    'best_config': best_config
}

print("\n\n=== FINAL ANSWERS ===")
for key, value in answers.items():
    print(f"{key}: {value}")

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("\nAnswers saved to answers.json")
