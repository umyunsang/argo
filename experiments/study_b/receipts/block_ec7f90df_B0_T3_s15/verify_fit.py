import json
import numpy as np
from scipy import stats

# Load data
with open('data.json', 'r') as f:
    data = json.load(f)

X = np.array(data['X'], dtype=np.float32)
y = np.array(data['y'], dtype=np.float32)

print("=== Data Verification ===")
print(f"X shape: {X.shape}")
print(f"y shape: {y.shape}")
print(f"y unique values: {np.unique(y)}")
print(f"y class distribution: {np.bincount(y.astype(int))}")

# Verify fold structure
n_samples = len(X)
n_folds = 5
fold_size = n_samples // n_folds
print(f"\n=== Fold Structure ===")
print(f"Total samples: {n_samples}")
print(f"Fold size: {fold_size}")
print(f"Total folds: {n_folds}")

folds = [(i * fold_size, i * fold_size + fold_size if i < n_folds - 1 else n_samples) for i in range(n_folds)]
for i, (start, end) in enumerate(folds):
    print(f"Fold {i}: samples {start}-{end-1} (size: {end-start})")

# Verify that test+train == total
for i, (start, end) in enumerate(folds):
    test_size = end - start
    train_size = n_samples - test_size
    print(f"Fold {i}: test={test_size}, train={train_size}, total={test_size + train_size}")

print("\n=== Lambda Candidates ===")
lambdas = [0.0, 0.01, 0.1, 1.0, 10.0]
print(f"Lambda values to test: {lambdas}")

print("\n=== Interaction Features ===")
print(f"Original features: {X.shape[1]}")
print(f"Interaction pairs: x0*x1, x1*x2, x2*x3, x0*x3")
print(f"Number of interaction features: 4")

print("\n=== Compression Configs ===")
sparsities = [20, 40, 60]
bits_list = [8, 4]
print(f"Sparsity percentages: {sparsities}")
print(f"Bit depths: {bits_list}")
print(f"Total configs: {len(sparsities) * len(bits_list)}")
configs = []
for s in sparsities:
    for b in bits_list:
        configs.append(f"sparsity{s}_bits{b}")
for c in configs:
    print(f"  - {c}")

# Load and display answers
print("\n=== Final Answers ===")
with open('answers.json', 'r') as f:
    answers = json.load(f)

for key, value in answers.items():
    print(f"{key}: {value}")

# Verify answer types
print("\n=== Answer Type Verification ===")
assert isinstance(answers['best_lambda'], (int, float)), "best_lambda should be numeric"
assert isinstance(answers['improvement_over_baseline'], float), "improvement_over_baseline should be float"
assert isinstance(answers['paired_t_stat'], float), "paired_t_stat should be float"
assert isinstance(answers['interaction_helps'], bool), "interaction_helps should be boolean"
assert isinstance(answers['best_config'], str), "best_config should be string"
print("✓ All answer types are correct")

# Verify best_lambda is in the candidate list
assert answers['best_lambda'] in lambdas, f"best_lambda {answers['best_lambda']} not in {lambdas}"
print(f"✓ best_lambda {answers['best_lambda']} is valid")

# Verify best_config format
config_parts = answers['best_config'].split('_')
assert len(config_parts) == 2, "best_config should have format sparsityXX_bitsY"
assert config_parts[0].startswith('sparsity'), "first part should start with 'sparsity'"
assert config_parts[1].startswith('bits'), "second part should start with 'bits'"
print(f"✓ best_config format is valid: {answers['best_config']}")

# Extract sparsity and bits from config
sparsity_str = config_parts[0].replace('sparsity', '')
bits_str = config_parts[1].replace('bits', '')
sparsity_val = int(sparsity_str)
bits_val = int(bits_str)
assert sparsity_val in sparsities, f"sparsity {sparsity_val} not in {sparsities}"
assert bits_val in bits_list, f"bits {bits_val} not in {bits_list}"
print(f"✓ best_config sparsity {sparsity_val} and bits {bits_val} are valid")

print("\n✅ All verifications passed!")
