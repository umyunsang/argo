# House Price P0 준비 결과

**시작 승인은 기록됐으며, 실제 P0 학습은 아직 시작하지 않았다.**

완료: 필요한 데이터 2개 취득(행 값/라벨 미노출), 공식 규칙 확인, 고정 CPU 이미지 빌드, 합성 테스트17개와 clean commit `npm run check` 통과. 네이티브 변경·Kaggle 제출은0이다.

남은 새 중요 결정은 **신뢰 경계**다.

- **권장 A:** 기존 Prime와 검토된 확장 코드를 신뢰한다. 평가 모델은 task 도구만 호출하고, 생성 코드는 네트워크 없는 제한된 컨테이너에서 실행한다. 같은UID의 Prime 자체까지 OS 격리됐다고 주장하지 않는다.
- **B:** Prime controller/extension 전체를 별도 OS principal 또는 host에서 격리한다. 추가 host/credential-broker 구성과 검증이 필요하다.

A는 현재 네이티브를 수정하지 않는 최소 경로다. task 도구 공간을 제한한 통합 실행 가능성 P0로 해석하며, 변경 없는 Prime 성능이나 B/C/G 효과라고 하지 않는다. A/B 결정 뒤에도 도구팩·runner 구현, 데이터 분할·scorer custody, 실제 boundary negative tests와 고정 비용/시간/명령 검토는 필요하다.

[상세 준비·범위 기록](../paper/research/public-ml-programme-qualification/house-price-p0/integration/preparation-summary-ko.md)

[시작 승인 기록](../paper/research/public-ml-programme-qualification/house-price-p0/start-user-confirmation-v1.json) · [환경 검증](../paper/research/public-ml-programme-qualification/house-price-p0/environment-build-v1.json) · [커밋된 scorer 검증](../paper/research/public-ml-programme-qualification/house-price-p0/scorer-immutable-validation-v1.json)
