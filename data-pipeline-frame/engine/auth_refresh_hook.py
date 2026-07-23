"""
인증 및 세션 자동 갱신 훅 모듈 (auth_refresh_hook.py)

이 프로그램은 HTTP 401/403 토큰 및 세션 만료 발생 시 Playwright Headless 브라우저를 구동하여
네트워크 패킷을 가로채 갱신된 인증 헤더/토큰을 동적으로 재캡처하는 자가치유 모듈입니다.

작성일: 2026-07-23
"""

import json
from playwright.sync_api import sync_playwright

def run_auth_refresh_hook(target_url: str, token_header_key: str = "Authorization") -> dict:
    print(f"[AUTH-HOOK] 인증 세션 만료 감지 -> Playwright 동적 토큰 재캡처 시도: {target_url}")
    captured_headers = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        def handle_request(request):
            nonlocal captured_headers
            headers = request.headers
            if token_header_key.lower() in [k.lower() for k in headers.keys()]:
                captured_headers = dict(headers)

        page.on("request", handle_request)
        page.goto(target_url, wait_until="networkidle")
        browser.close()

    if captured_headers:
        print("[AUTH-HOOK SUCCESS] 신규 토큰 헤더 갱신 성공!")
        with open("src/api_config.json", "w", encoding="utf-8") as f:
            json.dump(captured_headers, f, ensure_ascii=False, indent=2)
        return captured_headers
    return {}
