# trade-gen2.1-un-sourcing — 스킬 문서

> 사용법 자체는 상위 폴더의 [`../SKILL.md`](../SKILL.md)를 참고하세요. 여기서는
> **파이프라인에서의 위치**와 **다른 스킬과의 데이터 계약**을 다룹니다.

---

## 1. 파이프라인에서의 역할

5단계 무역 파트너 발굴 파이프라인의 **2단계(가공 단계)**입니다. 전체 흐름은
[`../../trade-gen-docs/README.md`](../../trade-gen-docs/README.md) 참고.

```
[1] trade-gen1-un-eda 의 EDA 리포트
      │  (TOP N HS Code별 TOP 10 유망 타겟시장 11대 명세 표를 파싱)
      ▼
[2] trade-gen2.1-un-sourcing  ← 지금 이 스킬
      │  (국가별 집계·우선순위화 → Sourcing_Candidates 시트)
      ▼
[2.2 / 4] 실제 파트너 검색이 이 시트의 빈 칸을 채움
```

**입력**: `trade-gen1-un-eda`가 생성한 `{output_dir}/reports/BIZ-{품목}_Gathered_EDA_Report.md`
(사전 조건 — 이 리포트 없이는 실행할 수 없음)
**출력**: `{output_dir}/data/{slug}_buyers_leads.xlsx` (`Sourcing_Candidates` + `Sourcing_History` 시트),
`{output_dir}/data/{slug}_sourcing_history.csv`, `{output_dir}/reports/{품목}_Buyers_Lead_List.md`
**다음 단계가 읽는 파일**: `trade-gen2.2`/`trade-gen4`가 `Sourcing_Candidates` 시트를 읽어 우선순위
순으로 실제 파트너를 조사하고, `Verified_Partners` 시트에 결과를 채웁니다. `trade-gen4`의
전체-프로젝트 자동 발견(`run_all_projects.py`)은 정확히 이 파일(`{slug}_buyers_leads.xlsx`에
`Sourcing_Candidates` 시트가 존재하는지)을 스캔 기준으로 삼습니다 — 즉 **이 스킬을 한 번이라도
실행해두면 그 프로젝트는 자동으로 매일 자정 자동조사 대상에 포함됩니다.**

---

## 2. 필드 갱신 규칙 (재실행 안전성)

재실행해도 사람이 조사한 값을 절대 덮어쓰지 않도록 필드가 두 그룹으로 나뉘어 있습니다:

| 그룹 | 필드 | 재실행 시 |
|---|---|---|
| EDA 데이터 기반 | 국가, 데이터 수집일, EDA 데이터 근거, 후보 HS Code 수, 최고 순위, 우선순위 점수 | 매번 최신 값으로 자동 갱신 |
| 사용자 조사 항목 | 조사 상태, 후보 파트너/에이전트명, 회사 이메일, 웹사이트/LinkedIn, Messenger, 본사 위치, 비고 | 항상 보존 (덮어쓰지 않음) |

우선순위 점수 = `(해당 국가가 상위권에 등장한 HS Code 표 개수) × 100 − (최고 순위)`.

## 3. 이 스킬이 하지 않는 것

실제 웹 검색이나 현지 실사를 수행하지 않습니다. 회사명/이메일/웹사이트 등은 빈 칸으로 시작하며
`trade-gen2.2`(대화형) 또는 `trade-gen4`(완전자동)가 채웁니다. 상세 배경(과거 하드코딩 가짜
업체 문제)은 `../SKILL.md`의 "이 스킬이 하지 않는 것" 절 참고.
