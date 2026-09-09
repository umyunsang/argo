# STATISTICS 원문 보존·부분 독서 기록

- 기준일: 2026-09-05 KST. 상태: 보존, 부분 재열람, 서지·독서 locator 기록 완료.
- 소유 범위: 이 폴더와 상위 `statistics-review.md`만. 원시 실험·테스트·네이티브 구현·외부 위임 없음.
- **전체 파일을 다운로드하거나 전체 텍스트를 추출한 것과 논문 전체를 읽은 것은 다르다. 다섯 자료 모두 전체 정독으로 표시하지 않는다.**
- 이 파일들은 추가 요청 후 다시 받은 bytes다. 이전 `web.run` 응답의 원래 bytes를 복원한 것이 아니며, 이전 열람 자료와의 바이트 동일성을 주장하지 않는다.
- `manifest.json`에 각 요청 URL, effective URL, 수신 시각, HTTP 상태, byte 수, SHA256, PDF 페이지 수와 구조화된 독서 범위를 기록했다. 원시 응답 헤더와 curl 수신 기록도 함께 보존했다.
- PDF 페이지는 파일 첫 페이지를 1로 센 물리 페이지다. 인쇄 페이지가 다른 ACL은 둘 다 적었다. HTML은 페이지를 만들지 않고 section anchor 또는 항목명과 보존 추출문의 행을 사용한다.
- `*.txt`는 검색·locator 확인용 기계 추출물이다. 원문 bytes는 PDF/HTML이다. 행 번호는 현재 보존 추출물에만 유효하다.

## 1. 보존 bytes 및 SHA256

| 자료 | 파일 | bytes | SHA256 |
|---|---|---:|---|
| S1 | `s1-hal-v1.html` | 690,370 | `1ee00bb2aa96262a03f64af4151d50f998bb21ada66103b6f1e40323692029c1` |
| S1 | `s1-hal-v1.pdf` | 12,428,285 | `f224b5ef6ec2a9e1606878e39e81acd4e0ed8ac9f4d80b120f17266c5c281d0f` |
| S1-status | `s1-iclr2026-poster.html` | 85,183 | `9c902266769f5abdf0d81913e9d7782d7c16eaf9ac1e20a7c6a79a72164a9560` |
| S2 | `s2-agarwal2021.pdf` | 10,255,284 | `7553e280d4a1560860bc5f6be2d70539fc5b510e0e3bb2d556824e51e9a80252` |
| S3 | `s3-dror2018.pdf` | 239,199 | `e3b6e07cf7e404443e4b516db9b2a72c5d24a38285a9a6691ed2e3b01b02235b` |
| S4-failed-mirror | `s4-unimelb-access-denied.html` | 5,743 | `419f7da0fa61413cfd4facf685a6c49976d3ffc0a3edbfe84f937e8d32ed4948` |
| S4 | `s4-pmc.html` | 196,972 | `470216ff8fd08b072dde4e1ace1bcc19ad9cf66b727b25ab954ac6e3d2c66bf8` |
| S4-failed-pdf | `s4-pmc-pdf-access-check.html` | 1,817 | `1b676cdc96b00a5b2c387590e50be234e543a4c60136ae5ca4f9662e00f7a831` |
| S5 | `s5-neurips-checklist.html` | 72,682 | `46407b080e1f16ae1548b27e44d441df5768fd59429b30e8fbab771553be1371` |

S1-status는 출판 상태 확인용 페이지이며 독립된 여섯 번째 연구논문이 아니다. S4-failed 두 파일은 접근 실패 증거이며 일차 본문으로 세지 않는다. 성공한 본문: HAL v1 PDF/HTML, Agarwal PDF, Dror PDF, Nosek PMC HTML, NeurIPS 공식 지침 HTML.

## 2. 실제 읽은 범위와 정확한 locator

이전 검토의 선택 구간은 `statistics-review.md` §2에 남겼다. 다음은 **이번에 보존한 bytes에서 실제 재열람한 범위**다. 이전 기록만 있는 구간과 이번 재열람을 합쳐 전체 정독으로 부풀리지 않는다.

### S1 — HAL, arXiv v1

