import json
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'], dtype=np.float64)
y = np.array(data['y'], dtype=np.float64)

n_samples, n_features = X.shape
print(f"Data shape: {n_samples} samples, {n_features} features")

# Helper functions
def sigmoid(z):
    """Sigmoid function with clipping for numerical stability"""
    z = np.clip(z, -30, 30)
    return 1 / (1 + np.exp(-z))

def brier_score(y_true, y_pred):
    """Brier score: mean squared error between predicted probabilities and actual labels"""
    return np.mean((y_pred - y_true) ** 2)

def fit_logistic(X_train, y_train, lambda_reg=0.0, n_iter=200, lr=0.1):
    """
    Fit logistic regression with full-batch gradient descent.
    
    Update rule:
    w -= lr * (grad_w / n + lambda * w)
    b -= lr * (grad_b / n)
    """
    n, d = X_train.shape
    w = np.zeros(d)
    b = 0.0
    
    for iteration in range(n_iter):
        # Forward pass
        z = X_train @ w + b
        z = np.clip(z, -30, 30)
        y_pred = sigmoid(z)
        
        # Compute gradients
        error = y_pred - y_train
        grad_w = X_train.T @ error
        grad_b = np.sum(error)
        
        # Update with L2 regularization
        w -= lr * (grad_w / n + lambda_reg * w)
        b -= lr * (grad_b / n)
    
    return w, b

def predict_logistic(X, w, b):
    """Predict probabilities"""
    z = X @ w + b
    z = np.clip(z, -30, 30)
    return sigmoid(z)

# Create 5-fold CV splits (contiguous blocks, no shuffle)
fold_size = n_samples // 5
folds = []
for k in range(5):
    start_idx = k * fold_size
    end_idx = (k + 1) * fold_size if k < 4 else n_samples
    folds.append((start_idx, end_idx))

print(f"Fold sizes: {[end - start for start, end in folds]}")

# ============= Task 1: Find best lambda =============
lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
cv_scores = {lam: [] for lam in lambdas}

for lam in lambdas:
    for fold_idx in range(5):
        val_start, val_end = folds[fold_idx]
        
        # Training data: all except fold_idx
        train_indices = []
        for k in range(5):
            if k != fold_idx:
                start, end = folds[k]
                train_indices.extend(range(start, end))
        
        X_train = X[train_indices]
        y_train = y[train_indices]
        X_val = X[val_start:val_end]
        y_val = y[val_start:val_end]
        
        # Fit and evaluate
        w, b = fit_logistic(X_train, y_train, lambda_reg=lam)
        y_pred_val = predict_logistic(X_val, w, b)
        brier = brier_score(y_val, y_pred_val)
        cv_scores[lam].append(brier)

# Find best lambda
mean_scores = {lam: np.mean(cv_scores[lam]) for lam in lambdas}
best_lambda = min(mean_scores, key=mean_scores.get)
baseline_score = mean_scores[0.0]
best_score = mean_scores[best_lambda]
improvement = baseline_score - best_score

print(f"\nTask 1: Best Lambda")
print(f"Lambda scores: {mean_scores}")
print(f"Best lambda: {best_lambda}")
print(f"Improvement: {improvement}")

# ============= Task 2: Interaction terms =============
# Add interaction features
X_with_interactions = np.hstack([
    X,
    (X[:, 0] * X[:, 1]).reshape(-1, 1),  # x0*x1
    (X[:, 1] * X[:, 2]).reshape(-1, 1),  # x1*x2
    (X[:, 2] * X[:, 3]).reshape(-1, 1),  # x2*x3
    (X[:, 0] * X[:, 3]).reshape(-1, 1),  # x0*x3
])

cv_brier_raw = []
cv_brier_interaction = []

