"""
생성된 심화 EDA 통계 CSV 파일들의 내용을 콘솔에 표준 출력하는 스크립트 (utf-8 적용).
"""

import os
import sys
import pandas as pd

sys.stdout.reconfigure(encoding='utf-8')

DOCS_DIR = 'BIZ-laver/docs'

files = [
    'adv_stat_01_yearly_item.csv',
    'adv_stat_02_price_bracket_summary.csv',
    'adv_stat_03_market_portfolio_matrix.csv',
    'adv_stat_04_price_volatility.csv'
]

for filename in files:
    filepath = os.path.join(DOCS_DIR, filename)
    if os.path.exists(filepath):
        print(f"\n==================== {filename} ====================")
        df = pd.read_csv(filepath)
        print(df.to_string(index=False))
