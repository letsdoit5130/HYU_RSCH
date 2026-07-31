"""
마른김(HS 121221) 2021~2025년 데이터 기반 Top 10 수출 국가 정량 분석 스크립트.

기능:
1. 마른김 2025년 수출액, 5개년 성장률(%), 평균 단가($/kg) 추출
2. 국가별 주요 현지 가공 공장 및 B2B 원초 바이어 리스트 정리
"""

import os
import sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

DATA_PATH = 'BIZ-laver/data/HaeYu-Laver-EXP.csv'
df = pd.read_csv(DATA_PATH)

def clean_curr(v):
    if pd.isna(v):
        return 0.0
    return float(str(v).replace('$', '').replace(',', '').strip())

df['primary_value_usd'] = df['primaryValue'].apply(clean_curr)
df['unit_price_usd_kg'] = df['Unit Price ($PV/kg)'].apply(clean_curr)
df['qty_tons'] = df['Qty (t)']

# 마른김 (HS 121221) 데이터 필터링
df_raw = df[(df['cmdCode'] == 121221) & (~df['partnerISO'].isin(['W00', 'G20'])) & (df['primary_value_usd'] > 0)].copy()

# 국가별 2025년 수출액 Top 10
pivot_val = df_raw.pivot_table(index='partnerDesc', columns='refYear', values='primary_value_usd', aggfunc='sum').fillna(0)
pivot_val['growth_rate'] = np.where(pivot_val[2021] > 0, ((pivot_val[2025] / pivot_val[2021]) - 1) * 100, np.nan)

raw_summary = df_raw.groupby('partnerDesc').agg(
    total_val_all=('primary_value_usd', 'sum'),
    avg_price=('unit_price_usd_kg', 'mean')
).reset_index().merge(pivot_val[[2025, 'growth_rate']], left_on='partnerDesc', right_index=True)

top10_raw = raw_summary.sort_values(by=2025, ascending=False).head(10)

print("==================== 마른김 (HS 121221) Top 10 국가 정량 수치 ====================")
for r_idx, row in top10_raw.reset_index(drop=True).iterrows():
    val_m = row[2025] / 1e6
    print(f"{r_idx+1}위: {row['partnerDesc']} - 2025년: ${val_m:.2f}M | 5년성장: {row['growth_rate']:.1f}% | 단가: ${row['avg_price']:.2f}/kg")
