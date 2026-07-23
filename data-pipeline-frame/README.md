# 🚀 data-pipeline-frame (범용 데이터 수집 및 EDA/오피스 분석 파이프라인 프레임워크)

어떠한 타겟 웹사이트에 대해서도 데이터 수집(Scraping), API 탐색(Inspect API), 사전/사후 검증(Pre/Post Hooks & Auth/Retry/Security/Schema), 탐색적 데이터 분석(EDA), 엑셀/웹 대시보드 및 Word/PPTX 보고서를 1분 이내에 자동 생성하고 오케스트레이션하는 범용 프레임워크 모듈 집합입니다.

---

## 📂 디렉토리 및 모듈 구조

```text
data-pipeline-frame/
├── engine/                # 스캐폴딩, 파이프라인 오케스트레이터 및 5대 핵심 자가치유/보안 엔진
│   ├── generate_scaffolding.py
│   ├── run_pipeline.py
│   ├── auth_refresh_hook.py
│   ├── self_healing_retry.py
│   ├── schema_validator.py
│   └── pii_secret_guard.py
├── scraping/              # 크롤링, 동적 웹 수집, Post-Hook 및 체크포인트 관리자
│   ├── scraper.py
│   ├── dynamic_scraper.py
│   ├── post_hook.py
│   └── checkpoint_manager.py
├── inspect_api/           # API 탐색, 패킷 캡처 및 Pre-Hook 접속 가용성 검증
│   ├── capture_api.py
│   ├── inspect_api.py
│   └── pre_hook.py
├── eda/                   # 탐색적 데이터 분석 및 마크다운 보고서 생성 엔진
│   └── eda.py
└── dashboard/             # 오피스 3종(Excel/Word/PPTX) 및 HTML1페이저 웹 대시보드 빌더
    ├── build_excel_dashboard.py
    ├── build_html_dashboard.py
    ├── convert_to_docx.py
    └── build_pptx_slides.py
```
