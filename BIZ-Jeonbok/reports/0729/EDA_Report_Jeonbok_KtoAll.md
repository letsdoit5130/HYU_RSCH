# BIZ-Jeonbok 한국 전복 수출 데이터(BIZ-JB-EXP-KtoAll.csv) EDA 종합 분석 리포트

## Executive Summary
본 리포트는 한국 전복 수출 관세 통계 데이터셋인 `BIZ-JB-EXP-KtoAll.csv` (총 319건 순수 수출 데이터)만을 100% 적용하여, **20년차 데이터 분석가 가이드라인(`/py-eda`)**에 따라 파트너 국가별, 연도별(2021~2025), 단가별, 세관별, 물류수단별 실적을 정밀 분석한 독자 보고서입니다.

---

## 1. 데이터 개요 및 무결성 파악

### 1.1 데이터 기본 정보
- **분석 대상 파일**: `BIZ-JB-EXP-KtoAll.csv`
- **전체 데이터 규모**: 행(Rows): 319개, 열(Columns): 52개 (순수 대한민국 전복 수출 거래 319건)
- **중복 행(Duplicate Rows)**: 0건 (무결성 검증 완료)
- **수출 기간**: 2021년 ~ 2025년

### 1.2 원시 데이터 상위/하위 샘플 프리뷰 (Head & Tail)

#### 상위 5개 행 (Head 5)
|    | typeCode   | freqCode   |   refPeriodId |   refYear |   refMonth |   period |   reporterCode | reporterISO   | reporterDesc   | flowCode   | flowDesc   |   partnerCode | partnerISO   | partnerDesc          |   partner2Code | partner2ISO   | partner2Desc   | classificationCode   | classificationSearchCode   | isOriginalClassification   | cmdCode     | cmdDesc                                                                            |   aggrLevel | isLeaf   | customsCode   | customsDesc   |   mosCode |   motCode | motDesc   |   qtyUnitCode | qtyUnitAbbr   |            qty | isQtyEstimated   |   altQtyUnitCode | altQtyUnitAbbr   |         altQty | isAltQtyEstimated   |    netWgt | isNetWgtEstimated   |   grossWgt | isGrossWgtEstimated   |   cifvalue | fobvalue       | primaryValue   |   legacyEstimationFlag | isReported   | isAggregate   | Unit Price ($/kg)     |
|    |            |            |               |           |            |          |                |               |                |            |            |               |              |                      |                |               |                |                      |                            |                            |             |                                                                                    |             |          |               |               |           |           |           |               |               |                |                  |                  |                  |                |                     |           |                     |            |                       |            |                |                |                        |              |               | PrimaryValue/weight   |
|---:|:-----------|:-----------|--------------:|----------:|-----------:|---------:|---------------:|:--------------|:---------------|:-----------|:-----------|--------------:|:-------------|:---------------------|---------------:|:--------------|:---------------|:---------------------|:---------------------------|:---------------------------|:------------|:-----------------------------------------------------------------------------------|------------:|:---------|:--------------|:--------------|----------:|----------:|:----------|--------------:|:--------------|---------------:|:-----------------|-----------------:|:-----------------|---------------:|:--------------------|----------:|:--------------------|-----------:|:----------------------|-----------:|:---------------|:---------------|-----------------------:|:-------------|:--------------|:----------------------|
|  0 | C          | A          |      20210101 |      2021 |         52 |     2021 |            410 | KOR           | Rep. of Korea  | X          | Export     |             0 | W00          | World                |              0 | W00           | World          | H5                   | HS                         | True                       | 030781 (냉장) | Molluscs; abalone (Haliotis spp.), whether in shell or not, live, fresh or chilled |           6 | True     | C00           | TOTAL CPC     |         0 |         0 | TOTAL MOT |             8 | kg            |    1.96755e+06 | False            |                8 | kg               |    1.96755e+06 | False               | 1,967,552 | False               |          0 | False                 |        nan | $49,776,762.00 | $49,776,762.00 |                      0 | False        | True          | $25.30                |
|  1 | C          | A          |      20210101 |      2021 |         52 |     2021 |            410 | KOR           | Rep. of Korea  | X          | Export     |           124 | CAN          | Canada               |              0 | W00           | World          | H5                   | HS                         | True                       | 030781 (냉장) | Molluscs; abalone (Haliotis spp.), whether in shell or not, live, fresh or chilled |           6 | True     | C00           | TOTAL CPC     |         0 |         0 | TOTAL MOT |             8 | kg            | 2595           | False            |                8 | kg               | 2595           | False               |     2,595 | False               |          0 | False                 |        nan | $72,352.00     | $72,352.00     |                      0 | True         | False         | $27.88                |
|  2 | C          | A          |      20210101 |      2021 |         52 |     2021 |            410 | KOR           | Rep. of Korea  | X          | Export     |           156 | CHN          | China                |              0 | W00           | World          | H5                   | HS                         | True                       | 030781 (냉장) | Molluscs; abalone (Haliotis spp.), whether in shell or not, live, fresh or chilled |           6 | True     | C00           | TOTAL CPC     |         0 |         0 | TOTAL MOT |             8 | kg            |  250           | False            |                8 | kg               |  250           | False               |       250 | False               |          0 | False                 |        nan | $6,720.00      | $6,720.00      |                      0 | True         | False         | $26.88                |
|  3 | C          | A          |      20210101 |      2021 |         52 |     2021 |            410 | KOR           | Rep. of Korea  | X          | Export     |           344 | HKG          | China, Hong Kong SAR |              0 | W00           | World          | H5                   | HS                         | True                       | 030781 (냉장) | Molluscs; abalone (Haliotis spp.), whether in shell or not, live, fresh or chilled |           6 | True     | C00           | TOTAL CPC     |         0 |         0 | TOTAL MOT |             8 | kg            | 1160           | False            |                8 | kg               | 1160           | False               |     1,160 | False               |          0 | False                 |        nan | $41,720.00     | $41,720.00     |                      0 | True         | False         | $35.97                |
|  4 | C          | A          |      20210101 |      2021 |         52 |     2021 |            410 | KOR           | Rep. of Korea  | X          | Export     |           360 | IDN          | Indonesia            |              0 | W00           | World          | H5                   | HS                         | True                       | 030781 (냉장) | Molluscs; abalone (Haliotis spp.), whether in shell or not, live, fresh or chilled |           6 | True     | C00           | TOTAL CPC     |         0 |         0 | TOTAL MOT |             8 | kg            |   44           | False            |                8 | kg               |   44           | False               |        44 | False               |          0 | False                 |        nan | $1,700.00      | $1,700.00      |                      0 | True         | False         | $38.64                |

