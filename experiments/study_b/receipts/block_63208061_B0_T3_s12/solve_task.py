import json
import numpy as np
from scipy import stats

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'], dtype=np.float64)
y = np.array(data['y'], dtype=np.float64)

n_samples = len(y)
n_features = X.shape[1]

print(f"Data shape: X={X.shape}, y={y.shape}")

# Create 5 contiguous folds
def create_contiguous_folds(n_samples, n_folds=5):
    """Create n contiguous folds by dividing samples into blocks"""
    fold_size = n_samples // n_folds
    folds = []
    for i in range(n_folds):
        start = i * fold_size
        if i == n_folds - 1:
            end = n_samples
        else:
            end = (i + 1) * fold_size
        test_idx = list(range(start, end))
        train_idx = list(range(0, start)) + list(range(end, n_samples))
        folds.append((train_idx, test_idx))
    return folds

# Logistic regression implementation
def sigmoid(z):
    z = np.clip(z, -30, 30)  # Clip logits
    return 1 / (1 + np.exp(-z))

def logistic_fit(X_train, y_train, lambda_reg=0.0, n_iterations=200, learning_rate=0.1):
    """Fit logistic regression using full-batch GD"""
    n_samples, n_features = X_train.shape
    w = np.zeros(n_features)
    b = 0.0
    
    for iteration in range(n_iterations):
        # Forward pass
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)
        y_pred = sigmoid(logits)
        
        # Compute gradients
        error = y_pred - y_train
        grad_w = X_train.T @ error / n_samples
        grad_b = np.mean(error)
        
        # Update with L2 regularization
        w = w - learning_rate * (grad_w + lambda_reg * w)
        b = b - learning_rate * grad_b
    
    return w, b

def brier_score(y_true, y_pred_prob):
    """Compute Brier score"""
    return np.mean((y_pred_prob - y_true) ** 2)

def predict_prob(X, w, b):
    """Predict probability"""
    logits = np.clip(X @ w + b, -30, 30)
    return sigmoid(logits)

# Task 1: Find best lambda
print("\n=== Task 1: Finding best lambda ===")
lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
folds = create_contiguous_folds(n_samples, n_folds=5)

brier_scores_by_lambda = {lam: [] for lam in lambdas}

for fold_idx, (train_idx, test_idx) in enumerate(folds):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    for lam in lambdas:
        w, b = logistic_fit(X_train, y_train, lambda_reg=lam)
        y_pred_prob = predict_prob(X_test, w, b)
        brier = brier_score(y_test, y_pred_prob)
        brier_scores_by_lambda[lam].append(brier)

# Calculate mean Brier scores
mean_brier = {lam: np.mean(brier_scores_by_lambda[lam]) for lam in lambdas}
print("Mean Brier scores:")
for lam in lambdas:
    print(f"  lambda={lam}: {mean_brier[lam]:.6f}")

best_lambda = min(lambdas, key=lambda x: mean_brier[x])
baseline_brier = mean_brier[0.0]
best_brier = mean_brier[best_lambda]
improvement = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda}")
print(f"Baseline Brier (lambda=0): {baseline_brier:.6f}")
print(f"Best Brier (lambda={best_lambda}): {best_brier:.6f}")
print(f"Improvement: {improvement:.6f}")

# Task 2: Test interaction terms
print("\n=== Task 2: Interaction terms analysis ===")

# Create interaction features
X_interaction = X.copy()
X_interaction = np.column_stack([
    X_interaction,
    X[:, 0] * X[:, 1],  # x0*x1
    X[:, 1] * X[:, 2],  # x1*x2
    X[:, 2] * X[:, 3],  # x2*x3
    X[:, 0] * X[:, 3],  # x0*x3
])

print(f"Raw features: {X.shape}")
print(f"Interaction features: {X_interaction.shape}")

# Fit both models on folds with lambda=0.1
raw_brier_scores = []
interaction_brier_scores = []

