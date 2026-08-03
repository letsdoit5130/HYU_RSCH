# trade-gen2.2-un-partner-deep-mining — 스킬 문서

> 사용법 자체는 상위 폴더의 [`../SKILL.md`](../SKILL.md)를 참고하세요. 여기서는
> **파이프라인에서의 위치**와 **trade-gen4와의 관계**를 다룹니다.

---

## 1. 파이프라인에서의 역할

5단계 무역 파트너 발굴 파이프라인의 **3단계(실제 조사 단계, 대화형)**입니다. 전체 흐름은
[`../../trade-gen-docs/README.md`](../../trade-gen-docs/README.md) 참고.

```
[2] trade-gen2.1-un-sourcing 의 Sourcing_Candidates 시트
      ▼
[3-A] trade-gen2.2-un-partner-deep-mining  ← 지금 이 스킬 (대화형, 온디맨드)
      │  AI 에이전트가 WebSearch/WebFetch로 직접 검색
      ▼
      Verified_Partners 시트에 병합 (merge_research_findings.py)
```

같은 3단계를 **완전 자동(GitHub Actions + Gemini API)** 으로 수행하는 자매 스킬이
[`trade-gen4-un-auto-mining`](../../trade-gen4-un-auto-mining/)입니다. 둘 다 같은 파일의 같은
시트(`Verified_Partners`)에 누적되므로 서로의 결과를 지우지 않습니다. 이 스킬은 대화 세션이 켜져
있을 때만 동작하고, `trade-gen4`는 세션과 무관하게 매일 자정 자동 실행됩니다.

**입력**: `{output_dir}/data/{slug}_buyers_leads.xlsx`의 `Sourcing_Candidates` 시트
**출력**: 같은 파일의 `Verified_Partners` 시트 (실제 회사명/이메일/웹사이트/출처 URL)
**실행 주체**: Claude Code, Gemini 등 WebSearch/WebFetch(또는 동등 도구)를 가진 대화형 AI 에이전트
— 정적 스크립트가 아니라 이 SKILL.md를 읽는 에이전트 자신이 검색을 수행합니다.

---

## 2. 절대 규칙 (요약 — 상세는 `../SKILL.md`)

1. 출처 URL 없는 정보는 절대 기록하지 않는다 (`merge_research_findings.py`가 `source_url` 없는
   레코드를 자동 거부).
2. 확실하지 않으면 빈 칸으로 둔다 — 이메일 패턴 추정 등 지어내기 금지.
3. LinkedIn은 공개 검색 결과에 노출된 프로필 URL만 기록 (로그인 스크래핑/계정 자동화 금지).
4. **회사 자체 웹사이트도 반드시 별도로 열어 접속 여부·이메일을 확인한다** (LinkedIn 등 제3자
   페이지만 보고 검증을 끝내지 않는다 — 2026-08-02 강화된 규칙. 이메일이 홈페이지에 안 보여도
   `/contact`, `/inquiry` 등 연락처 페이지를 추가로 확인한 뒤에만 "이메일 미기재"로 결론 낸다).

## 3. Playwright 등 브라우저 자동화가 필요 없는 이유

이 스킬은 정적 스크립트가 아니라 **AI 에이전트 자신의 WebSearch/WebFetch 도구**로 검색·열람을
수행합니다. 헤드리스 브라우저(Playwright/Selenium 등)로 스크래핑하는 구조가 아니며, 로그인이
필요한 페이지 접근이나 계정 자동화는 애초에 지원하지 않습니다 (규칙 3번). 스크린샷 증빙까지
필요해지면 별도로 `.agents/skills/webapp-testing/`(Playwright 기반)을 붙이는 것을 고려하되,
현재 파트너 마이닝 용도로는 불필요합니다.
