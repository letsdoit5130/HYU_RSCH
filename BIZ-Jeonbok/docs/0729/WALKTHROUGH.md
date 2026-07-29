# 완도 전복 글로벌 파트너 DB 24대 컬럼 엄격 검증 Walkthrough

## 1. 주요 실행 파이프라인 명령어
전체 수집, 실측 커넥션 검증, 24대 컬럼 스키마 정제, 5대 산출물 갱신을 한 번에 실행하는 파이프라인 커맨드입니다:

```bash
uv run python BIZ-Jeonbok/src/run_pipeline.py
```

---

## 2. 24대 컬럼 스키마 검증 결과 요약

* **생성 레코드 수**: 15개 유망국가 825개사
* **공란 처리 기준**: 데이터 부재 및 미검증 항목은 `N/A` 표기 대신 **100% 완전 공란(`""`)**으로 정제.
* **오탐 박탈 기준**: `google.com/search` 패턴 및 더미 메신저 주소는 증빙 무효화 처리하여 `Ver_*` 컬럼의 `O` 표기 박탈 및 공란 처리.

---

## 3. 5대 산출물 갱신 확인

1. **CSV 데이터베이스**: `BIZ-Jeonbok/data/abalone_buyers_db_cleaned.csv`
2. **JSON 데이터베이스**: `BIZ-Jeonbok/data/abalone_buyers_db_cleaned.json`
3. **Excel 데이터북**: `BIZ-Jeonbok/reports/Wando_Abalone_Integrated_Data.xlsx` (Product_Top_Buyers_DB 시트)
4. **HTML 대시보드**: `BIZ-Jeonbok/reports/Wando_Abalone_Dashboard.html`
5. **DOCX 및 PPTX 문서**: `BIZ-Jeonbok/reports/Wando_Abalone_Integrated_Report_v6.docx` & `Wando_Abalone_Market_Entry.pptx`
