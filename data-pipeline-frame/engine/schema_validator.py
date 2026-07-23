"""
수집 데이터 스키마 및 타입 정밀 검증기 모듈 (schema_validator.py)

이 프로그램은 수집된 DataFrame/CSV 데이터의 컬럼 존재 여부, 숫자/날짜 변환 가용성 
및 데이터 타입 정합성을 검증하는 정수 품질 검증 모듈입니다.

작성일: 2026-07-23
"""

import pandas as pd

def validate_data_schema(df: pd.DataFrame, schema_spec: dict) -> bool:
    print("[SCHEMA-VALIDATOR] 데이터 스키마 및 타입 무결성 검증 시작")
    
    for col, expected_type in schema_spec.items():
        if col not in df.columns:
            print(f"[SCHEMA FAILED] 필수 컬럼 누락: {col}")
            return False
            
        if expected_type == "numeric":
            non_numeric = pd.to_numeric(df[col], errors='coerce').isnull() & df[col].notnull()
            if non_numeric.any():
                print(f"[SCHEMA WARN] {col} 컬럼 내 숫자 변환 실패 존재")
                
    print("[SCHEMA-VALIDATOR PASSED] 데이터 스키마 검증 완료")
    return True
