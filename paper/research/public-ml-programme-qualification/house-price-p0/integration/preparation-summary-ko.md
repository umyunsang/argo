# House Price P0 준비 결과와 실행 경계 결정

## 완료

- 사용자 과제 선택 `49159554`, 약관·데이터·실제 P0 승인 `f1601306`, 시작 재확인 `dc771d57`을 기록했다. 같은 권한을 다시 요청하지 않는다.
- `home-data-for-ml-course`의 공식 규칙/평가/데이터 설명을 공개 API에서 읽었다. Kaggle 공식 로그 RMSE와 선택된 MLAgentBench의 달러 단위 MAE는 다른 평가다.
- 필요한 `train.csv`와 설명 파일만 저장소 밖에 받았다. 1,460행·81열·ID 고유성과 해시만 연구 기록에 남겼다. 행 값·라벨·토큰은 공개 저장소/모델 입력/자식 작업자에 제공하지 않았다. 약관 수락 API나 Kaggle 제출은 수행하지 않았다.
- 고정 base digest와 10개 exact wheel version/hash로 Linux arm64 CPU 환경을 만들었다. 첫 빌드는 지원하지 않는 출력 옵션 `--progress`로 시작 전 실패했다. 같은 recipe에서 그 옵션만 뺀 두 번째 빌드가 성공했다.
- 이미지 `sha256:cd43d0d8edac942bd67cd097caf08edd2def45016bf011c1635849f15ebc7835`의 Python 3.11.16·패키지 import, 실제 비root/네트워크 없는 컨테이너에서 합성 테스트 17개가 통과했다.
- strict MAE scorer는 자식 소유 commit `3c99042ae951b7d6bbc85dcd9a4d55f4a6c7d39a`에 고정했다. 별도 clean clone에서도 17 tests와 `npm run check`가 통과했다.

## 아직 실제 P0는 시작하지 않았다

현재 구현된 것은 parser/math와 산출물 byte binding, 실행 패키지 환경이다. 실제 평가 모델 도구팩, 고정 ORX/Docker runner, 데이터 분할/격리 manifest, 정확한 model/runtime/cost 상한과 실제 boundary negative tests는 아직 필요하다. 정적 검사 성공을 P0 성공·라벨 격리·아키텍처 효능으로 바꾸지 않는다.

## 중요한 선택: 신뢰하는 구성요소

독립 runtime source audit는 기존 Prime 0.9.2에서 아래 **권장안 A**가 조건부 가능하다고 판단했다.

- 기존 Prime worker·검토한 task extension·OS/Docker·trusted scorer를 신뢰 기반으로 둔다.
- 평가 모델은 별도 fresh headless session에서 정확한 task 도구만 사용한다. 임의 host REPL/shell/file/MCP/RLM 도구는 없다.
- 모델이 만든 코드는 네트워크 없는, 제한된 파일·CPU·메모리의 고정 컨테이너에서만 실행한다.
- 원본/hidden labels와 raw stdout은 모델에게 반환하지 않는다. 최종 locked prediction만 trusted scorer에 넘긴다.

이 방법은 **평가 모델과 생성 코드**를 제한한다. 같은 UID의 Prime/extension 자체가 host 파일을 읽을 수 없다는 주장은 하지 않는다. Root는 기존 RLM으로 연구 준비/독립 검토를 계속하지만 평가 controller를 기존 RLM 자식의 열린 REPL로 만들지 않는다.

**대안 B**는 controller와 extension 전체를 별도 OS principal/host에서 격리하는 것이다. 별도 host·credential broker·설정 범위가 필요하므로 지금의 구현이나 권한이 있다고 가정하지 않는다.

A는 네이티브 코드를 고치지 않고 현재 Prime 인터페이스를 쓰는 최소 P0 경로다. 다만 도구 공간이 줄어들므로 결과는 제한된 통합 실행 가능성으로 해석한다. 변경 없는 Prime/RLM의 성능이나 B/C/G 인과 효과가 아니다. 후속 arm은 동일 경계·도구·환경·scorer·budget을 공유해야 한다.

**확인할 사항은 A/B 신뢰 경계이지 시작 승인이 아니다. 권장안 A로 진행할지 사용자 확인 후, 실제 escaping/output/cancellation/caps 검사를 통과한 고정 프로토콜에서만 실행한다.**

## 보존과 다음 단계

프로토콜/경계 원검토는 `integration/` 사본에 원형 보존했다. root 검증은 `preparation-intake-v1.json`, 환경은 `environment-build-v1.json`, 커밋된 scorer 검증은 `scorer-immutable-validation-v1.json`, 현행 권위는 상위 `effective-authority-v3.json`, 현재 진행 지점은 `working-frontier-v2.json`이다. 모든 HousePrice 작업자는 완료 후 해제했고, 임시 ORX dashboard와 합성 검사 컨테이너도 종료했다.

원본 데이터·토큰·개인 프로젝트 내용은 이 준비 bundle에 없다. 실제 House Price training/model/scorer calls는 0, Kaggle submissions는 0, native changes는 0이다. ResearchDone와 원고 gate는 여전히 닫혀 있다.
