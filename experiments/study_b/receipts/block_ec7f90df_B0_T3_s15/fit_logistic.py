import json
import numpy as np
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'], dtype=np.float32)
y = np.array(data['y'], dtype=np.float32)

print(f"X shape: {X.shape}, y shape: {y.shape}")
print(f"Number of samples: {len(X)}")

n_samples = len(X)
n_features = X.shape[1]
print(f"Features: {n_features}")

def sigmoid(z):
    """Numerically stable sigmoid"""
    z = np.clip(z, -30, 30)
    return 1 / (1 + np.exp(-z))

def brier_score(y_true, y_pred):
    """Brier score: mean squared error between predicted probabilities and labels"""
    return np.mean((y_pred - y_true) ** 2)

def fit_logistic(X_train, y_train, lambda_reg, n_iter=200, learning_rate=0.1):
    """Fit logistic regression with specified conventions"""
    n_samples, n_features = X_train.shape
    
    # Initialize weights and bias at 0
    w = np.zeros(n_features, dtype=np.float32)
    b = 0.0
    
    # Full-batch gradient descent for 200 iterations
    for iteration in range(n_iter):
        # Forward pass
        logits = X_train @ w + b
        logits = np.clip(logits, -30, 30)
        y_pred = sigmoid(logits)
        
        # Compute gradients
        error = y_pred - y_train
        grad_w = X_train.T @ error / n_samples
        grad_b = np.sum(error) / n_samples
        
        # Update with L2 regularization
        # w -= 0.1 * (grad_w / n + lambda * w)
        # b -= 0.1 * (grad_b / n)
        w = w - learning_rate * (grad_w + lambda_reg * w)
        b = b - learning_rate * grad_b
    
    return w, b

def predict(X, w, b):
    """Make predictions"""
    logits = X @ w + b
    logits = np.clip(logits, -30, 30)
    return sigmoid(logits)

# Split data into 5 contiguous folds
def create_folds(n_samples, n_folds=5):
    """Create contiguous folds"""
    fold_size = n_samples // n_folds
    folds = []
    for i in range(n_folds):
        start = i * fold_size
        end = start + fold_size if i < n_folds - 1 else n_samples
        folds.append((start, end))
    return folds

folds = create_folds(n_samples, n_folds=5)
print(f"Folds: {folds}")

# Question 1: Find best lambda
print("\n=== Question 1: Best Lambda ===")
lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
lambda_scores = {}

for lambda_val in lambdas:
    fold_scores = []
    for fold_idx, (start, end) in enumerate(folds):
        # Create train/test split
        X_test = X[start:end]
        y_test = y[start:end]
        X_train = np.vstack([X[:start], X[end:]])
        y_train = np.hstack([y[:start], y[end:]])
        
        # Fit model
        w, b = fit_logistic(X_train, y_train, lambda_val)
        
        # Evaluate on test fold
        y_pred = predict(X_test, w, b)
        brier = brier_score(y_test, y_pred)
        fold_scores.append(brier)
    
    cv_score = np.mean(fold_scores)
    lambda_scores[lambda_val] = cv_score
    print(f"Lambda {lambda_val}: CV Brier = {cv_score:.6f}")

best_lambda = min(lambda_scores, key=lambda_scores.get)
best_score = lambda_scores[best_lambda]
baseline_score = lambda_scores[0.0]
improvement = baseline_score - best_score

print(f"\nBest lambda: {best_lambda}")
print(f"Best CV Brier: {best_score:.6f}")
print(f"Baseline (lambda=0): {baseline_score:.6f}")
print(f"Improvement: {improvement:.6f}")

# Question 2: Interaction features
print("\n=== Question 2: Interaction Features ===")

# Create interaction features
X_with_interactions = []
for row in X:
    interactions = [
        row[0] * row[1],  # x0*x1
        row[1] * row[2],  # x1*x2
        row[2] * row[3],  # x2*x3
        row[0] * row[3],  # x0*x3
    ]
    X_with_interactions.append(interactions)

X_interactions = np.array(X_with_interactions, dtype=np.float32)
print(f"X_interactions shape: {X_interactions.shape}")

# Fit both models with lambda=0.1
lambda_test = 0.1
raw_fold_scores = []
interaction_fold_scores = []

