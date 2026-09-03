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
# Logistic Regression Implementation
# ============================================================================

def sigmoid(z):
    """Sigmoid function with clipping for numerical stability."""
    z = np.clip(z, -30, 30)
    return 1.0 / (1.0 + np.exp(-z))

def logistic_loss(X, y, w, b, lambda_reg):
    """Binary cross-entropy loss with L2 regularization."""
    logits = np.clip(X @ w + b, -30, 30)
    pred = sigmoid(logits)
    # Avoid log(0)
    pred = np.clip(pred, 1e-15, 1 - 1e-15)
    loss = -np.mean(y * np.log(pred) + (1 - y) * np.log(1 - pred))
    loss += lambda_reg / 2.0 * np.sum(w ** 2)
    return loss

def logistic_gradient(X, y, w, b, lambda_reg):
    """Gradient for weights and bias."""
    logits = np.clip(X @ w + b, -30, 30)
    pred = sigmoid(logits)
    error = pred - y
    grad_w = X.T @ error / len(y) + lambda_reg * w
    grad_b = np.mean(error)
    return grad_w, grad_b

def fit_logistic(X, y, lambda_reg=0.0, learning_rate=0.1, iterations=200):
    """Fit logistic regression with full-batch gradient descent."""
    n_samples, n_features = X.shape
    w = np.zeros(n_features)
    b = 0.0
    
    for _ in range(iterations):
        grad_w, grad_b = logistic_gradient(X, y, w, b, lambda_reg)
        w -= learning_rate * grad_w
        b -= learning_rate * grad_b
    
    return w, b

def predict_proba(X, w, b):
    """Predict probability for positive class."""
    logits = np.clip(X @ w + b, -30, 30)
    return sigmoid(logits)

def brier_score(y_true, y_pred):
    """Brier score: mean squared error of predictions."""
    return np.mean((y_pred - y_true) ** 2)

# ============================================================================
# Task 1: Find best lambda via 5-fold CV
# ============================================================================

def create_folds(n_samples, n_folds=5):
    """Create 5 contiguous folds in row order."""
    fold_size = n_samples // n_folds
    folds = []
    for k in range(n_folds):
        start = k * fold_size
        end = start + fold_size if k < n_folds - 1 else n_samples
        folds.append((start, end))
    return folds

folds = create_folds(n_samples, n_folds=5)
print(f"Fold splits: {folds}")

lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
cv_scores = {lam: [] for lam in lambdas}

for lam in lambdas:
    for k, (test_start, test_end) in enumerate(folds):
        # Create train/test split
        test_indices = slice(test_start, test_end)
        X_test = X[test_indices]
        y_test = y[test_indices]
        
        train_indices = np.concatenate([np.arange(0, test_start), np.arange(test_end, n_samples)])
        X_train = X[train_indices]
        y_train = y[train_indices]
        
        # Fit model
        w, b = fit_logistic(X_train, y_train, lambda_reg=lam)
        
        # Evaluate on test fold
        y_pred = predict_proba(X_test, w, b)
        brier = brier_score(y_test, y_pred)
        cv_scores[lam].append(brier)

# Compute mean CV scores
mean_cv_scores = {lam: np.mean(cv_scores[lam]) for lam in lambdas}
print("\n=== Task 1: Lambda Selection ===")
for lam, score in mean_cv_scores.items():
    print(f"Lambda {lam}: Mean Brier = {score:.6f}")

best_lambda = min(lambdas, key=lambda lam: mean_cv_scores[lam])
improvement = mean_cv_scores[0.0] - mean_cv_scores[best_lambda]
print(f"\nBest Lambda: {best_lambda}")
print(f"Improvement over baseline (lambda=0): {improvement:.6f}")

# ============================================================================
# Task 2: Interaction features and paired t-test
# ============================================================================

print("\n=== Task 2: Interaction Features ===")

# Create feature matrix with interactions
X_with_interactions = np.hstack([
    X,
    (X[:, 0] * X[:, 1]).reshape(-1, 1),  # x0*x1
    (X[:, 1] * X[:, 2]).reshape(-1, 1),  # x1*x2
    (X[:, 2] * X[:, 3]).reshape(-1, 1),  # x2*x3
    (X[:, 0] * X[:, 3]).reshape(-1, 1),  # x0*x3
])

