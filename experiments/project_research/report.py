"""Generate a bounded initial report from recorded ORX receipts, not summaries."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .contracts import utc_now
from .dispatch import ROOT
from .state import Store


def generate(destination: Path):
    return _generate(destination)


def campaign_section(campaigns: list) -> str:
    if not campaigns:
        return "자율 캠페인 세션에서 제출된 후보는 아직 없다."
    lines = ["## 자율 캠페인 세션", "", "아래는 에이전트가 스스로 질문·방법·실험을 정해 제출한 후보다. **품질(AAA)·우위·PI 판정은 모두 미정**이며, 제출 자체는 완료 판정이 아니다. 모델 요청은 기존 구독의 포함 사용량 전후 관측으로 추가 과금0원을 확인했다.", "",
             "| 캠페인 | 팀/모델 | 모델 요청 | 토큰 | 추가 과금 | ORX 실행 | 상태 |", "|---|---|---|---|---|---|---|"]
    for c in campaigns:
        runs = ", ".join(f"{r['run_id'][:8]} {r['status']}" for r in c["orx_runs"]) or "없음"
        unknown = f" (미확인 {c['charges_unknown']})" if c["charges_unknown"] else ""
        lines.append(f"| {c['campaign_id']} | {c['team_id']} / {c['model_id']} | {c['model_requests']} | {c['total_tokens']:,} | {c['actual_krw']}원{unknown} | {runs} | {c['status']} / AAA {c['quality']} / PI {c['pi_acceptance']} |")
    for c in campaigns:
        lines += ["", f"**{c['campaign_id']} 후보 주장** (에이전트 작성, 미검증):", ""] + [f"- {claim[:400]}" for claim in c["claims"]] + ["", "에이전트가 스스로 밝힌 한계:", ""] + [f"- {lim[:300]}" for lim in c["limitations"]]
    return "\n".join(lines)


def _generate(destination: Path):
    snapshot = Store(ROOT / "control/state.sqlite").snapshot()
    measurements = []
    for event in snapshot["events"]:
        if event.get("event") == "development_research_result":
            receipt = json.loads(Path(event["receipt"]).read_text())
            measurements.append(receipt)
    initial = {domain: next((r for r in measurements if r["domain"] == domain and r["status"] == "SUCCEEDED"), None)
               for domain in ("wine", "duckdb", "diffusion")}
    runs = []
    for event in snapshot["events"]:
        if event.get("event") == "orx_launch":
            runs.append({"experiment_id": event["identity"]["experiment_id"], "run_id": event.get("run_id"),
                         "commit": event["identity"]["commit_sha"], "project_id": event["project_id"],
                         "launch_state": event["state"], "intent": event["intent"]})
    results = {"schema": "initial-project-research-report/v1", "generated_at": utc_now(),
               "evidence_scope": "DEVELOPMENT_BASELINES_AND_HYPOTHESES", "native_construction": "PAUSED",
               "autonomous_campaigns_completed": 0, "AAA": "UNASSESSED", "superiority": "NOT_ASSESSED", "PI": "PENDING",
               "orx_project": "4d54d8cb-64b6-4091-a739-85cf18a15d94", "runs": runs,
               "development_runs": [{"id": r["id"], "domain": r["domain"], "status": r["status"], "result_sha256": r["result_sha256"],
                                     "output_path": r["output_path"], "resources": r["resources"], "timing_admissibility": r.get("timing_admissibility")} for r in measurements],
               "accounting": {"charges": snapshot["charges"], "compute": snapshot["compute"]},
               "decisions": [r for r in snapshot["records"] if r["type"] == "DecisionRecord"]}
    rows = []
    if initial["wine"]:
        data = initial["wine"]["result"]["result"]
        results["wine"] = {"observations": data["observations"], "hypothesis_result": data["hypothesis_result"], "input_files": data["input_files"]}
        scores = data["observations"]
        pooled = scores["pooled_extra_trees"]["metrics"]["equal_weight_mae"]
        separate = scores["separate_color_extra_trees"]["metrics"]["equal_weight_mae"]
        rows.append(f"| Wine | pooled ExtraTrees {pooled:.6f}, 색상별 ExtraTrees {separate:.6f} 동일가중 MAE | 차이가 작음. 한 개발 분할의 우위·일반화는 미확정 |")
    if initial["duckdb"]:
        data = initial["duckdb"]["result"]["result"]
        results["duckdb"] = {"comparison": data["comparison"], "median_total_seconds": data["median_total_seconds"], "verification": data["verification"]}
        comparison = data["comparison"]
        lower, upper = comparison["ci95"]
        rows.append(f"| DuckDB | 준비 비용 포함 {100*comparison['observed_reduction']:.2f}% 감소, 대응 bootstrap95%구간 {100*lower:.2f}–{100*upper:.2f}%, {comparison['paired_repeats']}쌍 | 질의 답 동등. 개발 Q1 재구성 범위; 최종 목표 달성은 미확정 |")
    if initial["diffusion"]:
        data = initial["diffusion"]["result"]["result"]
        ratios = [1-c["candidate_total_reduction_against_fastest_baseline"] for c in data["cases"] if c["candidate_total_reduction_against_fastest_baseline"] is not None]
        results["diffusion"] = {"verification": data["verification"], "cases": [{k:c[k] for k in ("grid", "epsilon", "angle_radians", "fastest_correct_baseline", "candidate_total_reduction_against_fastest_baseline", "summary")} for c in data["cases"]]}
        rows.append(f"| 이방성 확산 | {len(data['cases'])}개 개발 설정, 세 해법 정확성 통과. AMG 총비용은 가장 빠른 기준선의 {min(ratios):.2f}–{max(ratios):.2f}배 | 이번 크기·우변 수에서 AMG 이점 없음. 더 넓은 범위 일반화는 하지 않음 |")
    reproduction = ROOT / "control/wine-reproduction-check.json"
    if reproduction.exists():
        results["wine_reproduction"] = json.loads(reproduction.read_text())
    campaigns = []
    for candidate_path in sorted((ROOT / "control/campaigns").glob("*/*/*/candidate-*.json")):
        candidate = json.loads(candidate_path.read_text())
        session_dir = candidate_path.parent
        journal = json.loads((session_dir / "model-requests.json").read_text()) if (session_dir / "model-requests.json").exists() else []
        observations = [e for e in snapshot["events"] if e.get("event") == "hypothesis_observation" and e.get("project_id") == candidate["project_id"] and e.get("team_id") == candidate["team_id"]]
        seen = set()
        unique_runs = [o for o in observations if not (o["run_id"] in seen or seen.add(o["run_id"]))]
        charges = [c for c in snapshot["charges"] if c["project"] == candidate["project_id"]]
        campaigns.append({"campaign_id": candidate["project_id"], "team_id": candidate["team_id"], "session_id": candidate["session_id"], "model_id": candidate["model_id"],
                          "status": candidate["status"], "quality": candidate["quality"], "superiority": candidate["superiority"], "pi_acceptance": candidate["pi_acceptance"],
                          "model_requests": len(journal), "model_request_states": {s: sum(1 for e in journal if e["state"] == s) for s in {e["state"] for e in journal}},
                          "total_tokens": sum((e.get("usage") or {}).get("totalTokens") or 0 for e in journal),
                          "charges_settled": sum(1 for c in charges if c["state"] == "SETTLED"), "charges_unknown": sum(1 for c in charges if c["state"] == "UNKNOWN"),
                          "actual_krw": sum(c["actual"] or 0 for c in charges if c["state"] == "SETTLED"),
                          "orx_runs": [{"run_id": o["run_id"], "experiment_id": o["experiment_id"], "status": o["result_status"], "receipt_sha256": o["receipt_sha256"]} for o in unique_runs],
                          "claims": candidate["claims"], "limitations": candidate["limitations"], "candidate_file": str(candidate_path)})
    results["autonomous_campaign_sessions"] = campaigns
    results["autonomous_campaigns_with_submitted_candidate"] = len(campaigns)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "first-results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    report = """# 첫 실행 보고

