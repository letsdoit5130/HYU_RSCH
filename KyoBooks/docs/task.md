# 교보문고 베스트셀러 분석 자동화 프로젝트 작업 이력 (Task List)

본 문서는 교보문고 실시간 베스트셀러 데이터 수집 및 고도화 분석 자동화 프로젝트의 수행 단계와 진행 상황을 관리하는 문서입니다.

---

## 1. 프로젝트 개요
- **목적**: 교보문고 실시간 베스트셀러 API 정보의 자동 탐색 및 정밀 데이터 수집, 비즈니스 지표 대시보드 구축 및 분석 문서/발표자료 자동 빌드
- **대상**: 교보문고 실시간 베스트셀러 전체 목록 (상위 50권)

---

## 2. 세부 작업 진행 상황 (Task Status)

- [x] **1단계: Playwright 기반 API 정보 자동 탐색 스크립트 작성 및 수행**
  - 파일: [capture_api.py](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/src/capture_api.py)
  - 내용: 브라우저 XHR 네트워크 요청을 가로채 `x-api-gw-key` 헤더 값 캡처 성공
- [x] **2단계: 교보문고 API 기반 고속 데이터 수집기 구현 (순위 보정)**
  - 파일: [scraper.py](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/src/scraper.py)
  - 내용: 교보문고 API의 6위 순위 누락으로 인한 51위 포함 이슈를 1~50위 순차 재지정하는 보정 로직을 탑재하여 [bestsellers.csv](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/data/bestsellers.csv) 갱신 완료
- [x] **3단계: 탐색적 데이터 분석(EDA) 시각화 스크립트 구현**
  - 파일: [eda.py](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/src/eda.py)
  - 내용: 한글 깨짐 방지 폰트 처리, 출판사 점유율, 가격/할인율 분포, 장르 워드클라우드 및 상관관계 맵 등 이미지 5종 생성 완료
- [x] **4단계: openpyxl 기반 분석 및 KPI 엑셀 대시보드 구축**
  - 파일: [build_excel_dashboard.py](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/src/build_excel_dashboard.py)
  - 내용: 엑셀 파일 잠금 해제 조치 완료 후 [bestsellers_dashboard.xlsx](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/docs/bestsellers_dashboard.xlsx) 최종 정상 생성 및 갱신 완료
- [x] **5단계: 데이터 분석 보고서 마크다운 자동 빌드 및 MS Word 문서 변환**
  - 파일: [convert_to_docx.py](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/src/convert_to_docx.py)
  - 내용: 요약 지표가 반영된 마크다운 보고서([eda_report.md](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/docs/eda_report.md)) 작성 및 스타일 테마가 지정된 [eda_report.docx](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/docs/eda_report.docx) 파일로 변환 성공
- [x] **6단계: 16:9 와이드스크린 규격 PPTX 발표 자료 자동 생성 (10장 확장)**
  - 파일: [build_pptx_slides.py](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/src/build_pptx_slides.py)
  - 내용: 슬라이드 장수를 10장으로 분리하고, 하단 슬라이드 노트에 구체적인 한국어 발표자 스크립트를 포함한 [bestsellers_presentation.pptx](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/docs/bestsellers_presentation.pptx) 완성
- [x] **7단계: 작업 완료 보고서(Walkthrough) 및 태스크 이력(Task) 문서화**
  - 파일: [walkthrough.md](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/docs/walkthrough.md), [task.md](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/KyoBooks/docs/task.md)
  - 내용: 프로젝트 진행 결과 보고 및 전체 작업 일정 목록 백업 완료
