---
name: trade-gen1-un-eda
description: UN Comtrade 등 무역 통계 CSV 데이터를 기반으로 범용 EDA 리포트, 17개 시각화 차트, 자국(--home_country) 수출 포지션 벤치마크, 신시장 개척 TOP 5, 적정 수출단가 산출, 삼국무역(중계무역) 후보 매트릭스, 1인 상사 시장개척 전략 및 HS Code별 TOP 10 유망 타겟시장 분석표를 자동 생성하는 스킬입니다. 무역 데이터, UN Comtrade CSV, EDA 리포트 자동 생성 요청 시 활성화됩니다.
---

# 📊 Trade EDA Generator (범용 무역 데이터 EDA 리포트 생성 스킬)

이 스크립트는 UN Comtrade 또는 무역 통계 데이터 CSV 파일이 주어졌을 때, 1인 종합상사 창업자 시각에서
**다차원 통계 분석, 17개 시각화 차트 PNG 저장, 무역액 기준 동적 산출 TOP 10 HS Code별 TOP 10 유망
타겟시장 분석표, 자국 수출 포지션 벤치마크, 신시장 개척 TOP 5, 적정 수출단가 산출, 바이어 전략 부록이
결합된 종합 EDA 보고서를 자동으로 완벽 생성**합니다.

---

## ⭐ 핵심 설계 원칙 — Import/Export 방향을 반드시 구분한다

UN Comtrade 데이터를 "수출(Export) 데이터 + 수입(Import) 데이터"를 합쳐서 수집하는 경우
(예: 1) 내 소싱국(자국) → 전세계 Export, 2) 전세계 ↔ 전세계 Import), 두 데이터는 성격이
완전히 다릅니다:

- **Import 행**: `reporterDesc` = 수입국(**타겟시장 후보**), `partnerDesc` = 원산지(**경쟁 수출국**)
- **Export 행**: `reporterDesc` = 수출국, `partnerDesc` = 목적지

이걸 구분 없이 하나로 합쳐서 처리하면 "TOP 10 수출국/수입국" 랭킹이 실제로는 뒤바뀐 값을 보여주는
치명적 오류가 발생합니다 (실사용 데이터에서 실제로 확인된 문제). 이 스크립트는 `flowDesc` 컬럼을
기준으로 **Import 서브셋과 Export 서브셋을 항상 분리해서 처리**합니다. `flowDesc` 컬럼이 없는 CSV는
레거시 모드로 전체 데이터를 방향 구분 없이 처리하며, 이 경우 리포트 상단에 경고 문구가 표시됩니다.

### Export 데이터 수집 권장 사항

- Export를 **자국(예: 한국) 단독**으로만 수집하면(1)의 방식), "자국 포지션 벤치마크" 섹션은 정확히
  나오지만 "글로벌 경쟁 수출국" 랭킹(02번 차트)은 Import 쪽 원산지 데이터로 **간접 추정**할 수밖에
  없습니다 (리포트에 이 사실이 명시됩니다).
- Export를 **`reporter=all`**로 수집하면(모든 국가가 자기 수출을 직접 신고한 데이터), 02번 차트가
  간접 추정이 아닌 **직접 신고 기준**으로 정확해지고, Comtrade에 수입 통계를 잘 보고하지 않는
  국가(중동/아프리카 등)까지 경쟁 수출국의 신고를 통해 간접적으로 포착할 수 있습니다. 자국 벤치마크는
  이 확장된 데이터셋에서 `--home_country`로 필터링하면 그대로 나오므로 데이터를 잃지 않습니다.

---

## 🛠️ 스킬 사용법 (Usage)

터미널이나 Python 명령어로 무역 CSV 파일 경로와 품목명, 출력 폴더를 지정하여 실행합니다:

```bash
uv run python .agents/skills/trade-gen1-un-eda/scripts/generate_trade_eda.py \
  --input BIZ-Jeonbok/BIZ-JB-Gathered.csv \
  --item "전복 (Abalone)" \
  --output_dir BIZ-Jeonbok \
  --home_country "Korea"
```

### 입력 파라미터

