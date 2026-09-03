import json
import numpy as np
from scipy import stats

# Load data
with open('data.json') as f:
    data = json.load(f)

X = np.array(data['X'])
y = np.array(data['y'])

n_samples = X.shape[0]
n_features = X.shape[1]

print(f"Data loaded: {n_samples} samples, {n_features} features")

# Task 1: Find best lambda and improvement over baseline
def sigmoid(z):
    """Sigmoid function with clipping"""
    z = np.clip(z, -30, 30)
    return 1 / (1 + np.exp(-z))

def brier_score(y_true, y_pred):
    """Compute Brier score"""
    return np.mean((y_pred - y_true) ** 2)

def fit_logistic_gd(X_train, y_train, lambda_reg=0.0, iterations=200, lr=0.1):
    """
    Fit logistic regression using full-batch gradient descent.
    w -= 0.1 * (grad_w / n + lambda * w); b -= 0.1 * (grad_b / n)
    """
    n = X_train.shape[0]
    d = X_train.shape[1]
    
    # Initialize weights and bias to 0
    w = np.zeros(d)
    b = 0.0
    
    for iteration in range(iterations):
        # Forward pass
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)
        y_pred = sigmoid(logits)
        
        # Compute gradients
        error = y_pred - y_train
        grad_w = X_train.T @ error
        grad_b = np.sum(error)
        
        # Update weights
        w -= lr * (grad_w / n + lambda_reg * w)
        b -= lr * (grad_b / n)
    
    return w, b

def predict_proba(X, w, b):
    """Compute probability predictions"""
    logits = X @ w + b
    logits = np.clip(logits, -30, 30)
    return sigmoid(logits)

# Create 5-fold CV splits (contiguous blocks, no shuffle)
fold_size = n_samples // 5
folds = []
for k in range(5):
    start_idx = k * fold_size
    if k == 4:  # Last fold takes remaining samples
        end_idx = n_samples
    else:
        end_idx = (k + 1) * fold_size
    
    test_idx = list(range(start_idx, end_idx))
    train_idx = list(range(0, start_idx)) + list(range(end_idx, n_samples))
    
    folds.append((train_idx, test_idx))

print(f"Fold sizes:")
for k, (train_idx, test_idx) in enumerate(folds):
    print(f"  Fold {k}: train={len(train_idx)}, test={len(test_idx)}")

# Test different lambdas
lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
cv_scores = {lam: [] for lam in lambdas}

for lam in lambdas:
    brier_scores_cv = []
    for fold_idx, (train_idx, test_idx) in enumerate(folds):
        X_train, y_train = X[train_idx], y[train_idx]
        X_test, y_test = X[test_idx], y[test_idx]
        
        # Fit model
        w, b = fit_logistic_gd(X_train, y_train, lambda_reg=lam, iterations=200, lr=0.1)
        
        # Predict
        y_pred = predict_proba(X_test, w, b)
        
        # Compute Brier score
        brier = brier_score(y_test, y_pred)
        brier_scores_cv.append(brier)
    
    mean_brier = np.mean(brier_scores_cv)
    cv_scores[lam] = (mean_brier, brier_scores_cv)
    print(f"Lambda={lam}: mean Brier={mean_brier:.6f}, fold scores={[f'{x:.6f}' for x in brier_scores_cv]}")

# Find best lambda
best_lambda = min(lambdas, key=lambda x: cv_scores[x][0])
best_brier = cv_scores[best_lambda][0]
baseline_brier = cv_scores[0.0][0]
improvement = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda}")
print(f"Best Brier: {best_brier:.6f}")
print(f"Baseline (lambda=0) Brier: {baseline_brier:.6f}")
print(f"Improvement: {improvement:.6f}")

# Task 2: Interaction features and paired t-test
print("\n" + "="*60)
print("Task 2: Interaction features")
print("="*60)

# Create interaction features
X_with_interactions = np.concatenate([
    X,
    (X[:, 0] * X[:, 1]).reshape(-1, 1),  # x0*x1
    (X[:, 1] * X[:, 2]).reshape(-1, 1),  # x1*x2
    (X[:, 2] * X[:, 3]).reshape(-1, 1),  # x2*x3
    (X[:, 0] * X[:, 3]).reshape(-1, 1),  # x0*x3
], axis=1)

print(f"Original features: {X.shape[1]}")
print(f"With interactions: {X_with_interactions.shape[1]}")

# Fit both models with lambda=0.1 on each fold
lambda_val = 0.1
brier_raw = []
brier_interaction = []