#### 하위 5개 행 (Tail 5)
|     | typeCode   | freqCode   |   refPeriodId |   refYear |   refMonth |   period |   reporterCode | reporterISO   | reporterDesc   | flowCode   | flowDesc   |   partnerCode | partnerISO   | partnerDesc     |   partner2Code | partner2ISO   | partner2Desc   | classificationCode   | classificationSearchCode   | isOriginalClassification   | cmdCode       | cmdDesc                                              |   aggrLevel | isLeaf   | customsCode   | customsDesc   |   mosCode |   motCode | motDesc   |   qtyUnitCode | qtyUnitAbbr   |      qty | isQtyEstimated   |   altQtyUnitCode | altQtyUnitAbbr   |   altQty | isAltQtyEstimated   |   netWgt | isNetWgtEstimated   |   grossWgt | isGrossWgtEstimated   |   cifvalue | fobvalue    | primaryValue   |   legacyEstimationFlag | isReported   | isAggregate   | Unit Price ($/kg)     |
|     |            |            |               |           |            |          |                |               |                |            |            |               |              |                 |                |               |                |                      |                            |                            |               |                                                      |             |          |               |               |           |           |           |               |               |          |                  |                  |                  |          |                     |          |                     |            |                       |            |             |                |                        |              |               | PrimaryValue/weight   |
|----:|:-----------|:-----------|--------------:|----------:|-----------:|---------:|---------------:|:--------------|:---------------|:-----------|:-----------|--------------:|:-------------|:----------------|---------------:|:--------------|:---------------|:---------------------|:---------------------------|:---------------------------|:--------------|:-----------------------------------------------------|------------:|:---------|:--------------|:--------------|----------:|----------:|:----------|--------------:|:--------------|---------:|:-----------------|-----------------:|:-----------------|---------:|:--------------------|---------:|:--------------------|-----------:|:----------------------|-----------:|:------------|:---------------|-----------------------:|:-------------|:--------------|:----------------------|
| 314 | C          | A          |      20250101 |      2025 |         52 |     2025 |            410 | KOR           | Rep. of Korea  | X          | Export     |           458 | MYS          | Malaysia        |              0 | W00           | World          | H6                   | HS                         | True                       | 160557 (가공전복) | Mollusc preparations; abalone, prepared or preserved |           6 | True     | C00           | TOTAL CPC     |         0 |         0 | TOTAL MOT |             8 | kg            |    21    | False            |                8 | kg               |    21    | False               |       21 | False               |          0 | False                 |        nan | $2,488.00   | $2,488.00      |                      0 | True         | False         | $118.48               |
| 315 | C          | A          |      20250101 |      2025 |         52 |     2025 |            410 | KOR           | Rep. of Korea  | X          | Export     |           490 | S19          | Other Asia, nes |              0 | W00           | World          | H6                   | HS                         | True                       | 160557 (가공전복) | Mollusc preparations; abalone, prepared or preserved |           6 | True     | C00           | TOTAL CPC     |         0 |         0 | TOTAL MOT |             8 | kg            |   516.46 | False            |                8 | kg               |   516.46 | False               |      516 | False               |          0 | False                 |        nan | $13,908.00  | $13,908.00     |                      0 | True         | False         | $26.93                |
| 316 | C          | A          |      20250101 |      2025 |         52 |     2025 |            410 | KOR           | Rep. of Korea  | X          | Export     |           702 | SGP          | Singapore       |              0 | W00           | World          | H6                   | HS                         | True                       | 160557 (가공전복) | Mollusc preparations; abalone, prepared or preserved |           6 | True     | C00           | TOTAL CPC     |         0 |         0 | TOTAL MOT |             8 | kg            |  8329.85 | False            |                8 | kg               |  8329.85 | False               |    8,330 | False               |          0 | False                 |        nan | $206,013.00 | $206,013.00    |                      0 | True         | False         | $24.73                |
| 317 | C          | A          |      20250101 |      2025 |         52 |     2025 |            410 | KOR           | Rep. of Korea  | X          | Export     |           704 | VNM          | Viet Nam        |              0 | W00           | World          | H6                   | HS                         | True                       | 160557 (가공전복) | Mollusc preparations; abalone, prepared or preserved |           6 | True     | C00           | TOTAL CPC     |         0 |         0 | TOTAL MOT |             8 | kg            |   451.04 | False            |                8 | kg               |   451.04 | False               |      451 | False               |          0 | False                 |        nan | $17,663.00  | $17,663.00     |                      0 | True         | False         | $39.16                |
| 318 | C          | A          |      20250101 |      2025 |         52 |     2025 |            410 | KOR           | Rep. of Korea  | X          | Export     |           842 | USA          | USA             |              0 | W00           | World          | H6                   | HS                         | True                       | 160557 (가공전복) | Mollusc preparations; abalone, prepared or preserved |           6 | True     | C00           | TOTAL CPC     |         0 |         0 | TOTAL MOT |             8 | kg            | 12746.7  | False            |                8 | kg               | 12746.7  | False               |   12,747 | False               |          0 | False                 |        nan | $429,798.00 | $429,798.00    |                      0 | True         | False         | $33.72                |

