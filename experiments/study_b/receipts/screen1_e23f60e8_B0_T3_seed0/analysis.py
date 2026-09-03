import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import KFold
from sklearn.metrics import brier_score_loss
from scipy import stats

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'])
y = np.array(data['y'])

print(f"Data shape: X={X.shape}, y={y.shape}")

# ============================================================================
# 1. LAMBDA TUNING: Find best L2 strength for Brier score
# ============================================================================
print("\n" + "="*70)
print("TASK 1: Lambda Tuning (L2 Regularization)")
print("="*70)

lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
kf = KFold(n_splits=5, shuffle=True, random_state=42)

brier_scores_by_lambda = {}

for lam in lambdas:
    brier_scores = []
    
    for fold_idx, (train_idx, test_idx) in enumerate(kf.split(X)):
        X_train, X_test = X[train_idx], X[test_idx]
        y_train, y_test = y[train_idx], y[test_idx]
        
        # Fit logistic regression with L2 penalty (C = 1/lambda)
        if lam == 0.0:
            C = 1e10  # No regularization (very large C)
        else:
            C = 1.0 / lam
        
        model = LogisticRegression(penalty='l2', C=C, solver='lbfgs', max_iter=1000, random_state=42)
        model.fit(X_train, y_train)
        
        # Predict probabilities and compute Brier score
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        brier = brier_score_loss(y_test, y_pred_proba)
        brier_scores.append(brier)
        
        print(f"  Lambda={lam:.2f}, Fold {fold_idx+1}: Brier={brier:.6f}")
    
    mean_brier = np.mean(brier_scores)
    brier_scores_by_lambda[lam] = mean_brier
    print(f"Lambda={lam:.2f} -> Mean Brier Score: {mean_brier:.6f}\n")

# Find best lambda
best_lambda = min(brier_scores_by_lambda, key=brier_scores_by_lambda.get)
best_brier = brier_scores_by_lambda[best_lambda]
baseline_brier = brier_scores_by_lambda[0.0]  # Lambda=0 is baseline
improvement = baseline_brier - best_brier

print(f"Best Lambda: {best_lambda:.2f}")
print(f"Best Brier Score: {best_brier:.6f}")
print(f"Baseline Brier (lambda=0.0): {baseline_brier:.6f}")
print(f"Improvement over baseline: {improvement:.6f}")

# ============================================================================
# 2. INTERACTION FEATURES: Paired t-test
# ============================================================================
print("\n" + "="*70)
print("TASK 2: Interaction Features (Paired t-test)")
print("="*70)

# Create interaction features: x0*x1, x1*x2, x2*x3, x0*x3
X_interactions = np.column_stack([
    X[:, 0] * X[:, 1],  # x0*x1
    X[:, 1] * X[:, 2],  # x1*x2
    X[:, 2] * X[:, 3],  # x2*x3
    X[:, 0] * X[:, 3],  # x0*x3
])

X_with_interactions = np.hstack([X, X_interactions])

print(f"Original features: {X.shape[1]}")
print(f"Added interaction features: {X_interactions.shape[1]}")
print(f"Total features with interactions: {X_with_interactions.shape[1]}")

# Cross-validation: compare raw vs interactions
raw_brier_scores = []
interaction_brier_scores = []

for fold_idx, (train_idx, test_idx) in enumerate(kf.split(X)):
    # Raw features
    X_train_raw, X_test_raw = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    model_raw = LogisticRegression(penalty='l2', C=1.0, solver='lbfgs', max_iter=1000, random_state=42)
    model_raw.fit(X_train_raw, y_train)
    y_pred_raw = model_raw.predict_proba(X_test_raw)[:, 1]
    brier_raw = brier_score_loss(y_test, y_pred_raw)
    raw_brier_scores.append(brier_raw)
    
    # With interactions
    X_train_int = X_with_interactions[train_idx]
    X_test_int = X_with_interactions[test_idx]
    
    model_int = LogisticRegression(penalty='l2', C=1.0, solver='lbfgs', max_iter=1000, random_state=42)
    model_int.fit(X_train_int, y_train)
    y_pred_int = model_int.predict_proba(X_test_int)[:, 1]
    brier_int = brier_score_loss(y_test, y_pred_int)
    interaction_brier_scores.append(brier_int)
    
    print(f"Fold {fold_idx+1}: Raw Brier={brier_raw:.6f}, Interaction Brier={brier_int:.6f}, Diff={brier_raw-brier_int:.6f}")

raw_brier_scores = np.array(raw_brier_scores)
interaction_brier_scores = np.array(interaction_brier_scores)

# Paired t-test: H0: no difference in means
# We want to test if interactions help (lower brier score)
# So we compute differences: raw_brier - interaction_brier (positive means interactions help)
differences = raw_brier_scores - interaction_brier_scores
t_stat, p_value = stats.ttest_rel(raw_brier_scores, interaction_brier_scores)

