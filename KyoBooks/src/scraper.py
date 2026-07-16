"""
교보문고 실시간 베스트셀러 데이터 수집기 (Scraper)

이 모듈은 교보문고 실시간 베스트셀러 API를 호출하여 도서 데이터를 수집하는 프로그램입니다.
x-api-gw-key 만료 상황을 감지하면 자동으로 capture_api.py를 백그라운드에서 실행하여
새로운 인증 헤더를 획득하고 수집을 재개하는 복구 로직을 포함하고 있습니다.
수집된 데이터는 중복을 제거한 뒤 CSV 파일로 저장됩니다.

주요 기능:
1. api_config.json 로드 및 HTTP GET 요청 수행
2. 401 에러 또는 게이트웨이 인증 실패 시 capture_api.py 연동 자동 복구
3. 도서 정보 파싱 (상품번호, 순위, 도서명, 저자, 출판사, 출판일, 가격, 할인율, 리뷰수, 평점, 카테고리, 이미지 URL 등)
4. UTF-8-SIG 인코딩으로 CSV 포맷 저장 (엑셀 한글 깨짐 방지)
"""

import os
import sys
import json
import subprocess
import requests
import pandas as pd
import time
import random

def get_api_config(project_dir):
    """api_config.json 설정 파일을 로드하여 반환합니다."""
    config_path = os.path.join(project_dir, "data", "api_config.json")
    if not os.path.exists(config_path):
        return None
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"설정 파일 읽기 오류: {e}")
        return None

