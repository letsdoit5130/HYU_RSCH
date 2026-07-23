"""
자가치유 데이터 재수집 메커니즘 모듈 (self_healing_retry.py)

이 프로그램은 데이터 수집 실패, 건수 미달, 결측치 초과 시
지수 백오프(Exponential Backoff) 대기 시간을 두고 2차 수집 및 자가치유를 수행하는 모듈입니다.

작성일: 2026-07-23
"""

import time

def execute_with_self_healing(scrape_func, max_retries: int = 3, initial_delay: float = 2.0):
    delay = initial_delay
    for attempt in range(1, max_retries + 1):
        print(f"[SELF-HEALING] 수집 시도 {attempt}/{max_retries} 실행 중...")
        success = scrape_func()
        if success:
            print("[SELF-HEALING SUCCESS] 수집 성공!")
            return True
        
        print(f"[SELF-HEALING RETRY] 수집 미달/실패 -> {delay}초 후 재시도")
        time.sleep(delay)
        delay *= 2.0
        
    print("[SELF-HEALING FAILED] 재시도 횟수 초과")
    return False
