# trade-gen4-un-auto-mining — 스킬 문서

> 사용법 자체는 상위 폴더의 [`../SKILL.md`](../SKILL.md)를 참고하세요. 여기서는
> **파이프라인에서의 위치**와 **trade-gen2.2와의 관계**를 다룹니다.

---

## 1. 파이프라인에서의 역할

5단계 무역 파트너 발굴 파이프라인의 **3단계(실제 조사 단계, 완전자동)**입니다. 전체 흐름은
[`../../trade-gen-docs/README.md`](../../trade-gen-docs/README.md) 참고.

```
[2] trade-gen2.1-un-sourcing 의 Sourcing_Candidates 시트
      ▼
[3-B] trade-gen4-un-auto-mining  ← 지금 이 스킬 (완전자동, GitHub Actions + Gemini API)
      │  매일 KST 자정, run_all_projects.py가 전 프로젝트 자동 발견 후 처리
      ▼
      Verified_Partners 시트에 병합 (merge_research_findings.py — trade-gen2.2와 동일 스크립트)
```

**입력**: 저장소 내 모든 `BIZ-*/data/*_buyers_leads.xlsx` 중 `Sourcing_Candidates` 시트가 있는 프로젝트
(=`trade-gen2.1-un-sourcing`을 한 번이라도 돌려둔 프로젝트는 전부 자동 포함됨)
**출력**: 각 프로젝트의 `Verified_Partners` 시트 + `{slug}_auto_mining_log.jsonl` 감사 로그
**실행 주체**: GitHub Actions(`.github/workflows/auto_deep_mining.yml`) + Gemini API
(Google Search grounding) — 대화형 세션이나 사람 개입 없이 클라우드에서 실행됨

## 2. trade-gen2.2와의 차이 (요약 — 상세는 `../SKILL.md`)

| | trade-gen2.2 (대화형) | trade-gen4 (이 스킬, 완전자동) |
|---|---|---|
| 실행 주체 | Claude/Gemini 등 대화형 세션 | GitHub Actions + Gemini API |
| 컴퓨터/세션 종료 시 | 즉시 중단 | 계속 실행됨 |
| 비용 | 세션 사용 시간에 포함 | 실행마다 API 종량 과금 |
| 새 프로젝트 추가 방법 | 자연어로 요청 | 워크플로우 수정 불필요 — `trade-gen2.1` 한 번만 돌리면 다음 자정부터 자동 포함 |
| 결과 저장 위치/병합 로직 | 동일 (`Verified_Partners` 시트, `merge_research_findings.py`) | 동일 |

## 3. 필수 사전 설정 & 비용 (요약)

- GitHub 저장소 **Settings → Secrets and variables → Actions**(Environments 아님)에
  `GEMINI_API_KEY` 매핑용 secret 등록 필요 (현재 이름: `HAEYU_RESEARCH`). 없으면 워크플로우가
  명확한 `[ERROR]` 메시지와 함께 즉시 실패.
- API 종량제 — 매일 자정 1회, 등록된 전 프로젝트의 미조사 후보국을 처리(`top_n=10000` 기본).
  비용을 줄이려면 워크플로우의 `top_n`을 낮추거나 `cron` 주기를 늘리면 됨.
- 로컬 단독 실행 시 기본 `--top_n 3`(비용 안전장치)로 제한됨.

상세 배경(무결성 규칙, 감사 로그 형식 등)은 `../SKILL.md` 참고.
