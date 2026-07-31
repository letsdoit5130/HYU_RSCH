---
name: trade-gen3-un-partner-pipeline
description: trade-gen1-un-eda와 trade-gen2.1-un-sourcing를 한 번의 명령으로 순차 실행하는 오케스트레이터입니다. "파이프라인 전체 실행", "EDA부터 소싱까지 한번에", "새 품목 CSV로 전체 진행해줘" 요청 시 활성화됩니다.
---

# 🔗 Trade Partner Pipeline (원샷 실행 오케스트레이터)

`trade-gen1-un-eda` → `trade-gen2.1-un-sourcing`를 한 번의 명령으로 순차 실행합니다.
둘 다 결정적(deterministic) 스크립트라 CLI 한 줄로 안전하게 묶을 수 있습니다.

```bash
uv run python .agents/skills/trade-gen3-un-partner-pipeline/scripts/run_pipeline.py \
  --input <새 무역통계 CSV 경로> \
  --item "<품목명>" \
  --output_dir <프로젝트 폴더>
```

한 단계가 실패하면 다음 단계로 넘어가지 않고 즉시 중단합니다 (부분 실패를 성공으로 오인하지 않도록).

---

## ⚠️ 3단계(실제 파트너 검색)는 여기 포함되지 않습니다

`trade-gen2.2-un-partner-deep-mining`(실제 웹 검색으로 회사 찾기)은 AI의 실시간 판단이 필요한 작업이라
단일 CLI 명령으로 만들 수 없습니다. 이 스크립트 실행 후 아래처럼 **자연어로 AI 에이전트(Claude,
Gemini 등 `.agents/skills/`를 읽을 수 있는 코딩 에이전트)에게 요청**하면 이어서 3단계까지 한
세션 안에서 진행됩니다:

> "위 파이프라인 다 하고, 우선순위 상위 국가들 로컬파트너 실제로 찾아서 Verified_Partners에 정리해줘"

즉 "완전한 원샷"을 원하면 터미널에서 이 스크립트를 먼저 실행한 뒤, 또는 처음부터 AI 에이전트에게
"새 CSV로 파이프라인 전체 진행해줘"라고 말하면 1~3단계를 한 번에 이어서 수행합니다
(터미널에서 직접 돌릴 때만 이 스크립트가 1~2단계를 커버).

---

## 참고
- 1단계: `.agents/skills/trade-gen1-un-eda/`
- 2단계: `.agents/skills/trade-gen2.1-un-sourcing/`
- 3단계(온디맨드): `.agents/skills/trade-gen2.2-un-partner-deep-mining/`
