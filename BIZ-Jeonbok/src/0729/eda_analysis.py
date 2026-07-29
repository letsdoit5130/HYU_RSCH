"""
BIZ-JB-Gathered.csv 전복 무역 데이터 EDA 및 시각화 스크립트 (BIZ-Jeonbok 하위 전용)

본 스크립트는 BIZ-Jeonbok 하위의 전복 국제 무역 데이터셋(BIZ-JB-Gathered.csv)을 정제하고,
11종의 일변량, 이변량, 다변량 시각화 차트 및 텍스트 TF-IDF 분석 결과를 생성하여
BIZ-Jeonbok/images/ 폴더에 저장하며, 주요 통계표 및 해석 텍스트를 추출합니다.
"""

import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
from sklearn.feature_extraction.text import TfidfVectorizer

# 1. 디렉토리 설정
os.makedirs("BIZ-Jeonbok/images", exist_ok=True)
os.makedirs("BIZ-Jeonbok/reports", exist_ok=True)

# 2. 데이터 로드
file_path = "BIZ-Jeonbok/BIZ-JB-Gathered.csv"
if not os.path.exists(file_path):
    file_path = "BIZ-Jeonbok/data/BIZ-JB-Gathered.csv"

try:
    df = pd.read_csv(file_path, encoding='utf-8-sig')
except Exception:
    df = pd.read_csv(file_path, encoding='cp949')

# 3. 데이터 정제 함수
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
df['cifvalue_num'] = df['cifvalue'].apply(clean_currency)
df['fobvalue_num'] = df['fobvalue'].apply(clean_currency)
df['netWgt_num'] = df['netWgt'].apply(clean_currency)
unit_price_col = [c for c in df.columns if 'Unit Price' in c][0]
df['unit_price_num'] = df[unit_price_col].apply(clean_currency)

print("--- DATA CLEANING COMPLETED ---")
print(f"Total Rows: {len(df)}")

# -------------------------------------------------------------
# Chart 01: 무역 유형(flowDesc) 빈도 및 비율 (일변량)
# -------------------------------------------------------------
plt.figure(figsize=(8, 5))
flow_counts = df['flowDesc'].value_counts()
plt.bar(flow_counts.index, flow_counts.values, color='#2b5c8f')
plt.title('무역 유형(flowDesc) 거래 건수 분포', fontsize=14, pad=12)
plt.xlabel('무역 유형', fontsize=11)
plt.ylabel('건수 (Count)', fontsize=11)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('BIZ-Jeonbok/images/01_univariate_flow_dist.png', dpi=300)
plt.close()

# -------------------------------------------------------------
# Chart 02: 연도별(refYear) 거래 건수 추이 (일변량)
# -------------------------------------------------------------
plt.figure(figsize=(8, 5))
year_counts = df['refYear'].value_counts().sort_index()
plt.plot(year_counts.index.astype(str), year_counts.values, marker='o', color='#d9534f', linewidth=2.5, markersize=8)
plt.title('연도별(refYear) 전복 무역 데이터 건수 추이', fontsize=14, pad=12)
plt.xlabel('연도', fontsize=11)
plt.ylabel('건수 (Count)', fontsize=11)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('BIZ-Jeonbok/images/02_univariate_year_dist.png', dpi=300)
plt.close()

# -------------------------------------------------------------
# Chart 03: 주요 무역 보고 국가(reporterDesc) 상위 30개 (일변량)
# -------------------------------------------------------------
plt.figure(figsize=(10, 8))
reporter_top30 = df['reporterDesc'].value_counts().head(30)
plt.barh(reporter_top30.index[::-1], reporter_top30.values[::-1], color='#337ab7')
plt.title('상위 30개 전복 무역 보고 국가 (reporterDesc)', fontsize=14, pad=12)
plt.xlabel('거래 건수', fontsize=11)
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('BIZ-Jeonbok/images/03_univariate_reporter_top30.png', dpi=300)
plt.close()

# -------------------------------------------------------------
# Chart 04: 주요 무역 파트너 국가(partnerDesc) 상위 30개 (일변량)
# -------------------------------------------------------------
plt.figure(figsize=(10, 8))
partner_top30 = df['partnerDesc'].value_counts().head(30)
plt.barh(partner_top30.index[::-1], partner_top30.values[::-1], color='#5cb85c')
plt.title('상위 30개 전복 무역 파트너 국가 (partnerDesc)', fontsize=14, pad=12)
plt.xlabel('거래 건수', fontsize=11)
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('BIZ-Jeonbok/images/04_univariate_partner_top30.png', dpi=300)
plt.close()

# -------------------------------------------------------------
# Chart 05: 품목별(cmdCode / HS Code) 분포 (일변량)
# -------------------------------------------------------------
plt.figure(figsize=(9, 5))
cmd_counts = df['cmdCode'].astype(str).value_counts()
plt.bar(cmd_counts.index, cmd_counts.values, color='#f0ad4e')
plt.title('전복 HS 품목 코드(cmdCode)별 거래 건수 분포', fontsize=14, pad=12)
plt.xlabel('HS 코드', fontsize=11)
plt.ylabel('건수 (Count)', fontsize=11)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('BIZ-Jeonbok/images/05_univariate_cmd_dist.png', dpi=300)
plt.close()

