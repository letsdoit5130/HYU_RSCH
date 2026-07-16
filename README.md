# 📚 교보문고 실시간 베스트셀러 분석 자동화 & 웹앱 대시보드

본 저장소는 교보문고의 실시간 베스트셀러(상위 99권) 데이터를 수집, 정제하여 데이터 기반의 탐색적 데이터 분석(EDA), 보고서(Excel, Word, PPTX) 자동 생성 및 인터랙티브 웹 대시보드로 배포하는 데이터 사이언스 파이프라인 프로젝트입니다.

---

## 🌐 라이브 웹 대시보드 배포 링크
본 프로젝트의 최종 웹 애플리케이션 대시보드는 **GitHub Pages**를 통해 호스팅되고 있습니다. 아래 링크를 클릭하시면 웹 브라우저 상에서 인터랙티브한 차트와 상세 도서 목록을 바로 탐색하실 수 있습니다.

> ### 🔗 **[실시간 웹앱 대시보드 바로가기 (Click)](https://letsdoit5130.github.io/HYU_RSCH/)**
> *접속 시 루트 리다이렉터를 거쳐 최신 99종 데이터 대시보드 화면으로 즉시 연결됩니다.*

---

## 🛠️ 대시보드 주요 기능
1. **4대 핵심 KPI 카드**: 총 도서 수, 평균 가격, 평균 할인율, 누적 리뷰 건수를 실시간 갱신.
2. **Chart.js 연동 인터랙티브 시각화**:
   - 🏭 *출판사 점유율 (수평 막대)*: 상위 10개 출판사의 도서 등록 현황.
   - 💸 *도서 가격대 분포 (라인 영역)*: 5천 원 단위 가격 저항선 분석.
   - 🧩 *장르별 비중 (도넛)*: 인문, 소설, 경제경영 등 카테고리 비율.
   - 📈 *독자 반응 상관관계 (산점도)*: 평점 만족도와 리뷰 수 간의 디커플링 진단.
3. **데이터 그리드 테이블**: 순위, 가격, 평점, 리뷰수 등을 열 클릭 시 실시간 정렬(Sort) 및 10권 단위 페이징(Pagination).
4. **상세 정보 모달 팝업**: 각 도서 행 클릭 시 표지 이미지, 상세 출판 정보 및 부제목(요약 소개글) 팝업 렌더링.

---

## 📂 프로젝트 구조 및 산출물 경로

```
HYU_RSCH/
├── KyoBooks/
│   ├── data/
│   │   ├── api_config.json       # API 헤더 및 인증 키 설정
│   │   └── bestsellers.csv       # 정제 완료된 99종 도서 csv 원천 데이터
│   ├── src/
│   │   ├── capture_api.py        # Playwright 기반 API 게이트웨이 키 캡처 스크립트
│   │   ├── scraper.py            # API 기반 전체 페이지 수집 및 중복 제거 수집기
│   │   ├── eda.py                # matplotlib/seaborn 한글 폰트 적용 차트 이미지 생성기
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
│       └── task.md               # 프로젝트 작업 이력서
├── index.html                    # GitHub Pages 루트 리다이렉터 웹페이지
└── README.md                     # 본 프로젝트 소개 및 배포 안내서
```

---

## 🚀 파이프라인 스크립트 실행 방법

로컬 환경에서 데이터를 새로 수집하고 문서를 갱신하려면 가상환경(`.venv`) 내에서 아래 스크립트들을 순서대로 실행하십시오.

```bash
# 1. API 게이트웨이 키 캡처 및 도서 데이터 전체 수집 (99권)
python KyoBooks/src/scraper.py

# 2. EDA 이미지 생성
python KyoBooks/src/eda.py

# 3. 엑셀 대시보드 갱신
python KyoBooks/src/build_excel_dashboard.py

# 4. 워드 보고서 갱신
python KyoBooks/src/convert_to_docx.py

# 5. PPTX 슬라이드 갱신
python KyoBooks/src/build_pptx_slides.py

# 6. 배포용 HTML 웹앱 대시보드 빌드
python KyoBooks/src/build_html_dashboard.py
```