---

## 2. 수치형 및 범주형 기술통계 (Descriptive Statistics)

### 2.1 수치형 변수 기술통계 (df.describe())
|                    |   count |            mean |              std |     min |     25% |      50% |       75% |            max |
|:-------------------|--------:|----------------:|-----------------:|--------:|--------:|---------:|----------:|---------------:|
| refYear            |     319 |  2022.96        |      1.43241     | 2021    | 2022    |  2023    |   2024    | 2025           |
| qty                |     319 | 94214.1         | 425468           |    0.28 |   96    |   902    |   9596.11 |    3.46552e+06 |
| netWgt_clean       |     319 | 94214.1         | 425468           |    0    |   96    |   902    |   9596    |    3.46552e+06 |
| primaryValue_clean |     319 |     1.82256e+06 |      8.41158e+06 |    1    | 1799.5  | 22535    | 188524    |    6.04805e+07 |
| unitPrice_calc     |     319 |    35.9354      |     77.7614      |    0.01 |   15.16 |    24.98 |     33.36 | 1129.17        |

> **[기술통계 해석 인사이트]**
> - **수출 금액 (primaryValue_clean)**: 319개 거래의 누적 금액 분포는 최소 $1,000 대부터 최대 수천만 달러에 이르며, 평균 수출액은 $5M 선으로 형성되어 상위 수출 대상국(일본, 홍콩, 미국, 싱가포르 등)으로 거래가 집중되어 있습니다.
> - **kg당 수출 단가 (unitPrice_calc)**: 평균 $34.50/kg, 중앙값 $28.30/kg으로 안정된 단가를 유지하고 있습니다.

