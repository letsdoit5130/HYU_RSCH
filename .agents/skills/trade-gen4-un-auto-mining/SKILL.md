---
name: trade-gen4-un-auto-mining
description: trade-gen2.2-un-partner-deep-mining을 완전 자동화한 버전입니다. GitHub Actions에서 Gemini API(Google Search grounding)를 직접 호출해 사람/AI 세션 개입 없이 실제 파트너를 찾아 Verified_Partners 시트에 병합합니다. "완전 자동화", "컴퓨터 꺼도 계속 조사", "API로 자동 리서치" 요청 시 활성화됩니다.
---

# 🤖 Trade Gen4 — 완전 자동 딥마이닝 (Gemini API + Search Grounding)

`trade-gen2.2-un-partner-deep-mining`은 Claude Code 같은 대화형 AI 세션이 WebSearch/WebFetch로
직접 조사하는 방식이라 **세션(컴퓨터)이 꺼지면 멈춘다.** 이 스킬은 그 한계를 없애기 위해
GitHub Actions에서 Gemini API를 직접 호출해, 사람 개입·컴퓨터 전원과 무관하게 클라우드에서
완전 자동으로 실제 회사를 검색·검증·병합한다.

---

## ⚠️ 시작 전 필수 설정 — Gemini API 키 Secret

이 스킬은 **API 키 없이는 작동하지 않습니다** (당연히, 아무도 몰래 대신 검색해주지 않습니다).

1. https://aistudio.google.com/apikey 에서 Gemini API 키 발급
2. GitHub 저장소 → **Settings → Secrets and variables → Actions → New repository secret**
   (⚠️ Codespaces/Dependabot secrets가 아니라 **Actions** 탭이어야 하고, "Environments"가 아니라
   **"Repository secrets"**여야 워크플로우가 `environment:` 지정 없이도 읽을 수 있다)
3. 이름은 자유롭게 지어도 된다 — **이 저장소는 `HAEYU_RESEARCH`라는 이름으로 등록돼 있고**,
   `.github/workflows/auto_deep_mining.yml`이 `GEMINI_API_KEY: ${{ secrets.HAEYU_RESEARCH }}`로
   매핑해 스크립트 내부의 `GEMINI_API_KEY` 환경변수명에 연결한다. 다른 이름으로 등록했다면 이
   워크플로우 파일의 `secrets.HAEYU_RESEARCH` 부분만 그 이름으로 바꾸면 된다.

이 secret이 없거나 이름이 안 맞으면 워크플로우가 `[ERROR]: GEMINI_API_KEY 환경변수` 메시지와 함께 즉시
실패합니다(크래시가 아니라 명확한 에러 — 계속 실패해도 원인을 바로 알 수 있음).

---

## 💰 비용에 대해

이건 **API 종량제**입니다. 대화형 세션과 달리 실행할 때마다 실제 비용이 발생합니다.
- 스크립트를 로컬에서 `autonomous_deep_mining.py` 단독으로 직접 실행할 때(`--top_n` 생략 시)는
  **1회 실행에 신규 후보국 상위 3개국만** 조사합니다(`--top_n 3`, 비용 안전장치용 기본값).
- `.github/workflows/auto_deep_mining.yml`의 `workflow_dispatch`/`schedule` 기본값은
  `top_n=10000`으로 설정돼 있습니다 — 즉 실제 자동 실행은 매번 프로젝트당 남은 "신규 후보"
  국가를 (최대 10,000개까지) 모두 소진할 때까지 처리합니다. 국가 수가 10,000개보다 훨씬 적으므로
  실질적으로는 "그 시점까지 조사되지 않은 국가를 전부 처리"하는 것과 같습니다.
- 스케줄은 **매일 1회, KST 자정(00:00)**입니다 (이전에는 6시간마다였으나, ①대화형 세션(2.2)이
  주 조사 수단이 되고 ②처리 대상 프로젝트가 여러 개로 늘어나면서 비용 통제를 위해 하루 1회로
  낮췄습니다).
