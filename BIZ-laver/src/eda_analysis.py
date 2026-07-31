"""
해유 김 수출 데이터(HaeYu-Laver-EXP.csv) 종합 EDA 분석, 고화질 시각화 및 데이터 통계표 생성 스크립트.

주요 기능:
1. 데이터 정제: primaryValue, fobvalue, Unit Price, netWgt 문자열을 숫자형으로 변환
2. 품목(마른김 HS 121221 vs 조미김 HS 200899) 및 주요 국가별 aggregation
3. 11개 차원의 일변량/이변량/다변량/TF-IDF 고화질 그래프 생성 (images/ 저장)
4. 차트별 1:1 매핑 교차표, 피봇테이블, 기술통계표 CSV/MD 저장 (docs/ 저장)
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
from sklearn.feature_extraction.text import TfidfVectorizer

# 경로 설정
DATA_PATH = 'BIZ-laver/data/HaeYu-Laver-EXP.csv'
IMAGE_DIR = 'BIZ-laver/images'
REPORT_DIR = 'BIZ-laver/reports'
DOCS_DIR = 'BIZ-laver/docs'

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

# 1. 데이터 로드 및 전처리
try:
    df = pd.read_csv(DATA_PATH, encoding='utf-8')
except UnicodeDecodeError:
    try:
        df = pd.read_csv(DATA_PATH, encoding='cp949')
    except UnicodeDecodeError:
        df = pd.read_csv(DATA_PATH, encoding='euc-kr')

def clean_currency(val):
    if pd.isna(val):
        return np.nan
    val_str = str(val).replace('$', '').replace(',', '').strip()
    try:
        return float(val_str)
    except ValueError:
        return np.nan

df['primary_value_usd'] = df['primaryValue'].apply(clean_currency)
df['fob_value_usd'] = df['fobvalue'].apply(clean_currency)
df['unit_price_usd_kg'] = df['Unit Price ($PV/kg)'].apply(clean_currency)
df['net_wgt_kg'] = df['netWgt'].apply(clean_currency)
df['qty_tons'] = df['Qty (t)']

item_map = {
    121221: '마른김 (HS 121221)',
    200899: '조미김 (HS 200899)'
}
df['item_label'] = df['cmdCode'].map(item_map).fillna(df['cmdCode'].astype(str))

# 국가 레코드와 World 누적 레코드 분리
df_country = df[df['partnerISO'] != 'W00'].copy()

# ==========================================
# 통계표 1: 기초 기술통계 (수치형)
# ==========================================
num_cols = ['qty_tons', 'primary_value_usd', 'unit_price_usd_kg', 'net_wgt_kg']
num_desc = df_country[num_cols].describe().T
num_desc['median'] = df_country[num_cols].median()
num_desc.to_csv(os.path.join(DOCS_DIR, 'stat_00_numerical_describe.csv'), encoding='utf-8-sig')

# ==========================================
# 통계표 2: 품목별 기술통계 및 비중
# ==========================================
item_stat = df_country.groupby('item_label').agg(
    record_count=('primary_value_usd', 'count'),
    total_val_usd=('primary_value_usd', 'sum'),
    total_qty_tons=('qty_tons', 'sum'),
    mean_unit_price=('unit_price_usd_kg', 'mean'),
    median_unit_price=('unit_price_usd_kg', 'median'),
    std_unit_price=('unit_price_usd_kg', 'std')
).reset_index()
item_stat['val_share_pct'] = (item_stat['total_val_usd'] / item_stat['total_val_usd'].sum()) * 100
item_stat['qty_share_pct'] = (item_stat['total_qty_tons'] / item_stat['total_qty_tons'].sum()) * 100
item_stat.to_csv(os.path.join(DOCS_DIR, 'stat_01_item_summary.csv'), index=False, encoding='utf-8-sig')

# Chart 1: 품목별 비중
fig, ax = plt.subplots(1, 2, figsize=(13, 5.5))
item_val = item_stat.set_index('item_label')['total_val_usd'] / 1e6
ax[0].pie(item_val, labels=item_val.index, autopct='%1.1f%%', startangle=140, colors=['#3498db', '#e74c3c'], explode=(0.04, 0))
ax[0].set_title('품목별 총 수출액 비중 (백만 달러)', fontsize=13, fontweight='bold')

item_counts = df_country['item_label'].value_counts()
ax[1].bar(item_counts.index, item_counts.values, color=['#2ecc71', '#f39c12'], width=0.45)
ax[1].set_title('품목별 수출 거래 레코드 수', fontsize=13, fontweight='bold')
ax[1].set_ylabel('레코드 수')
for i, v in enumerate(item_counts.values):
    ax[1].text(i, v + 4, f"{v}건", ha='center', fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(IMAGE_DIR, '01_univariate_item_distribution.png'), dpi=300)
plt.close()

# ==========================================
# 통계표 3 & Chart 2: 연도별 전체 수출액/수출량 추이
# ==========================================
yearly_stat = df_country.groupby('refYear').agg(
    total_val_usd=('primary_value_usd', 'sum'),
    total_val_m_usd=('primary_value_usd', lambda x: x.sum() / 1e6),
    total_qty_tons=('qty_tons', 'sum'),
    total_qty_k_tons=('qty_tons', lambda x: x.sum() / 1e3),
    avg_unit_price=('unit_price_usd_kg', 'mean')
).reset_index()
yearly_stat.to_csv(os.path.join(DOCS_DIR, 'stat_02_yearly_summary.csv'), index=False, encoding='utf-8-sig')

fig, ax1 = plt.subplots(figsize=(10, 5.5))
color = '#1f77b4'
ax1.set_xlabel('연도', fontsize=11, fontweight='bold')
ax1.set_ylabel('총 수출액 (백만 달러)', color=color, fontsize=11, fontweight='bold')
bars = ax1.bar(yearly_stat['refYear'].astype(str), yearly_stat['total_val_m_usd'], color=color, alpha=0.75, width=0.4)
ax1.tick_params(axis='y', labelcolor=color)

for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height + 8, f"${height:,.1f}M", ha='center', va='bottom', fontsize=9.5, fontweight='bold')

ax2 = ax1.twinx()
color = '#ff7f0e'
ax2.set_ylabel('총 수출량 (천 톤)', color=color, fontsize=11, fontweight='bold')
ax2.plot(yearly_stat['refYear'].astype(str), yearly_stat['total_qty_k_tons'], color=color, marker='o', linewidth=2.5, markersize=7)
ax2.tick_params(axis='y', labelcolor=color)

for i, txt in enumerate(yearly_stat['total_qty_k_tons']):
    ax2.annotate(f"{txt:,.1f}k t", (str(yearly_stat['refYear'].iloc[i]), txt), textcoords="offset points", xytext=(0,8), ha='center', fontweight='bold', color=color)

plt.title('연도별 김 전체 수출액 및 수출물량 추이 (2021~2025)', fontsize=13, fontweight='bold', pad=12)
plt.tight_layout()
plt.savefig(os.path.join(IMAGE_DIR, '02_univariate_yearly_trend.png'), dpi=300)
plt.close()

# ==========================================
# 통계표 4 & Chart 3: 단가($/kg) 분위수 및 히스토그램
# ==========================================
unit_price_quantiles = df_country['unit_price_usd_kg'].quantile([0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99]).to_frame(name='quantile_val')
unit_price_quantiles.to_csv(os.path.join(DOCS_DIR, 'stat_03_unit_price_quantiles.csv'), encoding='utf-8-sig')

plt.figure(figsize=(9.5, 5.5))
filtered_unit_price = df_country[df_country['unit_price_usd_kg'] <= 50]['unit_price_usd_kg'].dropna()
plt.hist(filtered_unit_price, bins=40, color='#9b59b6', alpha=0.6, edgecolor='black', density=True)
sns.kdeplot(filtered_unit_price, color='#2c3e50', linewidth=2)
plt.title('김 수출 단가 ($/kg) 분포 (상한 $50/kg)', fontsize=13, fontweight='bold')
plt.xlabel('수출 단가 ($/kg)', fontsize=11)
plt.ylabel('밀도 (Density)', fontsize=11)

mean_p = filtered_unit_price.mean()
median_p = filtered_unit_price.median()
plt.axvline(mean_p, color='red', linestyle='--', linewidth=2, label=f'평균: ${mean_p:.2f}/kg')
plt.axvline(median_p, color='green', linestyle='-', linewidth=2, label=f'중앙값: ${median_p:.2f}/kg')
plt.legend(fontsize=10.5)
plt.tight_layout()
plt.savefig(os.path.join(IMAGE_DIR, '03_univariate_unit_price_distribution.png'), dpi=300)
plt.close()

# ==========================================
# 통계표 5 & Chart 4: 주요 수출 대상국 Top 20
# ==========================================
country_stat = df_country.groupby(['partnerDesc', 'partnerISO']).agg(
    total_val_usd=('primary_value_usd', 'sum'),
    total_qty_tons=('qty_tons', 'sum'),
    mean_unit_price=('unit_price_usd_kg', 'mean')
).reset_index().sort_values(by='total_val_usd', ascending=False)
country_stat['val_share_pct'] = (country_stat['total_val_usd'] / country_stat['total_val_usd'].sum()) * 100
country_stat.head(20).to_csv(os.path.join(DOCS_DIR, 'stat_04_top20_countries.csv'), index=False, encoding='utf-8-sig')

top20_country = country_stat.set_index('partnerDesc')['total_val_usd'].head(20) / 1e6

plt.figure(figsize=(11, 7.5))
y_pos = np.arange(len(top20_country))
plt.barh(y_pos, top20_country.values[::-1], color='#34495e', align='center', alpha=0.85)
plt.yticks(y_pos, top20_country.index[::-1], fontsize=10.5)
plt.xlabel('누적 수출액 (백만 달러)', fontsize=11, fontweight='bold')
plt.title('한국 김 주요 수출 대상국 Top 20 (2021~2025 누적)', fontsize=13, fontweight='bold')

for i, v in enumerate(top20_country.values[::-1]):
    plt.text(v + 3, i, f"${v:,.1f}M", va='center', fontweight='bold', fontsize=8.5)

plt.tight_layout()
plt.savefig(os.path.join(IMAGE_DIR, '04_bivariate_top20_countries.png'), dpi=300)
plt.close()

# ==========================================
# 통계표 6 & Chart 5: 연도별 x 품목별 교차표
# ==========================================
pivot_year_item = df_country.pivot_table(
    index='refYear',
    columns='item_label',
    values='primary_value_usd',
    aggfunc='sum'
) / 1e6
pivot_year_item.to_csv(os.path.join(DOCS_DIR, 'stat_05_pivot_year_item.csv'), encoding='utf-8-sig')

plt.figure(figsize=(10, 5.5))
x = np.arange(len(pivot_year_item.index))
width = 0.35

plt.bar(x - width/2, pivot_year_item['마른김 (HS 121221)'], width, label='마른김 (HS 121221)', color='#3498db')
plt.bar(x + width/2, pivot_year_item['조미김 (HS 200899)'], width, label='조미김 (HS 200899)', color='#e74c3c')

plt.xlabel('연도', fontsize=11, fontweight='bold')
plt.ylabel('수출액 (백만 달러)', fontsize=11, fontweight='bold')
plt.title('연도별 마른김 vs 조미김 수출액 비교 (2021~2025)', fontsize=13, fontweight='bold')
plt.xticks(x, pivot_year_item.index)
plt.legend(fontsize=10.5)

for i in range(len(x)):
    val1 = pivot_year_item['마른김 (HS 121221)'].iloc[i]
    val2 = pivot_year_item['조미김 (HS 200899)'].iloc[i]
    plt.text(x[i] - width/2, val1 + 4, f"${val1:.0f}M", ha='center', fontsize=8.5, fontweight='bold')
    plt.text(x[i] + width/2, val2 + 4, f"${val2:.0f}M", ha='center', fontsize=8.5, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(IMAGE_DIR, '05_bivariate_item_yearly_comparison.png'), dpi=300)
plt.close()

# ==========================================
# 통계표 7 & Chart 6: 품목별 단가 사분위수 비교
# ==========================================
item_price_box_stat = df_country.groupby('item_label')['unit_price_usd_kg'].describe()
item_price_box_stat.to_csv(os.path.join(DOCS_DIR, 'stat_06_item_price_describe.csv'), encoding='utf-8-sig')

plt.figure(figsize=(8.5, 5.5))
df_filtered_p = df_country[df_country['unit_price_usd_kg'] <= 100]

sns.boxplot(x='item_label', y='unit_price_usd_kg', data=df_filtered_p, palette=['#3498db', '#e74c3c'], width=0.35)
plt.title('품목별 수출 단가($/kg) 분포 비교', fontsize=13, fontweight='bold')
plt.xlabel('품목 구분', fontsize=11, fontweight='bold')
plt.ylabel('수출 단가 ($/kg)', fontsize=11, fontweight='bold')

means = df_filtered_p.groupby('item_label')['unit_price_usd_kg'].mean()
for i, mean_val in enumerate(means):
    plt.text(i, mean_val + 2, f"평균: ${mean_val:.2f}/kg", ha='center', fontweight='bold', color='black', bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))

plt.tight_layout()
plt.savefig(os.path.join(IMAGE_DIR, '06_bivariate_item_unit_price_boxplot.png'), dpi=300)
plt.close()

# ==========================================
# 통계표 8 & Chart 7: 산점도 분석
# ==========================================
plt.figure(figsize=(9.5, 5.5))
scatter_df = df_country[(df_country['qty_tons'] > 0) & (df_country['primary_value_usd'] > 0)].copy()

sns.scatterplot(
    data=scatter_df,
    x='qty_tons',
    y='primary_value_usd',
    hue='item_label',
    palette=['#3498db', '#e74c3c'],
    alpha=0.7,
    s=55
)
plt.xscale('log')
plt.yscale('log')
plt.title('수출 물량(톤, Log) vs 수출 금액(달러, Log) 상관관계', fontsize=13, fontweight='bold')
plt.xlabel('수출 물량 (톤, Log Scale)', fontsize=11, fontweight='bold')
plt.ylabel('수출 금액 (달러, Log Scale)', fontsize=11, fontweight='bold')
plt.grid(True, which="both", ls="--", alpha=0.5)
plt.legend(title='품목', fontsize=9.5)

plt.tight_layout()
plt.savefig(os.path.join(IMAGE_DIR, '07_bivariate_qty_vs_value_scatter.png'), dpi=300)
plt.close()

# ==========================================
# 통계표 9 & Chart 8: Top 5 국가 연도별 추이
# ==========================================
top5_countries = country_stat.head(5)['partnerDesc'].tolist()
df_top5 = df_country[df_country['partnerDesc'].isin(top5_countries)]
pivot_top5_yearly = df_top5.pivot_table(
    index='refYear',
    columns='partnerDesc',
    values='primary_value_usd',
    aggfunc='sum'
) / 1e6
pivot_top5_yearly.to_csv(os.path.join(DOCS_DIR, 'stat_08_pivot_top5_yearly.csv'), encoding='utf-8-sig')

plt.figure(figsize=(10.5, 5.5))
markers = ['o', 's', '^', 'D', 'v']
colors = ['#e74c3c', '#2ecc71', '#3498db', '#9b59b6', '#f1c40f']

for i, country in enumerate(top5_countries):
    if country in pivot_top5_yearly.columns:
        plt.plot(pivot_top5_yearly.index.astype(str), pivot_top5_yearly[country], marker=markers[i], color=colors[i], label=country, linewidth=2.2, markersize=6.5)

plt.title('주요 상위 5개국 연도별 수출액 변화 추이 (2021~2025)', fontsize=13, fontweight='bold')
plt.xlabel('연도', fontsize=11, fontweight='bold')
plt.ylabel('수출액 (백만 달러)', fontsize=11, fontweight='bold')
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend(title='국가', fontsize=10, loc='upper left')

plt.tight_layout()
plt.savefig(os.path.join(IMAGE_DIR, '08_multivariate_top5_yearly_trend.png'), dpi=300)
plt.close()

# ==========================================
# 통계표 10 & Chart 9: Top 15 국가 x 품목 교차 히트맵
# ==========================================
top15_countries = country_stat.head(15)['partnerDesc'].tolist()
df_top15 = df_country[df_country['partnerDesc'].isin(top15_countries)]
pivot_c_i = df_top15.pivot_table(
    index='partnerDesc',
    columns='item_label',
    values='primary_value_usd',
    aggfunc='sum'
).loc[top15_countries] / 1e6
pivot_c_i.to_csv(os.path.join(DOCS_DIR, 'stat_09_pivot_top15_country_item.csv'), encoding='utf-8-sig')

plt.figure(figsize=(9.5, 7.5))
sns.heatmap(pivot_c_i, annot=True, fmt=".1f", cmap="YlGnBu", cbar_kws={'label': '수출액 (백만 달러)'}, linewidths=.5)
plt.title('상위 15개국 x 품목별 누적 수출액 히트맵 (백만 달러)', fontsize=13, fontweight='bold')
plt.xlabel('품목 구분', fontsize=11, fontweight='bold')
plt.ylabel('수출 대상국', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(IMAGE_DIR, '09_multivariate_country_item_heatmap.png'), dpi=300)
plt.close()

# ==========================================
# 통계표 11 & Chart 10: 상관계수 행렬
# ==========================================
corr_df = df_country[['qty_tons', 'primary_value_usd', 'unit_price_usd_kg', 'net_wgt_kg', 'refYear']].corr()
corr_df.to_csv(os.path.join(DOCS_DIR, 'stat_10_correlation_matrix.csv'), encoding='utf-8-sig')

plt.figure(figsize=(7.5, 5.5))
sns.heatmap(corr_df, annot=True, fmt=".3f", cmap="Blues", vmin=-1, vmax=1, linewidths=1)
plt.title('수출 주요 수치 변수 간 상관계수 히트맵', fontsize=13, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(IMAGE_DIR, '10_multivariate_correlation_heatmap.png'), dpi=300)
plt.close()

# ==========================================
# 통계표 12 & Chart 11: TF-IDF 텍스트 키워드 분석
# ==========================================
text_data = df['cmdDesc'].dropna().tolist()
tfidf = TfidfVectorizer(stop_words='english', max_features=100)
tfidf_matrix = tfidf.fit_transform(text_data)
feature_names = tfidf.get_feature_names_out()
weights = np.asarray(tfidf_matrix.mean(axis=0)).ravel()

tfidf_df = pd.DataFrame({'keyword': feature_names, 'weight': weights}).sort_values(by='weight', ascending=False).head(30)
tfidf_df.to_csv(os.path.join(DOCS_DIR, 'stat_11_tfidf_top30_keywords.csv'), index=False, encoding='utf-8-sig')

plt.figure(figsize=(11, 7.5))
y_pos = np.arange(len(tfidf_df))
plt.barh(y_pos, tfidf_df['weight'].values[::-1], color='#16a085', align='center', alpha=0.85)
plt.yticks(y_pos, tfidf_df['keyword'].values[::-1], fontsize=10.5)
plt.xlabel('TF-IDF 가중치 (Mean Weight)', fontsize=11, fontweight='bold')
plt.title('품목 설명(cmdDesc) TF-IDF 상위 30개 키워드', fontsize=13, fontweight='bold')

for i, v in enumerate(tfidf_df['weight'].values[::-1]):
    plt.text(v + 0.002, i, f"{v:.4f}", va='center', fontweight='bold', fontsize=8.5)

plt.tight_layout()
plt.savefig(os.path.join(IMAGE_DIR, '11_text_tfidf_top30_keywords.png'), dpi=300)
plt.close()

print("모든 EDA 시각화 및 통계표 생성이 완벽하게 끝났습니다.")
