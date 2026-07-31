# 🔎 Partner Deep Mining — 실제 웹 검색 기반 파트너 발굴 구현 계획서 (Implementation Plan)

- **최종 업데이트 일시**: 2026년 07월 31일
- **프로젝트 명**: BIZ-Jeonbok 글로벌 바이어 & 독립 에이전트 소싱 파이프라인 — 딥마이닝 확장
- **실행 주체**: Claude(WebSearch/WebFetch 직접 수행) + `merge_research_findings.py`(결정적 병합기)

---

## 🎯 1. 배경 — 왜 다시 만들었나

기존 `BIZ-Jeonbok/src/partner_sourcing_agent.py`(2026-07-31 제거)는 `--item_slug`로 무엇을 넘기든
**항상 동일한 10개 하드코딩 가상 업체**(가짜 이메일·전화번호 포함)를 "데이터 검증: 실존 검증
완료"라고 표시해 저장하고 있었다. 실제로 EDA 리포트를 파싱하는 함수(`parse_eda_report_tables`)는
코드 어디서도 호출되지 않는 죽은 코드였다.

일반 Python 스크립트는 구글/LinkedIn을 실제로 검색할 수 없기 때문에, "무인 자동 딥마이닝"을
정직하게 구현하려면 **검색과 판단은 실제 웹 접근이 가능한 에이전트(Claude)가 하고, 스크립트는
그 결과를 정해진 스키마로 정확히 기록하는 역할만 해야 한다**는 것이 이번 재설계의 출발점이다.

---

## 🧩 2. 아키텍처 — 역할 분리

```
[trade-eda-generator]                     실제 무역 통계 → HS Code별 TOP 10 국가 리포트
        │
        ▼
[partner-sourcing-generator]  (4x cron)    국가별 우선순위 점수 산출 (Sourcing_Candidates 시트)
        │                                  ※ 실제 회사를 검색하지 않음 — 정적 스크립트라서 애초에 불가능
        ▼
[partner-deep-mining]         (온디맨드)    Claude가 WebSearch/WebFetch로 실재 회사·에이전트 검색
        │                                  → findings JSON (출처 URL 필수)
        ▼
[merge_research_findings.py]               findings를 Verified_Partners 시트에 결정적으로 병합
                                            + Sourcing_Candidates의 조사 상태 갱신
```

**핵심 원칙**: "회사가 실제로 존재하는지 찾는 것"은 스크립트의 책임이 아니다. 스크립트는 오직
"출처 URL 없는 레코드는 거부한다"는 무결성 검증만 담당한다.

---

## ⚠️ 3. 절대 규칙

1. **출처 URL 없는 정보는 절대 기록하지 않는다.** `merge_research_findings.py`가 `source_url`이
   없거나 `http`로 시작하지 않는 레코드를 자동 거부한다.
2. **확실하지 않으면 빈 칸으로 둔다.** 이메일이 공개돼 있지 않으면 지어내지 않고 `note`에 사유를 남긴다.
3. **추측/패턴 기반 생성 금지.** "이 나라 회사는 보통 이런 이메일을 쓴다" 같은 추정 금지.
4. LinkedIn은 **공개 검색 결과에 노출된 프로필 URL만** 기록. 로그인 스크래핑/계정 자동화 없음.

---

## 🕐 4. 실행 주기 — 온디맨드 vs 4x cron 자동화 (별도 실행, 결과는 같은 시트)

| | `partner-sourcing-generator` | `partner-deep-mining` |
|---|---|---|
| 실행 시점 | 하루 4회 GitHub Actions cron | 사용자가 자연어로 요청할 때만 |
| 하는 일 | EDA 리포트 재파싱 → 국가 우선순위 갱신 | 실제 WebSearch/WebFetch로 회사 검색·검증 |
| 트리거 예시 | (자동) | *"표1, 표2에 있는 일본 로컬파트너 먼저 검색해줘, 최대한 많이 수집해줘"* |
| 기록 위치 | `Sourcing_Candidates` 시트 | `Verified_Partners` 시트 (같은 xlsx 파일) |