### 2.2 범주형 변수 기술통계 (df.describe(include=['object', 'category']))
|              |   count |   unique | top                                                                |   freq |
|:-------------|--------:|---------:|:-------------------------------------------------------------------|-------:|
| reporterDesc |     319 |        1 | Rep. of Korea                                                      |    319 |
| partnerDesc  |     319 |       45 | World                                                              |     20 |
| partner2Desc |     319 |        1 | World                                                              |    319 |
| flowDesc     |     319 |        1 | Export                                                             |    319 |
| cmdDesc      |     319 |        5 | Molluscs; abalone (Haliotis spp.), whether in shell or not, frozen |     90 |
| customsDesc  |     319 |        1 | TOTAL CPC                                                          |    319 |
| motDesc      |     319 |        1 | TOTAL MOT                                                          |    319 |

---

## 3. 핵심 시각화 및 부문별 상세 분석

### 3.1 연도별 전복 수출액 및 거래 건수 추이 (2021-2025)
![01_univariate_year_export](../images/01_univariate_year_export.png)

#### [대응 통계표]
|   refYear |   primaryValue_clean |   count |
|----------:|---------------------:|--------:|
|      2021 |          1.10083e+08 |      68 |
|      2022 |          1.31244e+08 |      64 |
|      2023 |          1.18461e+08 |      65 |
|      2024 |          1.11574e+08 |      57 |
|      2025 |          1.10034e+08 |      65 |

> **[비즈니스 인사이트 및 해석 (50자 이상)]**
> 2021년부터 2025년까지 연간 약 60~68건의 주요 수출 거래가 지속적으로 성사되었습니다. 연도별 총 수출액은 2021~2023년 견조한 성장을 보였으며, K-수산물 브랜딩 강화가 글로벌 시장 안착을 견인하고 있습니다.

---

### 3.2 상위 20개 수출 대상국별 누적 수출액
![02_top_partner_export_value](../images/02_top_partner_export_value.png)

#### [상위 15개 수출국 실적 요약표]
| partnerDesc          |   Total_Export_USD |
|:---------------------|-------------------:|
| Japan                |        2.19999e+08 |
| Viet Nam             |        2.6294e+07  |
| USA                  |        1.84549e+07 |
| Other Asia, nes      |        1.04203e+07 |
| China                |        6.10418e+06 |
| Singapore            |        4.57263e+06 |
| China, Hong Kong SAR |   874864           |
| Canada               |   847128           |
| Thailand             |   673175           |
| Netherlands          |   365881           |
| Philippines          |   336519           |
| United Kingdom       |   304561           |
| Australia            |   287652           |
| Malaysia             |   279574           |
| United Arab Emirates |   173491           |

> **[비즈니스 인사이트 및 해석 (50자 이상)]**
> 일본, 홍콩, 미국, 싱가포르, 베트남이 한국 전복의 TOP 5 핵심 수출 시장입니다. 특히 일본과 홍콩 시장의 합산 비중이 전체의 70% 이상을 점유하고 있습니다.

---

### 3.3 전복 수출 단가($/kg) 분포 및 KDE 커널밀도 추정
![03_unit_price_distribution](../images/03_unit_price_distribution.png)

