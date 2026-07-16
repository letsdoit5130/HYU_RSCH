# 교보문고 베스트셀러 데이터 수집 및 분석 자동화 구현 계획서

본 계획서는 교보문고 실시간 베스트셀러 데이터를 수집(스크래핑)하고, 이를 바탕으로 탐색적 데이터 분석(EDA), 엑셀 대시보드 구축, Word 보고서 생성, 그리고 PowerPoint 발표 자료 작성까지의 전 과정을 자동화하는 파이프라인 구축 계획을 담고 있습니다.

## 1. 목표 및 범위 (Goal)
- **수집 대상**: 교보문고 실시간 베스트셀러 전체 목록 ([실시간 베스트셀러 페이지](https://store.kyobobook.co.kr/bestseller/realtime?page=1&per=50))
- **수집 방식**: Playwright를 활용하여 브라우저 네트워크 패킷을 가로채고, 실제 데이터가 제공되는 내부 REST API의 URL 및 `x-api-gw-key` 헤더 값을 자동으로 탐색/추출. 이후 이 정보를 이용해 가볍고 빠른 `requests` 기반의 수집기(`scraper.py`) 작동.
- **산출물**:
  1. **데이터**: `KyoBooks/data/bestsellers.csv`
  2. **시각화 이미지**: `KyoBooks/images/` 내부 (출판사 점유율, 가격 분포, 상관관계 등)
  3. **엑셀 대시보드**: `KyoBooks/docs/bestsellers_dashboard.xlsx` (오픈파이엑셀로 포맷팅 및 실제 차트 삽입)
  4. **보고서 (Word)**: `KyoBooks/docs/bestsellers_report.docx` (분석 보고서 양식의 문서)
  5. **발표 슬라이드 (PPTX)**: `KyoBooks/docs/bestsellers_presentation.pptx` (디자인 스타일 적용 슬라이드)

---

## 2. 사용자 검토 및 확인 필요 사항 (User Review Required)
- **Playwright 라이브러리 및 브라우저 설치**:
  - API 정보의 자동 탐색을 위해 가상환경 내에 `playwright` 라이브러리 설치와 Chromium 브라우저 바이너리 다운로드가 필요합니다. 본 계획 승인 시 스크립트 실행 전에 자동으로 설치 과정을 거칩니다.
- **API 키 만료 대응**:
  - 교보문고 게이트웨이 키(`x-api-gw-key`)가 주기적으로 만료되는 특성을 가집니다. 따라서, 자동 탐색 스크립트(`KyoBooks/src/capture_api.py`)를 개발하여, 수집 실패 시 자동으로 새로운 키를 갱신하여 긁어오도록 스크래퍼와 연동시킬 계획입니다.

---

## 3. 세부 구현 단계 (Proposed Roadmap)

### 1단계: Playwright 기반 API 탐색 및 자동 기입 스크립트 개발
- **목적**: 교보문고 실시간 베스트셀러 페이지를 Chromium 브라우저(headless)로 로드하고, 발생하는 API 통신 중 `x-api-gw-key` 헤더를 포함한 요청을 가로채 파일에 자동 기록합니다.
- **새로 생성할 파일**: `KyoBooks/src/capture_api.py` [NEW]
  - 이 파일은 가로챈 정보를 `KyoBooks/docs/scaraping_prompt.md` 파일의 특정 빈칸에 업데이트합니다.

### 2단계: 교보문고 API 기반 고속 수집기 (`scraper.py`) 개발
- **목적**: 1단계에서 추출된 API URL과 헤더 정보를 기반으로 데이터를 고속으로 긁어와 CSV 파일로 누적 저장합니다.
- **새로 생성할 파일**: `KyoBooks/src/scraper.py` [NEW]
  - 상품번호, 순위, 도서명, 부제목, 저자, 출판사, 출판일, 정가, 할인가, 할인율, 판매지수, 리뷰건수, 평점, 태그, 이미지 URL 등 수집.
  - 수집 완료 후 중복을 제거하고 `KyoBooks/data/bestsellers.csv`로 저장.

### 3단계: 탐색적 데이터 분석 (`eda.py`) 개발
- **목적**: Pandas, Matplotlib, Seaborn 등을 이용하여 시각화 이미지 5종을 생성하고 저장합니다.
- **새로 생성할 파일**: `KyoBooks/src/eda.py` [NEW]
  - 점유율 상위 10개 출판사 분석
  - 주요 수치형 지표(정가, 할인가, 판매지수 등) 상관관계 Heatmap
  - 가격 분포 차트 (정가 vs 할인가)
  - 평점 분포 및 리뷰 수 분석
  - 도서 태그 키워드 빈도 WordCloud

### 4단계: 엑셀 분석 대시보드 (`build_excel_dashboard.py`) 개발
- **목적**: openpyxl을 사용해 수식 집계(COUNTIF, AVERAGEIFS 등)와 엑셀 내장 차트가 포함된 멋진 보고서 형태의 대시보드를 생성합니다.
- **새로 생성할 파일**: `KyoBooks/src/build_excel_dashboard.py` [NEW]
  - **시트 구성**: Dashboard (KPI 카드 및 주요 차트), Analysis (수식 집계), RawData (원본 데이터)
  - 감청색(Dark Navy) 혹은 교보문고 브랜드 색상(초록/Dark Green) 중심의 세련된 디자인 가이드라인 적용.

### 5단계: 워드 보고서 변환 (`convert_to_docx.py`) 및 PPTX 발표자료 작성 (`build_pptx_slides.py`)
- **목적**: 분석 결과를 문서(docx) 및 디자인 스타일이 반영된 슬라이드(pptx)로 자동 빌드합니다.
- **새로 생성할 파일**:
  - `KyoBooks/src/convert_to_docx.py` [NEW]
  - `KyoBooks/src/build_pptx_slides.py` [NEW]

---

## 4. 검증 계획 (Verification Plan)
1. **API 탐색 검증**: `capture_api.py`를 실행하여 `scaraping_prompt.md` 파일에 유효한 API 정보와 헤더 정보가 갱신되는지 확인합니다.
2. **수집기 검증**: `scraper.py`를 구동하여 실제 베스트셀러 도서 목록 50개 이상이 에러 없이 수집 및 정제되어 `bestsellers.csv`에 올바르게 저장되는지 검증합니다.
3. **분석 및 포맷팅 검증**: EDA 이미지 생성 여부, 엑셀/워드/PPT 파일이 손상 없이 열리고 서식 및 차트가 의도대로 반영되었는지 확인합니다.
