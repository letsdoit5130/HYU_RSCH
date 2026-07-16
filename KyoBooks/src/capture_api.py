"""
교보문고 베스트셀러 API 정보 자동 탐색 스크립트

이 모듈은 Playwright를 사용하여 교보문고 실시간 베스트셀러 페이지를 열고,
웹 브라우저에서 백엔드 API로 전송되는 HTTP 요청 중 베스트셀러 데이터를 조회하는
API URL과 필수 헤더(x-api-gw-key 등)를 자동으로 캡처하여 저장합니다.
수집된 정보는 이후 scraper.py에서 requests 모듈을 통해 빠르게 데이터를 가져오는 데 사용됩니다.

주요 기능:
1. Playwright 기반 네트워크 요청 인터셉트 및 필터링
2. x-api-gw-key 헤더 및 API 요청 URL 식별
3. 추출된 정보 KyoBooks/docs/scaraping_prompt.md 에 기록
4. 데이터 전송 및 가독성을 위한 KyoBooks/data/api_config.json 에 구조화된 데이터 저장
"""

import os
import json
import re
from playwright.sync_api import sync_playwright

def run_capture():
    # 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_dir)
    prompt_path = os.path.join(project_dir, "docs", "scaraping_prompt.md")
    config_dir = os.path.join(project_dir, "data")
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, "api_config.json")
    
    captured_data = {
        "url": None,
        "headers": {}
    }
    
    print("Playwright를 시작합니다...")
    with sync_playwright() as p:
        # Chromium 브라우저 실행 (상황을 보기 편하게 headless=True로 실행하되 로그 출력)
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # 네트워크 요청 인터셉트 핸들러 정의
        def handle_request(request):
            url = request.url
            # 교보문고 베스트셀러 API 주소 패턴 매칭
            if "best-seller/online" in url or "best-seller" in url or "bestseller" in url:
                headers = request.headers
                if "x-api-gw-key" in headers:
                    print(f"\n[API 매칭 성공] 발견된 URL: {url}")
                    captured_data["url"] = url
                    captured_data["headers"] = dict(headers)
        
        # 페이지 내 모든 요청에 대해 이벤트 리스너 등록
        page.on("request", handle_request)
        
        # 실시간 베스트셀러 페이지 접속
        target_url = "https://store.kyobobook.co.kr/bestseller/realtime?page=1&per=50"
        print(f"대상 페이지로 이동 중: {target_url}")
        page.goto(target_url, wait_until="networkidle")
        
        # 동적 로딩이 완료될 때까지 잠시 대기
        page.wait_for_timeout(5000)
        
        browser.close()
        
    if captured_data["url"] and captured_data["headers"].get("x-api-gw-key"):
        print("\n성공적으로 API 정보와 x-api-gw-key 값을 추출했습니다!")
        
        # 1. api_config.json 저장
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(captured_data, f, ensure_ascii=False, indent=4)
        print(f"API 설정 파일 저장 완료: {config_path}")
        
        # 2. scaraping_prompt.md 파일 자동 업데이트
        update_prompt_file(prompt_path, captured_data)
    else:
        print("\n[실패] 필요한 API 정보나 x-api-gw-key 값을 찾지 못했습니다.")

def update_prompt_file(filepath, data):
    """scaraping_prompt.md 문서의 빈칸을 채워 업데이트합니다."""
    if not os.path.exists(filepath):
        print(f"경고: {filepath} 파일이 존재하지 않습니다.")
        return
        
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    # 헤더 딕셔너리를 예쁘게 포맷팅
    headers_str = json.dumps(data["headers"], ensure_ascii=False, indent=2)
    
    # 마크다운 내용 보강
    new_content = re.sub(
        r"## 네트워크 메뉴를 통해 실제 데이터를 가져오는 URL\s*",
        f"## 네트워크 메뉴를 통해 실제 데이터를 가져오는 URL\n\n```\n{data['url']}\n```\n\n",
        content
    )
    
    # Header 정보 업데이트
    new_content = re.sub(
        r"## 해당 Request에 대한 Header 정보\s*",
        f"## 해당 Request에 대한 Header 정보\n\n```json\n{headers_str}\n```\n\n",
        new_content
    )
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
        
    print(f"안내서 문서 업데이트 완료: {filepath}")

if __name__ == "__main__":
    run_capture()
