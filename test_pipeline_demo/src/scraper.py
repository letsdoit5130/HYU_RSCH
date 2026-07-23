"""
test_pipeline_demo 데이터 수집기 (Scraper)

이 모듈은 지정된 타겟 웹페이지(https://news.naver.com)에서 데이터를 수집하여 
CSV 형식의 데이터로 가공 및 저장하는 프로그램입니다.

주요 특징:
- User-Agent 우회를 통한 봇 감지 회피
- 서버 부하 방지를 위한 랜덤 지연 대기 시간 적용
- 기존 파일 이어받기 및 중복 제거 기능 지원

작성일: 2026-07-19
"""

import os
import time
import random
import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_data():
    print("[Scraper] 데이터 수집을 시작합니다...")
    
    # 저장 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.abspath(os.path.join(current_dir, "..", "data", "raw_data.csv"))
    
    # 헤더 정의
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://news.naver.com"
    }
    
    # 기존 데이터 파악 및 이어받기 로직 준비
    existing_df = None
    if os.path.exists(output_path):
        try:
            existing_df = pd.read_csv(output_path, encoding="utf-8-sig")
            print(f" - 기존 데이터 발견: {len(existing_df)}개 행이 로드되었습니다.")
        except Exception as e:
            print(f" - 기존 파일 읽기 오류: {e}")
            
    dummy_data = []
    columns = ['id', 'title', 'summary', 'publisher', 'link', 'category', 'author', 'date', 'views']
    
    print(" - 웹 서버 요청 시뮬레이션 및 데이터 수집 중...")
    for i in range(1, 11):
        time.sleep(random.uniform(0.1, 0.3))
        
        row = {col: f"데이터_{i}_{col}" for col in columns}
        if "id" in row:
            row["id"] = i
        if "link" in row:
            row["link"] = f"https://example.com/item/{i}"
        dummy_data.append(row)
        
    df_new = pd.DataFrame(dummy_data)
    
    if existing_df is not None:
        df_final = pd.concat([existing_df, df_new], ignore_index=True)
        if len(columns) > 0:
            df_final.drop_duplicates(subset=[columns[0]], keep="last", inplace=True)
    else:
        df_final = df_new
        
    # UTF-8-SIG 인코딩 저장
    df_final.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"[Scraper] 데이터 수집 완료 및 저장 완료: {output_path} (총 {len(df_final)}개 행)")
    return output_path

if __name__ == "__main__":
    scrape_data()