for fold_idx, (start, end) in enumerate(folds):
    X_test = X[start:end]
    X_test_interactions = X_interactions[start:end]
    y_test = y[start:end]
    X_train = np.vstack([X[:start], X[end:]])
    X_train_interactions = np.vstack([X_interactions[:start], X_interactions[end:]])
    y_train = np.hstack([y[:start], y[end:]])
    
    # Fit raw model
    w_raw, b_raw = fit_logistic(X_train, y_train, lambda_test)
    y_pred_raw = predict(X_test, w_raw, b_raw)
    brier_raw = brier_score(y_test, y_pred_raw)
    raw_fold_scores.append(brier_raw)
    
    # Fit interaction model
    w_inter, b_inter = fit_logistic(X_train_interactions, y_train, lambda_test)
    y_pred_inter = predict(X_test_interactions, w_inter, b_inter)
    brier_inter = brier_score(y_test, y_pred_inter)
    interaction_fold_scores.append(brier_inter)
    
    print(f"Fold {fold_idx}: Raw Brier = {brier_raw:.6f}, Interaction Brier = {brier_inter:.6f}")

# Paired t-test: raw - interaction
differences = np.array(raw_fold_scores) - np.array(interaction_fold_scores)
print(f"\nDifferences (raw - interaction): {differences}")

# One-sample t-test on differences
t_stat, p_val = stats.ttest_1samp(differences, 0)
print(f"Paired t-statistic (raw - interaction): {t_stat:.6f}")
print(f"P-value: {p_val:.6f}")

interaction_helps = t_stat > 2.0
print(f"Interaction helps (t > 2.0): {interaction_helps}")

# Question 3: Compression
print("\n=== Question 3: Best Compression Config ===")

# Fit dense model on all data with lambda=0.1
w_dense, b_dense = fit_logistic(X, y, 0.1)
y_pred_dense = predict(X, w_dense, b_dense)
brier_dense = brier_score(y, y_pred_dense)
print(f"Dense model Brier: {brier_dense:.6f}")

sparsities = [20, 40, 60]  # percent
bits_list = [8, 4]
configs = []

for sparsity_pct in sparsities:
    for bits in bits_list:
        # Apply sparsity: zero smallest magnitude weights
        w_sparse = w_dense.copy()
        k = round(sparsity_pct / 100.0 * len(w_dense))
        if k > 0:
            threshold_idx = np.argsort(np.abs(w_sparse))[k-1] if k <= len(w_sparse) else 0
            threshold = np.abs(w_sparse[threshold_idx]) if k <= len(w_sparse) else np.inf
            w_sparse[np.abs(w_sparse) <= threshold] = 0
            # More precise: keep only the largest |w| values
            sorted_indices = np.argsort(np.abs(w_sparse))
            w_sparse[sorted_indices[:k]] = 0
        
        # Apply quantization: map to 2^bits levels
        w_quantized = w_sparse.copy()
        non_zero_mask = w_quantized != 0
        if np.any(non_zero_mask):
            w_min = np.min(w_quantized[non_zero_mask])
            w_max = np.max(w_quantized[non_zero_mask])
            if w_min < w_max:
                n_levels = 2 ** bits
                # Map to [0, n_levels-1]
                w_normalized = (w_quantized[non_zero_mask] - w_min) / (w_max - w_min)
                w_quantized_levels = np.round(w_normalized * (n_levels - 1))
                # Map back to original range
                w_quantized[non_zero_mask] = w_min + w_quantized_levels / (n_levels - 1) * (w_max - w_min)
        
        # Evaluate compressed model
        y_pred_compressed = predict(X, w_quantized, b_dense)
        brier_compressed = brier_score(y, y_pred_compressed)
        retention = brier_dense / brier_compressed if brier_compressed > 0 else 0
        
        config_name = f"sparsity{sparsity_pct}_bits{bits}"
        configs.append({
            'name': config_name,
            'sparsity': sparsity_pct,
            'bits': bits,
            'brier': brier_compressed,
            'retention': retention
        })
        print(f"{config_name}: Brier = {brier_compressed:.6f}, Retention = {retention:.6f}")

# Find best config (highest retention)
best_config = max(configs, key=lambda x: x['retention'])
print(f"\nBest config: {best_config['name']} with retention {best_config['retention']:.6f}")

# Prepare answers
answers = {
    'best_lambda': best_lambda,
    'improvement_over_baseline': float(improvement),
    'paired_t_stat': float(t_stat),
    'interaction_helps': bool(interaction_helps),
    'best_config': best_config['name']
}

print("\n=== FINAL ANSWERS ===")
print(json.dumps(answers, indent=2))

# Save to file
with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("\nAnswers saved to answers.json")
