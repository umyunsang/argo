# UI-parity 방법론 문헌 합성 v1

상태: **범위 제한 방법론 맥락**. 이 문서는 ARGO 효능이나 DiscoveryWorld 성능 결과를 추가하지 않는다. 원문 PDF와 `pdftotext -layout` 파생 바이트의 해시는 `receipts/ui-parity-method-literature-read-v1.json`에 고정했다.

## 현재 설계에 주는 결론

1. **재현 동일성과 과제 정답성은 다르다.** `Deterministic Replay for AI Agent Systems`는 실행을 순서가 있는 typed step sequence로 모델링하고 strict replay에서 trace miss를 live network로 대체하지 말아야 한다고 정의한다. 그러나 그 fidelity는 기록된 출력의 재현일 뿐 task truth가 아니다. 현재 UI-parity 실험도 UI/state trace 동일성만 판정하며 task outcome이나 adapter의 일반적 정확성을 주장하지 않는다.
2. **미관측을 제거하면 안 된다.** `How Many Tasks Are Enough for Agent Benchmark Decisions?`는 decision error, group coverage, unresolved/defer 비율을 함께 요구하고 unresolved 사례를 조건부 오류율 분모에서 보존한다. 현재 controller가 timeout/crash/malformed를 `UNOBSERVABLE`로 만들고 하나라도 있으면 PASS를 금지하는 규칙과 일치한다.
3. **부분 증거의 범위는 사전에 고정해야 한다.** 같은 논문은 threshold, reveal order, grouping, decision rule, unresolved target을 함께 보고해야 한다고 지적한다. 현재 실험은 두 family, seed 0–4, 고정 action/tick, official 1회와 UI-only 2회, 1,000 transition을 manifest에서 미리 고정한다. 따라서 독립 추론 단위는 family `n=2`이며 다른 family, policy, task-solving 성능으로 외삽하지 않는다.
4. **harness와 model 효과를 분리하지 않은 비교는 배치 구성 비교다.** `HarnessRisk`는 안전을 model+harness의 결합 속성으로 정의하고 utility, attack success, persistence, detection을 분리한다. 동시에 저자들은 cross-harness 결과가 harness-only causal effect가 아니며 provider failure 제외와 judge 오차가 남는다고 명시한다. 향후 ARGO 효능 연구는 동일 model/resource/evidence 조건을 고정하고 invalid/null을 교체하지 않아야 한다.
5. **“sandbox”라는 이름만으로 OS 경계를 주장할 수 없다.** `HarnessRisk` 부록은 자체 sandbox가 kernel namespace, chroot, firewall이 아닌 process/configuration isolation이라고 명시한다. 현재 UI-parity 준비는 별도 `sandbox-exec` OS policy로 network를 허용하지 않고, engine repository·credential store·다른 test instance read를 거부하며, child write를 임시 cell directory로 제한한다. 실제 DiscoveryWorld cell에서 이 경계가 작동했는지는 아직 `NOT_RUN`이고 승인 전 claim으로 사용하지 않는다.

## 채택하지 않은 주장

- `2607.16200v1`의 평가 문장은 “5 workloads × 5 replay”와 `n=250`을 동시에 제시하여 표시된 산술이 맞지 않는다. 따라서 그 논문의 100% fidelity/98.3% latency 수치는 ARGO 근거로 채택하지 않는다.
- `2608.17597v1`의 수치 결과는 LLM judge와 valid-run filtering에 조건부이다. ARGO의 deterministic primary scorer를 대체하지 않는다.
- 세 논문 모두 현재 버전의 외부 preprint이다. 원리와 한계는 설계 맥락으로만 사용하고 독립 재현으로 간주하지 않는다.
