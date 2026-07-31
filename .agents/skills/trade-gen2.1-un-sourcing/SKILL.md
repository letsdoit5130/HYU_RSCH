---
name: trade-gen2.1-un-sourcing
description: trade-gen1-un-eda 스킬이 만든 EDA 리포트(TOP N HS Code별 TOP 10 유망국가 표)를 파싱해, 데이터 기반 "소싱 후보국가 & 파트너 리서치 트래커"를 자동/누적 생성하는 범용 스킬입니다. 잠재 파트너/바이어 국가 조사, 소싱 후보국 리스트, 무역 데이터 기반 파트너 우선순위 요청 시 활성화됩니다.
---

# 🌐 Partner Sourcing Generator (범용 소싱 후보국가 트래커 생성 스킬)

`trade-gen1-un-eda` 스킬이 만든 EDA 리포트의 TOP N HS Code x TOP 10 유망국가 표를 읽어,
**국가별로 집계·우선순위화한 소싱 후보 리스트**를 엑셀/CSV/마크다운으로 자동 생성·누적합니다.

이 스킬은 특정 품목(예: 전복)에 종속되지 않습니다. `--item`, `--output_dir`만 바꾸면
어떤 프로젝트 폴더에서도 재사용할 수 있습니다.

---

## ⚠️ 이 스킬이 하지 않는 것 (중요)

이 스크립트는 **실제 웹 검색이나 현지 실사를 수행하지 않습니다.** 따라서:

- 회사명, 이메일, 전화번호, LinkedIn 프로필 같은 "실제 파트너 컨택 정보"를 지어내서 채워 넣지 않습니다.
- 채워지는 것은 EDA 리포트에서 실제로 산출된 값(**국가, HS Code, 순위, 수입액/물량 근거**)뿐입니다.
- 회사명/이메일/웹사이트/메신저 등은 빈 칸("조사 상태: 🆕 신규 후보")으로 시작하며, 사람(또는 별도의
  실시간 웹 검색이 가능한 에이전트)이 직접 조사해 채워야 합니다.
- 재실행 시 EDA 데이터 기반 필드(순위, 수입액 등)는 최신 값으로 갱신되지만, 이미 사람이 채워 넣은
  조사 결과(조사 상태/회사명/이메일 등)는 절대 덮어쓰지 않습니다.

> 이전 버전(`BIZ-Jeonbok/src/partner_sourcing_agent.py`)은 품목과 무관하게 항상 동일한 10개
> 하드코딩 가상 업체를 "실존 검증 완료"라고 표시해 저장하는 문제가 있었습니다. 이 스킬은 그 문제를
> 해결하기 위해 재설계되었습니다.

---

## 🛠️ 스킬 사용법 (Usage)

**사전 조건**: 먼저 `trade-gen1-un-eda` 스킬로 해당 품목의 EDA 리포트를 생성해야 합니다.

```bash
# 1) EDA 리포트 생성 (trade-gen1-un-eda 스킬)
uv run python .agents/skills/trade-gen1-un-eda/scripts/generate_trade_eda.py \
  --input BIZ-Jeonbok/BIZ-JB-Gathered.csv \
  --item "전복 (Abalone)" \
  --output_dir BIZ-Jeonbok

# 2) 소싱 후보국가 트래커 생성/갱신 (이 스킬)
uv run python .agents/skills/trade-gen2.1-un-sourcing/scripts/generate_partner_sourcing.py \
  --item "전복 (Abalone)" \
  --output_dir BIZ-Jeonbok
```

### 입력 파라미터
- `--item` (필수): 품목명 (예: `"전복 (Abalone)"`, `"김 (Laver)"`). trade-gen1-un-eda에 넘긴 값과 동일해야 합니다.
- `--output_dir` (필수): 프로젝트 루트 폴더 (예: `BIZ-Jeonbok`). `data/`, `reports/` 하위에 결과가 저장됩니다.
- `--eda_report` (선택): 참조할 EDA 리포트 경로. 생략 시 `{output_dir}/reports/BIZ-{품목}_Gathered_EDA_Report.md`를 자동으로 찾습니다.
- `--item_slug` (선택): 데이터 파일명에 쓸 영문 슬러그 (예: `abalone`). 생략 시 `--item`에서 자동 생성합니다.

---

## 📋 생성되는 산출물

```
{output_dir}/
├── data/
│   ├── {slug}_buyers_leads.xlsx        # Sourcing_Candidates + Sourcing_History 시트
│   └── {slug}_sourcing_history.csv     # 실행 이력 로그
└── reports/
    └── {품목}_Buyers_Lead_List.md      # 사람이 보는 결과 리포트
```

**`Sourcing_Candidates` 시트 컬럼:**

| 구분 | 컬럼 | 설명 |
|---|---|---|
| EDA 데이터 기반 (재실행 시 자동 갱신) | 국가, 데이터 수집일, EDA 데이터 근거, 후보 HS Code 수, 최고 순위, 우선순위 점수 | trade-gen1-un-eda 리포트에서 파싱한 실제 값 |
| 사용자 조사 항목 (재실행해도 보존) | 조사 상태, 후보 파트너/에이전트명, 회사 이메일, 웹사이트/LinkedIn, Messenger, 본사 위치, 비고/메모 | 사람이 직접 조사해 채우는 빈 칸 |

우선순위 점수는 `(해당 국가가 상위권에 등장한 HS Code 표 개수) × 100 − (최고 순위)`로 계산되어,
여러 HS Code에서 동시에 상위권인 국가일수록, 순위가 높을수록 우선순위가 올라갑니다.

---

## 🔁 자동화 (GitHub Actions)

`.github/workflows/partner_sourcing.yml`이 하루 4회(KST 06/12/18/00) 이 스크립트를 실행하고
결과를 자동 커밋합니다. 새 품목에 자동화를 추가하려면 워크플로우에 동일한 패턴으로
`--item`/`--output_dir`만 바꾼 step을 추가하면 됩니다.
