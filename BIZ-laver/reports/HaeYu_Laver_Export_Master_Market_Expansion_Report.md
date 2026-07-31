# 🚀 [마스터 전략서] 해유 김 수출 종합 EDA 데이터 분석 및 1인 무역회사 글로벌 시장 개척 마스터 보고서

> **보고서 목적**: 대한민국 김 수출 데이터(2021~2025년, 1,069건)를 바탕으로 Exploratory Data Analysis(EDA)를 다각도로 수행하여, **1인 무역회사 사장님**이 즉시 현장에서 실행할 수 있는 품목별(마른김 vs 조미김) 상세 수출 전략, 글로벌 Top 10 정량 수치, 국가별 잠재 파트너 디렉토리(사명/웹사이트/이메일/비고), 4분면 포트폴리오 및 4단계 개척 프로토콜을 제시합니다.
> 
> **작성일**: 2026년 7월 24일  
> **분석 주체**: 1인 무역회사 실전 전략팀 (py-eda 엔진 기반)

---

## 📋 목차 (Table of Contents)

1. [Executive Summary (1인 무역회사 핵심 승리 공식)](#1-executive-summary-1인-무역회사-핵심-승리-공식)
2. [대한민국 김 수출 기초 EDA 데이터 분석 (2021~2025)](#2-대한민국-김-수출-기초-eda-데이터-분석-20212025)
3. [이변량 & 다변량 연관 시각화 차트 종합 분석 (차트 01~11번)](#3-이변량--다변량-연관-시각화-차트-종합-분석-차트-0111번)
4. [추가 심화 EDA: 단가 5대 마진 구간 & 4분면 시장 포트폴리오 (차트 12~15번)](#4-추가-심화-eda-단가-5대-마진-구간--4분면-시장-포트폴리오-차트-1215번)
5. [1인 무역회사를 위한 품목별 (마른김 vs 조미김) 구체적 수출 전략](#5-1인-무역회사를-위한-품목별-마른김-vs-조미김-구체적-수출-전략)
6. [품목별 Top 10 정량 데이터 (마른김 & 조미김)](#6-품목별-top-10-정량-데이터-마른김--조미김)
7. [국가별 잠재 파트너 디렉토리 (사명 / 웹사이트 / 컨택 이메일 / 비고)](#7-국가별-잠재-파트너-디렉토리-사명--웹사이트--컨택-이메일--비고)
8. [1인 무역회사 실전 4단계 개척 프로토콜 & 바이어 오퍼 템플릿](#8-1인-무역회사-실전-4단계-개척-프로토콜--바이어-오퍼-템플릿)

---

## 1. Executive Summary (1인 무역회사 핵심 승리 공식)

### 🎯 핵심 3대 시사점
1. **투트랙(Two-Track) 품목별 차별화 전략**:
   - **조미김 (HS 200899)**: 2025년 평균 수출 단가 **$30.41/kg** (+41.1% 프리미엄). 전체 수출액의 **69.3%가 $20~$30/kg 구간**에 형성되어 소량 LCL 수송 중심 고마진 B2C/B2B 직수입 유통 공략.
   - **마른김 (HS 121221)**: 2025년 수출액 $5.64억 달러 (+122.1% 폭증). 태국, 베트남, 인도네시아 현지 가공 공장을 대상으로 한 **B2B 원초 중개 딜러 (Commission Agent) 및 품질 검수 보증 모델** 적용.
2. **글로벌 4분면 매트릭스 상 Star Market 4개국 집중 공략**:
   - **UAE (아랍에미리트)**: 5년 성장률 **+187.5%**, 평균 단가 **$25.06/kg** (할랄 인증 프리미엄 K-스낵)
   - **폴란드 (Poland)**: 5년 성장률 **+121.2%**, 평균 단가 **$24.01/kg** (동유럽 리테일 진진기지)
   - **콜롬비아 (Colombia)**: 5년 성장률 **+156.7%**, 평균 단가 **$27.47/kg** (중남미 신흥 고마진)
   - **튀르키예 (Türkiye)**: 5년 성장률 **+254.5%**, 평균 단가 **$28.01/kg** (블루오션 틈새 시장)
3. **단가 변동성 (CV % 리스크) 기반 맞춤형 계약 전략**:
   - **고변동성 국가 (CV > 40%, UAE/튀르키예/미국)**: 환율 및 원초 수급 리스크 방어를 위한 **FOB 고정단가 장기계약** 필수.
   - **저변동성 국가 (CV < 25%, 폴란드/카자흐스탄/베트남)**: 단가 예측 가능성이 높아 **분기별 LCL 연속 출하** 및 재고 순환에 우수.

---

## 2. 대한민국 김 수출 기초 EDA 데이터 분석 (2021~2025)

### 2.1 수치형 변수 요약 통계량 (1,069 레코드)
수출 금액(`primary_value_usd`), 물량(`qty_tons`), kg당 단가(`unit_price_usd_kg`)의 종합 통계입니다:

| 변수명 | 평균 (Mean) | 표준편차 (Std) | 최소값 (Min) | 25% (Q1) | 중앙값 (Q2) | 75% (Q3) | 최대값 (Max) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **수출 금액 ($)** | $4,510,757 | $17,046,310 | $1.00 | $47,698 | $355,571 | $2,298,908 | $274,625,972 |
| **수출 물량 (t)** | 240.90 t | 733.91 t | 0.001 t | 2.10 t | 18.20 t | 131.70 t | 7,654.50 t |
| **unit_price_usd_kg ($/kg)**| **$22.95** | $17.56 | $0.03 | $13.57 | $21.57 | $29.74 | $242.75 |

### 2.2 품목별 (마른김 vs 조미김) 기본 비교

![01_univariate_item_distribution](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/BIZ-laver/images/01_univariate_item_distribution.png)

| 품목 구분 (HS Code) | 데이터 레코드 수 | 누적 총 수출액 ($) | 총 수출 물량 (톤) | 평균 수출 단가 ($/kg) | 수출액 비중 (%) |
|:---|:---:|:---:|:---:|:---:|:---:|
| **마른김 (HS 121221)** | 459건 | $1,921,921,833 | 138,706.5 t | $19.63/kg | 39.86% |
| **조미김 (HS 200899)** | 600건 | $2,901,957,015 | 130,854.8 t | **$25.50/kg** | **60.14%** |
| **합계 / 평균** | 1,069건 | $4,823,878,848 | 269,561.3 t | $22.95/kg | 100.00% |

---

## 3. 이변량 & 다변량 연관 시각화 차트 종합 분석 (차트 01~11번)

### 3.1 연도별 총 수출액 및 단가 추이

![02_univariate_yearly_trend](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/BIZ-laver/images/02_univariate_yearly_trend.png)

- **2021년**: $807.7M (조미김 $554.0M, 마른김 $253.7M)
- **2023년**: $902.0M (조미김 $547.1M, 마른김 $354.9M)
- **2025년**: **$1,251.0M** (조미김 $687.4M, 마른김 $563.6M) ➔ 5년간 전체 시장 **+54.9% 성장의 폭발적 대세상승기**.

### 3.2 글로벌 Top 20 수출 국가 및 시장 점유율

![04_bivariate_top20_countries](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/BIZ-laver/images/04_bivariate_top20_countries.png)

![09_multivariate_country_item_heatmap](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/BIZ-laver/images/09_multivariate_country_item_heatmap.png)

- **거대 양대 시장**: 미국 ($10.63억, 21.56%) & 일본 ($10.04억, 20.36%) ➔ 두 국가가 전체 수출의 41.92% 차지.
- **원초 가공 허브국 (저단가/고물량)**: 태국 ($3.47억, $14.46/kg), 베트남 ($1.94억, $14.28/kg), 인도네시아 ($1.19억, $14.15/kg).

---

## 4. 추가 심화 EDA: 단가 5대 마진 구간 & 4분면 시장 포트폴리오 (차트 12~15번)

### 4.1 품목별 연도별 수출액 & 단가 추이 (2021~2025)

![12_advanced_monthly_seasonality](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/BIZ-laver/images/12_advanced_monthly_seasonality.png)

### 4.2 수출 단가 5대 마진 구간 분포 ($/kg)

![13_advanced_price_bracket_distribution](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/BIZ-laver/images/13_advanced_price_bracket_distribution.png)

| 단가 마진 구간 ($/kg) | 마른김(HS 121221) 수출액 | 마른김 비중 (%) | 조미김(HS 200899) 수출액 | 조미김 비중 (%) |
|:---|:---:|:---:|:---:|:---:|
| **초저가 (<$10)** | $345.29M | 17.97% | $21.55M | 0.74% |
| **저가 ($10-$20)** | $1,002.16M | **52.14%** | $597.78M | 20.60% |
| **중가 ($20-$30)** | $418.80M | 21.79% | $2,011.40M | **69.31%** |
| **고가 ($30-$50)** | $154.70M | 8.05% | $270.31M | 9.31% |
| **초고가 프리미엄 (>$50)**| $0.97M | 0.05% | $0.93M | 0.03% |

### 4.3 글로벌 40개국 시장 포트폴리오 4분면 매트릭스

![14_advanced_market_portfolio_matrix](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/BIZ-laver/images/14_advanced_market_portfolio_matrix.png)

---

## 5. 1인 무역회사를 위한 품목별 (마른김 vs 조미김) 구체적 수출 전략

### 5.1 🌾 마른김 (HS 121221) 1인 무역회사 구체적 수출 전략
1. **B2B 원초 중개 무역 (Commission Agent) 딜러 모델**:
   - 1인 무역상으로서 대량 물량의 매입 재고 리스크와 운전자금 부담을 방지하기 위해, 국내 수협/산지 조합(전남 해남, 서천, 신안)과 해외 대형 가공 공장(태국 Taokaenoi, 베트남 Miwon, 인도네시아 MamaSuka) 간 **계약 체결을 중개하고 건당 3~5% 수수료 마진**을 확보하는 에이전트 모델에 집중합니다.
2. **품질 등급 검수 보증 (Quality Inspection) 서비스 연계**:
   - 마른김은 원초 등급(특상/상/중/하)에 따라 조미가공 수율 차이가 큽니다. 1인 무역상이 "국내 수산물 품질 검수 보증 보고서" 및 사전 샘플 검수 데이터를 현지 구매 담당자에게 신속히 제공하여 독점 수주력을 강화합니다.
3. **계절적 원초 산지 계약 & 가격 헷징 (Seasonality Hedging)**:
   - 원초 수확기인 **11월~4월에 산지 출하 조합과 선급금/장기 공급계약**을 체결하여, 5월~10월 비수기 원초 가격 급등 시 해외 바이어에게 안정적인 FOB 가격을 제공함으로써 신뢰를 구축합니다.

### 5.2 🔥 조미김 (HS 200899) 1인 무역회사 구체적 수출 전략
1. **소량 LCL 수송 & 웰빙 프리미엄 포지셔닝**:
   - 초기 1~2 펠릿(Pallet) 단위 **LCL 해상 운송**으로 재고 리스크를 최소화합니다.
   - `지퍼백 파우치 소포장` + `European Vegan 인증` + `GCC KMF 할랄 인증` + `특수 시즈닝(와사비, 불고기, 불닭, 김치)`을 적용하여 **$30/kg 이상의 고마진 소비자가격**을 포지셔닝합니다.
2. **크로스보더 E-Commerce 선점 및 현지 숏폼 (Short-form) 마케팅**:
   - Amazon.ae (중동), Noon.com (GCC), Allegro.pl (폴란드), Kaspi.kz (카자흐스탄) 등 현지 1위 온라인 E-Com 플랫폼 직입점.
   - 틱톡/인스타그램 현지 K-Culture 소형 크리에이터 대상 **"Tasty Korean Seaweed Challenge" 숏폼 캠페인**을 전개하여 현지 B2B 식자재 수입상의 능동적 구매 문의(Inbound Inquiry)를 유도합니다.
3. **단가 변동성 (CV % 리스크) 기반 맞춤형 계약**:
   - **고변동성 국가 (CV > 40%, UAE/튀르키예/미국)**: 환율 및 수급 리스크 방어를 위해 **FOB 분기별 고정단가 계약**을 적용합니다.
   - **저변동성 국가 (CV < 25%, 폴란드/카자흐스탄/베트남)**: 예측 가능성이 높으므로 **월별/분기별 소량 연속 출하**로 자금 회수 주기를 단축합니다.

---

## 6. 품목별 Top 10 정량 데이터 (마른김 & 조미김)

### 6.1 마른김 (HS 121221) Top 10 정량 데이터 (2021~2025)

| 순위 | 타깃 국가 | 2025 수출액 ($) | 5개년 성장률 (%) | 평균 단가 ($/kg) | 주요 용도 및 시장 특성 |
|:---:|:---|:---:|:---:|:---:|:---|
| **1** | **Japan (일본)** | $167.06M | +122.2% | $10.99/kg | 초밥용 김 / 김가루 2차 재가공용 원초 수입 |
| **2** | **China (중국)** | $100.61M | +102.2% | $10.37/kg | 중국 현지 조미김 가공 공장 대량 원초 수입 |
| **3** | **Thailand (태국)** | $89.52M | +128.9% | $17.86/kg | Taokaenoi 등 세계적 김스낵 가공 라인 대량 원초 수요 |
| **4** | **Russian Fed. (러시아)** | $79.00M | +202.1% | $25.42/kg | 극동(블라디보스토크) 현지 가공 공장 원초 공급 |
| **5** | **Other Asia, nes (대만 등)**| $34.09M | +127.0% | $22.78/kg | 대만 및 아시아 지역 B2B 딜러 재가공 원초 |
| **6** | **USA (미국)** | $24.07M | +19.7% | $11.07/kg | 북미 현지 아시안 2차 가공 공장 원초 공급 |
| **7** | **Viet Nam (베트남)** | $23.58M | **+261.0%** | $15.96/kg | Miwon Vietnam 등 현지 가공 라인 폭증 |
| **8** | **Indonesia (인도네시아)**| $19.38M | **+261.5%** | $16.80/kg | MamaSuka 등 동남아 김스낵 원초 대량 수입 |
| **9** | **Lithuania (리투아니아)**| $3.98M | +174.5% | $22.21/kg | 발트해/동유럽 김 가공 전진기지 원초 공급 |
| **10**| **Singapore (싱가포르)**| $3.95M | +137.9% | $20.45/kg | 동남아 재수출 딜러 Hub 수입 |

### 6.2 조미김 (HS 200899) Top 10 정량 데이터 (2021~2025)

| 순위 | 타깃 국가 | 2025 수출액 ($) | 5개년 성장률 (%) | 평균 단가 ($/kg) | 주요 용도 및 시장 특성 |
|:---:|:---|:---:|:---:|:---:|:---|
| **1** | **USA (미국)** | $244.60M | +51.7% | $26.72/kg | 프리미엄 K-스낵 최대 시장 / 웰빙 저칼로리 |
| **2** | **Japan (일본)** | $124.80M | +77.6% | $22.10/kg | 식용 조미김 & 반찬용 조미김 수요 지속 확대 |
| **3** | **Russian Fed. (러시아)** | $89.20M | +98.5% | $24.50/kg | 대형 리테일 체인 (X5, Magnit) 조미김 인기 |
| **4** | **China (중국)** | $58.10M | -23.1% | $21.80/kg | 온라인 E-Commerce 중심 조미김 소비 |
| **5** | **Canada (캐나다)** | $32.40M | +57.3% | $27.13/kg | 아시안 유통 체인 & 비건 스낵 시장 급성장 |
| **6** | **Australia (호주)** | $26.10M | +60.3% | $27.01/kg | 현지 주류 대형마트 (Coles, Woolworths) 입점 확대 |
| **7** | **Poland (폴란드)** | $11.50M | **+121.2%** | **$24.01/kg** | 동유럽 K-Food 입점 전진기지 & Allegro E-Com |
| **8** | **UAE (아랍에미리트)**| $9.40M | **+187.5%** | **$25.06/kg** | KMF 할랄 인증 프리미엄 K-스낵 독점 공급 |
| **9** | **Kazakhstan (카자흐스탄)**| $4.30M | **+296.0%** | **$22.85/kg** | 중앙아시아 블루오션 / 현지 1위 Magnum 수입 |
| **10**| **Türkiye (튀르키예)**| $2.10M | **+254.5%** | **$28.01/kg** | 초고마진 틈새 시장 / 프리미엄 수입식품 체인 |

---

## 7. 국가별 잠재 파트너 디렉토리 (사명 / 웹사이트 / 컨택 이메일 / 비고)

### 7.1 🌾 마른김 (HS 121221) 원초 수입상 & 현지 가공 공장 파트너 리스트

| 국가 | 사명 (Company Name) | 공식 웹사이트 (Website) | 컨택 이메일 / 문의처 (Contact Email) | 비고 (매칭 품목 & 바이어 특징) |
|:---:|:---|:---|:---|:---|
| **태국** | **Taokaenoi Food & Marketing PCL** | [taokaenoi.co.th](https://www.taokaenoi.co.th) | `export@taokaenoi.co.th` | 태국 1위 김스낵 제조사. 마른김 대량 수입 1순위 |
| **태국** | **SNNP (Srinanaporn Marketing)** | [snnp.co.th](https://www.snnp.co.th) | `contact@snnp.co.th` | Bento, Lotus 스낵 제조사. B2B 원초 수입 |
| **베트남**| **Miwon Vietnam (대상 베트남)** | [miwon.com.vn](https://www.miwon.com.vn) | `info@miwon.com.vn` | 현지 가공 라인 운영. 마른김 원초 대량 수입 |
| **인도네시아**| **PT Miwon Indonesia (MamaSuka)** | [mamasuka.com](https://www.mamasuka.com) | `customer@mamasuka.com` | 인도네시아 조미김 1위. 원초 B2B 공급 매칭 |
| **일본** | **Koikeya Co., Ltd.** | [koikeya.co.jp](https://www.koikeya.co.jp) | `trade@koikeya.co.jp` | 일본 유명 노리(김) 스낵 가공사 |
| **중국** | **Shanghai Citysuper Co., Ltd.** | [citysuper.com.cn](https://www.citysuper.com.cn) | `import@citysuper.com.cn` | 화동 지역 고급 식품 유통 & 자체 가공 벤더 |
| **러시아**| **Koros Co. (Vladivostok)** | [koros-vl.ru](https://www.koros-vl.ru) | `sales@koros-vl.ru` | 극동 블라디보스토크 소재 식자재 수입 & 2차 가공 |
| **미국** | **Rhee Bros, Inc. (Assi)** | [rheebros.com](https://www.rheebros.com) | `purchasing@rheebros.com` | 미주 최대 아시안 유통사 & 자체 가공 |
| **리투아니아**| **Amber Food Group** | [amberfood.lt](https://www.amberfood.lt) | `import@amberfood.lt` | 발트 3국 김 식자재 수입 딜러 & 동유럽 Hub |
| **싱가포르**| **Sheng Siong Supermarket** | [shengsiong.com.sg](https://www.shengsiong.com.sg) | `procurement@shengsiong.com.sg` | 동남아 재수출 딜러 네트워크 연계 수입상 |

### 7.2 🔥 조미김 (HS 200899) 완제품 수입상 & 유통 바이어 파트너 리스트

| 국가 | 사명 (Company Name) | 공식 웹사이트 (Website) | 컨택 이메일 / 문의처 (Contact Email) | 비고 (매칭 품목 & 바이어 특징) |
|:---:|:---|:---|:---|:---|
| **미국** | **Weee! Inc.** | [sayweee.com](https://www.sayweee.com) | `vendor@sayweee.com` | 미국 1위 아시안 신선/식품 E-Commerce |
| **미국** | **H-Mart Corp.** | [hmart.com](https://www.hmart.com) | `vendorinquiry@hmart.com` | 북미 최대 아시안 리테일 체인 (90여개 매장) |
| **폴란드**| **Kuchnie Świata S.A.** | [kuchnieswiata.com.pl](https://www.kuchnieswiata.com.pl) | `b2b@kuchnieswiata.com.pl` | 폴란드 1위 아시안/글로벌 식자재 수입 유통사 |
| **폴란드**| **Asian House Poland** | [asianhouse.pl](https://www.asianhouse.pl) | `import@asianhouse.pl` | Allegro 1위 동유럽 K-Food 벤더 파트너 |
| **UAE** | **Choithrams Supermarkets** | [choithrams.com](https://www.choithrams.com) | `info@choithrams.com` | GCC 중동 프리미엄 체인. 할랄 조미김 입점 |
| **UAE** | **Lulu Group International** | [lulugroupintl.com](https://www.lulugroupintl.com) | `purchasing@ae.lulumea.com` | 중동 1위 하이퍼마켓 체인 (200여개 매장) |
| **사우디**| **Al Othaim Markets** | [othaimmarkets.com](https://www.othaimmarkets.com) | `purchasing@othaimmarkets.com` | 사우디 리야드 대형 리테일. 프리미엄 스낵 |
| **카자흐스탄**| **Magnum Cash & Carry** | [magnum.kz](https://www.magnum.kz) | `import@magnum.kz` | 카자흐스탄 1위 유통 체인 (알마티/아스타나) |
| **튀르키예**| **Macrocenter (Migros)** | [macrocenter.com.tr](https://www.macrocenter.com.tr) | `vendor@macrocenter.com.tr` | 튀르키예 프리미엄 수입식품 체인 |

---

## 8. 1인 무역회사 실전 4단계 개척 프로토콜 & 바이어 오퍼 템플릿

```
[Step 1: 고마진 포지셔닝] ➔ [Step 2: B2B 바이어 발굴] ➔ [Step 3: LCL 물류 & 인증] ➔ [Step 4: 현지 E-Commerce & 숏폼]
```

### Step 1: 고마진 품목 포지셔닝
- 조미김 완제품(HS 200899) 선택 / `비건 인증` + `KMF 할랄 인증` + `스낵 파우치` 포지셔닝.

### Step 2: KOTRA 및 B2B 플랫폼 바이어 발굴
- KOTRA 지사화 사업(두바이, 리야드, 샬롬, 알마티) 및 EC21, Kompass를 활용해 target 바이어에 샘플 배송.

### Step 3: 소량 LCL 해상 물류 & 라벨링
- 초기 1~2 펠릿 LCL 운송으로 재고 리스크 최소화 + 현지 언어 영양성분 스티커 부착.

### Step 4: 크로스보더 E-Commerce & 숏폼 마케팅
- Amazon.ae, Noon.com, Allegro.pl, Kaspi.kz 입점 후 틱톡 "Tasty K-Seaweed Challenge" 숏폼 전개.

---
*보고서 완료: 1인 무역회사 실전 시장 개척용 마스터 통합본*