raw_briers = []
interaction_briers = []

for k, (test_start, test_end) in enumerate(folds):
    # Create train/test split
    test_indices = slice(test_start, test_end)
    X_test_raw = X[test_indices]
    X_test_inter = X_with_interactions[test_indices]
    y_test = y[test_indices]
    
    train_indices = np.concatenate([np.arange(0, test_start), np.arange(test_end, n_samples)])
    X_train_raw = X[train_indices]
    X_train_inter = X_with_interactions[train_indices]
    y_train = y[train_indices]
    
    # Fit models with lambda=0.1
    w_raw, b_raw = fit_logistic(X_train_raw, y_train, lambda_reg=0.1)
    w_inter, b_inter = fit_logistic(X_train_inter, y_train, lambda_reg=0.1)
    
    # Evaluate
    y_pred_raw = predict_proba(X_test_raw, w_raw, b_raw)
    y_pred_inter = predict_proba(X_test_inter, w_inter, b_inter)
    
    brier_raw = brier_score(y_test, y_pred_raw)
    brier_inter = brier_score(y_test, y_pred_inter)
    
    raw_briers.append(brier_raw)
    interaction_briers.append(brier_inter)
    
    print(f"Fold {k}: Raw Brier = {brier_raw:.6f}, Interaction Brier = {brier_inter:.6f}")

# Paired t-test
differences = np.array(raw_briers) - np.array(interaction_briers)
print(f"\nDifferences (raw - interaction): {differences}")
mean_diff = np.mean(differences)
std_diff = np.std(differences, ddof=1)
t_stat = mean_diff / (std_diff / np.sqrt(len(differences))) if std_diff > 0 else 0.0

print(f"Mean difference: {mean_diff:.6f}")
print(f"Paired t-test statistic: {t_stat:.6f}")

interaction_helps = t_stat > 2.0
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# ============================================================================
# Task 3: Compression (Sparsity + Quantization)
# ============================================================================

print("\n=== Task 3: Compression ===")

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic(X, y, lambda_reg=0.1)
y_pred_dense = predict_proba(X, w_dense, b_dense)
brier_dense = brier_score(y, y_pred_dense)
print(f"Dense model Brier (in-sample): {brier_dense:.6f}")

sparsities = [20, 40, 60]  # percent
bit_widths = [8, 4]
best_retention = 0.0
best_config = None

for sparsity in sparsities:
    for bits in bit_widths:
        # Apply sparsity
        w_sparse = w_dense.copy()
        k = max(1, round(sparsity / 100.0 * len(w_dense)))
        threshold = np.sort(np.abs(w_sparse))[k-1]
        w_sparse[np.abs(w_sparse) < threshold] = 0.0
        
        # Apply quantization
        w_quant = w_sparse.copy()
        mask_nonzero = w_sparse != 0
        if np.any(mask_nonzero):
            w_min = np.min(w_sparse[mask_nonzero])
            w_max = np.max(w_sparse[mask_nonzero])
            if w_min < w_max:
                # Map to 2^bits levels
                levels = 2 ** bits
                w_normalized = (w_sparse[mask_nonzero] - w_min) / (w_max - w_min)
                w_quantized = np.round(w_normalized * (levels - 1)) * (w_max - w_min) / (levels - 1) + w_min
                w_quant[mask_nonzero] = w_quantized
        
        # Evaluate compressed model
        y_pred_compressed = predict_proba(X, w_quant, b_dense)
        brier_compressed = brier_score(y, y_pred_compressed)
        retention = brier_dense / brier_compressed if brier_compressed > 0 else 0
        
        config_name = f"sparsity{sparsity}_bits{bits}"
        print(f"{config_name}: Brier = {brier_compressed:.6f}, Retention = {retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config = config_name

print(f"\nBest compression config: {best_config} with retention {best_retention:.6f}")

# ============================================================================
# Save results
# ============================================================================

results = {
    "best_lambda": best_lambda,
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config
}

print("\n=== Final Results ===")
for key, value in results.items():
    print(f"{key}: {value}")

with open('answers.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nAnswers saved to answers.json")
