---
name: trade-gen2.2-un-partner-deep-mining
description: trade-gen2.1-un-sourcing가 만든 소싱 후보국가 리스트를 입력으로, 실제 WebSearch/WebFetch를 사용해 진짜 존재하는 수입 디스트리뷰터·독립 에이전트를 출처 URL과 함께 찾아 트래커에 채워 넣는 스킬입니다. "딥마이닝", "실제 파트너 찾아줘", "바이어 리서치 해줘", "파트너 소싱 조사", "에이전트 발굴" 요청 시 활성화됩니다.
---

# 🔎 Partner Deep Mining (실제 웹 검색 기반 파트너 발굴 스킬)

`trade-gen2.1-un-sourcing`가 만든 "어느 나라를 먼저 조사해야 하는지"(우선순위 점수) 리스트를 입력받아,
**이 스킬을 실행하는 AI 에이전트가 직접 웹 검색·페이지 열람 도구로 실재하는 회사·에이전트를 찾아**
출처 URL과 함께 트래커에 채워 넣습니다.

> 이 문서는 Claude Code 기준(WebSearch/WebFetch 도구명)으로 작성됐지만, 특정 AI에 종속되지
> 않습니다. 동등한 웹 검색 + 페이지 열람 도구를 가진 다른 AI 에이전트(Gemini 등)가 이 SKILL.md를
> 읽고 절차·규칙을 그대로 따르면 동일하게 동작합니다. **단, 아래 "절대 규칙"을 실제로 얼마나
> 성실히 지키는지는 실행하는 AI의 판단력에 달려 있으며, 그 결과 품질은 이 문서를 작성한 주체가
> 보증할 수 없습니다.**

## 🕐 자동화(cron)와의 관계 — 별도 실행

- **`partner_sourcing.yml` (하루 4회 cron)**: `trade-gen2.1-un-sourcing`만 실행합니다. EDA 리포트의
  국가별 순위/수입액을 다시 읽어 `Sourcing_Candidates` 시트를 최신화할 뿐, **실제 회사를 검색하지
  않습니다** (정적 스크립트는 실제 웹 검색을 할 수 없기 때문에 애초에 자동화 대상이 아닙니다).
- **이 스킬(`trade-gen2.2-un-partner-deep-mining`)은 cron에 포함되지 않고, 사용자가 필요할 때 자연어로 요청하면
  그때 온디맨드로 실행됩니다.** 예: *"표1, 표2에 있는 일본 컨택해야 할 로컬파트너 먼저 검색해줘,
  최대한 많은 자료 수집해서 정리해줘"*
- 두 작업은 실행 시점이 다르지만 **결과는 항상 같은 파일(`{slug}_buyers_leads.xlsx`의
  `Verified_Partners` 시트)에 누적**됩니다. cron이 후보국 우선순위를 갱신해도, 이 스킬이 이미
  찾아 놓은 파트너 조사 결과(사용자가 입력/확인한 값)는 지워지지 않습니다
  (`trade-gen2.1-un-sourcing`의 병합 규칙 — 사용자 입력 필드는 보존).

---

## ⚠️ 절대 규칙 (이 스킬의 존재 이유)

이 프로젝트에는 과거에 "품목과 무관하게 항상 똑같은 10개 가짜 업체를 '실존 검증 완료'로 표시"하던
스크립트가 있었습니다 (`BIZ-Jeonbok/src/partner_sourcing_agent.py`, 2026-07-31 제거됨). 이 스킬은
그 문제를 반복하지 않기 위해 다음을 **절대 규칙**으로 강제합니다.

1. **출처 URL 없는 정보는 절대 기록하지 않는다.** 회사명·이메일·전화번호 등 모든 정성 정보는
   실제로 WebSearch 결과 또는 WebFetch로 읽은 페이지에서 나온 것이어야 하며, 그 URL을 반드시
   `source_url`로 함께 기록한다. (`merge_research_findings.py`가 `source_url`이 없으면 해당
   레코드를 자동으로 거부한다 — 이건 스크립트가 강제하는 안전장치이지 선택 사항이 아니다.)
