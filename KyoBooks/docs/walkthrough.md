# 교보문고 베스트셀러 데이터 수집 및 분석 자동화 완료 보고서 (Walkthrough)

교보문고 실시간 베스트셀러 데이터를 자동으로 탐색하여 수집하고, 이를 바탕으로 데이터 시각화(EDA), 엑셀 분석 대시보드 구축, 워드 문서 변환, 그리고 파워포인트 슬라이드 덱 생성까지의 파이프라인 구축을 성공적으로 완료하였습니다.

---

## 1. 생성 및 수정된 파일 리스트 (Changes Made)

### 코드 소스 (`KyoBooks/src/`)
1. **[capture_api.py](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/src/capture_api.py)** [NEW]
   - Playwright(headless Chromium)를 사용하여 교보문고 실시간 베스트셀러 페이지로 접속해 게이트웨이 인증 키(`x-api-gw-key`)를 자동으로 패킷 인터셉트하여 캡처하고 설정 파일에 기록합니다.
2. **[scraper.py](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/src/scraper.py)** [NEW]
   - 가볍고 빠른 `requests` 기반의 API 호출 수집기입니다. 호출 실패(토큰 만료 등) 감지 시 자동으로 `capture_api.py`를 서브프로세스로 구동하여 신규 헤더 정보를 갱신하고 연동을 재개하는 자가 치유 복구 로직이 적용되었습니다.
3. **[eda.py](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/src/eda.py)** [NEW]
   - Matplotlib와 Seaborn을 연동하여 수치형 전처리 및 분석 시각화 이미지 5종을 생성합니다.
4. **[build_excel_dashboard.py](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/src/build_excel_dashboard.py)** [NEW]
   - `openpyxl`을 활용하여 수식 기반 요약 및 KPI 카드 4종, 엑셀 내장 BarChart 2종이 배치된 감청색/초록색 비즈니스 대시보드 엑셀을 생성합니다.
5. **[convert_to_docx.py](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/src/convert_to_docx.py)** [NEW]
   - 수집 데이터를 정량 요약하여 `eda_report.md` 마크다운을 동적 빌드하고, 이를 깔끔한 표(Table)와 차트 이미지가 임베딩된 Word 문서로 완벽 파싱 변환합니다.
6. **[build_pptx_slides.py](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/src/build_pptx_slides.py)** [NEW]
   - 교보문고 시그니처 딥그린 테마를 반영한 16:9 와이드스크린 규격의 발표 자료 PPTX를 자동 빌드하며, 상세한 발표자 노트(Speaker Notes)를 포함합니다.

### 산출물 문서 (`KyoBooks/docs/` 및 `KyoBooks/data/`)
- **[bestsellers.csv](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/data/bestsellers.csv)**: 50권의 실시간 베스트셀러 상세 데이터 적재본.
- **[bestsellers_dashboard.xlsx](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/docs/bestsellers_dashboard.xlsx)**: 요약 통계 및 차트가 내장된 엑셀 보고서.
- **[eda_report.md](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/docs/eda_report.md)**: 분석 보고서용 마크다운 원본.
- **[eda_report.docx](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/docs/eda_report.docx)**: 고품질 정밀 서식 MS Word 보고서.
- **[bestsellers_presentation.pptx](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/docs/bestsellers_presentation.pptx)**: 포레스트 그린 테마의 발표용 파워포인트 슬라이드.
- **[scaraping_prompt.md](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/docs/scaraping_prompt.md)**: 자동 캡처된 API 주소 및 Header 세부 명세서.

---

## 2. 검증 항목 및 실행 결과 (What was Tested & Validation)

1. **Playwright API 캡처 모듈**:
   - `capture_api.py`를 실행하여 교보문고 실시간 베스트셀러 REST API와 `x-api-gw-key` 값을 성공적으로 캡처하고 `api_config.json` 및 `scaraping_prompt.md` 파일에 정상 기입되는 것을 검증하였습니다.
2. **REST API 수집기 안정성**:
   - `scraper.py`가 토큰 만료 없이 다이렉트로 API 호출을 하여 50개의 실시간 도서 정보를 정상 획득하고, UTF-8-SIG 인코딩으로 데이터프레임을 생성해 CSV 파일에 쓰기 처리되는 것을 검증하였습니다.
3. **EDA 시각화 연동**:
   - `eda.py` 실행 시 한글 폰트(맑은 고딕)가 깨지지 않고 깔끔하게 그래프 및 워드클라우드로 구현되어 `KyoBooks/images/` 디렉토리에 정상 저장되었습니다.
4. **포맷팅 변환 및 발표자료 빌드**:
   - 엑셀 수식(COUNTIF, AVERAGEIFS 등) 및 openpyxl의 BarChart가 에러 없이 렌더링되어 `bestsellers_dashboard.xlsx`가 완성되었습니다.
   - 워드 변환기를 구동해 테이블의 홀짝행 배경색과 딥그린 헤더 서식이 의도한 대로 `eda_report.docx`에 적용되었습니다.
   - `build_pptx_slides.py` 실행 결과 7페이지 규모의 포레스트 그린 카드 레이아웃의 슬라이드 및 스피커 노트가 완성되었습니다.

---

## 3. 분석 시각화 이미지 임베딩 (Visualizations)

### A. 출판사 점유율 상위 10개
![출판사 점유율](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/images/top_publishers.png)

### B. 도서 가격 분포 (정가 vs 할인가)
![가격 분포](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/images/price_distribution.png)

### C. 주요 지표 상관관계 열지도
![상관관계 열지도](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/images/correlation_heatmap.png)

### D. 도서 할인율 빈도 분포
![할인율 분포](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/images/discount_rates.png)

### E. 주요 도서 분야 워드클라우드
![워드클라우드](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/images/tag_wordcloud.png)