- `--input` (필수): 분석할 무역 통계 CSV 파일 경로 (예: `BIZ-Jeonbok/BIZ-JB-Gathered.csv` 또는 `BIZ-laver/data.csv`)
- `--item` (필수): 품목명 (예: `전복`, `김 (Laver)`, `광어`, `굴` 등)
- `--output_dir` (필수): 차트 이미지(`images/`) 및 최종 마크다운 리포트(`reports/`)가 저장될 프로젝트 루트 디렉터리
- `--home_country` (선택, 기본값 `Korea`): 벤치마크 기준이 되는 자국(수출국) 이름. CSV의
  `reporterDesc`/`partnerDesc` 표기에 **부분 문자열로 포함되면 매칭**됩니다 (예: 기본값 `Korea`는
  Comtrade 표기 `Rep. of Korea`와 자동으로 매칭됨). 한국이 아닌 다른 소싱국을 기준으로 벤치마크하고
  싶다면 국가명을 바꿔서 지정하세요.
- `--item_slug` (선택): 데이터/리포트 파일명 슬러그 (생략 시 `--item`에서 자동 생성)

---

## 📈 자동 생성되는 17개 필수 시각화 차트 목록

`py-eda` 지침을 준수하여 전역 테마 변경 없이 `koreanize-matplotlib`를 사용하여 17개의 차트를 `images/` 폴더에 자동 생성합니다:

1. `01_annual_trade_trend.png`: 연도별 무역 규모 및 수출입 추이 (최신연도 보고지연 시 각주 표시)
2. `02_top_exporter_ranking.png`: TOP 10 **글로벌 경쟁 수출국** 무역액 비교 (Export가 reporter=all이면 직접신고, 아니면 간접추정 — 출처 명시)
3. `03_top_importer_ranking.png`: TOP 10 **유망 타겟시장(수입국)** 무역액 비교
4. `04_unit_price_distribution.png`: 품목/국가별 단가($/kg) 분포 히스토그램
5. `05_monthly_seasonality.png`: 월별 수출입 계절성 분석
6. `06_hs_code_share.png`: HS Code별 무역 점유율 파이 차트
7. `07_price_vs_weight_scatter.png`: 단가 vs 물량 산점도 (Correlation)
8. `08_top5_importer_growth.png`: TOP 5 유망 타겟시장 연도별 **CAGR(연평균복합성장률)** 추이
9. `09_market_concentration_pareto.png`: 타겟시장 집중도 파레토 차트 (Pareto 80/20)
10. `10_export_price_heatmap.png`: 주요 타겟시장별/연도별 단가 변화 히트맵
11. `11_trade_balance_waterfall.png`: 무역 수지 폭포수 차트
12. `12_country_price_boxplot.png`: 타겟시장별 단가 변동성 박스플롯
13. `13_hhi_index_trend.png`: 타겟시장 **수요 집중도**(HHI Index) 연도별 추이
14. `14_size_pricing_structure.png`: 단가 기준 **가격대(4분위) 구조** (실제 사이즈/규격 데이터 아님 — 명칭 변경됨)
15. `15_promising_country_matrix.png`: TOP 10대 HS Code별 유망 타겟시장 성장성(CAGR) vs 단가 매트릭스
16. `16_home_price_positioning.png` **(신규)**: `--home_country` 수출단가 vs 시장평균 수입단가 포지셔닝 (가격 경쟁력 비교)
17. `17_market_supplier_hhi.png` **(신규)**: TOP 유망시장별 공급국 집중도(HHI) — 레드오션(≥2500)/중간(1500~2500)/블루오션(<1500) 판별

---

## 📋 생성되는 마크다운 종합 EDA 리포트 구성

`reports/BIZ-{ITEM}_Gathered_EDA_Report.md` 파일로 작성되며 아래 항목을 모두 포함합니다:

