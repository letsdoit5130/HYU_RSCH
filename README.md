# 🔬 한양대학교 도서 시장 실시간 데이터 마이닝 및 시각화 연구 저장소 (HYU_RSCH)

본 저장소는 국내 주요 온·오프라인 도서 유통 채널(교보문고, YES24 등)의 실시간 베스트셀러 데이터를 수집하여 통계 분석, 자동 보고서(Excel, Word, PPTX) 발행 및 대화형 웹 대시보드를 구축하는 통합 연구 프로젝트입니다.

---

## 🔗 교보문고 실시간 웹앱 대시보드 접근 주소
GitHub Pages 서비스를 통해 실시간으로 호스팅되는 교보문고 베스트셀러 대시보드 웹앱의 공식 접속 경로입니다. 

> ### 🟢 **[교보문고 실시간 웹앱 대시보드 바로가기 (Click)](https://letsdoit5130.github.io/HYU_RSCH/)**
> *접속 시 루트 리다이렉터를 거쳐 에메랄드 HSL 글래스모피즘 테마의 베스트셀러 99종 대시보드 화면으로 즉시 연결됩니다.*

---

## 📂 저장소 전체 프로젝트 구조 및 기능

저장소는 유통 채널별로 모듈화되어 관리됩니다.

### 1. 교보문고 프로젝트 (`KyoBooks/`)
교보문고 실시간 베스트셀러 99종 데이터 수집 및 웹 기반 시각화 대시보드를 전담하는 프로젝트 폴더입니다.
- **수집 기능**: Playwright 기반 API 토큰 자동 탐색 및 자가 갱신 수집기 구현. 6위 누락 오류를 강제 보정하여 1~99위 고유 도서 확보.
- **분석 및 리포팅**: 9,000자 분량의 정밀 기술통계 해석 리포트(Word, Markdown) 및 10장 확대 발표자료(PPTX) 자동 발행.
- **배포**: HSL 에메랄드 테마 및 Chart.js API 기반 정적 웹 대시보드 생성.

### 2. YES24 프로젝트 (`yes24/`)
YES24 베스트셀러 데이터를 수집 및 분석하는 프로젝트 폴더입니다.
- **수집 및 분석**: 수험서, 소설 등 주요 베스트셀러 목록 크롤링 및 EDA 이미지 생성.
- **문서 빌더**: 엑셀 KPI 대시보드 및 마크다운 기반 Word/Marp 발표 자료 슬라이드 생성 로직 포함.

---

## 🗂️ 저장소 상세 디렉토리 구조

```
HYU_RSCH/
├── index.html                    # GitHub Pages 기본 리다이렉터 웹페이지
├── README.md                     # 본 통합 저장소 소개 및 웹앱 배포 안내서 (현재 파일)
│
├── KyoBooks/                     # [프로젝트 1] 교보문고 베스트셀러 파이프라인
│   ├── data/
│   │   ├── api_config.json       # API 헤더 및 인증 키 보관
│   │   └── bestsellers.csv       # 정제 완료된 99종 도서 csv 데이터
│   ├── src/
│   │   ├── capture_api.py        # Playwright 기반 API 게이트웨이 키 자동 캡처
│   │   ├── scraper.py            # API 기반 전체 페이지 수집 및 중복 제거
│   │   ├── eda.py                # matplotlib 한글 폰트 적용 차트 이미지 생성기
│   │   ├── build_excel_dashboard.py   # openpyxl 수식 연동 엑셀 대시보드 빌더
│   │   ├── convert_to_docx.py    # py-eda 2000자 해석 규칙 적용 MS Word 변환기
│   │   ├── build_pptx_slides.py  # 10장 구성 포레스트그린 테마 PPTX 빌더
│   │   └── build_html_dashboard.py  # 데이터 인라인 주입 HTML 대시보드 빌더
│   ├── images/
│   │   └── *.png                 # 생성된 시각화 이미지 5종
│   └── docs/
│       ├── bestsellers_dashboard.xlsx   # 완성된 엑셀 보고서 파일
│       ├── bestsellers_presentation.pptx # 완성된 PPTX 발표 자료 (스피커 노트 내장)
│       ├── eda_report.docx       # 완성된 MS Word 종합 보고서
│       ├── eda_report.md         # 9,000자급 기술통계 해석 마크다운 보고서
│       ├── dashboard.html        # 로컬 구동용 대시보드 웹앱 (원본)
│       ├── dashboard_plan.md     # 웹앱 대시보드 정밀 개발 계획서
│       └── task.md               # 프로젝트 작업 이력서
│
└── yes24/                        # [프로젝트 2] YES24 베스트셀러 파이프라인
    ├── src/                      # YES24 데이터 처리 및 시각화 코드
    ├── images/                   # YES24 시각화 차트 이미지 저장
    └── docs/                     # YES24 엑셀 대시보드, Word 보고서, Marp 슬라이드
```

---

## 🚀 채널별 스크립트 실행 가이드

각 프로젝트 디렉토리 내의 가상환경(`.venv`) 내에서 아래 명령어들로 데이터 파이프라인을 구동할 수 있습니다.

### 교보문고 파이프라인 구동
```bash
# 1. API 키 캡처 및 도서 데이터 전체 수집 (99권)
python KyoBooks/src/scraper.py

# 2. EDA 이미지 생성
python KyoBooks/src/eda.py

# 3. 엑셀 대시보드 갱신
python KyoBooks/src/build_excel_dashboard.py

# 4. Word 및 마크다운 보고서 갱신
python KyoBooks/src/convert_to_docx.py

# 5. PPTX 슬라이드 갱신
python KyoBooks/src/build_pptx_slides.py

# 6. 배포용 HTML 웹앱 대시보드 빌드
python KyoBooks/src/build_html_dashboard.py
```

### YES24 파이프라인 구동
```bash
# 1. 데이터 수집 및 EDA 실행
python yes24/src/eda.py

# 2. 분석 엑셀 대시보드 구축
python yes24/src/build_excel_dashboard.py

# 3. Word 보고서 변환
python yes24/src/convert_to_docx.py
```