사용자가 특정 HS Code 표(표1, 표2 등) + 국가를 지정하면 **스코프 지정 모드**로 전환되어, 해당
HS Code 맥락에서만 검색 각도를 여러 개(도매상/전시회·협회 디렉토리/LinkedIn/현지어 검색)로 반복해
"최대한 많이" 수집한다. 기본 모드(범위 미지정)는 우선순위 상위 3~5개국을 국가당 2~3개 쿼리로
가볍게 조사한다.

---

## 📋 5. `Verified_Partners` 시트 스키마 (City/Country 분리 반영)

| 순서 | 컬럼명 | 비고 |
| :---: | :--- | :--- |
| 1 | 조사일 (Research Date) | |
| 2 | 국가 (Country) | Sourcing_Candidates와 연결되는 키 |
| 3 | 회사명/에이전트명 | |
| 4 | 구분 (법인/개인 에이전트) | |
| 5 | 이메일 | 페이지에 실제 공개된 것만 |
| 6 | 웹사이트 / LinkedIn URL | |
| 7 | Messenger/연락처 | |
| 8 | 조사 범위 (HS Code 표) | 스코프 지정 모드일 때 어떤 표를 대상으로 했는지 |
| 9 | **City** | **영문만.** 본사 도시 |
| 10 | **Country** | **영문만.** 본사 국가 |
| 11 | 본사 위치 (상세) | 시장/구역/상세주소 등 부가정보 |
| 12 | 주요 취급 품목 및 특징 | |
| 13 | 잠재적 협력 포인트 | |
| 14 | **출처 URL (검증 근거)** | **필수. 없으면 자동 거부** |
| 15 | 비고 | 불확실한 점, 문의폼만 존재 등 |

---

## 🔁 6. 실행 절차 (Claude가 직접 수행)

1. 조사 대상 선정 (기본 모드: 우선순위 상위 3~5개국 / 스코프 지정 모드: 지정된 표+국가)
2. WebSearch로 각도를 바꿔가며 검색 (도매상, 전시회 디렉토리, LinkedIn, 현지어)
3. 유망한 결과를 WebFetch로 직접 열어 품목 취급 여부·공개 연락처 확인
4. findings JSON 작성 (스크래치패드에 저장, 모든 레코드에 `source_url` 필수)
5. `merge_research_findings.py`로 병합 → `Verified_Partners` 시트 갱신 + `Sourcing_Candidates` 조사 상태 갱신 + 마크다운 리포트 재생성
6. 조사 개수/발견 건수/제외된 후보(출처 없음) 요약 보고

---

## 📁 7. 파일 목록

- **스킬 정의**: [.agents/skills/partner-deep-mining/SKILL.md](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/.agents/skills/partner-deep-mining/SKILL.md)
- **병합 스크립트**: [.agents/skills/partner-deep-mining/scripts/merge_research_findings.py](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/.agents/skills/partner-deep-mining/scripts/merge_research_findings.py)
- **국가 우선순위 스킬(선행 단계)**: [.agents/skills/partner-sourcing-generator/scripts/generate_partner_sourcing.py](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/.agents/skills/partner-sourcing-generator/scripts/generate_partner_sourcing.py)
- **엑셀 DB (Sourcing_Candidates + Verified_Partners + Sourcing_History)**: [BIZ-Jeonbok/data/abalone_buyers_leads.xlsx](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/BIZ-Jeonbok/data/abalone_buyers_leads.xlsx)
- **마크다운 리포트**: [BIZ-Jeonbok/reports/Abalone_Buyers_Lead_List.md](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/BIZ-Jeonbok/reports/Abalone_Buyers_Lead_List.md)
- **실행 보고서**: [BIZ-Jeonbok/artifacts/partner_deep_mining_walkthrough.md](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/BIZ-Jeonbok/artifacts/partner_deep_mining_walkthrough.md)

> ⚠️ 이전 문서 `partner_sourcing_automation_plan.md` / `walkthrough.md`(2026-07-29 작성)는 가짜
> 하드코딩 업체 데이터를 "실존 검증 완료"로 예시하고 있어 더 이상 유효하지 않다. 이 문서가
> 그것을 대체한다.