print(f"\nPaired t-test results:")
print(f"  Raw Brier mean: {np.mean(raw_brier_scores):.6f}")
print(f"  Interaction Brier mean: {np.mean(interaction_brier_scores):.6f}")
print(f"  Mean difference (raw - interaction): {np.mean(differences):.6f}")
print(f"  t-statistic: {t_stat:.6f}")
print(f"  p-value: {p_value:.6f}")

# interaction_helps is True only if t > 2.0
interaction_helps = t_stat > 2.0
print(f"  Interaction helps (t > 2.0)? {interaction_helps} (t={t_stat:.6f})")

# ============================================================================
# 3. SPARSITY & QUANTIZATION: Best configuration
# ============================================================================
print("\n" + "="*70)
print("TASK 3: Sparsity & Quantization")
print("="*70)

# First, compute baseline (dense, no quantization)
print("\nComputing baseline (dense model)...")
baseline_brier_dense = []

for fold_idx, (train_idx, test_idx) in enumerate(kf.split(X)):
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]
    
    model = LogisticRegression(penalty='l2', C=1.0, solver='lbfgs', max_iter=1000, random_state=42)
    model.fit(X_train, y_train)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    brier = brier_score_loss(y_test, y_pred_proba)
    baseline_brier_dense.append(brier)

baseline_dense_mean = np.mean(baseline_brier_dense)
print(f"Baseline (dense) mean Brier: {baseline_dense_mean:.6f}")

# Test different sparsity and quantization levels
sparsities = [20, 40, 60]  # percentage
quantizations = [8, 4]  # bits

results = {}

def quantize_weights(weights, bits):
    """Simple uniform quantization"""
    min_val = weights.min()
    max_val = weights.max()
    n_levels = 2 ** bits
    
    if max_val == min_val:
        return weights.copy()
    
    # Scale to [0, n_levels-1] and round
    scaled = (weights - min_val) / (max_val - min_val) * (n_levels - 1)
    quantized = np.round(scaled) / (n_levels - 1) * (max_val - min_val) + min_val
    return quantized

def sparsify_and_quantize(X, sparsity_pct, bits):
    """Apply sparsity and quantization"""
    X_sparse = X.copy()
    sparsity_ratio = sparsity_pct / 100.0
    n_zero = int(X_sparse.shape[1] * sparsity_ratio)
    
    # Zero out smallest weights
    if n_zero > 0:
        abs_weights = np.abs(X_sparse)
        threshold = np.sort(abs_weights.flatten())[n_zero - 1]
        X_sparse[np.abs(X_sparse) <= threshold] = 0
    
    # Quantize non-zero weights
    X_quant = quantize_weights(X_sparse, bits)
    return X_quant

for sparsity in sparsities:
    for bits in quantizations:
        config_name = f"sparsity_{sparsity}_bits_{bits}"
        config_brier = []
        
        for fold_idx, (train_idx, test_idx) in enumerate(kf.split(X)):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            
            # Train dense model
            model = LogisticRegression(penalty='l2', C=1.0, solver='lbfgs', max_iter=1000, random_state=42)
            model.fit(X_train, y_train)
            
            # Get coefficients and apply sparsity+quantization
            coef = model.coef_[0].reshape(-1, 1)
            coef_sparse = sparsify_and_quantize(coef, sparsity, bits).flatten()
            
            # Create modified predictions: apply sparsified coefficients
            # For testing: use quantized weights
            y_pred_logits = X_test @ coef_sparse + model.intercept_
            y_pred_proba = 1 / (1 + np.exp(-y_pred_logits))
            y_pred_proba = np.clip(y_pred_proba, 1e-15, 1 - 1e-15)
            
            brier = brier_score_loss(y_test, y_pred_proba)
            config_brier.append(brier)
        
        mean_brier = np.mean(config_brier)
        results[config_name] = mean_brier
        retention_pct = (1 - (mean_brier - baseline_dense_mean) / baseline_dense_mean) * 100
        print(f"{config_name}: Brier={mean_brier:.6f}, Retention={retention_pct:.2f}%")

# Find best configuration (highest retention = lowest Brier)
best_config_name = min(results, key=results.get)
best_config_brier = results[best_config_name]
best_retention = (1 - (best_config_brier - baseline_dense_mean) / baseline_dense_mean) * 100

print(f"\nBest configuration: {best_config_name}")
print(f"  Brier score: {best_config_brier:.6f}")
print(f"  Performance retention: {best_retention:.2f}%")

# ============================================================================
# SAVE RESULTS
# ============================================================================
print("\n" + "="*70)
print("SAVING RESULTS")
print("="*70)

answers = {
    "best_lambda": float(best_lambda),
    "improvement_over_baseline": float(improvement),
    "paired_t_stat": float(t_stat),
    "interaction_helps": bool(interaction_helps),
    "best_config": best_config_name
}

with open('answers.json', 'w') as f:
    json.dump(answers, f, indent=2)

print("Results saved to answers.json:")
print(json.dumps(answers, indent=2))
