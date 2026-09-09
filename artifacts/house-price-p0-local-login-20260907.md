# House Price P0 전용 Prime 로그인

기존 운영자 인증 파일을 읽거나 복사하지 않고, 과제 전용 프로필에서 기존 ChatGPT 구독으로 로그인한다. A 선택과 P0 시작 승인을 다시 요청하는 것이 아니라 별도 프로필의 접근 설정이다.

다음 명령을 로컬 터미널에서 실행한다.

```sh
env PRIME_AGENT_CODING_AGENT_DIR=/Users/um-yunsang/.cache/argo-research/house-price-p0/prime-agent-profile-v1 PRIME_AGENT_TELEMETRY=0 /opt/homebrew/bin/prime-agent --cwd /Users/um-yunsang/.cache/argo-research/house-price-p0/prime-login-cwd-v1 --no-session --no-tools --no-extensions --no-skills --no-prompt-templates --no-themes --no-context-files --append-system-prompt ''
```

1. `/login`을 입력한다.
2. **ChatGPT Plus/Pro (Codex)**를 선택하고 브라우저 인증을 완료한다.
3. 모델에게 질문하지 말고 `/quit`으로 종료한다.
4. 대화에는 **로그인 완료**만 알린다. 토큰·`auth.json` 내용은 보내지 않는다.

로그인용 디렉터리는 비어 있는 별도 작업 폴더다. 실제 평가의 cwd/session은 따로 생성한다. 저장 위치는 분리되지만 OAuth 자체가 공급자 측 과제별 권한·비용 제한 토큰은 아니다. 실제 P0는 도구/컨테이너/실행 사양 검토가 끝난 뒤 시작한다.
