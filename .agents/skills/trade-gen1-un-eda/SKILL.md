---
name: trade-gen1-un-eda
description: UN Comtrade 등 무역 통계 CSV 데이터를 기반으로 범용 EDA 리포트, 15개 시각화 차트, 1인 상사 시장개척 전략 및 HS Code별 TOP 10 유망국가 분석표를 자동 생성하는 스킬입니다. 무역 데이터, UN Comtrade CSV, EDA 리포트 자동 생성 요청 시 활성화됩니다.
---

# 📊 Trade EDA Generator (범용 무역 데이터 EDA 리포트 생성 스킬)

이 스크립트는 UN Comtrade 또는 무역 통계 데이터 CSV 파일이 주어졌을 때, 1인 종합상사 창업자 시각에서 **다차원 통계 분석, 15개 시각화 차트 PNG 저장, 무역액 기준 동적 산출 TOP 10 HS Code별 TOP 10 유망국가 분석표, 바이어 전략 부록이 결합된 종합 EDA 보고서를 자동으로 완벽 생성**합니다.

---

## 🛠️ 스킬 사용법 (Usage)

터미널이나 Python 명령어로 무역 CSV 파일 경로와 품목명, 출력 폴더를 지정하여 실행합니다:

```bash
uv run python .agents/skills/trade-gen1-un-eda/scripts/generate_trade_eda.py \
  --input BIZ-Jeonbok/BIZ-JB-Gathered.csv \
  --item "전복 (Abalone)" \
  --output_dir BIZ-Jeonbok
```

### 필수 입력 파라미터:
- `--input`: 분석할 무역 통계 CSV 파일 경로 (예: `BIZ-Jeonbok/BIZ-JB-Gathered.csv` 또는 `BIZ-laver/data.csv`)
- `--item`: 품목명 (예: `전복`, `김 (Laver)`, `광어`, `굴` 등)
- `--output_dir`: 차트 이미지(`images/`) 및 최종 마크다운 리포트(`reports/`)가 저장될 프로젝트 루트 디렉터리

---

## 📈 자동 생성되는 15개 필수 시각화 차트 목록

`py-eda` 지침을 준수하여 전역 테마 변경 없이 `koreanize-matplotlib`를 사용하여 15개의 차트를 `images/` 폴더에 자동 생성합니다:

1. `01_annual_trade_trend.png`: 연도별 무역 규모 및 수용 추이
2. `02_top_exporter_ranking.png`: TOP 10 수출국 무역액 비교
3. `03_top_importer_ranking.png`: TOP 10 수입국 무역액 비교
4. `04_unit_price_distribution.png`: 품목/국가별 단가($/kg) 분포 히스토그램
5. `05_monthly_seasonality.png`: 월별 수출입 계절성 분석
6. `06_hs_code_share.png`: HS Code별 무역 점유율 파이 차트
7. `07_price_vs_weight_scatter.png`: 단가 vs 물량 산점도 (Correlation)
8. `08_top5_importer_growth.png`: TOP 5 주요 수입국 연도별 성장률 추이
9. `09_market_concentration_pareto.png`: 시장 집중도 파레토 차트 (Pareto 80/20)
10. `10_export_price_heatmap.png`: 주요 국가별/연도별 단가 변화 히트맵
11. `11_trade_balance_waterfall.png`: 무역 수지 폭포수 차트
12. `12_country_price_boxplot.png`: 국가별 단가 변동성 박스플롯
13. `13_hhi_index_trend.png`: 허핀달-허쉬만 시장 집중도(HHI Index) 추이
14. `14_size_pricing_structure.png`: 품목별 규격/사이즈(Size & Spec) 및 가격 구조
15. `15_promising_country_matrix.png`: 3대 HS Code별 유망국가 종합 매트릭스

---

## 📋 생성되는 마크다운 종합 EDA 리포트 구성

`reports/{ITEM}_Gathered_EDA_Report.md` 파일로 작성되며 아래 항목을 모두 포함합니다:

1. **Executive Summary**: 핵심 수치 요약 및 품목별 규격/사이즈(Size & Spec) 가격 구조 표
2. **데이터 개요 및 정제 보고**: 누적 레코드, 주요 변수, 결측치 정제 내역
3. **15개 다차원 시각화 차트 및 200자 이상 통계 인사이트 해설**
4. **1인 상사 창업자 맞춤형 3대 시장개척 전략**
5. **동적 산출 TOP 10 HS Code별 TOP 10 유망국가 11대 필드 명세 표**
6. **B2B 오퍼서 초안, 콜드 어프로치 파이프라인, 박람회 일정 부록**
