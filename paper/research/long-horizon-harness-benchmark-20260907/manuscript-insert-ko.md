# 장기 지평 에이전트의 상태 보존과 검증: 관련 연구 보충 초안

> 편집 상태: 원문 검토에 따른 삽입 후보이다. 기존 원고에 적용하지 않았으며, 기존 근거 마감일과 인용 번호는 별도 편집 검토가 필요하다. 아래 성과는 선행연구 저자의 보고이며 본 연구에서 재현한 결과가 아니다.

## 관련 연구

대규모 언어모델 기반 에이전트의 연구 대상은 단일 응답의 생성에서 지속적인 실행 상태, 장기간의 정보 관리, 반복적 검증을 포함하는 시스템으로 확장되고 있다. Karten 등의 *Prime Agent: A Self-Improving RLM Harness*는 영속 실행 환경, 재귀적 하위 세션, 메시지 전달과 버전 관리되는 보조 상태를 결합한다. 이 연구는 장기 실행의 가능성을 보여 주는 동시에, 일부 비교에서 최종 성과 차이가 실험 잡음에 비해 작고 잘못된 전략도 지속 상태에 축적될 수 있음을 보고한다. 따라서 장기간 동작한 사실을 과제 성공이나 올바른 자기 개선과 동일시할 수 없다. [1]

Yan 등의 *Harness-of-Harness: Multi-Day Autonomous Software Development with Continual Improvement*는 고정된 하네스–모델 조합을 계획–개발–평가의 반복으로 조직한다. 핵심은 현재 산출물과 실행 증거를 구분하고, 개발자의 자체 검사를 완료 판정과 분리하는 데 있다. 평가자는 고정된 후보를 읽기 전용으로 관찰하며, 확인된 기능은 보존 조건으로, 실패와 불충분한 증거는 다음 반복의 과제로 전달한다. 반복 횟수를 맞춘 추가 비교도 제시하지만, 동일 반복 수에서 사용한 토큰은 다르므로 이를 동일 총비용에서의 인과효과로 일반화하지 않는다. [2]

Wu 등의 *HarnessDev: Can LLMs Create and Evolve Their Own Agent Harness?*는 하네스를 주어진 실행 조건이 아니라 생성·개선되는 평가 대상으로 다룬다. 하네스를 작성하는 모델과 이를 실행하는 모델을 구분하고, 개발 중 피드백 성과와 후보 동결 후 미관측 과제 성과를 분리한다. 보고된 개선은 실행 모델과 평가 분포에 의존하며, 개발 점수의 상승이 미관측 과제의 개선과 항상 일치하지 않았다. 이는 자기 개선의 횟수보다 고정 후보의 전이 성능과 회귀 여부를 측정할 필요를 뒷받침한다. [3]

Lin 등의 *Context as an Environment: Programmatic Context Management for Long-Horizon Agents*는 상호작용 이력을 영속 이벤트 기록과 실행 가능한 세션 환경으로 보존하고, 모델이 코드를 통해 필요한 부분만 작업 문맥에 노출하도록 한다. 이때 무손실성은 제거된 이력의 주소와 원문이 보존된다는 의미이다. 필요한 근거를 찾아 노출하고 판단에 사용하는 과정까지 완전하게 보장하지는 않는다. 같은 기반 모델을 사용하는 가까운 비교군과의 차이, 이질적인 공개 시스템 기준과의 차이도 구분해야 한다. [4]

Tan 등의 *SkillZip: Contract-Preserving Graph Compression for Scalable Agent Skill Libraries*는 스킬 내부의 절차를 입력·조건·자원·행동·검증기·출력의 계약 단위로 표현한다. 반복 부분은 출처로 확장 가능한 매크로로 압축한다. 그 구조 복원 성질은 기록된 계약과 비충돌 치환 조건에 의존하며, 원문은 이 보장이 의미적 동치나 검증기 자체의 정확성을 뜻하지 않음을 명시한다. 따라서 의존성 연결과 검증 경로가 남아 있는지, 실제 근거가 충분한지, 외부 과제가 성공했는지는 서로 다른 평가 항목이다. [5]

Pan 등의 *RecEvolve: A Knowledge-Driven Autonomous Agent System for Recommender Systems*는 가설 제안, 비평, 구현, 학습, 평가를 지식 기반 루프로 연결한다. 저자들은 완료된 41개 실험과 추천 성능 개선을 보고한다. 그러나 배치 크기 변경에 따른 지표 편법은 사람이 발견했으며, 이전에 실패한 가설의 반복 탐색과 단기 평가에 치우친 탐색도 관찰했다. 부정 결과를 기록하는 것만으로는 충분하지 않고, 그 결과가 적용되는 데이터·평가·자원 조건과 재검토를 정당화하는 변경을 함께 보존해야 한다. [6]

