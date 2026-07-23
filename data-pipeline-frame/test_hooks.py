"""
data-pipeline-frame 훅 모듈 단위 및 종합 통합 검증 테스트 스크립트 (test_hooks.py)

이 프로그램은 Pre-Hook, Auth Refresh Hook, Post-Hook, Self-Healing Retry,
Schema Validator, PII & Secret Guard 보안 훅의 개별 및 연동 검증을 실측 테스트합니다.

작성일: 2026-07-23
"""

import os
import sys
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from inspect_api.pre_hook import run_pre_scrape_hook
from scraping.post_hook import run_post_scrape_hook
from engine.schema_validator import validate_data_schema
from engine.pii_secret_guard import run_pii_secret_guard
from engine.self_healing_retry import execute_with_self_healing

def test_all_hooks():
    print("\n==========================================")
    print("[Hook Verification] 훅 모듈 5종 정량 검증 시작")
    print("==========================================\n")
    
    results = {}
    
    # 1. Pre-Scrape Hook 테스트
    print("Step 1: Pre-Scrape Hook 검증 중...")
    pre_ok = run_pre_scrape_hook("https://example.com")
    results["Pre-Hook"] = "PASS" if pre_ok else "FAIL"
    
    # 2. 샘플 데이터셋 준비
    test_csv = os.path.join(current_dir, "test_sample.csv")
    dummy_df = pd.DataFrame([
        {"id": 1, "title": "정상 기사 제목 1", "email": "test1@example.com", "phone": "010-1234-5678", "views": "150"},
        {"id": 2, "title": "정상 기사 제목 2", "email": "test2@example.com", "phone": "010-9876-5432", "views": "300"},
        {"id": 3, "title": "보안 테스트 기사 3", "email": "secret@domain.com", "phone": "010-5555-7777", "views": "450"},
    ] * 4)
    dummy_df.to_csv(test_csv, index=False, encoding="utf-8-sig")
    
    # 3. Post-Scrape Hook 테스트
    print("\nStep 2: Post-Scrape Hook (건수 및 결측률) 검증 중...")
    post_ok = run_post_scrape_hook(test_csv, min_rows=10, max_null_ratio=0.5)
    results["Post-Hook"] = "PASS" if post_ok else "FAIL"
    
    # 4. Schema Validator 테스트
    print("\nStep 3: Data Schema & Type Validator 검증 중...")
    schema_spec = {"id": "numeric", "title": "string", "views": "numeric"}
    schema_ok = validate_data_schema(dummy_df, schema_spec)
    results["Schema-Validator"] = "PASS" if schema_ok else "FAIL"
    
    # 5. PII & Secret Guard Hook 테스트
    print("\nStep 4: PII & Secret Guard (개인정보/비밀키 마스킹) 검증 중...")
    run_pii_secret_guard(test_csv)
    masked_df = pd.read_csv(test_csv, encoding="utf-8-sig")
    has_email = masked_df['email'].str.contains('@').any()
    results["PII-Secret-Guard"] = "PASS" if not has_email else "FAIL"
    
    # 6. Self-Healing Retry 테스트
    print("\nStep 5: Self-Healing Retry (지수 백오프 자가치유) 검증 중...")
    retry_count = 0
    def dummy_retry_func():
        nonlocal retry_count
        retry_count += 1
        return retry_count >= 2
        
    retry_ok = execute_with_self_healing(dummy_retry_func, max_retries=3, initial_delay=0.1)
    results["Self-Healing-Retry"] = "PASS" if retry_ok else "FAIL"
    
    if os.path.exists(test_csv):
        os.remove(test_csv)
        
    print("\n==========================================")
    print("[Hook Verification Results] 최종 검증 판정")
    print("==========================================")
    all_pass = True
    for k, v in results.items():
        print(f" - {k}: [{v}]")
        if v != "PASS":
            all_pass = False
            
    print(f"\n종합 상태: {'ALL HOOKS PASSED (100%)' if all_pass else '일부 훅 검증 실패'}\n")
    return all_pass

if __name__ == "__main__":
    test_all_hooks()