실제 공개 자료·수치 문제에서 세 분야 기준선과 첫 가설 시험을 시작했다. 이는 **개발 연구 측정**이다. 자율 B/P 캠페인12개, AAA, 독립 최종 평가와 PI 완료 판정은 별도이며 아직 완료되지 않았다. Native ARGO 건설 중지는 유지한다.

| 분야 | 관측 | 현재 해석 |
|---|---|---|
""" + "\n".join(rows) + """

Wine은 새 ORX 프로세스에서 같은 데이터·seed로 재학습했고 세 방법의 예측 파일 해시가 일치했다. 이 재현은 새 독립 데이터 표본이 아니다. 모든 자료의 중복 입력 그룹을 분할 간 격리했고, 최종·후속 자료는 작업 컨테이너에 마운트하지 않았다.

""" + campaign_section(campaigns) + """

첫 Wine 노드는 다른 프로젝트의 LiveKit 컨테이너 존재를 감지해 학습 전에 중단됐다. 실패를 보존하고 별도 수정 노드로 실행했다. 기존 서비스는 건드리지 않았다. 개발 성능 측정에는 기존 저활동 서비스의 전후 CPU 표본만 있으며 연속적인 무경쟁 환경 증명은 없다. 따라서 개발 timing만으로 최종 최소10% 개선을 확정하지 않는다. ORX 대시보드 연결 중단 후에도 기존 실행 ID로 종료 결과를 회수했고 재실행으로 바꾸지 않았다.

ORX 프로젝트는 `4d54d8cb-64b6-4091-a739-85cf18a15d94`, 고정 명령은 `/opt/homebrew/bin/python3 runner.py`다. 각 노드의 커밋·실행 ID·결과 해시·자원 기록은 [수치와 실행 목록](first-results.json)에 있다. 첫 준비와 초기 노드 이후 소스 수정은 새 커밋에만 적용했다. 원본·실패·이전 설계는 보존했다.

다음은 모델 경로·과금의 실제 인증, 독립 역할 전달과 새 감독 세션, B/P 정상 캠페인, 중단·모델 교체, 최종 평가의 비노출을 연결하는 일이다. 모델 카탈로그·로그인·프롬프트·모의 검사만으로 이 연결을 완료 처리하지 않는다. 추가 과금300000원·프로젝트8시간/8 CPU-core-hours·합계4 CPU/4.5GiB 상한은 유지한다. 미확인 사용량은0으로 처리하지 않는다.

[현재 실행 규약](README.md) · [대시보드](../../../.planning/2026-09-09-project-research-execution/dashboard.html) · [통합 검토](../../../.planning/2026-09-09-project-research-execution/integration-review.md)
"""
    (destination / "first-report.md").write_text(report, encoding="utf-8")
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = generate(args.output)
    print(json.dumps({"generated_at": result["generated_at"], "development_runs": len(result["development_runs"]), "autonomous_campaigns_completed": 0}))


if __name__ == "__main__":
    main()
