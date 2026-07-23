"""
naver_news_it 데이터 수집기 (Scraper)

이 모듈은 네이버 IT/과학 뉴스 섹션 페이지에서 최신 기사 제목, 요약, 
언론사, 링크 등의 정보를 크롤링하여 CSV 형식의 데이터로 저장합니다.

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
    print("[Scraper] 네이버 IT 뉴스 수집을 시작합니다...")
    
    # 저장 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.abspath(os.path.join(current_dir, "..", "data", "raw_data.csv"))
    
    # 헤더 정의
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/120.0.0.0",
        "Referer": "https://news.naver.com/"
    }
    
    # 기존 데이터 파악 및 이어받기 로직 준비
    existing_df = None
    collected_titles = set()
    if os.path.exists(output_path):
        try:
            existing_df = pd.read_csv(output_path, encoding="utf-8-sig")
            print(f" - 기존 데이터 발견: {len(existing_df)}개 행이 로드되었습니다.")
            for t in existing_df["title"]:
                collected_titles.add(str(t).strip())
        except Exception as e:
            print(f" - 기존 파일 읽기 오류: {e}")
            
    url = "https://news.naver.com/section/105"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"[Scraper] [ERROR] 연결 실패: 상태 코드 {response.status_code}")
            return output_path
            
        soup = BeautifulSoup(response.text, "lxml")
        items = soup.select("li.sa_item")
        print(f" - 페이지 내 기사 아이템 개수: {len(items)}개 발견")
        
        collected_data = []
        
        for i, item in enumerate(items):
            # 서버 부하 방지를 위해 루프 내 랜덤 sleep (0.1 ~ 0.3초)
            time.sleep(random.uniform(0.1, 0.3))
            
            # 1. 제목 추출
            title_el = item.select_one("a.sa_text_title") or item.select_one("strong.sa_text_title")
            title = title_el.text.strip() if title_el else ""
            
            if not title:
                continue
                
            # 기존에 이미 수집된 동일 제목 기사이면 건너뜀 (중복 수집 방지)
            if title in collected_titles:
                continue
                
            # 2. 링크 추출
            link = title_el.get("href") if title_el and title_el.name == "a" else ""
            if not link:
                link_el = item.select_one("a")
                link = link_el.get("href") if link_el else ""
                
            # 3. 언론사 추출
            press_el = item.select_one(".sa_text_press") or item.select_one(".sa_press")
            publisher = press_el.text.strip() if press_el else "네이버뉴스"
            
            # 4. 본문 요약 추출
        else:
            df_final = df_new
            
        # 제목 기준으로 중복 제거
        df_final.drop_duplicates(subset=["title"], keep="last", inplace=True)
        
        # 저장 경로 폴더 생성
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # UTF-8-SIG 인코딩 저장 (엑셀 깨짐 방지)
        df_final.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"[Scraper] 데이터 수집 완료 및 저장 완료: {output_path} (총 {len(df_final)}개 행)")
        
    except Exception as e:
        print(f"[Scraper] [ERROR] 수집 도중 오류 발생: {e}")
        
    return output_path

if __name__ == "__main__":
    scrape_data()
