"""
UN Comtrade 공식 API 연동 무역 데이터 자동 수집 스크립트

이 스크립트는 UN Comtrade v1 REST API를 통해 지정한 HS Code(예: 030781 활전복, 121221 김 등)의 
최근 무역 데이터(수출국, 수입국, 거래 금액, 거래 물량, 단가)를 무인 자동으로 쿼리하여 CSV 파일로 저장합니다.
"""
import os
import sys
import argparse
import datetime
import urllib.request
import json
import numpy as np
import pandas as pd

# Windows 콘솔 인코딩 방어
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def fetch_un_comtrade_data(hs_code, reporter_code="all", period="2023", save_path="data/UNComtrade_Fetched.csv"):
    save_dir = os.path.dirname(save_path)
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
    
    # UN Comtrade Public Data API URL (v1 Preview API)
    url = f"https://comtradeapi.un.org/public/v1/preview/C/A/HS?period={period}&cmdCode={hs_code}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    
    print(f"[1] UN Comtrade API 호출 중 (HS Code: {hs_code}, Period: {period})...")
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            if response.status == 200:
                raw_json = response.read().decode('utf-8')
                data = json.loads(raw_json)
                
                records = data.get('data', [])
                if records:
                    df = pd.DataFrame(records)

                    def col_or_default(frame, col, default):
                        # DataFrame.get(col, default)는 col이 없으면 default를 그대로
                        # (스칼라라면 스칼라로) 반환하므로, 컬럼이 아예 없을 때는
                        # 명시적으로 행 수만큼 채운 Series를 만들어 반환한다.
                        if col in frame.columns:
                            return frame[col]
                        return pd.Series([default] * len(frame), index=frame.index)

                    # 주요 무역 컬럼 매핑 (raw UN Comtrade 스키마 이름 그대로 사용해
                    # generate_trade_eda.py가 별도 매핑 없이 바로 읽을 수 있게 한다)
                    df_clean = pd.DataFrame()
                    df_clean['refYear'] = col_or_default(df, 'period', period)
                    df_clean['flowDesc'] = col_or_default(df, 'flowDesc', 'Import')
                    df_clean['reporterDesc'] = col_or_default(df, 'reporterDesc', 'Rep. of Korea')
                    df_clean['partnerDesc'] = col_or_default(df, 'partnerDesc', 'Unknown')
                    df_clean['cmdCode'] = col_or_default(df, 'cmdCode', hs_code)
                    df_clean['cmdDesc'] = col_or_default(df, 'cmdDesc', hs_code)
                    df_clean['primaryValue'] = pd.to_numeric(col_or_default(df, 'primaryValue', np.nan), errors='coerce')
                    df_clean['netWgt'] = pd.to_numeric(col_or_default(df, 'netWgt', np.nan), errors='coerce')
                    df_clean = df_clean.dropna(subset=['primaryValue'])
                    if df_clean.empty:
                        raise ValueError("API 응답에 유효한 primaryValue가 없습니다.")
                    df_clean['unit_price'] = df_clean['primaryValue'] / df_clean['netWgt'].replace(0, np.nan)

                    df_clean.to_csv(save_path, index=False, encoding='utf-8-sig')
                    print(f"✅ UN Comtrade 무역 데이터 자동 수집 완료: {save_path} ({len(df_clean)}건)")
                    return save_path
    except Exception as e:
        print(f"⚠️ API 호출 중 예외 발생: {e}")

    # API 호출 실패 시: 이전 버전은 여기서 아무 경고 없이 5행짜리 가짜 데이터를 만들어
    # 마치 실제 수집이 성공한 것처럼 "✅ 수집 완료"를 출력했다. 이는 하위 EDA 리포트가
    # 조작된 숫자로 조용히 채워지는 결과로 이어지므로, 반드시 눈에 띄게 경고하고
    # is_simulated 플래그를 남긴다.
    print("=" * 60)
    print("[ERROR]: UN Comtrade API 호출 실패 — 실제 데이터가 아닌 예시(SIMULATED) 데이터로 대체합니다")
    print(f"- Missing: 실제 API 응답 (HS Code: {hs_code}, Period: {period})")
    print("- Required by: comtrade_api_collector.py")
    print("- Action: 네트워크/방화벽 상태를 확인하거나, UN Comtrade 웹사이트에서 수동으로 CSV를 내려받아 사용하세요.")
    print("⚠️ 아래 저장되는 CSV는 파이프라인 연속성 테스트용 예시 데이터이며 실제 무역 통계가 아닙니다.")
    print("=" * 60)

    df_sim = pd.DataFrame([
        {'refYear': 2024, 'flowDesc': 'Import', 'reporterDesc': 'Korea', 'partnerDesc': 'Japan', 'cmdCode': hs_code, 'cmdDesc': hs_code, 'primaryValue': 45000000, 'netWgt': 1200000, 'unit_price': 37.5},
        {'refYear': 2024, 'flowDesc': 'Import', 'reporterDesc': 'Korea', 'partnerDesc': 'USA', 'cmdCode': hs_code, 'cmdDesc': hs_code, 'primaryValue': 28000000, 'netWgt': 950000, 'unit_price': 29.4},
        {'refYear': 2024, 'flowDesc': 'Import', 'reporterDesc': 'Korea', 'partnerDesc': 'Hong Kong', 'cmdCode': hs_code, 'cmdDesc': hs_code, 'primaryValue': 18000000, 'netWgt': 500000, 'unit_price': 36.0},
        {'refYear': 2024, 'flowDesc': 'Import', 'reporterDesc': 'Australia', 'partnerDesc': 'Japan', 'cmdCode': hs_code, 'cmdDesc': hs_code, 'primaryValue': 35000000, 'netWgt': 800000, 'unit_price': 43.75},
        {'refYear': 2024, 'flowDesc': 'Import', 'reporterDesc': 'China', 'partnerDesc': 'USA', 'cmdCode': hs_code, 'cmdDesc': hs_code, 'primaryValue': 22000000, 'netWgt': 1100000, 'unit_price': 20.0},
    ])
    df_sim['is_simulated'] = True
    df_sim.to_csv(save_path, index=False, encoding='utf-8-sig')
    print(f"⚠️ 예시(SIMULATED) 데이터 저장 완료 (실제 데이터 아님): {save_path}")
    return save_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="UN Comtrade 무역 통계 데이터 자동 수집기")
    parser.add_argument("--hs_code", type=str, default="030781", help="수집할 HS Code (예: 030781 활전복, 121221 김 등)")
    parser.add_argument("--period", type=str, default="2023", help="수집 연도")
    parser.add_argument("--output", type=str, default="BIZ-Jeonbok/data/UNComtrade_Auto.csv", help="저장할 CSV 파일 경로")
    args = parser.parse_args()

    fetch_un_comtrade_data(args.hs_code, period=args.period, save_path=args.output)
