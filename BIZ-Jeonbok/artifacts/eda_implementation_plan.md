# BIZ-JB-Gathered.csv 전복 무역 데이터 EDA 분석 구현 계획서

## 1. 개요 (Goal Description)
`BIZ-Jeonbok/BIZ-JB-Gathered.csv` 전복 무역 데이터를 대상으로 `py-eda` 전문 데이터 분석가 지침을 철저히 준수하여 종합적인 탐색적 데이터 분석(EDA)을 수행합니다. 
전체 전복 무역 동향뿐만 아니라 **품목별(`cmdDesc`) 세부 무역 특성**, 주요 거래국 TOP 10, 단가 추이 및 수량/금액 관계를 탐색하고, 최소 10개 이상의 한국어 시각화 차트와 대응 통계표, 3,000자 이상의 최종 종합 분석 리포트(`BIZ-Jeonbok/reports/BIZ-JB-Gathered_EDA_Report.md`)를 작성합니다.

---

## 2. 사용자 검토 요구사항 (User Review Required)
> [!IMPORTANT]
> - **데이터 정제 규칙**: `primaryValue`, `cifvalue`, `fobvalue`, `netWgt`, `Unit Price ($/kg)...` 등 전처리 시 기호(`$`, `,`)를 제거하고 숫자형(float)으로 안전하게 파싱합니다.
> - **품목별(`cmdDesc`) 세부 분석**: 전체 전복 무역 통계뿐만 아니라 품목별(`cmdDesc`) 무역량, 단가, 주요 국가 비중을 세분화하여 분석합니다.
> - **가상환경 및 라이브러리**: 공통 가상환경 `.venv` 상에서 `uv`로 `koreanize-matplotlib`, `pandas`, `seaborn`, `scikit-learn` 등을 사용하여 수행합니다.

---

## 3. 계획된 디렉터리 및 파일 구조 (Proposed Changes)

### [Component] Directory Setup & Standard EDA Architecture
`BIZ-Jeonbok/` 하위에 전문 EDA 분석을 위한 표준 폴더 구조를 자동 구축합니다:
- [NEW] `BIZ-Jeonbok/src/`: 데이터 처리 및 시각화 코드
- [NEW] `BIZ-Jeonbok/images/`: 시각화 차트 이미지 (.png)
- [NEW] `BIZ-Jeonbok/reports/`: 종합 EDA 분석 리포트 (.md)
- [NEW] `BIZ-Jeonbok/docs/`: 분석 관련 문서 및 스키마 명세

---

### [Component] Python EDA Script
#### [NEW] `BIZ-Jeonbok/src/eda_analysis.py`
- `py-eda` 가이드라인 100% 준수:
  - `sns.set_theme()` 사용 안 함
  - `import koreanize_matplotlib` 사용으로 한글 깨짐 방지
  - 데이터 파악: `head(5)`, `tail(5)`, `info()`, `shape`, `duplicated().sum()`
  - 기술통계: 수치형 및 범주형 `describe()` + 인사이트
  - 수치형 데이터 정제 (문자열 `$`, `,` 제거 및 float 변환)
  - 10개 이상의 다차원(일변량/이변량/다변량) 시각화 및 대응 피봇/기술통계표 생성
  - 이미지 저장: `BIZ-Jeonbok/images/01_...png` ~ `10_...png`
  - TF-IDF 텍스트 키워드 분석 (상위 30개 막대 차트 + 표)
  - 실행 후 `BIZ-Jeonbok/reports/BIZ-JB-Gathered_EDA_Report.md` 자동 / 반자동 생성

#### 분석 차트 구성 (최소 10개)
1. **01_univariate_year_month_trend.png**: 연도/월별 전역 무역 수량 및 금액 추이
2. **02_bivariate_partner_top10.png**: 주요 거래 상대국(partnerDesc) TOP 10 물량 및 금액 분포
3. **03_item_cmd_distribution.png**: 품목별(`cmdDesc`) 거래 비중 및 무역액 비교
4. **04_flow_export_import_ratio.png**: 수출 vs 수입(flowDesc) 수량 및 금액 비중
5. **05_item_unit_price_boxplot.png**: 품목별(`cmdDesc`) 단가(Unit Price) 분포 및 이상치 (박스플롯)
6. **06_yearly_unit_price_trend.png**: 연도별/품목별 평균 단가 변화 추이 (라인 차트)
7. **07_multivariate_partner_cmd_heatmap.png**: 주요 거래국 x 품목별 무역액 다변량 히트맵
8. **08_tfidf_cmd_customs_keywords.png**: 텍스트 컬럼(cmdDesc/customsDesc) TF-IDF 상위 30 키워드 (표+막대)
9. **09_partner_item_stack_bar.png**: 주요 거래국별 품목 구성 비율 (누적 막대 그래프)
10. **10_qty_vs_value_scatter.png**: 수량(netWgt/qty) vs 금액(primaryValue) 산점도 및 비즈니스 구간 분석

---

### [Component] Comprehensive Report
#### [NEW] `BIZ-Jeonbok/reports/BIZ-JB-Gathered_EDA_Report.md`
- 3,000자 이상 한국어 종합 분석 보고서 작성
- 원시 데이터 파악, 기술 통계표, 10개 시각화 차트 이미지 링크 및 각 통계표, 비즈니스 인사이트(차트당 200자 이상 해석), 핵심 결론 및 시사점 포함

---

## 4. 검증 계획 (Verification Plan)

### Automated Verification
1. 필요 패키지 설치 확인: `uv pip install koreanize-matplotlib pandas seaborn scikit-learn`
2. 분석 스크립트 실행: `uv run python BIZ-Jeonbok/src/eda_analysis.py`
3. 생성 파일 자동 검증:
   - `BIZ-Jeonbok/images/` 내 차트 10개 이상 생성 여부 확인
   - `BIZ-Jeonbok/reports/BIZ-JB-Gathered_EDA_Report.md` 존재 및 용량/글자수 검증

### Manual Verification
1. `BIZ-Jeonbok/reports/BIZ-JB-Gathered_EDA_Report.md` 마크다운 리포트에서 한글 폰트 깨짐 및 이미지 차트 렌더링 확인
2. 전체 전복 및 품목별 무역 동향 인사이트의 논리적 타당성 검토
