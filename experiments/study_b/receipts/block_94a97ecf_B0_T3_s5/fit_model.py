import json
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'])
y = np.array(data['y'])

n_samples = len(X)
n_features = X.shape[1]

print(f"Data shape: {n_samples} samples, {n_features} features")

# Helper functions
def sigmoid(z):
    z = np.clip(z, -30, 30)
    return 1 / (1 + np.exp(-z))

def brier_score(y_true, y_pred_prob):
    """Calculate Brier score"""
    return np.mean((y_pred_prob - y_true) ** 2)

def fit_logistic_regression(X_train, y_train, lambda_reg=0.0, num_iterations=200, learning_rate=0.1):
    """
    Fit logistic regression with full-batch gradient descent
    w -= 0.1 * (grad_w / n + lambda * w)
    b -= 0.1 * (grad_b / n)
    """
    n = len(X_train)
    d = X_train.shape[1]
    
    w = np.zeros(d)
    b = 0.0
    
    for iteration in range(num_iterations):
        # Compute logits
        z = X_train @ w + b
        z = np.clip(z, -30, 30)
        
        # Compute predictions
        pred = sigmoid(z)
        
        # Compute gradients
        error = pred - y_train
        grad_w = X_train.T @ error / n
        grad_b = np.sum(error) / n
        
        # Update weights and bias
        w = w - learning_rate * (grad_w + lambda_reg * w)
        b = b - learning_rate * grad_b
    
    return w, b

def predict_proba(X_test, w, b):
    """Predict probability"""
    z = X_test @ w + b
    z = np.clip(z, -30, 30)
    return sigmoid(z)

# Create 5-fold CV splits (contiguous blocks)
n_folds = 5
fold_size = n_samples // n_folds
folds = []
for k in range(n_folds):
    start_idx = k * fold_size
    end_idx = (k + 1) * fold_size if k < n_folds - 1 else n_samples
    folds.append((start_idx, end_idx))

print(f"Fold sizes: {[f[1] - f[0] for f in folds]}")

# Question 1: Find best lambda
lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
cv_scores = {lam: [] for lam in lambdas}

for k, (test_start, test_end) in enumerate(folds):
    test_idx = slice(test_start, test_end)
    train_idx = np.concatenate([np.arange(0, test_start), np.arange(test_end, n_samples)])
    
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    for lam in lambdas:
        w, b = fit_logistic_regression(X_train, y_train, lambda_reg=lam)
        y_pred_prob = predict_proba(X_test, w, b)
        score = brier_score(y_test, y_pred_prob)
        cv_scores[lam].append(score)

# Compute mean CV scores for each lambda
mean_cv_scores = {lam: np.mean(cv_scores[lam]) for lam in lambdas}
print("\nMean CV Brier scores:")
for lam in lambdas:
    print(f"  lambda={lam}: {mean_cv_scores[lam]:.6f}")

best_lambda = min(lambdas, key=lambda x: mean_cv_scores[x])
baseline_score = mean_cv_scores[0.0]
best_score = mean_cv_scores[best_lambda]
improvement = baseline_score - best_score

print(f"\nBest lambda: {best_lambda}")
print(f"Baseline (lambda=0) score: {baseline_score:.6f}")
print(f"Best score: {best_score:.6f}")
print(f"Improvement: {improvement:.6f}")

# Question 2: Add interaction features and test
# Add products: x0*x1, x1*x2, x2*x3, x0*x3
X_with_interactions = np.column_stack([
    X,
    X[:, 0] * X[:, 1],  # x0*x1
    X[:, 1] * X[:, 2],  # x1*x2
    X[:, 2] * X[:, 3],  # x2*x3
    X[:, 0] * X[:, 3],  # x0*x3
])

print(f"\nX with interactions shape: {X_with_interactions.shape}")

# Run paired t-test across folds
lambda_for_interaction = 0.1
raw_briers = []
interaction_briers = []