2. **확실하지 않으면 빈 칸으로 둔다.** 웹페이지에 이메일이 공개돼 있지 않으면 이메일 칸을 지어내지
   않는다. "문의폼만 있음", "이메일 미기재" 등을 `note`에 적는다.
3. **추측/일반화 금지.** "일본 회사는 보통 이런 이메일 패턴을 쓴다" 같은 추정으로 이메일을
   만들어내지 않는다.
4. LinkedIn 개인 프로필은 **공개 검색 결과에 노출된 프로필 URL만** 기록한다. 로그인이 필요한
   페이지 스크래핑, 계정 자동화는 하지 않는다 (WebSearch/WebFetch 도구 자체가 이를 지원하지 않음).

---

## 🛠️ 실행 절차 (실행 AI 에이전트가 직접 수행)

### 사전 조건
`{output_dir}/data/{slug}_buyers_leads.xlsx`의 `Sourcing_Candidates` 시트가 이미 존재해야 합니다
(없다면 먼저 `trade-gen1-un-eda` → `trade-gen2.1-un-sourcing` 순서로 생성).

### 1단계 — 조사 대상 선정 (기본 모드 vs 스코프 지정 모드)

**기본 모드** (사용자가 범위를 지정하지 않은 경우): `Sourcing_Candidates` 시트를 읽어 우선순위
점수 순으로 정렬하고, `조사 상태`가 아직 `🆕 신규 후보`인 국가 중 상위 3~5개를 조사 대상으로 삼는다.
국가당 2~3개 쿼리로 가볍게 조사한다.

**스코프 지정 모드** (사용자가 "표N", 특정 국가, "최대한 많이/모두 찾아줘" 등을 명시한 경우): 예를
들어 *"표1, 표2에 있는 일본 로컬파트너 먼저 검색해줘, 최대한 많이 수집해줘"* 같은 요청이면:
1. EDA 리포트(`BIZ-{품목}_Gathered_EDA_Report.md`)에서 지정된 표(예: 표1=HS Code A, 표2=HS Code B)의
   해당 국가 행을 직접 찾아 그 표의 "구체적 근거"(수입액/물량)를 조사 컨텍스트로 사용한다
   (`Sourcing_Candidates`의 합산된 근거가 아니라, 표별 원문을 봐야 어떤 HS Code 맥락인지 정확함).
2. 그 국가·그 HS Code 범위에 한해 아래 4단계 쿼리를 **다양한 각도로 반복** — 도매상 검색,
   전시회/무역협회 디렉토리, LinkedIn 공개 프로필, 현지어 검색(가능하면 `site:.jp` 등 TLD 제한)
   — 결과가 더 안 나올 때까지(또는 사용자가 요청한 개수에 도달할 때까지) 계속한다. "최대한 많이"는
   기본 모드의 2~3개 쿼리보다 명백히 더 넓고 깊게 조사하라는 뜻이다.
3. 각 finding의 `scope` 필드에 어떤 표/HS Code를 대상으로 조사했는지 기록한다
   (예: `"표1 (HS 030781), 표2 (HS 160557)"`) — `Verified_Partners` 시트의 "조사 범위" 컬럼에 남는다.

### 2단계 — 국가별 실제 검색 (WebSearch)
대상 국가마다 서로 다른 각도로 검색한다 (기본 모드 2~3개, 스코프 지정 모드는 소진될 때까지). 예
(품목이 전복이라면):

- `"{품목 영문명} importer" {country}` (예: `"abalone importer" Japan`)
- `{품목 영문명} wholesale distributor {country 주요 항구/도시}`
- `{품목 HS Code 설명} trade show exhibitor directory {country}`
- `{품목 영문명} broker OR agent {country} site:linkedin.com` (LinkedIn 공개 프로필 탐색용)
- `{품목 영문명} importer {country} customs broker association directory`
- 현지어/현지 도메인 제한 검색 (예: `site:.jp {품목 현지어} 輸入 商社`)

