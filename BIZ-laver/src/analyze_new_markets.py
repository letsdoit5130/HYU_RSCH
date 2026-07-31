"""
1인 무역회사 관점에서 해유 김 수출 데이터(HaeYu-Laver-EXP.csv) 기반 신규 개척 시장 유망 후보 분석 스크립트.

분석 기준:
1. 최근 5개년 연평균 성장률(CAGR) 및 수출액 급증 국가
2. kg당 평균 수출 단가($/kg) 상위 고마진 국가
3. 조미김(HS 200899) 완제품 비중 및 소량 고부가가치 타깃 가능성
"""

import os
import sys
import pandas as pd
import numpy as np

# stdout utf-8 재설정
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

item_map = {121221: '마른김', 200899: '조미김'}
df['item_label'] = df['cmdCode'].map(item_map)

# World 및 불명확 국가 제외
df_c = df[~df['partnerISO'].isin(['W00', 'G20']) & (df['primary_value_usd'] > 0)].copy()

# 국가별 연도별 피봇
pivot_val = df_c.pivot_table(index='partnerDesc', columns='refYear', values='primary_value_usd', aggfunc='sum').fillna(0)

pivot_val['val_2021'] = pivot_val[2021]
pivot_val['val_2025'] = pivot_val[2025]
pivot_val['total_5y_usd'] = pivot_val[[2021, 2022, 2023, 2024, 2025]].sum(axis=1)

pivot_val['growth_rate_pct'] = np.where(pivot_val['val_2021'] > 0, ((pivot_val['val_2025'] / pivot_val['val_2021']) - 1) * 100, np.nan)

c_summary = df_c.groupby('partnerDesc').agg(
    total_val=('primary_value_usd', 'sum'),
    total_qty=('qty_tons', 'sum'),
    avg_unit_price=('unit_price_usd_kg', 'mean'),
    seasoned_val=('primary_value_usd', lambda x: x[df_c.loc[x.index, 'item_label'] == '조미김'].sum())
).reset_index()

c_summary['seasoned_ratio_pct'] = (c_summary['seasoned_val'] / c_summary['total_val']) * 100
c_summary = c_summary.merge(pivot_val[['val_2021', 'val_2025', 'growth_rate_pct']], left_on='partnerDesc', right_index=True)

out_text = []

out_text.append("=== 1. 고단가 & 고성장 유망 개척 시장 Top ===")
high_margin = c_summary[(c_summary['total_val'] >= 3e6) & (c_summary['avg_unit_price'] >= 22.0)].sort_values(by='growth_rate_pct', ascending=False)
out_text.append(high_margin[['partnerDesc', 'total_val', 'avg_unit_price', 'seasoned_ratio_pct', 'val_2021', 'val_2025', 'growth_rate_pct']].head(20).to_string())

out_text.append("\n=== 2. 유럽 주요국 (독일, 영국, 네덜란드, 프랑스 등) ===")
eu_countries = ['Germany', 'United Kingdom', 'Netherlands', 'France', 'Italy', 'Spain', 'Poland', 'Belgium']
eu_df = c_summary[c_summary['partnerDesc'].isin(eu_countries)].sort_values(by='total_val', ascending=False)
out_text.append(eu_df[['partnerDesc', 'total_val', 'avg_unit_price', 'seasoned_ratio_pct', 'val_2021', 'val_2025', 'growth_rate_pct']].to_string())

out_text.append("\n=== 3. 중동/남미/기타 신흥 유망국 ===")
emerging_countries = ['United Arab Emirates', 'Saudi Arabia', 'Mexico', 'Chile', 'Brazil', 'South Africa', 'India']
em_df = c_summary[c_summary['partnerDesc'].isin(emerging_countries)].sort_values(by='total_val', ascending=False)
out_text.append(em_df[['partnerDesc', 'total_val', 'avg_unit_price', 'seasoned_ratio_pct', 'val_2021', 'val_2025', 'growth_rate_pct']].to_string())

out_text.append("\n=== 4. 북미/아세안/오세아니아 고마진 소매 국가 ===")
retail_countries = ['Canada', 'Australia', 'Philippines', 'Malaysia', 'Viet Nam', 'New Zealand']
ret_df = c_summary[c_summary['partnerDesc'].isin(retail_countries)].sort_values(by='total_val', ascending=False)
out_text.append(ret_df[['partnerDesc', 'total_val', 'avg_unit_price', 'seasoned_ratio_pct', 'val_2021', 'val_2025', 'growth_rate_pct']].to_string())

result_str = "\n".join(out_text)
print(result_str)

with open('BIZ-laver/docs/market_opening_analysis.txt', 'w', encoding='utf-8') as f:
    f.write(result_str)
