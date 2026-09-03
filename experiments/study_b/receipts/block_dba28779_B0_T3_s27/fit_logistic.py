import numpy as np
import json
from scipy import stats

# Load data
with open('data.json') as f:
    data = json.load(f)

X = np.array(data['X'])
y = np.array(data['y'])

n_samples, n_features = X.shape
n_folds = 5
fold_size = n_samples // n_folds

print(f"Data shape: {X.shape}, labels shape: {y.shape}")
print(f"n_samples={n_samples}, n_features={n_features}")

def create_folds(n_samples, n_folds):
    """Create contiguous folds without shuffling."""
    fold_size = n_samples // n_folds
    folds = []
    for k in range(n_folds):
        start_idx = k * fold_size
        end_idx = (k + 1) * fold_size
        train_idx = list(range(0, start_idx)) + list(range(end_idx, n_samples))
        test_idx = list(range(start_idx, end_idx))
        folds.append((train_idx, test_idx))
    return folds

def sigmoid(z):
    """Sigmoid function with clipping for numerical stability."""
    z = np.clip(z, -30, 30)
    return 1 / (1 + np.exp(-z))

def logistic_loss(y_true, y_pred_proba):
    """Binary cross-entropy loss."""
    eps = 1e-15
    y_pred_proba = np.clip(y_pred_proba, eps, 1 - eps)
    return -np.mean(y_true * np.log(y_pred_proba) + (1 - y_true) * np.log(1 - y_pred_proba))

def brier_score(y_true, y_pred_proba):
    """Brier score: mean squared error between predicted probabilities and actual labels."""
    return np.mean((y_pred_proba - y_true) ** 2)

def fit_logistic_model(X_train, y_train, lambda_reg=0.0, n_iter=200, lr=0.1):
    """
    Fit logistic regression with full-batch gradient descent.
    
    w -= 0.1 * (grad_w / n + lambda * w)
    b -= 0.1 * (grad_b / n)
    """
    n_train = X_train.shape[0]
    n_feat = X_train.shape[1]
    
    w = np.zeros(n_feat)
    b = 0.0
    
    for iteration in range(n_iter):
        # Forward pass
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)
        y_pred = sigmoid(logits)
        
        # Gradients
        error = y_pred - y_train
        grad_w = X_train.T @ error / n_train
        grad_b = np.sum(error) / n_train
        
        # Update with regularization
        w -= lr * (grad_w + lambda_reg * w)
        b -= lr * grad_b
    
    return w, b

def predict(X, w, b):
    """Predict probabilities."""
    logits = X @ w + b
    logits = np.clip(logits, -30, 30)
    return sigmoid(logits)

# Task 1: Find best lambda with 5-fold CV
print("\n=== Task 1: Lambda Selection ===")
lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
folds = create_folds(n_samples, n_folds)

lambda_scores = {}
for lambda_val in lambdas:
    fold_brier_scores = []
    for train_idx, test_idx in folds:
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        w, b = fit_logistic_model(X_train, y_train, lambda_reg=lambda_val)
        y_pred = predict(X_test, w, b)
        brier = brier_score(y_test, y_pred)
        fold_brier_scores.append(brier)
    
    avg_brier = np.mean(fold_brier_scores)
    lambda_scores[lambda_val] = avg_brier
    print(f"Lambda {lambda_val}: Brier = {avg_brier:.6f}")

best_lambda = min(lambda_scores, key=lambda_scores.get)
baseline_brier = lambda_scores[0.0]  # lambda=0
best_brier = lambda_scores[best_lambda]
improvement = baseline_brier - best_brier

print(f"\nBest lambda: {best_lambda}")
print(f"Baseline Brier (lambda=0): {baseline_brier:.6f}")
print(f"Best Brier: {best_brier:.6f}")
print(f"Improvement: {improvement:.6f}")

# Task 2: Interaction features
print("\n=== Task 2: Interaction Features ===")

# Add interaction features: x0*x1, x1*x2, x2*x3, x0*x3
X_interaction = X.copy()
interaction_cols = [
    X[:, 0] * X[:, 1],  # x0*x1
    X[:, 1] * X[:, 2],  # x1*x2
    X[:, 2] * X[:, 3],  # x2*x3
    X[:, 0] * X[:, 3],  # x0*x3
]
X_interaction = np.column_stack([X_interaction] + interaction_cols)

