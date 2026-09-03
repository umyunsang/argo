import json
import numpy as np
from scipy import stats

# Load data
with open('data.json') as f:
    data = json.load(f)

X = np.array(data['X'])
y = np.array(data['y'], dtype=np.float32)

n_samples, n_features = X.shape
print(f"Data shape: {n_samples} samples, {n_features} features")

# Sigmoid function
def sigmoid(z):
    return 1 / (1 + np.exp(-np.clip(z, -30, 30)))

# Logistic regression fitting
def fit_logistic(X_train, y_train, lambda_reg=0.0, iterations=200, lr=0.1):
    """
    Fit logistic regression with full-batch gradient descent.
    """
    n, d = X_train.shape
    w = np.zeros(d)
    b = 0.0
    
    for _ in range(iterations):
        # Forward pass
        z = X_train @ w + b
        z = np.clip(z, -30, 30)
        pred = sigmoid(z)
        
        # Gradients
        error = pred - y_train
        grad_w = X_train.T @ error / n
        grad_b = np.mean(error)
        
        # Update
        w -= lr * (grad_w + lambda_reg * w)
        b -= lr * grad_b
    
    return w, b

# Brier score
def brier_score(y_true, y_pred_prob):
    return np.mean((y_pred_prob - y_true) ** 2)

# Prediction
def predict_proba(X, w, b):
    z = X @ w + b
    z = np.clip(z, -30, 30)
    return sigmoid(z)

# Create 5 contiguous folds
def get_folds(n_samples, n_folds=5):
    fold_size = n_samples // n_folds
    folds = []
    for i in range(n_folds):
        start = i * fold_size
        if i == n_folds - 1:
            end = n_samples
        else:
            end = (i + 1) * fold_size
        folds.append((start, end))
    return folds

folds = get_folds(n_samples, 5)

print("\n" + "="*80)
print("QUESTION 1: Best lambda and improvement")
print("="*80)

lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
results_q1 = {}

for lam in lambdas:
    fold_scores = []
    for fold_idx, (start, end) in enumerate(folds):
        # Create train/test split
        test_idx = np.arange(start, end)
        train_idx = np.concatenate([np.arange(0, start), np.arange(end, n_samples)])
        
        X_train = X[train_idx]
        y_train = y[train_idx]
        X_test = X[test_idx]
        y_test = y[test_idx]
        
        # Fit and evaluate
        w, b = fit_logistic(X_train, y_train, lambda_reg=lam)
        y_pred = predict_proba(X_test, w, b)
        score = brier_score(y_test, y_pred)
        fold_scores.append(score)
    
    mean_score = np.mean(fold_scores)
    results_q1[lam] = {
        'fold_scores': fold_scores,
        'mean_brier': mean_score
    }
    print(f"Lambda {lam:5.2f}: Mean Brier = {mean_score:.6f}, Folds = {[f'{s:.6f}' for s in fold_scores]}")

# Find best lambda
best_lambda = min(results_q1.keys(), key=lambda x: results_q1[x]['mean_brier'])
baseline_brier = results_q1[0.0]['mean_brier']
best_brier = results_q1[best_lambda]['mean_brier']
improvement = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda}")
print(f"Baseline Brier (lambda=0): {baseline_brier:.6f}")
print(f"Best Brier (lambda={best_lambda}): {best_brier:.6f}")
print(f"Improvement: {improvement:.6f}")

print("\n" + "="*80)
print("QUESTION 2: Interaction terms and paired t-test")
print("="*80)

# Add interaction features
def add_interactions(X):
    interactions = np.column_stack([
        X[:, 0] * X[:, 1],  # x0*x1
        X[:, 1] * X[:, 2],  # x1*x2
        X[:, 2] * X[:, 3],  # x2*x3
        X[:, 0] * X[:, 3]   # x0*x3
    ])
    return np.hstack([X, interactions])

X_with_interactions = add_interactions(X)

# Test with lambda=0.1
lambda_test = 0.1
raw_fold_scores = []
interaction_fold_scores = []