def refresh_api_config(project_dir):
    """capture_api.py를 실행하여 API 설정 정보를 갱신합니다."""
    print("\n[인증 만료 감지] API 게이트웨이 키를 갱신하기 위해 capture_api.py를 실행합니다...")
    capture_script = os.path.join(project_dir, "src", "capture_api.py")
    
    # 현재 실행 중인 파이썬 인터프리터 경로를 사용하여 스크립트 실행
    python_exe = sys.executable
    try:
        result = subprocess.run([python_exe, capture_script], capture_output=True, text=True, check=True)
        print(result.stdout)
        print("API 게이트웨이 키가 성공적으로 갱신되었습니다.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"API 키 갱신 중 오류 발생: {e}")
        print(e.stderr)
        return False

def scrape_kyobo_bestsellers():
    # 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_dir)
    data_dir = os.path.join(project_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    output_path = os.path.join(data_dir, "bestsellers.csv")
    
    # 1. API 설정 로드 (없다면 먼저 갱신)
    config = get_api_config(project_dir)
    if not config:
        print("API 설정 파일이 존재하지 않습니다. 최초 추출을 시도합니다.")
        if refresh_api_config(project_dir):
            config = get_api_config(project_dir)
            
    if not config:
        print("에러: API 설정을 가져올 수 없습니다. 수집을 중단합니다.")
        return
        
    url = config.get("url")
    headers = config.get("headers")
    
    data_list = []
    
    # 2. HTTP 요청 수행 (키 만료 시 최대 1회 자동 재시도)
    max_retries = 2
    for attempt in range(max_retries):
        print(f"\n교보문고 API 호출 중... (시도 {attempt+1}/{max_retries})")
        print(f"URL: {url}")
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            status_code = response.status_code
        except Exception as e:
            print(f"네트워크 요청 중 오류 발생: {e}")
            if attempt < max_retries - 1:
                if refresh_api_config(project_dir):
                    config = get_api_config(project_dir)
                    url = config.get("url")
                    headers = config.get("headers")
                continue
            else:
                print("최대 재시도 횟수를 초과했습니다. 수집을 실패했습니다.")
                return

        # 401 권한 오류 또는 API 오류 응답 처리
        is_unauthorized = (status_code == 401)
        api_data = {}
        if status_code == 200:
            try:
                api_data = response.json()
                # 교보문고 게이트웨이 응답 구조 상 status가 200이어도 에러 메시지가 있을 수 있음
                if api_data.get("statusCode") != 200:
                    is_unauthorized = True
            except:
                is_unauthorized = True
                
        if is_unauthorized:
            print("API 게이트웨이 인증에 실패했거나 토큰이 만료되었습니다.")
            if attempt < max_retries - 1:
                # 갱신 후 재시도
                if refresh_api_config(project_dir):
                    config = get_api_config(project_dir)
                    url = config.get("url")
                    headers = config.get("headers")
                    continue
            else:
                print("토큰 갱신 시도 후에도 실패하였습니다. 수집을 중단합니다.")
                return
                
        # 3. 데이터 파싱 진행
        if status_code == 200 and api_data.get("statusCode") == 200:
            best_sellers = api_data.get("data", {}).get("bestSeller", [])
            print(f"성공적으로 {len(best_sellers)}개의 도서 데이터를 수집했습니다.")
            
            for item in best_sellers:
                goods_no = str(item.get("saleCmdtid", "")).strip()
                rank = str(item.get("prstRnkn", ""))
                book_name = str(item.get("cmdtName", "")).strip()
                
                # 도서 소개 정보(inbukCntt)를 부제목 컬럼에 할당
                sub_name = str(item.get("inbukCntt", "")).strip()
                
                author = str(item.get("chrcName", "")).strip()
                publisher = str(item.get("pbcmName", "")).strip()
                
                # 출판일 YYYYMMDD -> YYYY-MM-DD 포맷 변환
                raw_date = str(item.get("rlseDate", "")).strip()
                pub_date = raw_date
                if len(raw_date) == 8 and raw_date.isdigit():
                    pub_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
                    
                price = item.get("price", 0)
                sale_price = item.get("sapr", 0)
                discount_rate = item.get("dscnRate", 0)
                
                # 리뷰 및 평점 정보
                review_count = item.get("buyRevwNumc", 0)
                rating = item.get("buyRevwRvgr", 0.0)
                
                # 카테고리명을 태그로 할당
                category = str(item.get("saleCmdtClstName", "")).strip()
                tags = category
                
                # ISBN(cmdtCode)을 기반으로 이미지 URL 동적 조합
                isbn = str(item.get("cmdtCode", "")).strip()
                img_url = ""
                if isbn:
                    img_url = f"https://contents.kyobobook.co.kr/sih/fit-in/200x0/pdt/{isbn}.jpg"
                
                data_list.append({
                    "상품번호": goods_no,
                    "순위": rank,
                    "도서명": book_name,
                    "부제목": sub_name,
                    "저자": author,
                    "출판사": publisher,
                    "출판일": pub_date,
                    "정가": price,
                    "할인가": sale_price,
                    "할인율": discount_rate,
                    "판매지수": 0, # 교보 API 미제공 항목
                    "리뷰건수": review_count,
                    "평점": rating,
                    "태그": tags,
                    "이미지URL": img_url
                })
            
            # 수집이 잘 처리되었으므로 루프 탈출
            break

    # 4. 저장 처리
    if data_list:
        new_df = pd.DataFrame(data_list)
        # 상품번호 기준으로 중복 제거
        new_df.drop_duplicates(subset=["상품번호"], keep="last", inplace=True)
        # 순위 기준으로 정렬
        new_df["순위"] = pd.to_numeric(new_df["순위"], errors="coerce")
        new_df.sort_values(by="순위", inplace=True)
        
        # 순위 인덱스 재부여 (6위 누락 등의 이슈를 보정하여 1부터 순차 재지정)
        new_df["순위"] = range(1, len(new_df) + 1)
        
        new_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"\n[성공] 최종 {len(new_df)}개 도서 정보를 {output_path}에 저장 완료했습니다 (순위 보정 완료).")
    else:
        print("\n[오류] 수집된 도서 데이터가 없습니다.")

if __name__ == "__main__":
    scrape_kyobo_bestsellers()
