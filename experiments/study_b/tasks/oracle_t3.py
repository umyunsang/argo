#!/usr/bin/env python3
"""T3 deterministic oracle. RUNS REAL COMPUTATION; no literals, no model call.

Pure standard library on purpose: the isolated clean-clone runner exposes
/usr/bin/python3 without numpy, and a previous run failed with exactly that error.

The oracle writes ground truth to a path the harness under test cannot read;
run_t3.py enforces the separation and refuses to start if they overlap.

origin: verifier
"""
from __future__ import annotations
import argparse, hashlib, json, math, random
from pathlib import Path


def make_data(seed, n=140, d=40, informative=4):
    rng = random.Random(seed)
    w = [rng.gauss(0, 2.0) if i < informative else 0.0 for i in range(d)]
    # seed-dependent true interaction strength so the sub2 answer is not guessable
    inter = 3.0 if (seed % 2 == 0) else 0.0
    X, y = [], []
    for _ in range(n):
        row = [rng.gauss(0, 1) for _ in range(d)]
        logit = sum(a * b for a, b in zip(row, w)) + inter * row[0] * row[1] + rng.gauss(0, 0.8)
        p = 1 / (1 + math.exp(-max(-30.0, min(30.0, logit))))
        X.append(row); y.append(1 if p > rng.random() else 0)
    return X, y


def fit(X, y, lam, iters=200, lr=0.1):
    d = len(X[0]); w = [0.0] * d; b = 0.0; n = len(y)
    for _ in range(iters):
        gw = [0.0] * d; gb = 0.0
        for row, t in zip(X, y):
            z = sum(a * c for a, c in zip(row, w)) + b
            e = 1 / (1 + math.exp(-max(-30.0, min(30.0, z)))) - t
            for j in range(d): gw[j] += e * row[j]
            gb += e
        for j in range(d): w[j] -= lr * (gw[j] / n + lam * w[j])
        b -= lr * (gb / n)
    return w, b


def brier(X, y, w, b):
    s = 0.0
    for row, t in zip(X, y):
        z = sum(a * c for a, c in zip(row, w)) + b
        p = 1 / (1 + math.exp(-max(-30.0, min(30.0, z))))
        s += (p - t) ** 2
    return s / len(y)


def kfold(X, y, lam, k=5, cols=None):
    n = len(y); size = n // k; out = []
    for i in range(k):
        lo, hi = i * size, (n if i == k - 1 else (i + 1) * size)
        def sel(r): return [r[c] for c in cols] if cols else r
        Xtr = [sel(X[j]) for j in range(n) if not (lo <= j < hi)]
        ytr = [y[j] for j in range(n) if not (lo <= j < hi)]
        Xte = [sel(X[j]) for j in range(lo, hi)]; yte = y[lo:hi]
        w, b = fit(Xtr, ytr, lam)
        out.append(brier(Xte, yte, w, b))
    return out


def mean(v): return sum(v) / len(v)


def sub1(seed):
    X, y = make_data(seed)
    grid = [0.0, 0.01, 0.1, 1.0, 10.0]
    means = {str(l): mean(kfold(X, y, l)) for l in grid}
    base = means["0.0"]; best = min(means, key=means.get)
    return {"grid": grid, "cv_brier_by_lambda": means, "baseline_brier": base,
            "best_lambda": float(best), "best_brier": means[best],
            "improvement_over_baseline": base - means[best],
            "monotone_in_lambda": all(means[str(grid[i])] <= means[str(grid[i+1])] for i in range(len(grid)-1))}


def sub2(seed):
    X, y = make_data(seed)
    Xi = [r + [r[0]*r[1], r[1]*r[2], r[2]*r[3], r[0]*r[3]] for r in X]
    a = kfold(X, y, 0.1); b = kfold(Xi, y, 0.1)
    d = [p - q for p, q in zip(a, b)]
    md = mean(d)
    sd = math.sqrt(sum((x - md) ** 2 for x in d) / (len(d) - 1)) if len(d) > 1 else 0.0
    t = md / (sd / math.sqrt(len(d))) if sd > 0 else 0.0
    return {"raw_cv_brier": mean(a), "interaction_cv_brier": mean(b),
            "paired_t_stat": t, "n_folds": len(d), "interaction_helps": bool(t > 2.0)}


def sub3(seed):
    X, y = make_data(seed)
    w, b = fit(X, y, 0.1); dense = brier(X, y, w, b); grid = {}
    for sp in (0.2, 0.4, 0.6):
        k = int(round(sp * len(w)))
        order = sorted(range(len(w)), key=lambda j: abs(w[j]))
        wp = list(w)
        for j in order[:k]: wp[j] = 0.0
        for bits in (8, 4):
            lo, hi = min(wp), max(wp)
            step = (hi - lo) / (2 ** bits - 1) if hi > lo else 1.0
            wq = [round((v - lo) / step) * step + lo for v in wp]
            bq = brier(X, y, wq, b)
            grid[f"sparsity{int(sp*100)}_bits{bits}"] = {"brier": bq,
                "retention": (dense / bq) if bq > 0 else 0.0}
    best = max(grid, key=lambda k_: grid[k_]["retention"])
    return {"dense_brier": dense, "grid": grid, "best_config": best,
            "best_retention": grid[best]["retention"]}


def build(seed):
    rec = {"origin": "verifier", "seed": seed, "sub1_regularization": sub1(seed),
           "sub2_interactions": sub2(seed), "sub3_compression": sub3(seed)}
    rec["oracle_digest"] = hashlib.sha256(json.dumps(rec, sort_keys=True).encode()).hexdigest()
    return rec


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260903)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    p = Path(a.out); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(build(a.seed), indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"wrote": str(p), "seed": a.seed, "digest": build(a.seed)["oracle_digest"][:16]}))
