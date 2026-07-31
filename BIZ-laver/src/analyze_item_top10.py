"""
마른김(HS 121221) 및 조미김(HS 200899) 각각의 Top 10 잠재 타깃 시장 상세 분석 스크립트.

주요 기능:
- 품목별 Top 10 국가 수출액, 수출물량, 평균 단가, 5개년 성장률 산출
- 마른김 vs 조미김 개별 전략 수립을 위한 데이터 수집
"""

import sys
import pandas as pd
import numpy as np

sys.stdout.reconfigure(encoding='utf-8')

DATA_PATH = 'BIZ-laver/data/HaeYu-Laver-EXP.csv'
df = pd.read_csv(DATA_PATH)

def clean_currency(val):
    if pd.isna(val):
        return np.nan
    val_str = str(val).replace('$', '').replace(',', '').strip()
    try:
        return float(val_str)
    except ValueError:
        return np.nan

df['primary_value_usd'] = df['primaryValue'].apply(clean_currency)
df['unit_price_usd_kg'] = df['Unit Price ($PV/kg)'].apply(clean_currency)
df['qty_tons'] = df['Qty (t)']

# World 제외
df_c = df[~df['partnerISO'].isin(['W00', 'G20']) & (df['primary_value_usd'] > 0)].copy()

# 마른김 (HS 121221) Top 10
df_raw = df_c[df_c['cmdCode'] == 121221]
pivot_raw_val = df_raw.pivot_table(index='partnerDesc', columns='refYear', values='primary_value_usd', aggfunc='sum').fillna(0)
pivot_raw_val['val_2021'] = pivot_raw_val[2021]
pivot_raw_val['val_2025'] = pivot_raw_val[2025]
pivot_raw_val['growth_pct'] = np.where(pivot_raw_val['val_2021'] > 0, ((pivot_raw_val['val_2025'] / pivot_raw_val['val_2021']) - 1) * 100, np.nan)

raw_summary = df_raw.groupby('partnerDesc').agg(
    total_val=('primary_value_usd', 'sum'),
    total_qty=('qty_tons', 'sum'),
    avg_unit_price=('unit_price_usd_kg', 'mean')
).reset_index().merge(pivot_raw_val[['val_2021', 'val_2025', 'growth_pct']], left_on='partnerDesc', right_index=True)

raw_top10 = raw_summary.sort_values(by='total_val', ascending=False).head(10)

# 조미김 (HS 200899) Top 10
df_seas = df_c[df_c['cmdCode'] == 200899]
pivot_seas_val = df_seas.pivot_table(index='partnerDesc', columns='refYear', values='primary_value_usd', aggfunc='sum').fillna(0)
pivot_seas_val['val_2021'] = pivot_seas_val[2021]
pivot_seas_val['val_2025'] = pivot_seas_val[2025]
pivot_seas_val['growth_pct'] = np.where(pivot_seas_val['val_2021'] > 0, ((pivot_seas_val['val_2025'] / pivot_seas_val['val_2021']) - 1) * 100, np.nan)

seas_summary = df_seas.groupby('partnerDesc').agg(
    total_val=('primary_value_usd', 'sum'),
    total_qty=('qty_tons', 'sum'),
    avg_unit_price=('unit_price_usd_kg', 'mean')
).reset_index().merge(pivot_seas_val[['val_2021', 'val_2025', 'growth_pct']], left_on='partnerDesc', right_index=True)

seas_top10 = seas_summary.sort_values(by='total_val', ascending=False).head(10)

print("=== [마른김 (HS 121221) Top 10 국가] ===")
print(raw_top10.to_string(index=False))

print("\n=== [조미김 (HS 200899) Top 10 국가] ===")
print(seas_top10.to_string(index=False))

# 결과 저장
with open('BIZ-laver/docs/item_top10_analysis.txt', 'w', encoding='utf-8') as f:
    f.write("=== [마른김 (HS 121221) Top 10 국가] ===\n")
    f.write(raw_top10.to_string(index=False))
    f.write("\n\n=== [조미김 (HS 200899) Top 10 국가] ===\n")
    f.write(seas_top10.to_string(index=False))