for fold_idx in range(5):
    val_start, val_end = folds[fold_idx]
    
    train_indices = []
    for k in range(5):
        if k != fold_idx:
            start, end = folds[k]
            train_indices.extend(range(start, end))
    
    X_train_raw = X[train_indices]
    X_train_inter = X_with_interactions[train_indices]
    y_train = y[train_indices]
    
    X_val_raw = X[val_start:val_end]
    X_val_inter = X_with_interactions[val_start:val_end]
    y_val = y[val_start:val_end]
    
    # Fit both models with lambda=0.1
    w_raw, b_raw = fit_logistic(X_train_raw, y_train, lambda_reg=0.1)
    w_inter, b_inter = fit_logistic(X_train_inter, y_train, lambda_reg=0.1)
    
    # Predict and compute Brier scores
    y_pred_raw = predict_logistic(X_val_raw, w_raw, b_raw)
    y_pred_inter = predict_logistic(X_val_inter, w_inter, b_inter)
    
    brier_raw = brier_score(y_val, y_pred_raw)
    brier_inter = brier_score(y_val, y_pred_inter)
    
    cv_brier_raw.append(brier_raw)
    cv_brier_interaction.append(brier_inter)

# Paired t-test: raw minus interaction
differences = np.array(cv_brier_raw) - np.array(cv_brier_interaction)
t_stat, p_value = stats.ttest_rel(cv_brier_raw, cv_brier_interaction)
interaction_helps = t_stat > 2.0

print(f"\nTask 2: Interaction Terms")
print(f"Raw Brier scores: {cv_brier_raw}")
print(f"Interaction Brier scores: {cv_brier_interaction}")
print(f"Differences (raw - interaction): {differences}")
print(f"Paired t-stat: {t_stat}")
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# ============= Task 3: Compression =============
# Train dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic(X, y, lambda_reg=0.1)
y_pred_dense = predict_logistic(X, w_dense, b_dense)
brier_dense = brier_score(y, y_pred_dense)

print(f"\nTask 3: Compression")
print(f"Dense model Brier: {brier_dense}")

sparsities = [20, 40, 60]
bits_options = [8, 4]

best_retention = 0.0
best_config_str = ""

for sparsity_percent in sparsities:
    for bits in bits_options:
        # Apply sparsity: zero the sparsity_percent smallest magnitude weights
        w_sparse = w_dense.copy()
        num_to_zero = round(sparsity_percent / 100.0 * len(w_dense))
        
        if num_to_zero > 0 and num_to_zero < len(w_dense):
            # Find indices of weights with smallest absolute values
            abs_weights = np.abs(w_sparse)
            indices_sorted = np.argsort(abs_weights)
            indices_to_zero = indices_sorted[:num_to_zero]
            w_sparse[indices_to_zero] = 0.0
        
        # Apply quantization to non-zero weights
        w_quant = w_sparse.copy()
        nonzero_mask = w_quant != 0
        
        if np.any(nonzero_mask):
            nonzero_weights = w_quant[nonzero_mask]
            min_val = np.min(nonzero_weights)
            max_val = np.max(nonzero_weights)
            
            if min_val != max_val:
                levels = 2 ** bits
                # For each non-zero weight, quantize it
                for i in range(len(w_quant)):
                    if w_quant[i] != 0:
                        # Map weight to level [0, levels-1]
                        normalized = (w_quant[i] - min_val) / (max_val - min_val)
                        level = round(normalized * (levels - 1))
                        # Reconstruct weight from level
                        w_quant[i] = min_val + level * (max_val - min_val) / (levels - 1)
        
        # Evaluate compressed model
        y_pred_compressed = predict_logistic(X, w_quant, b_dense)
        brier_compressed = brier_score(y, y_pred_compressed)
        
        # Retention: dense_brier / compressed_brier (higher is better)
        if brier_compressed > 0:
            retention = brier_dense / brier_compressed
        else:
            retention = float('inf')
        
        config_str = f"sparsity{sparsity_percent}_bits{bits}"
        print(f"{config_str}: retention = {retention:.6f}")
        
        if retention > best_retention:
            best_retention = retention
            best_config_str = config_str

print(f"\nBest config: {best_config_str} with retention {best_retention}")

# ============= Write answers =============
answers = {
    "best_lambda": best_lambda,
    "improvement_over_baseline": improvement,
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config_str
}

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("\n" + "="*50)
print("Final Answers:")
print(json.dumps(answers, indent=2))
