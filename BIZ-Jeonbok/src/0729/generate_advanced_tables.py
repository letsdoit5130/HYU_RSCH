"""
BIZ-JB-Gathered.csv 추가 고도화 통계표 수집 스크립트 (BIZ-Jeonbok 하위 전용)

이 스크립트는 6가지 추가 분석 과제(월별/연도별 추이, 통관/운송 수단, 2차 파트너국,
단가 변동계수 CV, 국가별 무역 수지, K-Means 군집 분석 결과)에 대한 수치 통계표를 출력합니다.
"""

import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans

file_path = "BIZ-Jeonbok/BIZ-JB-Gathered.csv"
if not os.path.exists(file_path):
    file_path = "BIZ-Jeonbok/data/BIZ-JB-Gathered.csv"

try:
    df = pd.read_csv(file_path, encoding='utf-8-sig')
except Exception:
    df = pd.read_csv(file_path, encoding='cp949')

def clean_currency(val):
    if pd.isna(val):
        return np.nan
    val_str = str(val).replace('$', '').replace(',', '').strip()
    if val_str == '#DIV/0!' or val_str == '' or val_str == 'nan':
        return np.nan
    try:
        return float(val_str)
    except ValueError:
        return np.nan

df['primaryValue_num'] = df['primaryValue'].apply(clean_currency)
df['netWgt_num'] = df['netWgt'].apply(clean_currency)
unit_price_col = [c for c in df.columns if 'Unit Price' in c][0]
df['unit_price_num'] = df[unit_price_col].apply(clean_currency)

print("=== Table 12: 연도별 무역액 평균/중앙값/총합 요약 ===")
year_summary = df.groupby('refYear')['primaryValue_num'].agg(
    평균무역액_USD='mean',
    중앙무역액_USD='median',
    총무역액_USD='sum'
).reset_index()
print(year_summary.to_markdown(index=False))

print("\n=== Table 13: 상위 세관/통관 방식(customsDesc) 통계 ===")
customs_table = df.groupby('customsDesc').agg(
    거래건수=('period', 'count'),
    총무역액_USD=('primaryValue_num', 'sum'),
    평균단가_USD_kg=('unit_price_num', 'mean')
).sort_values(by='거래건수', ascending=False).head(10).reset_index()
print(customs_table.to_markdown(index=False))

print("\n=== Table 14: 상위 15개 2차 파트너/경유 국가(partner2Desc) 통계 ===")
p2_table = df.groupby('partner2Desc').agg(
    거래건수=('period', 'count'),
    총무역액_USD=('primaryValue_num', 'sum'),
    평균단가_USD_kg=('unit_price_num', 'mean')
).sort_values(by='거래건수', ascending=False).head(15).reset_index()
print(p2_table.to_markdown(index=False))

print("\n=== Table 15: 주요 보고국별 단가 변동계수 (CV = Std / Mean) ===")
top_reporters = df['reporterDesc'].value_counts().head(15).index
cv_list = []
for rep in top_reporters:
    prices = df[df['reporterDesc'] == rep]['unit_price_num'].dropna()
    if len(prices) > 5 and prices.mean() > 0:
        cv = prices.std() / prices.mean()
        cv_list.append({
            '보고국(reporterDesc)': rep,
            '거래건수': len(prices),
            '평균단가($/kg)': round(prices.mean(), 2),
            '표준편차($/kg)': round(prices.std(), 2),
            '변동계수(CV)': round(cv, 2)
        })
cv_df = pd.DataFrame(cv_list).sort_values(by='변동계수(CV)', ascending=False)
print(cv_df.to_markdown(index=False))

print("\n=== Table 16: 상위 10개 보고국 무역 수지 (수입 vs 수출 총 무역액) ===")
tb = df.groupby(['reporterDesc', 'flowDesc'])['primaryValue_num'].sum().unstack().fillna(0)
top10_rep = df['reporterDesc'].value_counts().head(10).index
tb_top10 = tb.loc[top10_rep].reset_index()
if 'Export' not in tb_top10.columns:
    tb_top10['Export'] = 0
if 'Import' not in tb_top10.columns:
    tb_top10['Import'] = 0
tb_top10['총무역규모(USD)'] = tb_top10['Export'] + tb_top10['Import']
print(tb_top10[['reporterDesc', 'Export', 'Import', '총무역규모(USD)']].to_markdown(index=False))

print("\n=== Table 17: 국가별 전복 품목 포트폴리오 군집(Cluster) 특성 ===")
country_cmd_pivot = pd.crosstab(df['reporterDesc'], df['cmdCode'], values=df['primaryValue_num'], aggfunc='sum').fillna(0)
country_cmd_norm = country_cmd_pivot.div(country_cmd_pivot.sum(axis=1), axis=0).fillna(0)

kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
clusters = kmeans.fit_predict(country_cmd_norm)
country_cmd_norm['Cluster'] = clusters
cluster_summary = country_cmd_norm.groupby('Cluster').mean()
print(cluster_summary.to_markdown())
