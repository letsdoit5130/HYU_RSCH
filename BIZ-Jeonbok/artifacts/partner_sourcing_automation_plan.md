# 🚀 글로벌 수산물 파트너/에이전트 수집 무인 자동화 구축 실행 계획서 (Implementation Plan)

> ⚠️ **[2026-07-31 갱신 안내]** 이 문서(2026-07-29 작성)가 설명하는 "3중 딥 마이닝" 구현은 실제로는
> 하드코딩된 가짜 업체 데이터를 "실존 검증 완료"로 표시하던 버전이었습니다. 해당 스크립트는 제거됐고,
> 실제 WebSearch/WebFetch 기반으로 재구현한 버전은
> [partner_deep_mining_implementation_plan.md](./partner_deep_mining_implementation_plan.md)를
> 참고하세요. 이 문서는 과거 기록으로만 남겨둡니다.

- **최종 업데이트 일시**: 2026년 07월 29일
- **프로젝트 명**: BIZ-Jeonbok 글로벌 바이어 & 독립 에이전트 소싱 파이프라인
- **실행 주체**: BIZ-Jeonbok Partner Sourcing Agent & GitHub Actions Engine

---

## 🎯 1. 파이프라인 구축 목표
1인 종합상사 창업자가 한국산 전복(활전복 0307.81, 냉동전복 0307.83, 전복 통조림 1605.57)을 해외 유망 신시장에 수출할 수 있도록, **현지 로컬 수입 디스트리뷰터 및 LinkedIn 개인 수산 브로커(Agent)**를 매일 4회 무인 자동 소싱·정제·누적하는 시스템을 구축합니다.

---

## ⚙️ 2. 핵심 수집 & 정제 메커니즘 (A to Z)

```
[1단계: 원천 EDA 보고서 동적 파싱]
  └─ BIZ-JB-Gathered_EDA_Report.md 표 1~3 (HS Code, 주 미수, 타깃 국가, 컨택 파트너) 파싱

[2단계: 3중 다각도 딥 마이닝 (Inclusive OR 조건)]
  └─ 구글 현지어 검색 (site:.jp, site:.us) + 수산 산업 전시회(Trade Show) + LinkedIn (개인 에이전트/법인)

[3단계: 정밀 필드 규격 정제 & 레이아웃 재배치]
  └─ ① 회사명: 한글 전면 제외, 영문/현지어 전용 (개인 에이전트는 본인 성함 기입)
  └─ ② 회사 이메일: 부연설명 부호 100% 제거, 순수한 이메일 주소만 기입
  └─ ③ 웹사이트 URL: 개인 에이전트는 LinkedIn 개인 프로필 주소 매핑
  └─ ④ 영문 국가명: Japan, United States 등 영문 수집 및 '본사 위치 (도시)' 바로 왼쪽 옆으로 배치

[4단계: 누적 병합 & 중복 자동 제거 (Deduplication)]
  └─ 기존 엑셀(buyers_leads.xlsx)과 이어서 누적 병합 후 '회사명' 기준 중복 제거 (기존 데이터 100% 보존)

[5단계: 3가지 시기별 히스토리 대시보드 동시 자동 생성]
  └─ Buyers_Lead_List.md (마크다운) + sourcing_history.csv (CSV) + buyers_leads.xlsx (3개 시트: Buyer_Leads, Overall_Breakdown, Sourcing_History)

[6단계: 무인 일 4회 클라우드 자동 구동 & Git Push (GitHub Actions)]
  └─ 매일 KST 06:00, 12:00, 18:00, 00:00 무인 자동 구동 ➔ GitHub 저장소에 Commit & Push
```

---

## 📋 3. 10개 필드 표기 레이아웃 명세

| 순서 | 컬럼명 | 정제 및 수집 지침 |
| :---: | :--- | :--- |
| 1 | 데이터 수집일 | 수집 구동 일자 (YYYY-MM-DD) |
| 2 | 데이터 검증 | 실존 검증 출처 (Google site:.jp / Trade Show / LinkedIn 등) |
| 3 | 아이템 품목 (HS CODE) | 0307.81(활전복), 0307.83(냉동전복), 1605.57(통조림) 및 주 미수 |
| 4 | 회사명 (영어/현지어) | **한글 전면 제외**, 영문/현지어만 (개인 에이전트는 본인 성함 기입) |
| 5 | 회사 이메일 | 괄호 부호 제거, **순수한 이메일 주소만 기입** (예: `info@chuogyorui.co.jp`) |
| 6 | 웹사이트 URL / LinkedIn | 개인 에이전트는 LinkedIn 프로필 URL, 법인은 웹사이트 + 기업 LinkedIn |
| 7 | Messanger | Line / WhatsApp / WeChat / LinkedIn InMail / 대표 전화번호 |
| 8 | **국가 (Country)** | **영문 국가명 (Japan, United States, Hong Kong) - 본사위치 바로 왼쪽 배치** |
| 9 | **본사 위치 (도시)** | 현지 본사 도시 소재지 (Tokyo, Los Angeles, Hong Kong 등) |
| 10 | 주요 취급 품목 및 특징 | 로컬 유통망 특징 및 전시회/구글/LinkedIn 검증 사항 |
| 11 | 잠재적 협력/경쟁 포인트 | 1인 상사의 한국산 전복 공급 및 커미션 기반 에이전트 계약 포인트 |

---

## 📁 4. 파이프라인 관리 파일 전체 목록

- **소싱 에이전트 엔진 (Docstring 완비)**: [.agents/skills/partner-sourcing-generator/scripts/generate_partner_sourcing.py](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/.agents/skills/partner-sourcing-generator/scripts/generate_partner_sourcing.py) (2026-07-31: 전역 스킬로 이전, 하드코딩 가상 업체 데이터 제거)
- **GitHub Actions 워크플로우 (일 4회 매일 실행)**: [.github/workflows/partner_sourcing.yml](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/.github/workflows/partner_sourcing.yml)
- **마크다운 수집 리포트 및 히스토리 표**: [BIZ-Jeonbok/reports/Buyers_Lead_List.md](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/BIZ-Jeonbok/reports/Buyers_Lead_List.md)
- **CSV 히스토리 트래킹 파일**: [BIZ-Jeonbok/data/sourcing_history.csv](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/BIZ-Jeonbok/data/sourcing_history.csv)
- **엑셀 3개 시트 데이터베이스 (`Buyer_Leads`, `Overall_Breakdown`, `Sourcing_History`)**: [BIZ-Jeonbok/data/buyers_leads.xlsx](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/BIZ-Jeonbok/data/buyers_leads.xlsx)
