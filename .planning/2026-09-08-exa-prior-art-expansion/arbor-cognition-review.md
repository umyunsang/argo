# Arbor cognition 원문 검토

[Arbor: Tree Search as a Cognition Layer for Autonomous Agents](https://www.alphaxiv.org/abs/2606.12563), v1, 전체 추출본문899LF를 읽었다. AMD 연구진의 inference-serving 최적화 연구이며 공개 preprint다. 기존 코퍼스의 `Toward Generalist Autonomous Research via Hypothesis-Tree Refinement`(2606.11926)와 다른 논문이다. 서지·코드·효과를 Arbor라는 이름 하나로 합치지 않는다.

가장 중요한 설계 반례는 tree가 단순한 결과 보관함이 아니라는 점이다. 이 시스템은 tree를 공동 작업 상태로 쓰고, 실패의 진단·측정 조건·parameter-level KB가 이후 탐색을 제한한다. Orchestrator/Critic의 상호 제약도 있다(ARB-01/02). 따라서 G만 능동적 근거 제어를 수행한다는 넓은 주장은 성립하지 않는다. B/C 대조군의 원문·실패·복구 권리와 공통 측정 유효성 검사는 유지해야 한다.

no-DFS 조건은 단일 비구조화 agent와 복구 경로 부재를 함께 포함한다. no-Critic은 accuracy gating 누락과 concurrency 변경으로 측정 자체가 무효해진다(ARB-03). 저자의 결과가 recovery나 측정 integrity 없이도 graph만 우월하다는 근거는 아니다. 우리 C-G 비교에서는 의무와 집행 강도를 맞추는 원칙을 강화한다.

실험 범위는 AMD serving 최적화다. 역할별 모델 배정은 capability tier 수준으로 서술되고 인퍼런스 throughput이 결과다. 독립 반복은2개 model/device 조합에서 각2campaign이며, 동일task의 반복을 넓은 programme 모집단으로 확장하지 않는다. best-throughput와 원칙상 hidden single-final artifact는 다르다(ARB-04/05). 부록에는 storage-full시 인간에게 에스컬레이션한 사례도 있으므로 모든 사례를 무개입 완전자율로 묶지 않는다(ARB-06).

채택할 것은 강한 tree-control 기제의 설계 참고다. 새 hardware benchmark나 추가 arm을 바로 실행하지 않는다. 현재 HousePrice P0, 전체 예산 회계, 단일 lock과 독립 final scoring은 그대로 둔다. 다음P1 specification에서 common measurement/recovery와 추가 research-policy obligation을 구분해야 한다. G-C는 graph-control package 증분이며 순수 topology나 최초 능동 제어가 아니다.
