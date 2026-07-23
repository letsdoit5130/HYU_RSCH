import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.yes24.com/"
}

# 1페이지 확인
url_1 = "https://www.yes24.com/product/category/BestSellerContents?categoryNumber=001001025&sumGb=06&sex=A&age=255&goodsTp=0&addOptionTp=0&excludeTp=2&pageNumber=1&pageSize=24&goodsStatGb=06&eBookTp=0&bestType=DAY_BESTSELLER&type=day&saleYear=0&saleMonth=0&weekNo=0&saleDts=&viewMode=&freeYn="
# 10페이지 확인 (존재하지 않을 가능성이 큰 페이지)
url_10 = "https://www.yes24.com/product/category/BestSellerContents?categoryNumber=001001025&sumGb=06&sex=A&age=255&goodsTp=0&addOptionTp=0&excludeTp=2&pageNumber=10&pageSize=24&goodsStatGb=06&eBookTp=0&bestType=DAY_BESTSELLER&type=day&saleYear=0&saleMonth=0&weekNo=0&saleDts=&viewMode=&freeYn="

print("--- 1페이지 요청 ---")
res1 = requests.get(url_1, headers=headers, timeout=10)
soup1 = BeautifulSoup(res1.text, "lxml")
books1 = soup1.find_all("li", attrs={"data-goods-no": True})
print(f"1페이지 도서 개수: {len(books1)}")

print("--- 10페이지 요청 ---")
res10 = requests.get(url_10, headers=headers, timeout=10)
soup10 = BeautifulSoup(res10.text, "lxml")
books10 = soup10.find_all("li", attrs={"data-goods-no": True})
print(f"10페이지 도서 개수: {len(books10)}")
if len(books10) > 0:
    # 만약 있다면 첫번째 도서의 제목
    first_book = soup10.select_one("div.info_row.info_name a.gd_name")
    print(f"10페이지 첫 도서명: {first_book.text.strip() if first_book else '없음'}")