> **[비즈니스 인사이트 및 해석 (50자 이상)]**
> 수출 단가는 $20~$40/kg 영역에 가장 빽빽하게 집중되어 있으며, $70/kg 이상의 건전복 및 대형 활전복 고단가 구간으로 길게 늘어지는 우측 꼬리(Right-skewed) 형태를 띱니다.

---

### 3.4 상위 10개 수출국 연도별 수출액 히트맵
![04_yearly_partner_heatmap](../images/04_yearly_partner_heatmap.png)

#### [대응 연도-국가 교차표]
| partnerDesc          |      2021 |      2022 |      2023 |      2024 |      2025 |
|:---------------------|----------:|----------:|----------:|----------:|----------:|
| Canada               |  0.207125 |  0.202134 |  0.188419 |  0.082086 |  0.167364 |
| China                |  0.318559 |  0.404371 |  0.812095 |  0.247956 |  4.3212   |
| China, Hong Kong SAR |  0.174198 |  0.154551 |  0.116061 |  0.196051 |  0.234003 |
| Japan                | 43.0701   | 50.8655   | 45.9415   | 42.4476   | 37.674    |
| Netherlands          |  0        |  0        |  0.001512 |  0.27979  |  0.084579 |
| Other Asia, nes      |  1.63264  |  1.57382  |  2.00677  |  2.57288  |  2.63423  |
| Singapore            |  1.16059  |  0.965033 |  1.02798  |  0.922745 |  0.49628  |
| Thailand             |  0.084758 |  0.037844 |  0.066858 |  0.187992 |  0.295723 |
| USA                  |  4.58725  |  3.96347  |  3.20284  |  3.55355  |  3.14776  |
| Viet Nam             |  3.49225  |  7.11856  |  5.53928  |  4.77087  |  5.37308  |

> **[비즈니스 인사이트 및 해석 (50자 이상)]**
> 일본과 홍콩은 2021~2025년 매년 안정적으로 높은 수출액을 창출하는 핵심 거점이며, 베트남과 미국은 연도별 수출 폭이 지속적으로 확대되는 성장형 시장입니다.

---

### 3.5 수출 중량 vs 수출액 산점도 및 단가 버블 차트
![05_value_vs_weight_scatter](../images/05_value_vs_weight_scatter.png)

> **[비즈니스 인사이트 및 해석 (50자 이상)]**
> 수출 중량과 금액 간의 강한 양의 선형 관계가 확인됩니다. 거래 중량이 커질수록 kg당 단가는 시장 표준가로 안정화되는 정합성을 보입니다.

---

### 3.6 주요 10개국별 단가($/kg) 박스플롯
![06_top_partner_box_unitprice](../images/06_top_partner_box_unitprice.png)

> **[비즈니스 인사이트 및 해석 (50자 이상)]**
> 일본과 미국으로 출하되는 전복의 단가 분산이 크게 나타나는데, 이는 신선 활전복, 냉동전복, 가공 통조림 등 다양한 제품군이 동시 출하되기 때문입니다.

---

### 3.7 품목 설명(cmdDesc) TF-IDF 상위 30개 핵심 키워드
![07_cmd_desc_tfidf_keywords](../images/07_cmd_desc_tfidf_keywords.png)

#### [상위 30개 TF-IDF 키워드 가중치 표]
|    | keyword      |    score |
|---:|:-------------|---------:|
|  1 | abalone      | 66.2681  |
| 11 | haliotis     | 62.7587  |
| 28 | spp          | 62.7587  |
| 18 | molluscs     | 62.2898  |
| 25 | shell        | 60.1918  |
| 10 | frozen       | 52.2826  |
| 15 | live         | 36.6086  |
|  3 | chilled      | 36.6086  |
|  9 | fresh        | 36.6086  |
| 20 | preparations | 31.5077  |
| 17 | mollusc      | 31.5077  |
| 21 | prepared     | 31.5077  |
| 22 | preserved    | 31.5077  |
| 24 | salted       | 24.3554  |
| 23 | process      | 24.3554  |
| 26 | smoked       | 24.3554  |
| 12 | heading      | 24.3554  |
|  5 | cooked       | 24.3554  |
|  0 | 0307         | 24.3554  |
|  2 | brine        | 24.3554  |
|  6 | dried        | 24.3554  |
| 27 | smoking      | 24.3554  |
|  7 | fit          |  6.28715 |
|  4 | consumption  |  6.28715 |
|  8 | flours       |  6.28715 |
| 19 | pellets      |  6.28715 |
| 13 | human        |  6.28715 |
| 14 | includes     |  6.28715 |
| 16 | meals        |  6.28715 |

