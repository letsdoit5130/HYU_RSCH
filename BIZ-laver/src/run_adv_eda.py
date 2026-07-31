"""
심화 EDA 분석 및 시각화 이미지 4종(12~15번 PNG) 생성용 독립 실행 스크립트.

기능:
1. 연도별/품목별 수출액 시계열 추이
2. 단가 5대 마진 구간별 품목 비중
3. 40개 주요국 시장 포트폴리오 4분면 매트릭스 (Star, Cash Cow, Rising Volume, Watch List)
4. 수출 대상국 단가 변동성(CV%) 리스크 분석
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib

sys.stdout.reconfigure(encoding='utf-8')

DATA_PATH = 'BIZ-laver/data/HaeYu-Laver-EXP.csv'
IMAGE_DIR = 'BIZ-laver/images'
DOCS_DIR = 'BIZ-laver/docs'

os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

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

item_map = {121221: '마른김 (HS 121221)', 200899: '조미김 (HS 200899)'}
df['item_label'] = df['cmdCode'].map(item_map).fillna(df['cmdCode'].astype(str))

df_c = df[~df['partnerISO'].isin(['W00', 'G20']) & (df['primary_value_usd'] > 0)].copy()

# ==========================================
# 1. 연도별/품목별 수출액 시계열 추이 (Chart 12)
# ==========================================
monthly_agg = df_c.groupby(['refYear', 'item_label']).agg(
    total_val=('primary_value_usd', 'sum'),
    total_qty=('qty_tons', 'sum'),
    avg_unit_price=('unit_price_usd_kg', 'mean')
).reset_index()

monthly_agg['total_val_m'] = monthly_agg['total_val'] / 1e6
monthly_agg.to_csv(os.path.join(DOCS_DIR, 'adv_stat_01_yearly_item.csv'), index=False, encoding='utf-8-sig')

plt.figure(figsize=(10, 5.5))
sns.lineplot(data=monthly_agg, x='refYear', y='total_val_m', hue='item_label', marker='o', linewidth=2.5, palette=['#3498db', '#e74c3c'])
plt.title('연도별 품목별 총 수출액 추이 (2021~2025)', fontsize=13, fontweight='bold')
plt.xlabel('연도', fontsize=11, fontweight='bold')
plt.ylabel('수출액 (백만 달러)', fontsize=11, fontweight='bold')
plt.grid(True, linestyle='--', alpha=0.5)

for _, row in monthly_agg.iterrows():
    plt.text(row['refYear'], row['total_val_m'] + 15, f"${row['total_val_m']:.0f}M", ha='center', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(IMAGE_DIR, '12_advanced_monthly_seasonality.png'), dpi=300)
plt.close()

# ==========================================
# 2. 수출 단가 5대 마진 구간 분포 분석 (Chart 13)
# ==========================================
bins = [0, 10, 20, 30, 50, 1000]
labels = ['초저가 (<$10)', '저가 ($10-$20)', '중가 ($20-$30)', '고가 ($30-$50)', '초고가 프리미엄 (>$50)']

df_c['price_bracket'] = pd.cut(df_c['unit_price_usd_kg'], bins=bins, labels=labels)

bracket_summary = df_c.groupby(['price_bracket', 'item_label'], observed=False).agg(
    record_count=('primary_value_usd', 'count'),
    total_val=('primary_value_usd', 'sum')
).reset_index()

bracket_summary['val_share'] = bracket_summary.groupby('item_label', observed=False)['total_val'].transform(lambda x: (x / x.sum()) * 100)
bracket_summary.to_csv(os.path.join(DOCS_DIR, 'adv_stat_02_price_bracket_summary.csv'), index=False, encoding='utf-8-sig')

plt.figure(figsize=(10.5, 5.5))
ax = sns.barplot(data=bracket_summary, x='price_bracket', y='val_share', hue='item_label', palette=['#3498db', '#e74c3c'])
plt.title('품목별 수출 단가($/kg) 5대 마진 구간 비중 (%)', fontsize=13, fontweight='bold')
plt.xlabel('단가 마진 구간 ($/kg)', fontsize=11, fontweight='bold')
plt.ylabel('수출액 비중 (%)', fontsize=11, fontweight='bold')
plt.grid(True, axis='y', linestyle=':', alpha=0.6)

for p in ax.patches:
    h = p.get_height()
    if not np.isnan(h) and h > 0:
        ax.annotate(f"{h:.1f}%", (p.get_x() + p.get_width() / 2., h + 1.5), ha='center', va='bottom', fontsize=8.5, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(IMAGE_DIR, '13_advanced_price_bracket_distribution.png'), dpi=300)
plt.close()

# ==========================================
# 3. 4분면 시장 포트폴리오 매트릭스 (Chart 14)
# ==========================================
pivot_val = df_c.pivot_table(index='partnerDesc', columns='refYear', values='primary_value_usd', aggfunc='sum').fillna(0)
pivot_val['growth_rate'] = np.where(pivot_val[2021] > 0, ((pivot_val[2025] / pivot_val[2021]) - 1) * 100, np.nan)

country_portfolio = df_c.groupby('partnerDesc').agg(
    total_val=('primary_value_usd', 'sum'),
    avg_unit_price=('unit_price_usd_kg', 'mean')
).reset_index().merge(pivot_val[['growth_rate']], left_on='partnerDesc', right_index=True)

portfolio_df = country_portfolio[(country_portfolio['total_val'] >= 2e6) & (country_portfolio['growth_rate'].notna())].copy()

growth_threshold = 50.0
price_threshold = 23.0

def classify_quadrant(row):
    if row['growth_rate'] >= growth_threshold and row['avg_unit_price'] >= price_threshold:
        return 'Star Market (고성장/고마진)'
    elif row['growth_rate'] < growth_threshold and row['avg_unit_price'] >= price_threshold:
        return 'Cash Cow (안정적 고마진)'
    elif row['growth_rate'] >= growth_threshold and row['avg_unit_price'] < price_threshold:
        return 'Rising Volume (고성장/볼륨)'
    else:
        return 'Watch List (저성장/저마진)'

portfolio_df['quadrant'] = portfolio_df.apply(classify_quadrant, axis=1)
portfolio_df.to_csv(os.path.join(DOCS_DIR, 'adv_stat_03_market_portfolio_matrix.csv'), index=False, encoding='utf-8-sig')

plt.figure(figsize=(11, 7))
plot_p = portfolio_df[(portfolio_df['growth_rate'] <= 350) & (portfolio_df['growth_rate'] >= -80)].copy()

sns.scatterplot(
    data=plot_p,
    x='growth_rate',
    y='avg_unit_price',
    hue='quadrant',
    size='total_val',
    sizes=(60, 600),
    palette={'Star Market (고성장/고마진)': '#2ecc71', 'Cash Cow (안정적 고마진)': '#3498db',
             'Rising Volume (고성장/볼륨)': '#f39c12', 'Watch List (저성장/저마진)': '#e74c3c'},
    alpha=0.85
)

plt.axvline(growth_threshold, color='black', linestyle='--', linewidth=1.2)
plt.axhline(price_threshold, color='black', linestyle='--', linewidth=1.2)

top_countries_label = plot_p.sort_values(by='total_val', ascending=False).head(15)
for idx, row in top_countries_label.iterrows():
    plt.text(row['growth_rate'] + 2, row['avg_unit_price'] + 0.3, row['partnerDesc'], fontsize=8.5, fontweight='bold')

plt.title('글로벌 40개국 시장 포트폴리오 4분면 매트릭스 (성장률 x 평균단가)', fontsize=13, fontweight='bold')
plt.xlabel('5개년 수출 성장률 (2021→2025, %)', fontsize=11, fontweight='bold')
plt.ylabel('평균 수출 단가 ($/kg)', fontsize=11, fontweight='bold')
plt.legend(title='시장 분류 그룹', bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(IMAGE_DIR, '14_advanced_market_portfolio_matrix.png'), dpi=300)
plt.close()

# ==========================================
# 4. 단가 변동성 CV% 분석 (Chart 15)
# ==========================================
cv_stat = df_c.groupby('partnerDesc').agg(
    total_val=('primary_value_usd', 'sum'),
    mean_price=('unit_price_usd_kg', 'mean'),
    std_price=('unit_price_usd_kg', 'std')
).reset_index()
cv_stat['cv_pct'] = (cv_stat['std_price'] / cv_stat['mean_price']) * 100
cv_stat = cv_stat[cv_stat['total_val'] >= 5e6].sort_values(by='cv_pct', ascending=False)
cv_stat.to_csv(os.path.join(DOCS_DIR, 'adv_stat_04_price_volatility.csv'), index=False, encoding='utf-8-sig')

plt.figure(figsize=(10, 5.5))
top15_cv = cv_stat.head(15)
plt.barh(top15_cv['partnerDesc'][::-1], top15_cv['cv_pct'][::-1], color='#e67e22', alpha=0.85)
plt.title('주요 수출 대상국 수출 단가 변동성 (변동계수 CV %)', fontsize=13, fontweight='bold')
plt.xlabel('단가 변동계수 (Coefficient of Variation, %)', fontsize=11, fontweight='bold')
plt.ylabel('수출 대상국', fontsize=11, fontweight='bold')

for i, v in enumerate(top15_cv['cv_pct'][::-1]):
    plt.text(v + 1, i, f"{v:.1f}%", va='center', fontweight='bold', fontsize=8.5)

plt.tight_layout()
plt.savefig(os.path.join(IMAGE_DIR, '15_advanced_seasoned_vs_raw_monthly_trend.png'), dpi=300)
plt.close()

print("심화 EDA 시각화 12~15번 이미지 생성이 완료되었습니다.")
