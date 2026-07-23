"""
수집 데이터 사후 무결성 검증 훅 모듈 (post_hook.py)

이 프로그램은 데이터 수집 완료 후 최소 수집 행 수(건수) 및
컬럼별 결측치(Null) 임계 비율 초과 여부를 자동 검증하는 훅 모듈입니다.

작성일: 2026-07-23
"""

import pandas as pd

def run_post_scrape_hook(csv_filepath: str, min_rows: int = 10, max_null_ratio: float = 0.5) -> bool:
    print(f"[POST-HOOK] 수집 데이터 무결성 검증 시작: {csv_filepath}")
    
    try:
        df = pd.read_csv(csv_filepath, encoding="utf-8-sig")
    except Exception as e:
        print(f"[POST-HOOK FAILED] CSV 로드 에러: {e}")
        return False

    total_rows = len(df)
    if total_rows < min_rows:
        print(f"[POST-HOOK FAILED] 수집 건수 미달 (현재 {total_rows}건 < 기준 {min_rows}건)")
        return False

    null_ratios = df.isnull().mean()
    high_null_cols = null_ratios[null_ratios > max_null_ratio]
    if not high_null_cols.empty:
        print(f"[POST-HOOK FAILED] 결측 비율 초과 컬럼 발견: {high_null_cols.to_dict()}")
        return False

    print(f"[POST-HOOK PASSED] 무결성 검증 통과 (총 {total_rows}건)")
    return True
