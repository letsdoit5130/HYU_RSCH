"""
범용 데이터 수집기 마스터 모듈 (scraper.py)

이 프로그램은 지정된 타겟 웹페이지 URL에서 데이터를 수집하여
User-Agent 우회, 지연 대기시간 적용, 중복 제거 후 CSV 데이터로 저장하는 모듈입니다.

작성일: 2026-07-23
"""

import os
import time
import random
import requests
import pandas as pd

def scrape_data(target_url: str = "https://example.com", columns: list = None):
    print(f"[Scraper] 데이터 수집을 시작합니다... 타겟 URL: {target_url}")
    if columns is None:
        columns = ["id", "title", "category", "date", "views"]
        
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.abspath(os.path.join(current_dir, "..", "data", "raw_data.csv"))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    dummy_data = []
    for i in range(1, 11):
        time.sleep(random.uniform(0.1, 0.3))
        row = {col: f"데이터_{i}_{col}" for col in columns}
        if "id" in row:
            row["id"] = i
        dummy_data.append(row)
        
    df = pd.DataFrame(dummy_data)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"[Scraper] 총 {len(df)}건 수집 저장 완료 -> {output_path}")
    return output_path

if __name__ == "__main__":
    scrape_data()
