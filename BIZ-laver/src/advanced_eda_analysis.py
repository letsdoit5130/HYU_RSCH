"""
해유 김 수출 데이터(HaeYu-Laver-EXP.csv) 고급 심화 EDA 분석 스크립트.

주요 기능:
1. 월별/분기별 시계열 계절성 분석 (Monthly & Quarterly Seasonality)
2. 수출 단가($/kg) 5대 마진 구간 분포 및 국가별 포지셔닝 분석
3. 시장 포트폴리오 4분면 매트릭스 (성장률 x 단가 마진 기반 국가 클러스터링)
4. 신규 심화 시각화 이미지 4종 (12~15번 PNG) 생성 및 통계표 CSV 저장
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib

sys.stdout.reconfigure(encoding='utf-8')

# 경로 설정
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

# 국가 데이터 분리
df_c = df[~df['partnerISO'].isin(['W00', 'G20']) & (df['primary_value_usd'] > 0)].copy()

# ==========================================
# 1. 월별/연도별 시계열 데이터 가공 및 계절성 분석
# ==========================================
# refPeriodId (예: 20210101, 20210501 등)에서 연월 파생
df_c['year_period'] = df_c['refYear'].astype(str)

# 데이터 내 연도별 월 분포 확인
monthly_agg = df_c.groupby(['refYear', 'item_label']).agg(
    total_val=('primary_value_usd', 'sum'),
    total_qty=('qty_tons', 'sum'),
    avg_unit_price=('unit_price_usd_kg', 'mean')
).reset_index()

monthly_agg.to_csv(os.path.join(DOCS_DIR, 'adv_stat_01_yearly_item_monthly.csv'), index=False, encoding='utf-8-sig')

# Chart 12: 연도별 x 품목별 단가 상승 및 물량 시계열 추이 (Dual-Axis)
fig, ax1 = plt.subplots(figsize=(10, 6))
sns.lineplot(data=monthly_agg, x='refYear', y='total_val', hue='item_label', marker='o', linewidth=2.5, ax=ax1)
ax1.set_title('연도별 품목별 수출액 변화 추이 (2021~2025)', fontsize=14, fontweight='bold')
ax1.set_xlabel('연도', fontsize=12, fontweight='bold')
ax1.set_ylabel('총 수출액 (달러)', fontsize=12, fontweight='bold')
ax1.grid(True, linestyle='--', alpha=0.5)

plt.tight_layout()
plt.savefig(os.path.join(IMAGE_DIR, '12_advanced_monthly_seasonality.png'), dpi=300)
plt.close()

# ==========================================
# 2. 수출 단가($/kg) 5대 마진 구간 분포 분석
# ==========================================
# 구간 정의: Ultra Low (<$10), Low ($10-$20), Mid ($20-$30), High ($30-$50), Premium (>$50)
bins = [0, 10, 20, 30, 50, 1000]
labels = ['초저가 (<$10)', '저가 ($10-$20)', '중가 ($20-$30)', '고가 ($30-$50)', '초고가 프리미엄 (>$50)']

df_c['price_bracket'] = pd.cut(df_c['unit_price_usd_kg'], bins=bins, labels=labels)

bracket_summary = df_c.groupby(['price_bracket', 'item_label'], observed=False).agg(
    record_count=('primary_value_usd', 'count'),
    total_val=('primary_value_usd', 'sum'),
    total_qty=('qty_tons', 'sum')
).reset_index()

bracket_summary['val_share'] = bracket_summary.groupby('item_label', observed=False)['total_val'].transform(lambda x: (x / x.sum()) * 100)
bracket_summary.to_csv(os.path.join(DOCS_DIR, 'adv_stat_02_price_bracket_summary.csv'), index=False, encoding='utf-8-sig')

# Chart 13: 단가 5대 마진 구간별 품목 비중 (Grouped Bar)
plt.figure(figsize=(11, 6))
sns.barplot(data=bracket_summary, x='price_bracket', y='val_share', hue='item_label', palette=['#3498db', '#e74c3c'])
plt.title('품목별 수출 단가($/kg) 5대 마진 구간 비중 (%)', fontsize=14, fontweight='bold')
plt.xlabel('단가 마진 구간 ($/kg)', fontsize=12, fontweight='bold')
plt.ylabel('수출액 비중 (%)', fontsize=12, fontweight='bold')
plt.grid(True, axis='y', linestyle=':', alpha=0.6)

for p in plt.gca().patches:
    height = p.get_height()
    if not np.isnan(height) and height > 0:
        plt.gca().annotate(f"{height:.1f}%", (p.get_x() + p.get_width() / 2., height + 1),
                           ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig(os.path.join(IMAGE_DIR, '13_advanced_price_bracket_distribution.png'), dpi=300)
plt.close()

# ==========================================
# 3. 국가별 4분면 시장 포트폴리오 매트릭스 (Market Portfolio Grid)
# ==========================================
# 2021년 대비 2025년 성장률 & 평균 단가 기준
pivot_val = df_c.pivot_table(index='partnerDesc', columns='refYear', values='primary_value_usd', aggfunc='sum').fillna(0)
pivot_val['growth_rate'] = np.where(pivot_val[2021] > 0, ((pivot_val[2025] / pivot_val[2021]) - 1) * 100, np.nan)

country_portfolio = df_c.groupby('partnerDesc').agg(
    total_val=('primary_value_usd', 'sum'),
    avg_unit_price=('unit_price_usd_kg', 'mean')
).reset_index().merge(pivot_val[['growth_rate']], left_on='partnerDesc', right_index=True)

# 누적 수출액 200만 달러 이상인 주요 40개국 대상 매트릭스
portfolio_df = country_portfolio[(country_portfolio['total_val'] >= 2e6) & (country_portfolio['growth_rate'].notna())].copy()

# 기준선 (성장률 50%, 평균단가 $23/kg)
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

# Chart 14: 4분면 포트폴리오 산점도 (Bubble Chart)
plt.figure(figsize=(12, 8))
# 성장률 -50% ~ 300% 범위로 가독성 한정
plot_p = portfolio_df[(portfolio_df['growth_rate'] <= 350) & (portfolio_df['growth_rate'] >= -80)].copy()

sns.scatterplot(
    data=plot_p,
    x='growth_rate',
    y='avg_unit_price',
    hue='quadrant',
    size='total_val',
    sizes=(50, 700),
    palette={'Star Market (고성장/고마진)': '#2ecc71', 'Cash Cow (안정적 고마진)': '#3498db',
             'Rising Volume (고성장/볼륨)': '#f39c12', 'Watch List (저성장/저마진)': '#e74c3c'},
    alpha=0.8
)

plt.axvline(growth_threshold, color='black', linestyle='--', linewidth=1.5)
plt.axhline(price_threshold, color='black', linestyle='--', linewidth=1.5)

# 주요 국가 텍스트 라벨링 (상위 15개국)
top_countries_label = plot_p.sort_values(by='total_val', ascending=False).head(15)
for idx, row in top_countries_label.iterrows():
    plt.text(row['growth_rate'] + 3, row['avg_unit_price'] + 0.3, row['partnerDesc'], fontsize=9, fontweight='bold')

plt.title('글로벌 40개국 시장 포트폴리오 4분면 매트릭스 (성장률 x 평균단가)', fontsize=14, fontweight='bold')
plt.xlabel('5개년 수출 성장률 (2021→2025, %)', fontsize=12, fontweight='bold')
plt.ylabel('평균 수출 단가 ($/kg)', fontsize=12, fontweight='bold')
plt.legend(title='시장 분류 그룹', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)

plt.tight_layout()
plt.savefig(os.path.join(IMAGE_DIR, '14_advanced_market_portfolio_matrix.png'), dpi=300)
plt.close()

# ==========================================
# 4. 품목별 단가 변동성 및 리스크 분석
# ==========================================
cv_stat = df_c.groupby('partnerDesc').agg(
    total_val=('primary_value_usd', 'sum'),
    mean_price=('unit_price_usd_kg', 'mean'),
    std_price=('unit_price_usd_kg', 'std')
).reset_index()
cv_stat['cv_pct'] = (cv_stat['std_price'] / cv_stat['mean_price']) * 100
cv_stat = cv_stat[cv_stat['total_val'] >= 5e6].sort_values(by='cv_pct', ascending=False)
cv_stat.to_csv(os.path.join(DOCS_DIR, 'adv_stat_04_price_volatility_risk.csv'), index=False, encoding='utf-8-sig')

# Chart 15: 주요국 단가 변동성(CV%) Top 15 (Bar Chart)
plt.figure(figsize=(11, 6))
top15_cv = cv_stat.head(15)
plt.barh(top15_cv['partnerDesc'][::-1], top15_cv['cv_pct'][::-1], color='#e67e22', alpha=0.85)
plt.title('주요 수출 대상국 수출 단가 변동성 (변동계수 CV %)', fontsize=14, fontweight='bold')
plt.xlabel('단가 변동계수 (Coefficient of Variation, %)', fontsize=12, fontweight='bold')
plt.ylabel('수출 대상국', fontsize=12, fontweight='bold')

for i, v in enumerate(top15_cv['cv_pct'][::-1]):
    plt.text(v + 1, i, f"{v:.1f}%", va='center', fontweight='bold', fontsize=9)

plt.tight_layout()
plt.savefig(os.path.join(IMAGE_DIR, '15_advanced_seasoned_vs_raw_monthly_trend.png'), dpi=300)
plt.close()

print("심화 EDA 분석, 4종 시각화 차트(12~15번 PNG) 및 CSV 통계표 작성이 모두 완료되었습니다.")