# -------------------------------------------------------------
# Chart 06: 단위당 단가(Unit Price $/kg) 분포 (일변량 - 히스토그램/KDE)
# -------------------------------------------------------------
plt.figure(figsize=(9, 5))
valid_price = df['unit_price_num'].dropna()
valid_price_filtered = valid_price[valid_price <= valid_price.quantile(0.95)]
sns.histplot(valid_price_filtered, kde=True, color='#8e44ad', bins=30)
plt.title('전복 단위당 단가 ($/kg) 분포 (상위 95% 범위)', fontsize=14, pad=12)
plt.xlabel('단위당 단가 ($/kg)', fontsize=11)
plt.ylabel('빈도수', fontsize=11)
plt.grid(True, linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('BIZ-Jeonbok/images/06_univariate_unitprice_dist.png', dpi=300)
plt.close()

# -------------------------------------------------------------
# Chart 07: 연도별 총 무역액(Primary Value) 및 수량(Net Weight) 추이 (이변량)
# -------------------------------------------------------------
fig, ax1 = plt.subplots(figsize=(9, 5))
yearly_summary = df.groupby('refYear')[['primaryValue_num', 'netWgt_num']].sum().reset_index()

color = '#2c3e50'
ax1.set_xlabel('연도', fontsize=11)
ax1.set_ylabel('총 무역액 (USD)', color=color, fontsize=11)
line1 = ax1.plot(yearly_summary['refYear'].astype(str), yearly_summary['primaryValue_num'], color=color, marker='s', linewidth=2.5, label='총 무역액 ($)')
ax1.tick_params(axis='y', labelcolor=color)
ax1.grid(True, linestyle='--', alpha=0.5)

ax2 = ax1.twinx()
color = '#e74c3c'
ax2.set_ylabel('총 순중량 (kg)', color=color, fontsize=11)
line2 = ax2.plot(yearly_summary['refYear'].astype(str), yearly_summary['netWgt_num'], color=color, marker='o', linestyle='--', linewidth=2.5, label='총 순중량 (kg)')
ax2.tick_params(axis='y', labelcolor=color)

plt.title('연도별 전복 총 무역액 및 총 순중량 변화 추이', fontsize=14, pad=12)
fig.tight_layout()
plt.savefig('BIZ-Jeonbok/images/07_bivariate_year_tradevalue.png', dpi=300)
plt.close()

# -------------------------------------------------------------
# Chart 08: 무역 유형(flowDesc)별 단위당 단가 Boxplot (이변량)
# -------------------------------------------------------------
plt.figure(figsize=(9, 5))
df_flow_price = df[['flowDesc', 'unit_price_num']].dropna()
df_flow_price_filtered = df_flow_price[df_flow_price['unit_price_num'] <= df_flow_price['unit_price_num'].quantile(0.95)]
sns.boxplot(data=df_flow_price_filtered, x='flowDesc', y='unit_price_num', hue='flowDesc', palette='Set2', legend=False)
plt.title('무역 유형(flowDesc)별 전복 단위당 단가 ($/kg) 분포 비교', fontsize=14, pad=12)
plt.xlabel('무역 유형', fontsize=11)
plt.ylabel('단위당 단가 ($/kg)', fontsize=11)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('BIZ-Jeonbok/images/08_bivariate_flow_unitprice_box.png', dpi=300)
plt.close()

# -------------------------------------------------------------
# Chart 09: 상위 10개 보고국 x 무역 유형 히트맵 (다변량)
# -------------------------------------------------------------
plt.figure(figsize=(10, 6))
top10_reporters = df['reporterDesc'].value_counts().head(10).index
ct_reporter_flow = pd.crosstab(df[df['reporterDesc'].isin(top10_reporters)]['reporterDesc'], df['flowDesc'])
sns.heatmap(ct_reporter_flow, annot=True, fmt='d', cmap='Blues', cbar=True)
plt.title('상위 10개 보고국 vs 무역 유형 거래 건수 교차 히트맵', fontsize=14, pad=12)
plt.xlabel('무역 유형', fontsize=11)
plt.ylabel('보고 국가', fontsize=11)
plt.tight_layout()
plt.savefig('BIZ-Jeonbok/images/09_multivariate_reporter_flow_heatmap.png', dpi=300)
plt.close()

# -------------------------------------------------------------
# Chart 10: 수치형 변수 간 상관관계 히트맵 (다변량)
# -------------------------------------------------------------
plt.figure(figsize=(8, 6))
num_cols = ['refYear', 'primaryValue_num', 'netWgt_num', 'grossWgt', 'unit_price_num', 'cifvalue_num', 'fobvalue_num']
corr_matrix = df[num_cols].corr()
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', vmin=-1, vmax=1)
plt.title('전복 무역 주요 수치형 변수 간 상관관계 행렬', fontsize=14, pad=12)
plt.tight_layout()
plt.savefig('BIZ-Jeonbok/images/10_multivariate_corr_heatmap.png', dpi=300)
plt.close()

# -------------------------------------------------------------
# Chart 11: 텍스트 컬럼(cmdDesc) TF-IDF 상위 30 키워드 (텍스트 분석)
# -------------------------------------------------------------
text_data = df['cmdDesc'].dropna().astype(str)
vectorizer = TfidfVectorizer(stop_words='english', max_features=30)
tfidf_matrix = vectorizer.fit_transform(text_data)
words = vectorizer.get_feature_names_out()
weights = tfidf_matrix.sum(axis=0).A1
tfidf_df = pd.DataFrame({'word': words, 'weight': weights}).sort_values(by='weight', ascending=True)

plt.figure(figsize=(10, 8))
plt.barh(tfidf_df['word'], tfidf_df['weight'], color='#16a085')
plt.title('전복 품목 설명(cmdDesc) TF-IDF 상위 30개 단어 키워드', fontsize=14, pad=12)
plt.xlabel('TF-IDF 중요도 총합', fontsize=11)
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('BIZ-Jeonbok/images/11_tfidf_cmd_text.png', dpi=300)
plt.close()

print("--- ALL 11 CHARTS SUCCESSFULLY GENERATED & SAVED TO BIZ-Jeonbok/images/ ---")