- 원문: https://arxiv.org/html/2510.11977v1 ; https://arxiv.org/pdf/2510.11977v1
- 보존 PDF: 66쪽. 일부 파일 형식 도구의 휴리스틱 출력이 아닌 `pdfinfo` 기준이다.
- Appendix A2 선택 산문, PDF pp.19–20: `s1-hal-v1.txt` L1370–1388(오케스트레이션·logging), L1400–1438(task runner·timeout·exceptions·agent/benchmark 분리). HTML `#A2`.
- Appendix A3 도입과 항목 1–12, PDF pp.20–21: L1439–1503; HTML `#A3`. 실제 인용의 중심은 항목 1(대부분 단일 실행의 불확실성 한계), 2(endpoint 교체), 5(인프라 false negatives), 8(reasoning label 비비교성)이다. 주변 항목을 읽었다고 모두 ARGO 주장으로 채택하지 않는다.
- Appendix A4.2 “Fundamental constraints”, PDF p.22: L1545–1571; HTML `#A4.SS2`. provider parameter, latency variation, failure analysis의 인과성 한계 산문을 읽었다.
- 이전 검토 기록에만 있는 추가 선택 구간: §1, §4.2, A4.1, A5. 이번 보존 재열람 범위에 추가하지 않는다.
- 미열람: 66쪽 전체, 모든 결과 표·곡선·프롬프트, ICLR 최종 OpenReview PDF, 발표 영상. v1과 최종본 동일성 미확인.
- 출판 상태 근거: https://iclr.cc/virtual/2026/poster/10006806 ; `s1-iclr2026-poster-html.txt` L1–2 및 L25–28의 제목·학회·포스터 날짜·저자만 상태 확인에 사용. ICLR 2026 발표와 읽은 v1을 구분한다.

### S2 — Agarwal et al., NeurIPS 2021

- 원문: https://proceedings.neurips.cc/paper_files/paper/2021/file/f514cec81cb148559cf475e7426eed5e-Paper.pdf
- 보존 PDF: 17쪽.
- §2 Formalism, PDF pp.2–3: `s2-agarwal2021.txt` L132–202. 과제 M × 독립 run N의 모형, seed와 run의 차이 각주, 정규화·집계 및 CI 해석 산문을 읽었다.
- §4 및 §4.1 도입, PDF p.5: L351–360. §4.1의 층화 재표집 설명, PDF p.6: L419–434.
- Figure 6 캡션·설명, PDF p.6: L401–418. 적은 반복에서 명목 coverage와 실제 coverage가 어긋날 수 있다는 저자 설명을 읽었다. 그래프 전체의 좌표·수치 판독 또는 재현은 하지 않았다.
- 이전 기록에만 있는 추가 선택 구간: §3, §4.2. 보존본의 새 재열람으로 세지 않는다.
- 미열람: 17쪽 전체, 모든 부록·증명·그림, bootstrap 구현·시뮬레이션 재현. 논문의 특정 run 수를 ARGO 표본 수로 채택하지 않았다.

### S3 — Dror et al., ACL 2018

- 원문: https://aclanthology.org/P18-1128.pdf ; DOI https://doi.org/10.18653/v1/P18-1128
- 보존 PDF: 10쪽. 논문 인쇄 범위 1383–1392.
- §3.2.2 McNemar/Wilcoxon 및 주변 분류 산문, PDF p.5 = 인쇄 p.1387: `s3-dror2018.txt` L233–278.
- §3.2.2 permutation/paired bootstrap 및 §3.3 선택 논의 일부, PDF p.6 = 인쇄 p.1388: L287–327. 이 추출물은 2단 조판의 행을 함께 표시하므로 상세 인용 시 PDF에서 열을 확인한다.
- §5 “Open Questions”의 관측 의존성·cross-validation 논의 일부, PDF p.8 = 인쇄 p.1390: L441–461.
- 이전 기록에만 있는 추가 선택 구간: §2.1, §4. 미열람: 10쪽 전체, 문헌이 인용한 최초 검정 논문들, 구현·calibration. 이 ACL 방법론 논문을 검정의 최초 원전으로 부르지 않는다.

### S4 — Nosek et al., PNAS 2018

- **이번에 보존·읽은 원문은 PDF가 아닌 PMC 논문 HTML**: https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500/
- `#s3` “Preregistration Distinguishes Prediction and Postdiction”; `#s4` “Preregistration in Practice” 도입; `#s5` The Ideal; `#s6`, `#s7`, `#s8` Challenges 1–3. `s4-pmc-html.txt` L229–282. 사전 결정과 사후 설명, 계획 변경, 가정 위반, 기존 자료에서의 비열람 조건에 관한 선택 구간을 읽었다.
- `#s20` Conclusion: L384–385. 전체 논문 정독이나 모든 경험적 참고문헌 검토는 아니다. 출력에 함께 나온 Challenge 4 일부·감사·이해관계 문구는 이 권고의 근거 구간으로 채택하지 않았다.
- 논문 전체 서지 페이지 2600–2606 및 호 발행일 2018-03-13은 보존 HTML 메타데이터에 있다. 온라인 날짜 2018-03-12는 이전 검토의 서지 확인을 유지한 것으로, 이번 PMC 메타데이터에서 새로 확인했다고 주장하지 않는다.
- 이전 검토의 세부 PDF 페이지 2601–2603, 2605는 이번에 재검증하지 않았다. 정확한 현재 인용 locator는 위 HTML anchor이며, HTML 구간을 보존하지 못한 PDF의 페이지와 일치한다고 인증하지 않는다.
- 미열람: 사용 가능한 PDF bytes, 논문 전체, Challenges 4–9 전체, 인용된 개별 실험의 원문.