### 3단계 — 검증 (WebFetch)
검색 결과에서 유망해 보이는 회사/에이전트 페이지를 WebFetch로 열어:
- 실제로 해당 품목(또는 인접 수산물)을 취급하는지 확인
- 공개된 이메일/연락처/주소가 있으면 그대로, 없으면 빈칸 + note
- 회사 소개, 취급 품목, 규모 등 `features`에 요약

### 4단계 — findings JSON 작성
아래 스키마로 findings JSON을 만든다 (스크래치패드에 저장):

```json
[
  {
    "country": "Japan",
    "name": "회사명 또는 개인 에이전트 성함",
    "is_agent": false,
    "email": "",
    "website": "https://...",
    "linkedin": "https://www.linkedin.com/...",
    "messenger": "",
    "scope": "표1 (HS 030781), 표2 (HS 160557)",
    "city": "Tokyo",
    "country_en": "Japan",
    "location_detail": "Toyosu Market, store 1065-1068, Koto-ku (구체적 주소/구역)",
    "features": "실제 웹페이지에서 확인한 취급 품목/특징 요약",
    "coop_point": "협력 가능성에 대한 판단 (근거 기반)",
    "source_url": "https://... (반드시 실제 확인한 URL)",
    "note": "이메일 미기재, 문의폼만 존재 등 특이사항"
  }
]
```

- `city`, `country_en`은 **반드시 영문으로만** 기입한다 (한글 지명 금지).
- `scope`는 기본 모드에서는 생략 가능하지만, 스코프 지정 모드에서는 반드시 채운다.
- `location_detail`은 도시명이 아니라 시장/구역/상세주소 등 부가 정보만 담는다 (도시는 `city`에).

### 5단계 — 병합
```bash
uv run python .agents/skills/trade-gen2.2-un-partner-deep-mining/scripts/merge_research_findings.py \
  --findings <findings.json 경로> \
  --item "<품목명>" \
  --output_dir <프로젝트 폴더> \
  --item_slug <slug>
```

이 스크립트가 `Verified_Partners` 시트(출처 URL 포함)를 추가/갱신하고, 해당 국가의
`Sourcing_Candidates` 조사 상태를 `🔍 조사 완료 (N개사 발견)`으로 갱신하며, 마크다운 리포트를
재생성한다.

### 6단계 — 사용자에게 보고
몇 개국을 조사했는지, 몇 건을 찾았는지, 출처 URL이 없어 제외된 후보가 있었는지 요약해서 보고한다.
"확실하지 않다"는 판단이 있었다면 숨기지 말고 그대로 보고한다.

---

## 📋 출력 스키마 (`Verified_Partners` 시트)

| 컬럼 | 설명 |
|---|---|
| 조사일 | 실제 조사 실행 일시 |
| 국가 | 회사/에이전트가 귀속되는 후보국 (Sourcing_Candidates와 연결되는 키) |
| 회사명/에이전트명 | 법인명 또는 개인 성함 |
| 구분 | 법인 / 개인 에이전트 |
| 이메일 | 페이지에 실제로 공개된 것만 (없으면 빈칸) |
| 웹사이트 / LinkedIn URL | |
| Messenger/연락처 | |
| 조사 범위 (HS Code 표) | 스코프 지정 모드일 때 어떤 표/HS Code를 대상으로 조사했는지 |
| City | **영문만.** 본사 소재 도시 (예: Tokyo) |
| Country | **영문만.** 본사 소재 국가 (예: Japan) |
| 본사 위치 (상세) | 시장/구역/상세주소 등 City로 담기 애매한 부가 정보 |
| 주요 취급 품목 및 특징 | |
| 잠재적 협력 포인트 | |
| **출처 URL (검증 근거)** | **필수. 없으면 병합 스크립트가 자동 거부** |
| 비고 | 불확실한 점, 추가 확인 필요 사항 |

---

## 참고
- 국가 우선순위/집계 로직: `.agents/skills/trade-gen2.1-un-sourcing/`
- 무역 데이터 원천: `.agents/skills/trade-gen1-un-eda/`
