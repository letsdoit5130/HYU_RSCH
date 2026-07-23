"""
타겟 API 구조 스캐너 및 응답 스키마 분석기 모듈 (inspect_api.py)

이 프로그램은 타겟 REST API Endpoint에 GET/POST 요청을 전송하고
응답 JSON 스키마 구조, 상태 코드 및 필수 헤더 세트를 분석하는 탐색 모듈입니다.

작성일: 2026-07-23
"""

import requests

def inspect_target_api(api_url: str, headers: dict = None) -> dict:
    print(f"[INSPECT-API] 타겟 API 스펙 스캔 시작: {api_url}")
    if headers is None:
        headers = {"User-Agent": "Mozilla/5.0"}
        
    try:
        res = requests.get(api_url, headers=headers, timeout=5)
        schema_info = {
            "status_code": res.status_code,
            "content_type": res.headers.get("content-type", ""),
            "json_sample": res.json() if "application/json" in res.headers.get("content-type", "") else {}
        }
        print(f"[INSPECT-API COMPLETED] 응답 코드 {res.status_code} 확인")
        return schema_info
    except Exception as e:
        print(f"[INSPECT-API ERROR] API 스캔 실패: {e}")
        return {}