### S5 — NeurIPS 공식 Paper Checklist

- 원문: https://neurips.cc/public/guides/PaperChecklist
- 페이지 없는 공식 지침. 버전/개정일을 화면의 2026 탐색 연도에서 추정하지 않는다.
- 항목 1 “Claims”, 2 “Limitations”: `s5-neurips-checklist-html.txt` L54–62.
- 항목 6 “Experimental Setting/ Details”, 7 “Experiment Statistical Significance”, 8 “Experiments Compute Resource”: L101–124.
- 실제 읽은 것은 주장 범위, 독립성 등 가정·소표본 한계, 설정 명시, error bar의 변동 원인·계산법·SD/SE, 실패·예비 실험을 포함한 compute 공개 지침이다.
- 미열람: 나머지 모든 항목·연결 정책 전체. 공식 보고 지침이지 통계법의 효능 실험이 아니다. 원문의 예시 숫자를 ARGO의 유의수준·표본 수로 채택하지 않는다.

## 3. 접근 제약과 대체 경로

- 대학 PDF 요청: https://psychologicalsciences.unimelb.edu.au/__data/assets/pdf_file/0007/2888098/The-preregistration-revolution.pdf — HTTP 403, 5,743-byte HTML. `s4-unimelb-access-denied.html` 및 수신 기록을 보존. PDF라고 명명하거나 성공으로 세지 않았다.
- PMC PDF 요청: https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500/pdf/pnas.201708274.pdf — HTTP 200이지만 “Preparing to download ...” HTML. `s4-pmc-pdf-access-check.html` 및 `s4-pmc-pdf-response.fetch.txt` 보존. 접근 절차를 우회하지 않았고 PDF를 받았다고 하지 않는다.
- PMC 논문 페이지는 HTTP 200 정상 본문이며 title·DOI·section anchor 및 본문 산문을 확인했다. 이 HTML을 S4의 보존 일차 본문으로 삼았다.
- 이전 HAL 최종 OpenReview PDF 접근 제약은 기존 리뷰의 한계로 유지한다. 이번에는 최종 PDF를 다시 요청하지 않았으므로 새로운 실패 영수증도 없다. 공식 포스터 상태와 arXiv v1 본문만 보존했다.
- 이번 `web.run` 호출은 수행했으나 표시된 응답에 보존 가능한 본문 payload가 없었다. 실제 보존 bytes는 직접 HTTP 수신분이며 `web.run` 원래 응답을 저장했다고 주장하지 않는다.
- 초기 복합 터미널 출력 일부는 잘렸으므로 중요 본문을 작은 범위로 다시 읽었다. 검색어 hit나 추출 성공만으로 독서 완료를 판단하지 않았다.

## 4. 인계와 무결성 경계

- 공개 통계 인용은 `agarwal2021statistical`, `dror2018hitchhikers`, `nosek2018preregistration` 3편이다. `references.bib`와 상위 리뷰 §5가 일치하며, §4의 한국어 문구도 이 3편만 인용한다.
- 통합 결정(2026-09-05 KST): HAL은 최종 학회 PDF 미열람 때문에 공개 참고문헌에서 제외한다. S1 원문·수신 기록·실제 읽은 v1 범위와 버전 한계는 비공개 현재 연구 검토로 보존하며 최종본 추가 탐색은 하지 않는다.
- 고정 예산 estimand는 본 연구의 자체 정의·방법론적 제안이며 관측된 효과가 아니다. HAL이나 나머지 세 논문이 이 정의를 검증했다는 식으로 인용하지 않는다.
- 과제/중첩 rollout, paired 비교, 예산 estimand, 실패 유형 및 탐색/확증·중단 구분은 **적용 조건이 있는 방법 제안**이며 새 실험계획 승인이 아니다. 프로젝트 PASS 숫자와 격리 상태는 사용자 제공 맥락이지 이 문헌의 경험적 결과가 아니다.
- `SHA256SUMS`는 원문·파생 추출문·수신 기록·서지·이 README·manifest의 내용 무결성을 점검한다. checksum 파일 자체는 자기 참조 때문에 제외한다.
- 해시 일치는 현재 보존 파일이 바뀌지 않았다는 확인일 뿐, 학회 최종본 동일성·전체 정독·프로젝트 실험 타당성 인증이 아니다.
- 별도 재검증이 필요해지기 전에는 문헌 확장·PDF 우회 획득을 계속하지 않는다. 이 범위로 초안 문구의 추적 가능성을 확보했으므로 연구를 종료한다.