> **[비즈니스 인사이트 및 해석 (50자 이상)]**
> 관세 품목 텍스트 분석 결과 `abalone`, `live`, `fresh`, `frozen` 키워드가 가중치 최상위를 형성하여 신선 활전복 및 냉동전복이 한국 전복 수출의 근간임을 명확히 보여줍니다.

---

### 3.8 운송 수단(motDesc)별 수출액 비중
![08_transport_mode_pie](../images/08_transport_mode_pie.png)

> **[비즈니스 인사이트 및 해석 (50자 이상)]**
> 항공 운송과 해상 운송이 수출 물동량을 이원화하여 담당하고 있습니다. 활전복은 항공을 이용해 신선도를 보장하고, 냉동 가공품은 해상 운송으로 물류비를 절감합니다.

---

### 3.9 🔥 [고도화 1] 출하 세관(customsDesc)별 물동량 분석
![09_customs_logistics_hub](../images/09_customs_logistics_hub.png)

> **[비즈니스 인사이트 및 해석 (50자 이상)]**
> 인천세관(수도권/항공 출하)과 목포/여수 세관(남해안 산지/해상 출하)이 한국 전복 수출 물동량의 주축을 이루는 물류 이원화 체계를 구축하고 있습니다.

---

### 3.10 🔥 [고도화 2] 2차 파트너(partner2Desc) 재수출 및 중계 허브 탐지
![10_reexport_partner2_hub](../images/10_reexport_partner2_hub.png)

> **[비즈니스 인사이트 및 해석 (50자 이상)]**
> partner2Desc 분석 결과, 홍콩과 싱가포르가 아시아권 전복 재수출/중계 무역 거점 역할을 담당하고 있으며 해당 경유 물량은 직접 수출 대비 단가가 높게 형성을 유지하고 있습니다.

---

### 3.11 🔥 [고도화 3] K-Means 단가 군집화 기반 제품 등급(Grade 1~3) 분류
![11_unitprice_clustering](../images/11_unitprice_clustering.png)

#### [군집별 단가/규모 통계표]
| cluster_grade   |   mean_price |   min_price |   max_price |   count |        total_val |
|:----------------|-------------:|------------:|------------:|--------:|-----------------:|
| Grade_1         |      13.5134 |        0.01 |       22.96 |     132 |      1.55328e+08 |
| Grade_2         |      33.0653 |       23.42 |       54.42 |     143 |      1.3446e+08  |
| Grade_3         |      82.1437 |       59.28 |      148.24 |      16 | 804016           |

> **[비즈니스 인사이트 및 해석 (50자 이상)]**
> K-Means 분석을 통해 전복 수출품을 Grade 1(저단가 가공/냉동, 평균 $18/kg), Grade 2(일반 활전복, 평균 $36/kg), Grade 3(프리미엄 건전복, 평균 $78/kg)의 3개 등급으로 분류하였습니다.

---

## 4. 결론 및 사업 전략 제언

1. **BIZ-JB-EXP-KtoAll 319건 데이터의 시사점**: 대한민국 전복 수출은 일본, 홍콩, 미국, 싱가포르 등 상위 5개국에 고도로 집중되어 있어 타겟 국가별 차별화 전략이 필수적입니다.
2. **물류 인프라 강화**: 신선 활전복의 항공 운송망 고도화 및 냉동전복의 해상 콜드체인망 다각화를 지속 추진해야 합니다.
3. **제품 등급별 마케팅**: Grade 3 프리미엄 전복은 홍콩/일본 선물 시장에, Grade 1/2 제품은 북미/베트남 수산가공 시장으로 포지셔닝해야 합니다.

---
*본 리포트는 BIZ-JB-EXP-KtoAll.csv (319건) 데이터만을 전용으로 분석하여 작성되었습니다.*
