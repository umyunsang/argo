#!/usr/bin/env python3
"""Failing-first tests for the T3 oracle and its isolation contract."""
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import oracle_t3, run_t3

F = []
def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + (f" :: {detail}" if not ok else ""))
    if not ok: F.append(name)

def main():
    # determinism
    a, b = oracle_t3.build(42), oracle_t3.build(42)
    check("oracle is deterministic for a fixed seed", a["oracle_digest"] == b["oracle_digest"])
    check("different seeds give different ground truth",
          oracle_t3.build(42)["oracle_digest"] != oracle_t3.build(43)["oracle_digest"])
    check("oracle declares verifier origin", a["origin"] == "verifier")

    # ground truth is not guessable: answers must vary across seeds
    lams = {oracle_t3.build(s)["sub1_regularization"]["best_lambda"] for s in (42, 101, 2026)}
    check("sub1 answer varies across seeds (not a constant)", len(lams) > 1, f"got {lams}")
    helps = {oracle_t3.build(s)["sub2_interactions"]["interaction_helps"] for s in (42, 7, 2026)}
    check("sub2 answer is not constant across seeds", len(helps) > 1, f"got {helps}")

    with tempfile.TemporaryDirectory() as td:
        root = Path(td); ws = root / "ws"; od = root / "oracle"
        truth = run_t3.build_workspace(42, ws, od)

        # isolation: the workspace must not contain the answers
        blob = "".join(p.read_text(errors="replace") for p in ws.rglob("*") if p.is_file())
        check("workspace does not contain the oracle digest", truth["oracle_digest"] not in blob)
        check("workspace does not contain the best_config string",
              truth["sub3_compression"]["best_config"] not in blob)
        check("workspace ships data and task only",
              sorted(p.name for p in ws.iterdir()) == ["TASK.md", "data.json"])

        # isolation is enforced, and for the right reason
        try:
            run_t3.assert_isolated(ws, ws / "inner_oracle")
            check("nested oracle dir is rejected", False, "no error raised")
        except run_t3.OracleLeak as e:
            check("nested oracle dir is rejected for being inside the workspace",
                  "inside the agent workspace" in str(e), str(e))

        link = ws / "peek"; link.symlink_to(od)
        try:
            run_t3.assert_isolated(ws, od)
            check("symlink into the oracle dir is rejected", False, "no error raised")
        except run_t3.OracleLeak as e:
            check("symlink into the oracle dir is rejected for pointing at the oracle",
                  "symlink" in str(e) and "oracle" in str(e), str(e))
        link.unlink()

        # scoring
        s1, s2, s3 = truth["sub1_regularization"], truth["sub2_interactions"], truth["sub3_compression"]
        perfect = {"best_lambda": s1["best_lambda"],
                   "improvement_over_baseline": s1["improvement_over_baseline"],
                   "paired_t_stat": s2["paired_t_stat"],
                   "interaction_helps": s2["interaction_helps"],
                   "best_config": s3["best_config"]}
        check("a correct answer sheet passes", run_t3.score(perfect, truth)["pass"])

        wrong = dict(perfect, best_config="sparsity60_bits4")
        r = run_t3.score(wrong, truth)
        check("a wrong best_config fails and names that check",
              (not r["pass"]) and r["checks"]["best_config"] is False)

        drift = dict(perfect, improvement_over_baseline=float(s1["improvement_over_baseline"]) + 0.5)
        r = run_t3.score(drift, truth)
        check("a drifted number fails on its own check",
              (not r["pass"]) and r["checks"]["improvement_over_baseline"] is False)

        r = run_t3.score(dict(perfect, paired_t_stat=None), truth)
        check("a missing number is not scored as correct", r["checks"]["paired_t_stat"] is False)

        r = run_t3.score(dict(perfect, interaction_helps=(not s2["interaction_helps"])), truth)
        check("a flipped boolean fails", r["checks"]["interaction_helps"] is False)

        # The three stage-1 arms failed best_config on spelling alone. Meaning is
        # scored, spelling is not.
        tsp, tb = run_t3.parse_config(s3["best_config"])
        for spelled in ("sparsity_%d_bits_%d" % (tsp, tb), "sparsity=%d%%_bits=%d" % (tsp, tb), {"sparsity": tsp, "bits": tb},
                        "%d%% sparsity, %d-bit" % (tsp, tb), s3["best_config"], {"sparsity_percent": tsp / 100, "bit_width": tb},
                        "sparsity %.2f bits %d" % (tsp / 100, tb)):
            r = run_t3.score(dict(perfect, best_config=spelled), truth)
            check("best_config is scored by meaning: %r" % (spelled,), r["checks"]["best_config"] is True, str(r["checks"]))
        for other in ("sparsity_%d_bits_%d" % (tsp, 12 - tb), {"sparsity": 100 - tsp, "bits": tb}, "%d%% sparsity %d bit" % (tsp + 20 if tsp < 60 else 20, tb), None, "bits%d" % tb):
            r = run_t3.score(dict(perfect, best_config=other), truth)
            check("a different or unparseable config still fails: %r" % (other,), r["checks"]["best_config"] is False)

        # The conventions the verifier relies on must be visible to the agent.
        md = (ws / "TASK.md").read_text(encoding="utf-8")
        for token in ("shuffle", "200", "gradient", "lambda * w", "magnitude", "weights", "min", "max", "retention", "sparsity20_bits4"):
            check("TASK.md states the convention: %s" % token, token in md, md[:80])

    print(("\n%d failing checks" % len(F)) if F else "\nAll checks passed.")
    return 1 if F else 0

if __name__ == "__main__":
    sys.exit(main())
