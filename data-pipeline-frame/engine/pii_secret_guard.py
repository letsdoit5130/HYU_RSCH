"""
개인정보 및 비밀키 자동 마스킹 보안 훅 모듈 (pii_secret_guard.py)

이 프로그램은 수집된 텍스트 데이터에서 이메일, 전화번호, API Key 등의 민감정보를 
정규식(Regex)으로 감지하여 오피스 리포트 변환 전에 자동 마스킹 처리하는 보안 모듈입니다.

작성일: 2026-07-23
"""

import re
import pandas as pd

def run_pii_secret_guard(csv_filepath: str):
    print(f"[SECURITY-HOOK] 개인정보 및 비밀키 자동 마스킹 스캔: {csv_filepath}")
    df = pd.read_csv(csv_filepath, encoding="utf-8-sig")
    
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    phone_pattern = r'01[016789]-\d{3,4}-\d{4}'
    secret_key_pattern = r'(bearer\s+[a-zA-Z0-9\._\-]+|sk-[a-zA-Z0-9]{20,})'

    def mask_text(text):
        if not isinstance(text, str):
            return text
        text = re.sub(email_pattern, '[MASKED_EMAIL]', text)
        text = re.sub(phone_pattern, '[MASKED_PHONE]', text)
        text = re.sub(secret_key_pattern, '[MASKED_SECRET]', text, flags=re.IGNORECASE)
        return text

    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(mask_text)

    df.to_csv(csv_filepath, index=False, encoding="utf-8-sig")
    print("[SECURITY-HOOK COMPLETED] 보안 마스킹 완료 데이터 저장 성공")
