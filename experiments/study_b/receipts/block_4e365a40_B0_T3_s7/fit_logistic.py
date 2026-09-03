import json
import numpy as np
from scipy import stats

# Load data
with open('data.json') as f:
    data = json.load(f)

X = np.array(data['X'], dtype=np.float64)
y = np.array(data['y'], dtype=np.float64)

n_samples, n_features = X.shape
print(f"Data shape: {n_samples} x {n_features}")

# Create 5 contiguous folds (no shuffle)
n_folds = 5
fold_size = n_samples // n_folds
folds = []
for k in range(n_folds):
    test_indices = list(range(k, n_samples, n_folds))
    train_indices = [i for i in range(n_samples) if i not in test_indices]
    folds.append((train_indices, test_indices))

print(f"Fold sizes: {[len(f[1]) for f in folds]}")

def sigmoid(z):
    """Sigmoid with clipping to prevent overflow"""
    z = np.clip(z, -30, 30)
    return 1 / (1 + np.exp(-z))

def brier_score(y_true, y_pred):
    """Brier score: mean squared error of probabilities"""
    return np.mean((y_pred - y_true) ** 2)

def fit_logistic(X_train, y_train, lambda_reg=0.0, n_iter=200, lr=0.1):
    """
    Fit logistic regression with full-batch gradient descent
    """
    n_samples, n_features = X_train.shape
    
    # Initialize weights and bias
    w = np.zeros(n_features)
    b = 0.0
    
    for iteration in range(n_iter):
        # Forward pass
        z = X_train @ w + b
        z = np.clip(z, -30, 30)
        y_pred = sigmoid(z)
        
        # Backward pass
        error = y_pred - y_train
        grad_w = (X_train.T @ error) / n_samples
        grad_b = np.mean(error)
        
        # Update
        w -= lr * (grad_w + lambda_reg * w)
        b -= lr * grad_b
    
    return w, b

def predict_proba(X_test, w, b):
    """Predict probabilities"""
    z = X_test @ w + b
    z = np.clip(z, -30, 30)
    return sigmoid(z)

# Task 1: Find best lambda via cross-validation
lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
cv_scores = {lam: [] for lam in lambdas}

for lam in lambdas:
    for train_idx, test_idx in folds:
        X_train = X[train_idx]
        y_train = y[train_idx]
        X_test = X[test_idx]
        y_test = y[test_idx]
        
        w, b = fit_logistic(X_train, y_train, lambda_reg=lam)
        y_pred = predict_proba(X_test, w, b)
        score = brier_score(y_test, y_pred)
        cv_scores[lam].append(score)

# Average CV scores
mean_cv_scores = {lam: np.mean(cv_scores[lam]) for lam in lambdas}
print("\nCV Scores by lambda:")
for lam, score in mean_cv_scores.items():
    print(f"  lambda={lam}: {score:.6f}")

best_lambda = min(lambdas, key=lambda l: mean_cv_scores[l])
baseline_score = mean_cv_scores[0.0]
best_score = mean_cv_scores[best_lambda]
improvement = baseline_score - best_score

print(f"\nBest lambda: {best_lambda}")
print(f"Baseline (lambda=0): {baseline_score:.6f}")
print(f"Best score: {best_score:.6f}")
print(f"Improvement: {improvement:.6f}")

# Task 2: Test interaction features
print("\n--- Task 2: Interaction Features ---")

# Create interaction features: x0*x1, x1*x2, x2*x3, x0*x3
X_interactions = np.column_stack([
    X[:, 0] * X[:, 1],  # x0*x1
    X[:, 1] * X[:, 2],  # x1*x2
    X[:, 2] * X[:, 3],  # x2*x3
    X[:, 0] * X[:, 3]   # x0*x3
])

X_with_interactions = np.hstack([X, X_interactions])
n_features_with_interactions = X_with_interactions.shape[1]

# Fit both models with lambda=0.1 and collect Brier scores per fold
brier_raw = []
brier_interaction = []

for train_idx, test_idx in folds:
    # Raw model
    X_train = X[train_idx]
    y_train = y[train_idx]
    X_test = X[test_idx]
    y_test = y[test_idx]
    
    w, b = fit_logistic(X_train, y_train, lambda_reg=0.1)
    y_pred = predict_proba(X_test, w, b)
    score_raw = brier_score(y_test, y_pred)
    brier_raw.append(score_raw)
    
    # Interaction model
    X_train_int = X_with_interactions[train_idx]
    X_test_int = X_with_interactions[test_idx]
    
    w_int, b_int = fit_logistic(X_train_int, y_train, lambda_reg=0.1)
    y_pred_int = predict_proba(X_test_int, w_int, b_int)
    score_int = brier_score(y_test, y_pred_int)
    brier_interaction.append(score_int)

brier_raw = np.array(brier_raw)
brier_interaction = np.array(brier_interaction)

# Paired t-test: raw minus interaction
diff = brier_raw - brier_interaction
t_stat, p_value = stats.ttest_rel(brier_raw, brier_interaction)

print(f"Brier scores (raw): {brier_raw}")
print(f"Brier scores (interaction): {brier_interaction}")
print(f"Difference (raw - interaction): {diff}")
print(f"Paired t-statistic: {t_stat:.6f}")
print(f"P-value: {p_value:.6f}")

interaction_helps = t_stat > 2.0
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# Task 3: Compression
print("\n--- Task 3: Compression ---")

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic(X, y, lambda_reg=0.1)
y_pred_dense = predict_proba(X, w_dense, b_dense)
brier_dense = brier_score(y, y_pred_dense)

print(f"Dense model in-sample Brier: {brier_dense:.6f}")

sparsity_levels = [20, 40, 60]
bit_levels = [8, 4]
results = {}

for sparsity in sparsity_levels:
    for bits in bit_levels:
        # Apply sparsity: zero out smallest magnitude weights
        w_sparse = w_dense.copy()
        k = round(sparsity / 100.0 * len(w_dense))
        if k > 0:
            indices_to_zero = np.argsort(np.abs(w_sparse))[:k]
            w_sparse[indices_to_zero] = 0
        
        # Apply quantization
        w_quant = w_sparse.copy()
        nonzero_mask = w_quant != 0
        if np.any(nonzero_mask):
            min_val = np.min(w_quant[nonzero_mask])
            max_val = np.max(w_quant[nonzero_mask])
            
            if min_val < max_val:
                # Map to 2^bits levels
                levels = np.linspace(min_val, max_val, 2**bits)
                for i in np.where(nonzero_mask)[0]:
                    closest_idx = np.argmin(np.abs(levels - w_quant[i]))
                    w_quant[i] = levels[closest_idx]
        
        # Evaluate compressed model
        y_pred_comp = predict_proba(X, w_quant, b_dense)
        brier_comp = brier_score(y, y_pred_comp)
        
        retention = brier_dense / brier_comp if brier_comp > 0 else 0
        config_name = f"sparsity{sparsity}_bits{bits}"
        results[config_name] = retention
        
        print(f"{config_name}: Brier={brier_comp:.6f}, Retention={retention:.6f}")

best_config = max(results, key=results.get)
print(f"\nBest config: {best_config} (retention: {results[best_config]:.6f})")

# Output answers
answers = {
    "best_lambda": float(best_lambda),
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

print("\n=== ANSWERS ===")
print(json.dumps(answers, indent=2))

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)
