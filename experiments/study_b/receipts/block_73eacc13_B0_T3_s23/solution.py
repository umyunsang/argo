import json
import numpy as np
from scipy import stats

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'])
y = np.array(data['y'], dtype=np.float32)

n_samples = X.shape[0]
n_features = X.shape[1]

print(f"Data loaded: {n_samples} samples, {n_features} features")

# Define logistic function and Brier score
def sigmoid(z):
    return 1 / (1 + np.exp(-np.clip(z, -30, 30)))

def brier_score(y_true, y_pred_proba):
    return np.mean((y_true - y_pred_proba) ** 2)

# Create 5 contiguous folds (no shuffle)
def create_folds(n, n_folds=5):
    folds = []
    fold_size = n // n_folds
    for i in range(n_folds):
        start = i * fold_size
        end = (i + 1) * fold_size if i < n_folds - 1 else n
        folds.append((start, end))
    return folds

# Fit logistic regression with gradient descent
def fit_logistic(X_train, y_train, lambda_param=0.0, n_iter=200, lr=0.1):
    n = X_train.shape[0]
    d = X_train.shape[1]
    
    # Initialize weights and bias at 0
    w = np.zeros(d)
    b = 0.0
    
    for iteration in range(n_iter):
        # Compute logits
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)
        
        # Compute predictions
        y_pred = sigmoid(logits)
        
        # Compute gradients
        error = y_pred - y_train
        grad_w = X_train.T @ error / n
        grad_b = np.mean(error)
        
        # Update weights and bias
        w = w - lr * (grad_w + lambda_param * w)
        b = b - lr * grad_b
    
    return w, b

# Predict on new data
def predict(X_test, w, b):
    logits = X_test @ w + b
    logits = np.clip(logits, -30, 30)
    return sigmoid(logits)

# Task 1: Find best lambda
print("\n" + "="*60)
print("TASK 1: Best Lambda")
print("="*60)

lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
folds = create_folds(n_samples)

brier_scores_per_lambda = {}

for lambda_param in lambdas:
    fold_scores = []
    
    for fold_idx, (start, end) in enumerate(folds):
        # Create train/test split
        test_idx = np.arange(start, end)
        train_idx = np.concatenate([np.arange(0, start), np.arange(end, n_samples)])
        
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Fit model
        w, b = fit_logistic(X_train, y_train, lambda_param=lambda_param)
        
        # Evaluate
        y_pred = predict(X_test, w, b)
        score = brier_score(y_test, y_pred)
        fold_scores.append(score)
    
    mean_score = np.mean(fold_scores)
    brier_scores_per_lambda[lambda_param] = (mean_score, fold_scores)
    print(f"Lambda {lambda_param:5.2f}: mean Brier = {mean_score:.6f}, per-fold = {fold_scores}")

# Find best lambda
best_lambda = min(brier_scores_per_lambda, key=lambda k: brier_scores_per_lambda[k][0])
best_brier = brier_scores_per_lambda[best_lambda][0]
baseline_brier = brier_scores_per_lambda[0.0][0]
improvement = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda}")
print(f"Best Brier score: {best_brier:.6f}")
print(f"Baseline (lambda=0) Brier score: {baseline_brier:.6f}")
print(f"Improvement: {improvement:.6f}")

# Task 2: Test interaction terms
print("\n" + "="*60)
print("TASK 2: Interaction Terms")
print("="*60)

# Add interaction features
X_with_interactions = np.column_stack([
    X,
    X[:, 0] * X[:, 1],  # x0*x1
    X[:, 1] * X[:, 2],  # x1*x2
    X[:, 2] * X[:, 3],  # x2*x3
    X[:, 0] * X[:, 3]   # x0*x3
])

print(f"Original features: {X.shape[1]}")
print(f"Features with interactions: {X_with_interactions.shape[1]}")

# Compare models with lambda=0.1
lambda_comp = 0.1

raw_brier_scores = []
interaction_brier_scores = []

