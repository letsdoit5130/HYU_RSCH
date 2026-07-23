"""
수집 중단 지점 기록 및 이어받기 체크포인트 관리자 모듈 (checkpoint_manager.py)

이 프로그램은 대용량 수집 도중 중단이 발생했을 때 마지막 성공 지점(Page/Index)을
JSON 체크포인트 파일로 백업하고, 파이프라인 재개 시 해당 지점부터 수집을 시작하게 해주는 모듈입니다.

작성일: 2026-07-23
"""

import json
import os

CHECKPOINT_FILE = "data/checkpoint.json"

def load_checkpoint() -> int:
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"[CHECKPOINT RESUME] 복구된 지점: Page {data.get('last_page', 1)}")
            return data.get("last_page", 1)
    return 1

def save_checkpoint(last_page: int):
    with open(CHECKPOINT_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_page": last_page}, f, indent=2)
    print(f"[CHECKPOINT SAVED] 수집 위치 기록 완료: Page {last_page}")
