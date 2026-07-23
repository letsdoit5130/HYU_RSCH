"""
Playwright 네트워크 패킷 인터셉터 기반 API 키/헤더 자동 캡처 모듈 (capture_api.py)

이 프로그램은 Headless Chromium 브라우저를 구동하여 타겟 웹사이트 접속 시 발생하는
XHR/Fetch 요청 패킷의 Header(인증 토큰, Gateway Key 등) 및 Endpoint URL을 인터셉트하여 캡처하는 모듈입니다.

작성일: 2026-07-23
"""

import json
from playwright.sync_api import sync_playwright

def capture_api_headers(url: str, target_keyword: str = "api") -> dict:
    print(f"[CAPTURE-API] Playwright 기반 네트워크 패킷 스캔 시작: {url}")
    captured = {}
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        def handle_request(request):
            nonlocal captured
            if target_keyword in request.url:
                captured["url"] = request.url
                captured["headers"] = dict(request.headers)

        page.on("request", handle_request)
        page.goto(url, wait_until="networkidle")
        browser.close()

    print(f"[CAPTURE-API COMPLETED] 패킷 캡처 완료 여부: {bool(captured)}")
    return captured