for k, (test_start, test_end) in enumerate(folds):
    test_idx = slice(test_start, test_end)
    train_idx = np.concatenate([np.arange(0, test_start), np.arange(test_end, n_samples)])
    
    # Raw model
    X_train_raw = X[train_idx]
    X_test_raw = X[test_idx]
    w_raw, b_raw = fit_logistic_regression(X_train_raw, y[train_idx], lambda_reg=lambda_for_interaction)
    y_pred_raw = predict_proba(X_test_raw, w_raw, b_raw)
    brier_raw = brier_score(y[test_idx], y_pred_raw)
    raw_briers.append(brier_raw)
    
    # Interaction model
    X_train_int = X_with_interactions[train_idx]
    X_test_int = X_with_interactions[test_idx]
    w_int, b_int = fit_logistic_regression(X_train_int, y[train_idx], lambda_reg=lambda_for_interaction)
    y_pred_int = predict_proba(X_test_int, w_int, b_int)
    brier_int = brier_score(y[test_idx], y_pred_int)
    interaction_briers.append(brier_int)

print(f"\nPer-fold Brier scores (raw vs interaction):")
for k in range(n_folds):
    print(f"  Fold {k}: raw={raw_briers[k]:.6f}, interaction={interaction_briers[k]:.6f}")

# Paired t-test: test raw - interaction (positive means raw is worse, interaction is better)
differences = np.array(raw_briers) - np.array(interaction_briers)
print(f"\nDifferences (raw - interaction): {differences}")
print(f"Mean difference: {np.mean(differences):.6f}")

t_stat, p_value = stats.ttest_rel(raw_briers, interaction_briers)
print(f"Paired t-test: t={t_stat:.6f}, p-value={p_value:.6f}")

# interaction_helps is true only if t > 2.0
interaction_helps = t_stat > 2.0
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# Question 3: Find best compression configuration
# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic_regression(X, y, lambda_reg=0.1)
y_pred_dense = predict_proba(X, w_dense, b_dense)
brier_dense = brier_score(y, y_pred_dense)

print(f"\nDense model Brier score: {brier_dense:.6f}")

def apply_sparsity(w, sparsity_percent):
    """Zero out the smallest magnitude weights"""
    w_sparse = w.copy()
    k = round(sparsity_percent / 100.0 * len(w))
    if k > 0:
        indices = np.argsort(np.abs(w_sparse))[:k]
        w_sparse[indices] = 0
    return w_sparse

def quantize_weights(w, bits):
    """Quantize weights to 2^bits levels between min and max"""
    w_quant = w.copy()
    nonzero_mask = w_quant != 0
    
    if np.sum(nonzero_mask) == 0:
        return w_quant
    
    w_nonzero = w_quant[nonzero_mask]
    w_min = np.min(w_nonzero)
    w_max = np.max(w_nonzero)
    
    if w_min == w_max:
        return w_quant
    
    # Map to levels
    n_levels = 2 ** bits
    levels = np.linspace(w_min, w_max, n_levels)
    
    # Quantize
    for i in np.where(nonzero_mask)[0]:
        closest_level = levels[np.argmin(np.abs(levels - w_quant[i]))]
        w_quant[i] = closest_level
    
    return w_quant

# Test all compression configurations
sparsities = [20, 40, 60]
bit_configs = [8, 4]
results = []

for sparsity in sparsities:
    for bits in bit_configs:
        # Apply sparsity
        w_sparse = apply_sparsity(w_dense, sparsity)
        
        # Apply quantization
        w_compressed = quantize_weights(w_sparse, bits)
        
        # Evaluate
        y_pred_compressed = predict_proba(X, w_compressed, b_dense)
        brier_compressed = brier_score(y, y_pred_compressed)
        
        retention = brier_dense / brier_compressed if brier_compressed > 0 else 0
        
        config_name = f"sparsity{sparsity}_bits{bits}"
        results.append({
            'config': config_name,
            'sparsity': sparsity,
            'bits': bits,
            'brier_compressed': brier_compressed,
            'retention': retention
        })
        
        print(f"{config_name}: brier={brier_compressed:.6f}, retention={retention:.6f}")

best_config_result = max(results, key=lambda x: x['retention'])
best_config = best_config_result['config']

print(f"\nBest compression config: {best_config} with retention={best_config_result['retention']:.6f}")

# Prepare final answers
answers = {
    'best_lambda': best_lambda,
    'improvement_over_baseline': float(improvement),
    'paired_t_stat': float(t_stat),
    'interaction_helps': bool(interaction_helps),
    'best_config': best_config
}

print("\n" + "="*50)
print("FINAL ANSWERS:")
print("="*50)
for key, val in answers.items():
    print(f"{key}: {val}")

# Save answers
with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("\nAnswers saved to answers.json")