print(f"Original X shape: {X.shape}")
print(f"X with interactions shape: {X_interaction.shape}")

# Fit both representations with lambda=0.1 on all folds
lambda_interaction = 0.1
raw_brier_scores = []
interaction_brier_scores = []

for train_idx, test_idx in folds:
    # Raw features
    X_train_raw, X_test_raw = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    w_raw, b_raw = fit_logistic_model(X_train_raw, y_train, lambda_reg=lambda_interaction)
    y_pred_raw = predict(X_test_raw, w_raw, b_raw)
    brier_raw = brier_score(y_test, y_pred_raw)
    raw_brier_scores.append(brier_raw)
    
    # Interaction features
    X_train_inter, X_test_inter = X_interaction[train_idx], X_interaction[test_idx]
    w_inter, b_inter = fit_logistic_model(X_train_inter, y_train, lambda_reg=lambda_interaction)
    y_pred_inter = predict(X_test_inter, w_inter, b_inter)
    brier_inter = brier_score(y_test, y_pred_inter)
    interaction_brier_scores.append(brier_inter)

raw_brier_scores = np.array(raw_brier_scores)
interaction_brier_scores = np.array(interaction_brier_scores)

# Paired t-test: raw minus interaction
differences = raw_brier_scores - interaction_brier_scores
t_stat, p_value = stats.ttest_rel(raw_brier_scores, interaction_brier_scores)

print(f"Raw Brier scores: {raw_brier_scores}")
print(f"Interaction Brier scores: {interaction_brier_scores}")
print(f"Differences (raw - interaction): {differences}")
print(f"Paired t-test t-statistic: {t_stat:.6f}")
print(f"p-value: {p_value:.6f}")

interaction_helps = t_stat > 2.0
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# Task 3: Compression (sparsity and quantization)
print("\n=== Task 3: Compression ===")

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic_model(X, y, lambda_reg=0.1)
y_pred_dense = predict(X, w_dense, b_dense)
brier_dense = brier_score(y, y_pred_dense)
print(f"Dense model Brier: {brier_dense:.6f}")

sparsity_levels = [20, 40, 60]  # percent
bit_levels = [8, 4]

best_config = None
best_retention = 0.0

for sparsity_pct in sparsity_levels:
    for bits in bit_levels:
        # Apply sparsity: zero smallest magnitude weights
        k = round(sparsity_pct / 100.0 * n_features)
        w_sparse = w_dense.copy()
        
        # Find indices of k smallest magnitude weights
        smallest_idx = np.argsort(np.abs(w_sparse))[:k]
        w_sparse[smallest_idx] = 0.0
        
        # Apply quantization to remaining weights
        w_quant = w_sparse.copy()
        non_zero_mask = w_sparse != 0
        
        if np.any(non_zero_mask):
            w_nonzero = w_sparse[non_zero_mask]
            w_min = np.min(w_nonzero)
            w_max = np.max(w_nonzero)
            
            if w_min != w_max:
                # Map to 2^bits levels uniformly
                n_levels = 2 ** bits
                # Quantize non-zero weights
                w_quant_nonzero = w_nonzero.copy()
                # Normalize to [0, n_levels-1]
                normalized = (w_quant_nonzero - w_min) / (w_max - w_min) * (n_levels - 1)
                # Round to nearest integer level
                quantized_levels = np.round(normalized)
                # Map back to [w_min, w_max]
                w_quant_nonzero = w_min + quantized_levels / (n_levels - 1) * (w_max - w_min)
                w_quant[non_zero_mask] = w_quant_nonzero
        
        # Evaluate compressed model
        y_pred_quant = predict(X, w_quant, b_dense)
        brier_quant = brier_score(y, y_pred_quant)
        
        # Retention: dense brier / compressed brier
        if brier_quant > 0:
            retention = brier_dense / brier_quant
        else:
            retention = np.inf
        
        config_name = f"sparsity{sparsity_pct}_bits{bits}"
        print(f"{config_name}: Brier={brier_quant:.6f}, Retention={retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = config_name

print(f"\nBest config: {best_config} with retention {best_retention:.6f}")

# Prepare answers
answers = {
    "best_lambda": float(best_lambda),
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

print("\n=== Final Answers ===")
print(json.dumps(answers, indent=2))

# Write to answers.json
with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("\nAnswers written to answers.json")
