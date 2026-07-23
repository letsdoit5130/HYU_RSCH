"""
Playwright 기반 동적 DOM 및 무한 스크롤 웹 수집 모듈 (dynamic_scraper.py)

이 프로그램은 JavaScript 렌더링(SPA/React/Vue/Next.js) 및 무한 스크롤이 적용된
타겟 웹페이지의 요소를 Headless Chromium으로 자동 로딩하여 수집하는 모듈입니다.

작성일: 2026-07-23
"""

from playwright.sync_api import sync_playwright
import pandas as pd

def scrape_dynamic_page(url: str, selector: str, output_csv: str):
    print(f"[DYNAMIC-SCRAPER] Playwright 동적 수집 시작: {url}")
    results = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        
        for _ in range(3):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)
            
        elements = page.query_selector_all(selector)
        for elem in elements:
            text = elem.inner_text().strip()
            if text:
                results.append({"content": text})
                
        browser.close()
        
    df = pd.DataFrame(results)
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"[DYNAMIC-SCRAPER COMPLETE] 총 {len(df)}건 수집 완료 -> {output_csv}")