for fold_idx, (train_idx, test_idx) in enumerate(folds):
    # Raw features
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    w_raw, b_raw = logistic_fit(X_train, y_train, lambda_reg=0.1)
    y_pred_raw = predict_prob(X_test, w_raw, b_raw)
    brier_raw = brier_score(y_test, y_pred_raw)
    raw_brier_scores.append(brier_raw)
    
    # Interaction features
    X_train_int, X_test_int = X_interaction[train_idx], X_interaction[test_idx]
    w_int, b_int = logistic_fit(X_train_int, y_train, lambda_reg=0.1)
    y_pred_int = predict_prob(X_test_int, w_int, b_int)
    brier_int = brier_score(y_test, y_pred_int)
    interaction_brier_scores.append(brier_int)

# Paired t-test
raw_brier_scores = np.array(raw_brier_scores)
interaction_brier_scores = np.array(interaction_brier_scores)

print(f"Raw Brier scores: {raw_brier_scores}")
print(f"Interaction Brier scores: {interaction_brier_scores}")

# Paired t-test: testing if raw - interaction is significantly different from 0
differences = raw_brier_scores - interaction_brier_scores
t_stat, p_value = stats.ttest_rel(raw_brier_scores, interaction_brier_scores)

print(f"Differences (raw - interaction): {differences}")
print(f"Mean difference: {np.mean(differences):.6f}")
print(f"Paired t-statistic: {t_stat:.6f}")
print(f"P-value: {p_value:.6f}")

# Check if t > 2.0 (one-tailed would be different, but using absolute value for |t| > 2.0)
interaction_helps = abs(t_stat) > 2.0
print(f"Interaction helps (|t| > 2.0): {interaction_helps}")

# Task 3: Compression evaluation
print("\n=== Task 3: Compression evaluation ===")

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = logistic_fit(X, y, lambda_reg=0.1)
y_pred_dense = predict_prob(X, w_dense, b_dense)
dense_brier = brier_score(y, y_pred_dense)

print(f"Dense model Brier score: {dense_brier:.6f}")

# Test different configurations
sparsity_levels = [20, 40, 60]  # percentages
bit_levels = [8, 4]

best_config = None
best_retention = 0

results = []

for sparsity in sparsity_levels:
    for bits in bit_levels:
        # Apply sparsity
        w_sparse = w_dense.copy()
        k = round(sparsity / 100.0 * len(w_dense))
        
        # Zero out k smallest magnitude weights
        if k > 0:
            threshold_idx = np.argsort(np.abs(w_sparse))[:-k] if k < len(w_sparse) else np.argsort(np.abs(w_sparse))
            w_sparse[threshold_idx] = 0
        
        # Apply quantization to non-zero weights
        w_quant = w_sparse.copy()
        nonzero_mask = w_sparse != 0
        
        if np.sum(nonzero_mask) > 0:
            w_min = np.min(w_sparse[nonzero_mask])
            w_max = np.max(w_sparse[nonzero_mask])
            
            if w_min < w_max:
                # Map to 2^bits levels
                n_levels = 2 ** bits
                w_quant[nonzero_mask] = np.round((w_sparse[nonzero_mask] - w_min) / (w_max - w_min) * (n_levels - 1)) / (n_levels - 1) * (w_max - w_min) + w_min
        
        # Evaluate compressed model
        y_pred_compressed = predict_prob(X, w_quant, b_dense)
        compressed_brier = brier_score(y, y_pred_compressed)
        
        # Retention = dense Brier / compressed Brier
        retention = dense_brier / compressed_brier if compressed_brier > 0 else 0
        
        config_name = f"sparsity{sparsity}_bits{bits}"
        results.append({
            'config': config_name,
            'sparsity': sparsity,
            'bits': bits,
            'dense_brier': dense_brier,
            'compressed_brier': compressed_brier,
            'retention': retention
        })
        
        print(f"{config_name}: dense={dense_brier:.6f}, compressed={compressed_brier:.6f}, retention={retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = config_name

print(f"\nBest config: {best_config} (retention: {best_retention:.6f})")

# Prepare output
output = {
    "best_lambda": best_lambda,
    "improvement_over_baseline": improvement,
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

print("\n=== Final Answers ===")
print(json.dumps(output, indent=2))

# Write to answers.json
with open('answers.json', 'w') as f:
    json.dump(output, f, indent=2)

print("\nAnswers written to answers.json")