for fold_idx, (start, end) in enumerate(folds):
    test_idx = np.arange(start, end)
    train_idx = np.concatenate([np.arange(0, start), np.arange(end, n_samples)])
    
    # Raw model
    X_train = X[train_idx]
    y_train = y[train_idx]
    X_test = X[test_idx]
    y_test = y[test_idx]
    
    w_raw, b_raw = fit_logistic(X_train, y_train, lambda_reg=lambda_test)
    y_pred_raw = predict_proba(X_test, w_raw, b_raw)
    score_raw = brier_score(y_test, y_pred_raw)
    raw_fold_scores.append(score_raw)
    
    # Interaction model
    X_train_int = add_interactions(X_train)
    X_test_int = add_interactions(X_test)
    
    w_int, b_int = fit_logistic(X_train_int, y_train, lambda_reg=lambda_test)
    y_pred_int = predict_proba(X_test_int, w_int, b_int)
    score_int = brier_score(y_test, y_pred_int)
    interaction_fold_scores.append(score_int)

print(f"Raw model Brier scores (folds): {[f'{s:.6f}' for s in raw_fold_scores]}")
print(f"Interaction model Brier scores (folds): {[f'{s:.6f}' for s in interaction_fold_scores]}")

# Paired t-test: raw - interaction (positive t means raw is better)
differences = np.array(raw_fold_scores) - np.array(interaction_fold_scores)
print(f"Differences (raw - interaction): {[f'{d:.6f}' for d in differences]}")

# t-test
t_stat, p_value = stats.ttest_rel(raw_fold_scores, interaction_fold_scores)
print(f"Paired t-test: t = {t_stat:.6f}, p-value = {p_value:.6f}")

interaction_helps = t_stat > 2.0
print(f"Interaction helps (t > 2.0): {interaction_helps}")

print("\n" + "="*80)
print("QUESTION 3: Model compression")
print("="*80)

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic(X, y, lambda_reg=0.1)
y_pred_dense = predict_proba(X, w_dense, b_dense)
brier_dense = brier_score(y, y_pred_dense)
print(f"Dense model Brier: {brier_dense:.6f}")

# Test different compression configurations
sparsities = [20, 40, 60]  # percentage
bits_list = [8, 4]

best_retention = 0
best_config = None

for sparsity_pct in sparsities:
    for bits in bits_list:
        # Apply sparsity
        w_sparse = w_dense.copy()
        n_weights = len(w_sparse)
        k = round(sparsity_pct / 100.0 * n_weights)
        
        # Zero out smallest magnitude weights
        threshold_idx = np.argsort(np.abs(w_sparse))[:(k)]
        w_sparse[threshold_idx] = 0
        
        # Apply quantization to non-zero weights
        non_zero_mask = w_sparse != 0
        if np.sum(non_zero_mask) > 0:
            w_nonzero = w_sparse[non_zero_mask]
            w_min = np.min(w_nonzero)
            w_max = np.max(w_nonzero)
            
            if w_max > w_min:
                # Map to 2^bits levels
                levels = np.linspace(w_min, w_max, 2**bits)
                w_quantized = np.zeros_like(w_sparse)
                for i in np.where(non_zero_mask)[0]:
                    nearest_level = levels[np.argmin(np.abs(levels - w_sparse[i]))]
                    w_quantized[i] = nearest_level
                w_sparse = w_quantized
        
        # Evaluate compressed model
        y_pred_compressed = predict_proba(X, w_sparse, b_dense)
        brier_compressed = brier_score(y, y_pred_compressed)
        
        # Retention = dense / compressed
        retention = brier_dense / brier_compressed if brier_compressed > 0 else 0
        
        config_name = f"sparsity{sparsity_pct}_bits{bits}"
        print(f"{config_name}: Brier = {brier_compressed:.6f}, Retention = {retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = config_name

print(f"\nBest config: {best_config} with retention {best_retention:.6f}")

print("\n" + "="*80)
print("FINAL ANSWERS")
print("="*80)

results = {
    "best_lambda": best_lambda,
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

print(json.dumps(results, indent=2))

# Save to file
with open('answers.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nAnswers saved to answers.json")