1. **Executive Summary**: 핵심 수치 요약 + Import/Export 분리 처리 방식 안내 + 최신연도 보고지연 경고(해당 시)
2. **데이터 개요 및 정제 보고**: 누적 레코드, 주요 변수, 결측치 정제 내역
3. **17개 다차원 시각화 차트 및 통계 인사이트 해설**
> ⚠️ **4~7번은 전부 무역액 기준 TOP 3 HS Code별로 독립 산출**됩니다(`TOP_N_PRICE_HS`). 생물/냉동/건조/가공처럼
> 성격이 다른 상품을 블렌딩하면 단가가 심하게 왜곡되기 때문입니다(예: 생물 $6/kg vs 건조·가공 $500+/kg).
> 리포트 안에서 "📦 [HS 코드]" 하위 블록으로 HS Code마다 반복해서 보여줍니다.

4. **`--home_country` 포지션 벤치마크 (신규)**: HS Code별로, 자국이 실제로 어느 목적지에 얼마나,
   어떤 단가로, 얼마의 CAGR로 수출하고 있는지 (직접 신고 우선, 없으면 상대국 Import 미러 데이터로 대체 추정)
5. **신시장 개척 TOP 5 (신규)**: HS Code별로, TOP 유망 타겟시장 중 `--home_country` 수출 실적이 없는 곳을
   시장규모 순으로 최대 5개 선정 + 그 시장의 공급국 집중도(HHI)
6. **적정 수출단가(Target Price) 산출 (신규)**: HS Code별로, 타겟시장별 시장평균 수입단가, 권장
   오퍼밴드(평균±표준편차), `--home_country` 현재단가와의 포지션 비교. `primaryValue`는 Comtrade
   정의상 Export 행=FOB, Import 행=CIF 값이 이미 반영돼 있어 별도 환산 없이 그대로 비교합니다.
7. **삼국무역(중계무역) 후보 매트릭스 (신규)**: HS Code별로, `--home_country` 소싱이 여의치 않을 때를 대비한
   대안 전략. 대체 소싱국(B) → 판매 타겟시장(C/D) 조합을 마진갭 기준으로 자동 랭킹하고, B가 그
   시장에 이미 진출해 있는지(점유율)로 화이트스페이스 여부를 표시. FTA 미적용/중계무역 신고 절차/
   제재 대상국 확인 필요성을 항상 함께 명시.
8. **1인 상사 창업자 맞춤형 3대 시장개척 전략** (CAGR 기준으로 고성장 시장 산출)
9. **동적 산출 TOP 10 HS Code별 TOP 10 유망 타겟시장 11대 필드 명세 표** (재수출 허브 국가는
   `⚠️재수출허브` 배지 표시, `--home_country` 기수출 여부 표시)
10. **B2B 오퍼서 초안, 콜드 어프로치 파이프라인, 박람회 일정 부록**

---

## ⚠️ 알아두어야 할 데이터 한계 (정직하게 명시)

- **최신 연도 보고 지연**: UN Comtrade는 국가별 자발적 보고라 최신 연도일수록 보고국 수가 급감합니다.
  이 스크립트는 직전연도 대비 보고국 수가 60% 미만으로 급감한 최신 연도를 순위/CAGR 계산에서 자동
  제외하고 그 사실을 리포트에 명시합니다. 실제 수요 감소가 아니라 보고 시차 때문일 가능성이 높습니다.
- **재수출 허브**: 홍콩·싱가포르·네덜란드·UAE·벨기에·파나마는 최종 소비지가 아닐 가능성이 높아 표에
  `⚠️재수출허브` 배지가 붙습니다. 데이터에서 제외하지는 않으므로(실제 유효 시장일 수도 있어서) 해석
  시 주의가 필요합니다.
- **Comtrade 미보고국 사각지대**: 중동/아프리카 등 자체 수입 통계를 잘 보고하지 않는 나라는 Import
  데이터에 아예 안 잡힙니다. Export를 `reporter=all`로 수집하면(위 "Export 데이터 수집 권장 사항"
  참고) 경쟁 수출국의 신고를 통해 간접 포착이 가능합니다.
- **간접 추정 표기**: 02번 차트(글로벌 경쟁 수출국)와 여러 정성적 필드(파트너/인증/유통채널/마진 등)는
  실제 신고 데이터가 아니라 간접 추정 또는 업계 일반 템플릿인 경우 리포트에 반드시 그 사실을
  표기합니다. 확인 없이 그대로 영업 자료에 옮기지 마세요.
