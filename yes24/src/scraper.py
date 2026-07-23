"""
YES24 베스트셀러 데이터 수집기 (Scraper)

이 모듈은 YES24의 특정 카테고리 베스트셀러 페이지 API를 호출하여 도서 데이터를 수집하는 프로그램입니다.
1페이지부터 시작하여 마지막 페이지까지 페이지별로 순회하며 데이터를 수집하고,
수집 중 서버 차단을 방지하기 위해 랜덤 대기 시간을 적용하였으며, 최종 결과를 CSV 형식으로 저장합니다.

- 주요 기능:
  1. 기존 수집 파일(bestsellers.csv) 연동 및 이어받기 수집 지원
  2. 서버 부하 및 차단 방지를 위한 랜덤 대기 시간(0.1 ~ 0.5초) 적용
  3. 마지막 페이지 초과 감지 로직 적용 (중복 도서 ID 기반 자동 종료)
  4. 도서 상세 정보 파싱 (상품번호, 순위, 도서명, 부제목, 저자, 출판사, 출판일, 가격, 판매지수, 평점, 태그, 이미지 URL 등)

작성일: 2026-07-12
"""

import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import random

def scrape_bestseller():
    """
    YES24 카테고리 베스트셀러 목록을 수집하고 CSV 파일로 저장하는 핵심 함수입니다.
    
    상세 수행 프로세스:
    1. 데이터 저장 경로 설정 및 기존 CSV 파일 로드 시도
    2. 기존 파일에 데이터가 존재할 경우 시작 페이지 번호 자동 계산 (이어받기 기능)
    3. 마지막 페이지를 만날 때까지 루프 수행
       - 요청 전 랜덤 대기
       - HTML 요청 및 BeautifulSoup 파싱
       - 마지막 페이지 초과 여부 감지 (페이지 도서 ID 전체가 이미 수집된 것인지 확인)
       - 개별 도서 상세 데이터 파싱 및 리스트 적재
    4. 기존 데이터와 신규 데이터를 병합하고, 상품번호 기준으로 최종 중복 제거
    5. UTF-8-SIG 인코딩으로 CSV 파일 저장 (엑셀 한글 깨짐 방지)
    """
    # 1. 파일 저장 경로 및 파일명 정의
    current_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(current_dir, "..", "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "bestsellers.csv")
    
    # 2. 기존 수집 데이터 불러오기 및 시작 페이지 설정
    existing_df = None
    collected_goods_ids = set()
    start_page = 1
    
    if os.path.exists(output_path):
        try:
            existing_df = pd.read_csv(output_path, encoding="utf-8-sig")
            # 기존 데이터가 존재하면 다음 페이지부터 수집을 재개
            if len(existing_df) > 0:
                # 상품번호를 조회용 세트에 담아둠 (중복 확인 및 이어받기 용도)
                for gid in existing_df["상품번호"]:
                    collected_goods_ids.add(str(gid).strip())
                
                # YES24 API의 페이지당 수량인 24개 기준으로 이어받을 페이지 계산
                if len(existing_df) >= 24:
                    start_page = (len(existing_df) // 24) + 1
                    print(f"기존에 수집된 데이터({len(existing_df)}개)가 존재합니다. {start_page}페이지부터 수집을 이어갑니다.")
                else:
                    print("기존 데이터 개수가 24개 미만이므로 1페이지부터 새로 수집합니다.")
                    existing_df = None
                    collected_goods_ids.clear()
        except Exception as e:
            print(f"기존 CSV 파일을 읽는 중 오류 발생: {e}. 처음부터 새로 수집합니다.")
            existing_df = None
            collected_goods_ids.clear()

    # 3. 요청 헤더 정의 (봇 감지 우회)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.yes24.com/"
    }
    
    data_list = []
    page = start_page
    
    # 4. 페이지 순회 수집 루프 시작
    while True:
        # YES24 카테고리 베스트셀러 목록 요청 API URL
        url = f"https://www.yes24.com/product/category/BestSellerContents?categoryNumber=001001025&sumGb=06&sex=A&age=255&goodsTp=0&addOptionTp=0&excludeTp=2&pageNumber={page}&pageSize=24&goodsStatGb=06&eBookTp=0&bestType=DAY_BESTSELLER&type=day&saleYear=0&saleMonth=0&weekNo=0&saleDts=&viewMode=&freeYn="
        
        # 0.1 ~ 0.5초 랜덤 대기 적용 (서버 요청 간격 분산)
        sleep_time = random.uniform(0.1, 0.5)
        time.sleep(sleep_time)
        
        print(f"{page}페이지 요청 중... (대기 시간: {sleep_time:.3f}초)")
        try:
            response = requests.get(url, headers=headers, timeout=10)
        except Exception as e:
            print(f"네트워크 오류 발생: {e}. 수집을 중단합니다.")
            break
            
        if response.status_code != 200:
            print(f"요청 실패: 상태 코드 {response.status_code}. 수집을 중단합니다.")
            break
        
        # BeautifulSoup을 이용해 HTML 파싱
        soup = BeautifulSoup(response.text, "lxml")
        books = soup.find_all("li", attrs={"data-goods-no": True})
        
        if not books:
            print("더 이상 발견된 도서 태그가 없습니다. 수집을 완료합니다.")
            break
            
        # 5. 마지막 페이지 감지
        # 해당 페이지의 모든 도서 ID를 추출
        page_goods_ids = [str(book.get("data-goods-no", "")).strip() for book in books]
        
        # 만약 이 페이지의 모든 도서가 이미 수집된 상태라면, 루프를 종료합니다.
        # (YES24는 마지막 페이지를 초과하는 요청에 대해 동일한 데이터를 계속 반환하므로 중복 데이터 여부로 판단)
        if all(gid in collected_goods_ids for gid in page_goods_ids):
            print(f"더 이상 새로운 도서가 발견되지 않습니다 (이전 수집 데이터와 100% 중복). 수집을 완료합니다. (마지막 페이지: {page-1}페이지)")
            break
            
        print(f"{page}페이지에서 {len(books)}개의 도서 발견 (새로운 데이터 포함)")
        
        # 6. 개별 도서 상세 정보 추출
        for book in books:
            goods_no = str(book.get("data-goods-no", "")).strip()
            
            # 페이지 간 중복된 데이터가 존재하는 경우 건너뜀
            if goods_no in collected_goods_ids:
                continue
                
            collected_goods_ids.add(goods_no)
            
            # 6.1. 순위
            rank_elem = book.select_one("em.ico.rank")
            rank = rank_elem.text.strip() if rank_elem else ""
            
            # 6.2. 이미지 URL
            img_elem = book.select_one("div.item_img img.lazy")
            img_url = ""
            if img_elem:
                img_url = img_elem.get("data-original") or img_elem.get("src") or ""
            
            # 6.3. 도서명
            name_elem = book.select_one("div.info_row.info_name a.gd_name")
            book_name = name_elem.text.strip() if name_elem else ""
            
            # 6.4. 부제목 (있는 경우에만 파싱)
            sub_name_elem = book.select_one("div.info_row.info_name span.gd_nameE")
            sub_name = sub_name_elem.text.strip() if sub_name_elem else ""
            
            # 6.5. 저자 (끝의 ' 저' 또는 ' 편' 텍스트 제거)
            auth_elem = book.select_one("span.authPub.info_auth")
            author = ""
            if auth_elem:
                author = auth_elem.text.strip()
                author = re.sub(r'\s+저$', '', author)
                author = re.sub(r'\s+편$', '', author)
                author = author.strip()
                
            # 6.6. 출판사
            pub_elem = book.select_one("span.authPub.info_pub")
            publisher = pub_elem.text.strip() if pub_elem else ""
            
            # 6.7. 출판일
            date_elem = book.select_one("span.authPub.info_date")
            pub_date = date_elem.text.strip() if date_elem else ""
            
            # 6.8. 정가 (원가, 콤마 제거)
            original_price_elem = book.select_one("div.info_row.info_price span.txt_num.dash em.yes_m")
            original_price = original_price_elem.text.strip().replace(",", "") if original_price_elem else ""
            
            # 6.9. 할인가 (실제 판매가, 콤마 제거)
            sale_price_elem = book.select_one("div.info_row.info_price strong.txt_num em.yes_b")
            sale_price = sale_price_elem.text.strip().replace(",", "") if sale_price_elem else ""
            
            # 6.10. 할인율
            discount_rate_elem = book.select_one("div.info_row.info_price span.txt_sale em.num")
            discount_rate = discount_rate_elem.text.strip() if discount_rate_elem else ""
            
            # 6.11. 판매지수 (숫자만 추출)
            sale_num_elem = book.select_one("span.saleNum")
            sale_num = ""
            if sale_num_elem:
                sale_num_text = sale_num_elem.text.strip()
                sale_num_match = re.search(r'판매지수\s*([\d,]+)', sale_num_text)
                if sale_num_match:
                    sale_num = sale_num_match.group(1).replace(",", "")
                else:
                    sale_num = sale_num_text
            
            # 6.12. 회원리뷰 수
            review_count_elem = book.select_one("span.rating_rvCount em.txC_blue")
            review_count = review_count_elem.text.strip() if review_count_elem else "0"
            
            # 6.13. 리뷰 평점
            rating_elem = book.select_one("span.rating_grade em.yes_b")
            rating = rating_elem.text.strip() if rating_elem else "0.0"
            
            # 6.14. 도서 태그들 (쉼표로 구분하여 하나의 문자열로 결합)
            tag_elems = book.select("div.info_row.info_tag span.tag a")
            tags = ", ".join([tag.text.strip() for tag in tag_elems])
            
            # 도서 딕셔너리 생성 후 목록에 추가
            data_list.append({
                "상품번호": goods_no,
                "순위": rank,
                "도서명": book_name,
                "부제목": sub_name,
                "저자": author,
                "출판사": publisher,
                "출판일": pub_date,
                "정가": original_price,
                "할인가": sale_price,
                "할인율": discount_rate,
                "판매지수": sale_num,
                "리뷰건수": review_count,
                "평점": rating,
                "태그": tags,
                "이미지URL": img_url
            })
            
        page += 1

    # 7. 판다스 데이터프레임 변환 및 저장 처리
    new_df = pd.DataFrame(data_list)
    
    # 기존 데이터가 존재하면 병합 후 중복 도서 제거
    if existing_df is not None:
        final_df = pd.concat([existing_df, new_df], ignore_index=True)
        final_df.drop_duplicates(subset=["상품번호"], keep="last", inplace=True)
    else:
        final_df = new_df
        
    # UTF-8-SIG 인코딩으로 저장하여 한글 인코딩 호환성 확보
    final_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"전체 데이터 수집 완료! 총 {len(final_df)}개 도서 데이터 저장됨.")
    print(f"저장 경로: {output_path}")

if __name__ == "__main__":
    scrape_bestseller()
