"""
교보문고 실시간 베스트셀러 데이터 수집기 (전체 페이지 수집 및 중복 제거 개선 버전)

이 모듈은 교보문고 실시간 베스트셀러 API를 호출하여 전체 페이지의 데이터를 수집합니다.
기존에 로컬에 수집되어 있던 도서 정보(bestsellers.csv)를 읽어와 중복되는 도서는
추가하지 않고 새로 수집된 고유한 도서들만 병합하여 저장합니다.
x-api-gw-key 만료 상황을 자동 감지하면 capture_api.py를 수행하여 자동 갱신합니다.
"""

import os
import sys
import json
import subprocess
import requests
import pandas as pd
import time
import urllib.parse

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
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_dir)
    data_dir = os.path.join(project_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    output_path = os.path.join(data_dir, "bestsellers.csv")
    
    # 1. 기존 데이터 로드 (중복 체크용)
    existing_ids = set()
    existing_data = []
    if os.path.exists(output_path):
        try:
            old_df = pd.read_csv(output_path, encoding="utf-8-sig")
            if not old_df.empty and "상품번호" in old_df.columns:
                # 상품번호 타입 통일을 위해 문자열 처리 및 공백 제거
                old_df["상품번호"] = old_df["상품번호"].astype(str).str.strip()
                existing_ids = set(old_df["상품번호"].tolist())
                existing_data = old_df.to_dict(orient="records")
                print(f"기본 수집된 기존 도서 데이터를 로드했습니다: {len(existing_data)}권 (고유 ID 수: {len(existing_ids)}개)")
        except Exception as e:
            print(f"기존 데이터 로드 실패 (새 파일로 수집 진행): {e}")

    # 2. API 설정 로드
    config = get_api_config(project_dir)
    if not config:
        print("API 설정 파일이 존재하지 않습니다. 최초 추출을 시도합니다.")
        if refresh_api_config(project_dir):
            config = get_api_config(project_dir)
            
    if not config:
        print("에러: API 설정을 가져올 수 없습니다. 수집을 중단합니다.")
        return
        
    base_url = config.get("url")
    headers = config.get("headers")
    
    # URL 쿼리 구조 조립을 위한 파싱
    parsed_url = urllib.parse.urlparse(base_url)
    query_params = urllib.parse.parse_qs(parsed_url.query)
    
    new_data_list = []
    page = 1
    max_pages = 10 # 안전을 위한 최대 페이지 상한선
    
    while page <= max_pages:
        # page 파라미터 동적 갱신
        query_params['page'] = [str(page)]
        new_query = urllib.parse.urlencode(query_params, doseq=True)
        target_url = urllib.parse.urlunparse((
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            parsed_url.params,
            new_query,
            parsed_url.fragment
        ))
        
        # 3. HTTP 요청 수행 (인증 만료 시 1회 자동 재시도)
        max_retries = 2
        success = False
        api_data = {}
        
        for attempt in range(max_retries):
            print(f"\n교보문고 API 호출 중... (페이지: {page}, 시도 {attempt+1}/{max_retries})")
            try:
                response = requests.get(target_url, headers=headers, timeout=15)
                status_code = response.status_code
            except Exception as e:
                print(f"네트워크 요청 중 오류 발생: {e}")
                if attempt < max_retries - 1:
                    if refresh_api_config(project_dir):
                        config = get_api_config(project_dir)
                        headers = config.get("headers")
                    continue
                else:
                    break

            is_unauthorized = (status_code == 401)
            if status_code == 200:
                try:
                    api_data = response.json()
                    if api_data.get("statusCode") != 200:
                        is_unauthorized = True
                except:
                    is_unauthorized = True
                    
            if is_unauthorized:
                print("API 게이트웨이 인증에 실패했거나 토큰이 만료되었습니다.")
                if attempt < max_retries - 1:
                    if refresh_api_config(project_dir):
                        config = get_api_config(project_dir)
                        headers = config.get("headers")
                        continue
                else:
                    break
            
            if status_code == 200 and api_data.get("statusCode") == 200:
                success = True
                break
        
        if not success:
            print(f"페이지 {page} 호출 실패. 수집을 종료합니다.")
            break
            
        # 4. 데이터 파싱 진행
        best_sellers = api_data.get("data", {}).get("bestSeller", [])
        if not best_sellers:
            print(f"페이지 {page}에 더 이상 도서 데이터가 없습니다. 수집 루프를 종료합니다.")
            break
            
        print(f"성공적으로 페이지 {page}의 도서 {len(best_sellers)}개를 가져왔습니다.")
        
        duplicated_in_page_count = 0
        new_in_page_count = 0
        
        for item in best_sellers:
            goods_no = str(item.get("saleCmdtid", "")).strip()
            
            # 중복 체크: 기존 파일에 존재하는 도서는 건너뛰기
            if goods_no in existing_ids:
                duplicated_in_page_count += 1
                continue
                
            # 해당 루프 내에서 수집되는 신규 도서 간의 중복도 방지
            if any(x["상품번호"] == goods_no for x in new_data_list):
                duplicated_in_page_count += 1
                continue
                
            rank = str(item.get("prstRnkn", ""))
            book_name = str(item.get("cmdtName", "")).strip()
            sub_name = str(item.get("inbukCntt", "")).strip()
            author = str(item.get("chrcName", "")).strip()
            publisher = str(item.get("pbcmName", "")).strip()
            
            raw_date = str(item.get("rlseDate", "")).strip()
            pub_date = raw_date
            if len(raw_date) == 8 and raw_date.isdigit():
                pub_date = f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"
                
            price = item.get("price", 0)
            sale_price = item.get("sapr", 0)
            discount_rate = item.get("dscnRate", 0)
            review_count = item.get("buyRevwNumc", 0)
            rating = item.get("buyRevwRvgr", 0.0)
            category = str(item.get("saleCmdtClstName", "")).strip()
            tags = category
            
            isbn = str(item.get("cmdtCode", "")).strip()
            img_url = ""
            if isbn:
                img_url = f"https://contents.kyobobook.co.kr/sih/fit-in/200x0/pdt/{isbn}.jpg"
            
            new_data_list.append({
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
                "판매지수": 0,
                "리뷰건수": review_count,
                "평점": rating,
                "태그": tags,
                "이미지URL": img_url
            })
            new_in_page_count += 1
            
        print(f"-> 페이지 {page} 요약: 신규 추가 {new_in_page_count}권 / 중복 건너뜀 {duplicated_in_page_count}권")
        page += 1
        time.sleep(1) # 부하 방지를 위한 딜레이

    # 5. 최종 데이터 병합 및 저장 처리
    final_list = existing_data + new_data_list
    
    if final_list:
        final_df = pd.DataFrame(final_list)
        # 한번 더 상품번호 기준 유일성 보장
        final_df.drop_duplicates(subset=["상품번호"], keep="first", inplace=True)
        
        # 순위 컬럼을 숫자로 정렬
        final_df["순위"] = pd.to_numeric(final_df["순위"], errors="coerce")
        final_df.sort_values(by="순위", inplace=True)
        
        # 최종 순위 재부여 (1부터 전체 데이터 개수까지 빈틈없이 강제 보정)
        final_df["순위"] = range(1, len(final_df) + 1)
        
        final_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"\n[성공] 기존 대비 신규 도서 {len(new_data_list)}권이 추가되었습니다.")
        print(f"최종 {len(final_df)}개 도서 정보를 {output_path}에 저장 완료했습니다 (전체 페이지 수집 & 중복 보정 완료).")
    else:
        print("\n[오류] 수집된 도서 데이터가 전혀 없습니다.")

if __name__ == "__main__":
    scrape_kyobo_bestsellers()