Kim 등의 *Metaⁿ: Recursive Self-Improvement through Emergent Depth*는 개선 연산을 고정한 채 실행 이력과 이전 계층 코드에 반복 적용한다. 이 구조는 산출물을 만드는 코드까지 진단 대상으로 삼지만, 계층 간 간섭과 퇴행을 배제하지 않는다. 또한 과제별 archive 최대와 하나의 선택된 계층 사슬의 성능을 구분해야 한다. 과거 최선 점수의 단조 보존은 현재 유효한 근거와 새 과제 성능의 단조 개선을 의미하지 않는다. [7]

Wu 등의 *Terminal-Universe: Turning Agent Trajectories into Scalable Terminal Environments*는 기록에서 관찰된 변경 이전 파일을 재생하고 누락 부분을 보완하여 과제를 생성한다. 원문은 복원이 본질적으로 손실적임을 명시한다. 과제 수행에 충분하다고 판단된 환경은 원환경과 동일하게 복원된 환경과 다르며, 동일 모델이 과제·해법·검증기를 생성할 때 오류가 상관될 수 있다. 학습 데이터 선별과 연구 결과 보고의 실패 분모도 분리해야 한다. [8]

## 연구 질문의 정교화

선행연구를 종합하면 지속 상태, 반복 개발, 재귀적 개선, 절차 그래프 자체의 존재는 본 연구의 차별점을 구성하기에 충분하지 않다. 본 연구가 검토할 질문은 다음과 같다. **동일한 원문 접근, 결과 기반 탐색 트리, 명시적 버전·적용 조건과 자원 한도에서, 의존성에 따른 선택적 재검증 제어가 근거 교정 이후의 판단과 인계에 추가적인 가치를 제공하는가?** 이는 아직 실증되지 않은 가설이다.

이 질문을 평가할 때 원문 회수 가능성, 판단에 필요한 근거의 노출과 충분성, 현재 버전·조건에 대한 적용 가능성, 독립적인 과제 결과를 분리한다. 관련 조건 변경 시에는 영향을 받은 판단을 재검토하되, 무관한 결과는 보존해야 한다. 동일 조건의 실패를 이유 없이 반복하는 오류와 조건이 달라졌는데도 과거 실패를 영구 적용하는 오류를 동시에 측정한다. 주요 대조군에도 영속 원문 접근과 명시적 유효성 점검을 제공하여, 차이가 정보량이나 약한 대조군에서 비롯되지 않도록 한다.

스킬 압축, 재귀 깊이, 실행 모델 변경과 학습을 이 주 비교에 동시에 추가하지 않는다. 각 기제는 주 비교의 실패 분석이 해당 병목을 확인할 때 후속으로 분리한다. 학습용으로 선별한 성공 궤적은 별도의 파생 자료로 둘 수 있지만, 원래 연구 이력의 실패·무효·철회 기록을 제거하지 않는다. 최종 판단은 미관측 평가를 보고 다시 선택하지 않은 후보와 독립 과제 결과에 연결한다.

## 참고문헌 — 삽입 후보용 임시 번호

1. Karten et al. (2026). *Prime Agent: A Self-Improving RLM Harness*. arXiv:2608.23552v1. https://www.alphaxiv.org/abs/2608.23552
2. Yan et al. (2026). *Harness-of-Harness: Multi-Day Autonomous Software Development with Continual Improvement*. arXiv:2609.01481v1. https://www.alphaxiv.org/abs/2609.01481
3. Wu et al. (2026). *HarnessDev: Can LLMs Create and Evolve Their Own Agent Harness?* arXiv:2609.01437v1. https://www.alphaxiv.org/abs/2609.01437
4. Lin et al. (2026). *Context as an Environment: Programmatic Context Management for Long-Horizon Agents*. arXiv:2608.21690v1. https://www.alphaxiv.org/abs/2608.21690
5. Tan et al. (2026). *SkillZip: Contract-Preserving Graph Compression for Scalable Agent Skill Libraries*. arXiv:2608.05604v1. https://www.alphaxiv.org/abs/2608.05604
6. Pan et al. (2026). *RecEvolve: A Knowledge-Driven Autonomous Agent System for Recommender Systems*. arXiv:2609.01622v1. https://www.alphaxiv.org/abs/2609.01622
7. Kim et al. (2026). *Metaⁿ: Recursive Self-Improvement through Emergent Depth*. arXiv:2608.24735v1. https://www.alphaxiv.org/abs/2608.24735
8. Wu et al. (2026). *Terminal-Universe: Turning Agent Trajectories into Scalable Terminal Environments*. arXiv:2609.04148v1. https://www.alphaxiv.org/abs/2609.04148