for fold_idx, (start, end) in enumerate(folds):
    # Create train/test split
    test_idx = np.arange(start, end)
    train_idx = np.concatenate([np.arange(0, start), np.arange(end, n_samples)])
    
    # Raw model
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    w_raw, b_raw = fit_logistic(X_train, y_train, lambda_param=lambda_comp)
    y_pred_raw = predict(X_test, w_raw, b_raw)
    score_raw = brier_score(y_test, y_pred_raw)
    raw_brier_scores.append(score_raw)
    
    # Interaction model
    X_train_int = X_with_interactions[train_idx]
    X_test_int = X_with_interactions[test_idx]
    
    w_int, b_int = fit_logistic(X_train_int, y_train, lambda_param=lambda_comp)
    y_pred_int = predict(X_test_int, w_int, b_int)
    score_int = brier_score(y_test, y_pred_int)
    interaction_brier_scores.append(score_int)
    
    print(f"Fold {fold_idx}: Raw={score_raw:.6f}, Interaction={score_int:.6f}, Diff={score_raw - score_int:.6f}")

# Paired t-test: raw - interaction
differences = np.array(raw_brier_scores) - np.array(interaction_brier_scores)
t_stat, p_val = stats.ttest_1samp(differences, 0)

print(f"\nPaired t-test results:")
print(f"Raw Brier scores: {raw_brier_scores}")
print(f"Interaction Brier scores: {interaction_brier_scores}")
print(f"Differences (raw - interaction): {differences}")
print(f"t-statistic: {t_stat:.6f}")
print(f"p-value: {p_val:.6f}")

interaction_helps = t_stat > 2.0
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# Task 3: Compression configurations
print("\n" + "="*60)
print("TASK 3: Best Compression Configuration")
print("="*60)

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic(X, y, lambda_param=0.1)
y_pred_dense = predict(X, w_dense, b_dense)
brier_dense = brier_score(y, y_pred_dense)
print(f"Dense model Brier score (in-sample): {brier_dense:.6f}")

sparsities = [20, 40, 60]
bits_list = [8, 4]

def apply_sparsity(w, sparsity_percent):
    """Zero out the smallest magnitude weights"""
    num_zeros = int(np.round(sparsity_percent / 100.0 * len(w)))
    abs_w = np.abs(w)
    threshold = np.partition(abs_w, min(num_zeros, len(w) - 1))[min(num_zeros, len(w) - 1)]
    w_sparse = w.copy()
    w_sparse[abs_w <= threshold] = 0
    return w_sparse

def apply_quantization(w, bits):
    """Quantize weights uniformly to 2^bits levels"""
    w_quant = w.copy()
    nonzero_mask = w != 0
    if np.any(nonzero_mask):
        w_nonzero = w[nonzero_mask]
        w_min = np.min(w_nonzero)
        w_max = np.max(w_nonzero)
        
        if w_min == w_max:
            # All nonzero weights are the same
            return w_quant
        
        # Quantize
        num_levels = 2 ** bits
        quantized = np.round((w_nonzero - w_min) / (w_max - w_min) * (num_levels - 1))
        w_quant[nonzero_mask] = w_min + quantized / (num_levels - 1) * (w_max - w_min)
    
    return w_quant

configs = []

for sparsity in sparsities:
    for bits in bits_list:
        # Apply sparsity first, then quantization
        w_sparse = apply_sparsity(w_dense, sparsity)
        w_compressed = apply_quantization(w_sparse, bits)
        
        # Evaluate compressed model
        y_pred_compressed = predict(X, w_compressed, b_dense)
        brier_compressed = brier_score(y, y_pred_compressed)
        
        # Retention = dense_brier / compressed_brier
        retention = brier_dense / brier_compressed if brier_compressed > 0 else 0
        
        config_name = f"sparsity{sparsity}_bits{bits}"
        configs.append({
            'config': config_name,
            'sparsity': sparsity,
            'bits': bits,
            'brier_dense': brier_dense,
            'brier_compressed': brier_compressed,
            'retention': retention
        })
        
        print(f"{config_name}: dense_brier={brier_dense:.6f}, compressed_brier={brier_compressed:.6f}, retention={retention:.6f}")

# Find best config (highest retention)
best_config = max(configs, key=lambda x: x['retention'])
print(f"\nBest configuration: {best_config['config']} with retention {best_config['retention']:.6f}")

# Save results
results = {
    'best_lambda': float(best_lambda),
    'improvement_over_baseline': float(improvement),
    'paired_t_stat': float(t_stat),
    'interaction_helps': bool(interaction_helps),
    'best_config': best_config['config']
}

print("\n" + "="*60)
print("FINAL RESULTS")
print("="*60)
print(json.dumps(results, indent=2))

with open('answers.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to answers.json")