for fold_idx, (train_idx, test_idx) in enumerate(folds):
    # Raw model
    X_train, y_train = X[train_idx], y[train_idx]
    X_test, y_test = X[test_idx], y[test_idx]
    
    w_raw, b_raw = fit_logistic_gd(X_train, y_train, lambda_reg=lambda_val, iterations=200, lr=0.1)
    y_pred_raw = predict_proba(X_test, w_raw, b_raw)
    brier_raw.append(brier_score(y_test, y_pred_raw))
    
    # Interaction model
    X_train_int = X_with_interactions[train_idx]
    X_test_int = X_with_interactions[test_idx]
    
    w_int, b_int = fit_logistic_gd(X_train_int, y_train, lambda_reg=lambda_val, iterations=200, lr=0.1)
    y_pred_int = predict_proba(X_test_int, w_int, b_int)
    brier_interaction.append(brier_score(y_test, y_pred_int))
    
    print(f"Fold {fold_idx}: Raw Brier={brier_raw[-1]:.6f}, Interaction Brier={brier_interaction[-1]:.6f}")

brier_raw = np.array(brier_raw)
brier_interaction = np.array(brier_interaction)

# Paired t-test: raw minus interaction
diff = brier_raw - brier_interaction
t_stat, p_value = stats.ttest_rel(brier_raw, brier_interaction)

print(f"\nPaired t-test (raw vs interaction):")
print(f"  Diffs: {diff}")
print(f"  t-statistic: {t_stat:.6f}")
print(f"  p-value: {p_value:.6f}")
print(f"  t > 2.0: {t_stat > 2.0}")

# Task 3: Compression (sparsity and quantization)
print("\n" + "="*60)
print("Task 3: Compression")
print("="*60)

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic_gd(X, y, lambda_reg=0.1, iterations=200, lr=0.1)
y_pred_dense = predict_proba(X, w_dense, b_dense)
brier_dense = brier_score(y, y_pred_dense)
print(f"Dense model Brier: {brier_dense:.6f}")

# Test all compression configs
sparsities = [20, 40, 60]
bits_options = [4, 8]
results = {}

for sparsity_pct in sparsities:
    for bits in bits_options:
        # Apply sparsity
        w_sparse = w_dense.copy()
        k = round(sparsity_pct / 100.0 * len(w_sparse))
        
        # Zero out k smallest magnitude weights
        abs_w = np.abs(w_sparse)
        threshold = np.partition(abs_w, k-1)[k-1] if k > 0 else np.inf
        w_sparse[abs_w <= threshold] = 0
        
        # Count zeroed weights
        n_zeros = np.sum(w_sparse == 0)
        
        # Apply quantization to non-zero weights
        w_quant = w_sparse.copy()
        nonzero_mask = w_sparse != 0
        
        if np.sum(nonzero_mask) > 0:
            w_nz = w_sparse[nonzero_mask]
            w_min = np.min(w_nz)
            w_max = np.max(w_nz)
            
            if w_min == w_max:
                # All same value, quantize to middle level
                n_levels = 2 ** bits
                w_quant[nonzero_mask] = w_min
            else:
                # Map to 2^bits levels
                n_levels = 2 ** bits
                normalized = (w_nz - w_min) / (w_max - w_min)
                quantized = np.round(normalized * (n_levels - 1)) / (n_levels - 1)
                w_quant[nonzero_mask] = w_min + quantized * (w_max - w_min)
        
        # Predict with compressed model
        y_pred_comp = predict_proba(X, w_quant, b_dense)
        brier_comp = brier_score(y, y_pred_comp)
        
        # Retention = dense_brier / compressed_brier
        retention = brier_dense / brier_comp if brier_comp > 0 else np.inf
        
        config_name = f"sparsity{sparsity_pct}_bits{bits}"
        results[config_name] = {
            'retention': retention,
            'brier_comp': brier_comp,
            'sparsity': sparsity_pct,
            'bits': bits,
            'n_zeros': n_zeros
        }
        
        print(f"{config_name}: Brier={brier_comp:.6f}, Retention={retention:.6f}, n_zeros={n_zeros}")

# Find best config (highest retention)
best_config = max(results.keys(), key=lambda x: results[x]['retention'])
print(f"\nBest configuration: {best_config}")
print(f"  Retention: {results[best_config]['retention']:.6f}")

# Write answers
answers = {
    "best_lambda": float(best_lambda),
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(t_stat > 2.0),
    "best_config": str(best_config)
}

print("\n" + "="*60)
print("ANSWERS:")
print("="*60)
for key, val in answers.items():
    print(f"{key}: {val}")

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("\nAnswers written to answers.json")
