# 범용 웹 크롤링 및 데이터 분석 파이프라인 하네스 작업 이력 (Task List)

본 문서는 특정 웹사이트 도메인에 종속되지 않고, 임의의 웹 수집 및 탐색적 데이터 분석(EDA), 대시보드/보고서/발표자료 빌드를 1분 이내에 자동화하는 **범용 웹 크롤링 및 데이터 분석 파이프라인 하네스** 구축 작업 단계와 진행 상황을 관리하는 문서입니다.

---

## 1. 프로젝트 개요
- **목적**: 웹 크롤링부터 데이터 정제, EDA 시각화, 엑셀 대시보드(`.xlsx`), Word 보고서(`.docx`), PPTX 발표자료(`.pptx`)까지 일괄 수행하는 범용 파이프라인 하네스 정립
- **대상 범위**: 임의의 타겟 URL 및 웹 데이터 수집 파이프라인 전범위

---

## 2. 세부 작업 진행 상황 (Task Status)

- [x] **1단계: 범용 프로젝트 스캐폴딩 생성기 구현**
  - 파일: `generate_scaffolding.py`
  - 내용: 타겟 URL과 컬럼 목록 인자를 받아 표준 데이터 프로젝트 폴더 구조(`data/`, `docs/`, `images/`, `src/`) 및 뼈대 코드 자동 생성 완료

- [x] **2단계: 파이프라인 오케스트레이터 및 Pre/Post Hook 엔진 개발**
  - 파일: `run_pipeline.py`
  - 내용: 수집 전 URL 가용성/robots.txt 검증(Pre-Hook) 및 수집 후 최소 건수/결측치 비율 자동 검증(Post-Hook) 전이 로직 완성

- [x] **3단계: 크롤러 스크래퍼 템플릿 및 EDA 모듈 정립**
  - 파일: `scraper.py`, `eda.py`
  - 내용: User-Agent 우회, 요청 지연(Rate Limit), UTF-8-SIG 저장 및 Matplotlib/Seaborn 한글 깨짐 방지 폰트 자동 적용 시각화 엔진 구축

- [x] **4단계: openpyxl 기반 범용 엑셀 대시보드 자동 빌더 구축**
  - 파일: `excel_dashboard.py` (또는 `build_excel_dashboard.py`)
  - 내용: 비즈니스 테마 색상, KPI 카드 렌더링, 수식 및 피벗 데이터 시트 자동생성 기능 구현 완료

- [x] **5단계: python-docx 기반 비즈니스 문서 보고서 생성 모듈 구현**
  - 파일: `docx_report.py` (또는 `convert_to_docx.py`)
  - 내용: EDA 요약 마크다운 분석 결과를 바탕으로 스타일 서식이 적용된 Word 문서 자동 조립 기능 개발

- [x] **6단계: python-pptx 기반 발표 슬라이드 자동 빌더 구현**
  - 파일: `pptx_slides.py` (또는 `build_pptx_slides.py`)
  - 내용: 16:9 와이드스크린 규격, 카드형 UI 레이아웃 및 발표자 노트(Speaker Notes)를 포함한 PPTX 슬라이드 자동 완성

- [x] **7단계: 룰, 스킬 및 하네스 운영 문서 정립**
  - 파일: `crawler-analysis-pipeline.md`, `SKILL.md`, `implementation_plan.md`, `dashboard_plan.md`, `scraping_prompt.md`, `walkthrough.md`, `task.md`
  - 내용: 파이프라인 개발 및 검증 하네스 문서 백업 완료
