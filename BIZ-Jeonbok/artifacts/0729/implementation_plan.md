# 1인 종합상사를 위한 전복 신규 수출 시장 개척 실전 분석 구현 계획서

본 구현 계획서는 **1인 종합상사** 관점에서 리소스(자본, 인력) 한계를 극복하고, 리스크(바이어 대금 미결제, 검역 보류, 운송 폐사)를 최소화하면서 빠르게 고마진 신규 수출 시장을 개척하기 위한 **5대 실전 무역 분석 시스템 구축 계획**입니다.

---

## 1. 개요 및 5대 핵심 분석 요소

- **타겟 데이터**: `BIZ-JB-EXP-KtoAll.csv` (대한민국 전복 수출 무역 데이터) + 무역/관세/검역 지표 연계
- **분석 목적**: 1인 종합상사를 위한 최적의 전복 수출 타겟국, 물류 형태, 검역 난이도, 결제 안전성 및 마진 모델링
- **5대 실전 무역 분석 요소**:
  1. **관세율 및 비관세 장벽(SPS/검역) 난이도 분석**: 통관 수월성(홍콩, 싱가포르 등) vs 난이도 높음(미국 FDA 등) 매핑
  2. **소량 출하(MOQ 500kg~1톤) 고마진 타겟팅**: $40/kg 이상 고단가 수용국(프리미엄 파인다이닝/호텔 공급용) 추출
  3. **운송 방식별(항공 활전복 vs 해상 냉동전복) 폐손율 및 BEP 손익 모델링**: 활전복(폐사율 3~5% 감안) vs 냉동전복(저리스크)
  4. **신흥 블루오션 시장 탐지**: 연평균 성장률(CAGR)이 높은 신흥국(베트남, UAE, 태국, 호주 등) 선점 전략
  5. **대금 미결제 방지 및 무역보험(K-SURE) 안전성 매핑**: L/C vs T/T 안전거래 및 무역보험 인수 적합국 분류

---

## 2. 산출물 및 파일 경로 계획

- **분석 코드**: [`BIZ-Jeonbok/src/eda_solo_trader.py`](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/BIZ-Jeonbok/src/eda_solo_trader.py) (최상단 파이썬 한글 Docstring 준수)
- **실전 무역 가이드 리포트**: [`BIZ-Jeonbok/artifacts/Solo_Trader_Abalone_Export_Guide.md`](file:///C:/Users/leeak/OneDrive/1.HaeYu/HYU_RSCH/BIZ-Jeonbok/artifacts/Solo_Trader_Abalone_Export_Guide.md)
- **시각화 이미지 차트**: `BIZ-Jeonbok/images/` (1인 상사 전용 실전 차트 15종 저장)

---

## 3. 검증 계획 (Verification Plan)

1. `uv run python BIZ-Jeonbok/src/eda_solo_trader.py` 실행을 통한 오차 없는 15종 차트 및 보고서 자동 작성 검증
2. `BIZ-Jeonbok/artifacts/Solo_Trader_Abalone_Export_Guide.md` 분량 (5,000자 이상) 및 5대 무역 실전 분석 수치 검증
