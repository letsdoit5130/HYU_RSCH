# trade-gen3-un-partner-pipeline — 스킬 문서

> 사용법 자체는 상위 폴더의 [`../SKILL.md`](../SKILL.md)를 참고하세요. 여기서는
> **파이프라인에서의 위치**를 다룹니다.

---

## 1. 파이프라인에서의 역할

이 스킬은 새로운 단계가 아니라 **1단계+2단계를 한 번의 CLI 명령으로 묶은 오케스트레이터**입니다.
전체 5단계 흐름은 [`../../trade-gen-docs/README.md`](../../trade-gen-docs/README.md) 참고.

```
run_pipeline.py 한 번 실행
   │
   ├─▶ [1] trade-gen1-un-eda/scripts/generate_trade_eda.py
   │        (실패 시 여기서 즉시 중단 — 2단계로 넘어가지 않음)
   ▼
   └─▶ [2] trade-gen2.1-un-sourcing/scripts/generate_partner_sourcing.py
```

**입력**: 새 무역통계 CSV, 품목명, 프로젝트 폴더 (그대로 1단계 스크립트로 전달)
**출력**: 1단계 출력(EDA 리포트/차트) + 2단계 출력(Sourcing_Candidates 트래커) 전부
**포함되지 않는 것**: 3단계(실제 파트너 검색, `trade-gen2.2`)는 AI의 실시간 판단이 필요해
단일 CLI로 만들 수 없습니다. 터미널에서 이 스크립트만 실행했다면 이어서 AI 에이전트에게
자연어로 3단계를 요청해야 완결됩니다 (예: *"위 파이프라인 다 하고, 우선순위 상위 국가들 로컬파트너
실제로 찾아서 Verified_Partners에 정리해줘"*). 처음부터 AI 에이전트에게 "새 CSV로 파이프라인
전체 진행해줘"라고 요청하면 1~3단계가 한 세션 안에서 자연스럽게 이어집니다.

## 2. 언제 이 스킬을 쓰나

- **쓴다**: 이미 검증된 CSV로 1·2단계를 빠르게 반복 실행하고 싶을 때 (예: 데이터 재수집 후 재생성)
- **안 쓴다**: 1단계 리포트를 먼저 검토하고 2단계 실행 여부를 판단하고 싶을 때 — 이 경우
  `trade-gen1-un-eda`와 `trade-gen2.1-un-sourcing`을 따로 실행하세요.
