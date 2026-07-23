# GEMINI.md — Antigravity 운영 지시 (AI-Developer-KIT)

> Google Antigravity는 세션 시작 시 `AGENTS.md`와 이 `GEMINI.md`를 함께 읽고, 충돌 시 `GEMINI.md`를 우선합니다. 이 파일은 Antigravity 전용 지시만 담고, 실제 운영 계약은 `AGENTS.md`를 따릅니다.

## 이 작업 폴더는 AI-Developer-KIT로 운영됩니다

- **`AGENTS.md`를 이 워크스페이스의 운영 계약으로 삼아 그대로 따르세요.** 라우터 규칙·Phase 0~8 워크플로우·에이전트 카탈로그·선행조건 게이트가 거기에 있습니다.
- `.claude/` 폴더에는 Claude Code용 상세 에이전트·커맨드·라우터가 있습니다. Antigravity는 이를 **참조 자료**로 열어볼 수 있으나, 실행 계약의 정본은 `AGENTS.md`입니다.

## 세션 시작 시 (필수)

1. `AGENTS.md`를 로드해 라우터 계약과 Phase 흐름을 인지한다.
2. 사용자의 첫 메시지가 라우터 트리거(특히 **"지침에 따라 진행해"**)면, 임의로 구현을 시작하지 말고 **먼저 현재 상태(어느 Phase인지)를 판별해 다음 할 일 1개를 제시**한다.
3. `decision-lock.md` · `docs/07_architecture.md` · `tasks/task-list.md` 존재 여부로 진행 단계를 판단한다(없으면 해당 선행 Phase부터).

## "지침에 따라 진행해" 처리

- 응답 첫 줄에 `[ROUTER]`를 출력하고, `AGENTS.md`의 완성형 태그 블록(GATE/JUDGMENT/ITERATION_SCOPE) 중 맞는 것을 이어서 출력한다.
- 설명·미화 없이 **태그 블록 + 다음 질문 1개**만. 정보가 부족하면 구현하지 말고 `HOLD/NEED_INPUT`으로 멈춘다.

## 한 폴더 원칙

KIT는 지금 열린 이 폴더에서 동작합니다. 사용자에게 "Claude 등 다른 도구로 옮기라"고 안내하지 마세요 — **Antigravity 안에서 이 폴더를 대상으로 그대로 진행**하면 됩니다. 필요한 터미널 명령은 에이전트가 대신 실행합니다.

## 금지

- `AGENTS.md`의 선행조건 게이트를 건너뛰고 바로 코드 구현 ❌
- 라우터 태그 블록 생략 ❌
- 이 폴더 밖(사용자 전역 설정·시스템)으로 변경 확장 ❌