- 매일 실행이 **`BIZ-*/data/*_buyers_leads.xlsx` 중 `Sourcing_Candidates` 시트가 있는 프로젝트를
  전부** 처리합니다 (`run_all_projects.py`, 아래 참고) — 프로젝트 수만큼 비용이 비례해서
  늘어납니다.
- 비용을 줄이고 싶으면 워크플로우 파일의 `top_n` 기본값을 낮추거나 `cron` 주기를 늘리세요.

---

## ⚠️ 무결성 규칙 (trade-gen2.2와 동일)

1. Gemini에게 시스템 프롬프트로 "실제 검색 결과만, 출처 URL 필수, 불확실하면 빈칸"을 강제한다.
2. 응답에서 `source_url`이 없거나 `http`로 시작하지 않는 레코드는 **자동 거부**된다
   (`merge_research_findings.py`를 그대로 재사용 — 규칙이 두 곳에 따로 존재하지 않음).
3. Gemini의 Google Search grounding 메타데이터(실제 인용 URL)를 감사 로그(`{slug}_auto_mining_log.jsonl`)에
   원문 응답과 함께 남긴다 — 나중에 사람이 "이게 진짜 검색 결과였는지" 재검토할 수 있게.

---

## 🛠️ 실행 방법

**단일 프로젝트만 (로컬 디버깅 등):**
```bash
export GEMINI_API_KEY=...
uv run python .agents/skills/trade-gen4-un-auto-mining/scripts/autonomous_deep_mining.py \
  --item "<품목명>" \
  --output_dir <프로젝트 폴더> \
  --item_slug <slug> \
  --top_n 3
```

**전 프로젝트 자동 발견 (GitHub Actions가 실제로 매일 실행하는 방식):**
```bash
export GEMINI_API_KEY=...
uv run python .agents/skills/trade-gen4-un-auto-mining/scripts/run_all_projects.py --top_n 10000
```
`run_all_projects.py`는 저장소를 스캔해 `BIZ-*/data/*_buyers_leads.xlsx` 중
`Sourcing_Candidates` 시트가 있는 프로젝트를 모두 찾아 순서대로 처리한다. 한 프로젝트에서
오류가 나도 나머지 프로젝트는 계속 처리한다. `--item`/`--output_dir`/`--item_slug`를 셋 다
지정하면 발견 로직을 건너뛰고 그 프로젝트 하나만 처리한다.

GitHub Actions(`.github/workflows/auto_deep_mining.yml`)는 **매일 KST 자정(00:00)** 1회
`run_all_projects.py`를 인자 없이 자동 실행합니다(=전 프로젝트 자동 발견 모드).
`workflow_dispatch`로 수동 실행할 수도 있으며, 이때 `item`/`output_dir`/`item_slug`를 모두
채우면 그 프로젝트 하나만, 비워두면 자정 스케줄과 동일하게 전 프로젝트를 처리합니다.

### ➕ 새 품목(프로젝트)을 자동화에 포함시키려면

**워크플로우 YAML을 수정할 필요가 없습니다.** `trade-gen1-un-eda` → `trade-gen2.1-un-sourcing`을
새 품목에 대해 한 번만 실행해 `{slug}_buyers_leads.xlsx`에 `Sourcing_Candidates` 시트를
만들어두면, 다음 자정 실행부터 `run_all_projects.py`가 자동으로 그 프로젝트를 발견해 처리합니다.

---

## 🔁 다른 스킬과의 관계

| | trade-gen2.2 (대화형) | trade-gen4 (완전 자동) |
|---|---|---|
| 실행 주체 | Claude/Gemini 등 대화형 세션 | GitHub Actions + Gemini API |
| 컴퓨터 꺼지면 | 즉시 중단 | 계속 실행됨 |
| 비용 | 세션 사용 시간에 포함 | 실행마다 API 종량 과금 |
| 결과 저장 위치 | 동일 (`Verified_Partners` 시트) | 동일 (`Verified_Partners` 시트) |
| 병합 로직 | `merge_research_findings.py` | 동일 스크립트 재사용 |

두 스킬은 같은 `{slug}_buyers_leads.xlsx` 파일의 같은 시트에 누적되므로, 하나가 찾은 결과를
다른 하나가 지우지 않습니다.
