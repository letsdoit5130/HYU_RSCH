"""
BIZ-JB-Gathered.csv 전복 무역 데이터 고도화 추가 EDA 및 시각화 스크립트

이 스크립트는 6가지 추가 고급 분석 과제(월별 계절성, 운송수단별 물류 분석,
삼각무역/재수출 네트워크, 가격 변동성/이상치 감지, 세관/무역수지, 국가x품목 군집분석)를
수행하여 BIZ-Jeonbok/images/ 폴더에 12~17번 차트 이미지(.png)로 저장합니다.
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# 1. 디렉토리 설정
os.makedirs("BIZ-Jeonbok/images", exist_ok=True)
os.makedirs("BIZ-Jeonbok/reports", exist_ok=True)

# 2. 데이터 로드 및 정제
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

print("--- ADVANCED EDA START ---")

# -------------------------------------------------------------
# Chart 12: 계절성 및 월별 변동 분석 (refMonth)
# -------------------------------------------------------------
plt.figure(figsize=(10, 5))
monthly_agg = df.groupby('refMonth').agg(
    avg_price=('unit_price_num', 'mean'),
    total_val=('primaryValue_num', 'sum'),
    count=('period', 'count')
).reset_index()

# 월별 데이터가 0월만 기재되었거나 구분된 경우 처리
if len(monthly_agg) > 1 and not (monthly_agg['refMonth'] == 0).all():
    monthly_df = monthly_agg[monthly_agg['refMonth'] > 0]
    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.bar(monthly_df['refMonth'].astype(str) + '월', monthly_df['total_val'] / 1e6, color='#3498db', alpha=0.7, label='월별 총 무역액 (백만 달러)')
    ax1.set_xlabel('월 (Month)', fontsize=11)
    ax1.set_ylabel('총 무역액 (백만 USD)', color='#3498db', fontsize=11)
    ax1.grid(axis='y', linestyle='--', alpha=0.5)

    ax2 = ax1.twinx()
    ax2.plot(monthly_df['refMonth'].astype(str) + '월', monthly_df['avg_price'], color='#e74c3c', marker='o', linewidth=2.5, label='평균 단가 ($/kg)')
    ax2.set_ylabel('평균 단가 ($/kg)', color='#e74c3c', fontsize=11)

    plt.title('월별(refMonth) 전복 무역액 및 평균 단가 계절성 추이', fontsize=14, pad=12)
    fig.tight_layout()
    plt.savefig('BIZ-Jeonbok/images/12_monthly_seasonality.png', dpi=300)
    plt.close()
else:
    # 연도별-분기별 대체 시각화 (refPeriodId 또는 refYear 기준)
    plt.figure(figsize=(9, 5))
    year_agg = df.groupby('refYear')['primaryValue_num'].agg(['mean', 'median', 'sum']).reset_index()
    plt.plot(year_agg['refYear'].astype(str), year_agg['mean'], marker='o', label='평균 무역액 ($)', color='#2980b9')
    plt.plot(year_agg['refYear'].astype(str), year_agg['median'], marker='s', label='중앙 무역액 ($)', color='#27ae60')
    plt.title('연도별 무역액 평균 및 중앙값 비교 (계절성 대체)', fontsize=14, pad=12)
    plt.xlabel('연도', fontsize=11)
    plt.ylabel('무역액 (USD)', fontsize=11)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('BIZ-Jeonbok/images/12_monthly_seasonality.png', dpi=300)
    plt.close()

# -------------------------------------------------------------
# Chart 13: 운송 수단(motDesc)별 물류 및 단가 프리미엄 분석
# -------------------------------------------------------------
plt.figure(figsize=(9, 5))
mot_counts = df['motDesc'].value_counts()
if len(mot_counts) > 1 and not (mot_counts.index == 'N/A').all():
    mot_df = df.groupby('motDesc').agg(
        count=('period', 'count'),
        avg_price=('unit_price_num', 'mean'),
        total_weight=('netWgt_num', 'sum')
    ).reset_index()
    sns.barplot(data=mot_df, x='motDesc', y='avg_price', palette='Blues_d')
    plt.title('운송 수단(motDesc)별 전복 평균 단가 ($/kg) 비교', fontsize=14, pad=12)
    plt.xlabel('운송 수단', fontsize=11)
    plt.ylabel('평균 단가 ($/kg)', fontsize=11)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
else:
    # customsDesc (세관/관세 방식) 수단 대체 분석
    customs_top10 = df['customsDesc'].value_counts().head(10)
    plt.barh(customs_top10.index[::-1], customs_top10.values[::-1], color='#8e44ad')
    plt.title('상위 세관/통관 방식(customsDesc) 분포 (운송수단 대체)', fontsize=14, pad=12)
    plt.xlabel('거래 건수', fontsize=11)
    plt.grid(axis='x', linestyle='--', alpha=0.7)

plt.tight_layout()
plt.savefig('BIZ-Jeonbok/images/13_mot_transport_analysis.png', dpi=300)
plt.close()

# -------------------------------------------------------------
# Chart 14: 삼각 무역 및 2차 파트너국(partner2Desc) 네트워크
# -------------------------------------------------------------
plt.figure(figsize=(10, 6))
p2_counts = df['partner2Desc'].value_counts().head(15)
plt.barh(p2_counts.index[::-1], p2_counts.values[::-1], color='#e67e22')
plt.title('상위 15개 2차 파트너/경유 국가 (partner2Desc)', fontsize=14, pad=12)
plt.xlabel('거래 건수', fontsize=11)
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('BIZ-Jeonbok/images/14_reexport_partner2_hub.png', dpi=300)
plt.close()

# -------------------------------------------------------------
# Chart 15: 국가별 단가 변동계수(CV) 및 이상치 탐지
# -------------------------------------------------------------
plt.figure(figsize=(10, 6))
top_reporters = df['reporterDesc'].value_counts().head(15).index
cv_list = []
for rep in top_reporters:
    prices = df[df['reporterDesc'] == rep]['unit_price_num'].dropna()
    if len(prices) > 5 and prices.mean() > 0:
        cv = prices.std() / prices.mean()
        cv_list.append({'reporter': rep, 'cv': cv, 'mean_price': prices.mean()})

cv_df = pd.DataFrame(cv_list).sort_values(by='cv', ascending=True)
plt.barh(cv_df['reporter'], cv_df['cv'], color='#c0392b')
plt.title('주요 전복 무역 보고국별 단가 변동계수 (CV = Std/Mean)', fontsize=14, pad=12)
plt.xlabel('변동계수 (CV)', fontsize=11)
plt.grid(axis='x', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('BIZ-Jeonbok/images/15_price_volatility_anomaly.png', dpi=300)
plt.close()

# -------------------------------------------------------------
# Chart 16: 주요 국가별 무역 수지 및 거래 형태 비교
# -------------------------------------------------------------
plt.figure(figsize=(10, 6))
trade_balance = df.groupby(['reporterDesc', 'flowDesc'])['primaryValue_num'].sum().unstack().fillna(0)
top_trade_countries = df['reporterDesc'].value_counts().head(10).index
tb_top10 = trade_balance.loc[top_trade_countries] / 1e6  # 백만 달러

tb_top10.plot(kind='bar', stacked=True, figsize=(10, 6), color=['#27ae60', '#2980b9'])
plt.title('상위 10개 보고국별 수출입 총 무역액 규모 (백만 USD)', fontsize=14, pad=12)
plt.xlabel('보고 국가', fontsize=11)
plt.ylabel('무역액 (백만 USD)', fontsize=11)
plt.xticks(rotation=45, ha='right')
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig('BIZ-Jeonbok/images/16_customs_trade_balance.png', dpi=300)
plt.close()

# -------------------------------------------------------------
# Chart 17: 국가 x 품목 군집 분석 (K-Means Clustering)
# -------------------------------------------------------------
plt.figure(figsize=(9, 6))
country_cmd_pivot = pd.crosstab(df['reporterDesc'], df['cmdCode'], values=df['primaryValue_num'], aggfunc='sum').fillna(0)
country_cmd_norm = country_cmd_pivot.div(country_cmd_pivot.sum(axis=1), axis=0).fillna(0)

# K-Means (k=3)
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
clusters = kmeans.fit_predict(country_cmd_norm)
country_cmd_norm['Cluster'] = clusters

# 시각화 (PCA 또는 주요 2개 수치 기반)
from sklearn.decomposition import PCA
pca = PCA(n_components=2)
pca_res = pca.fit_transform(country_cmd_norm.drop(columns=['Cluster']))

plt.scatter(pca_res[:, 0], pca_res[:, 1], c=clusters, cmap='viridis', s=100, alpha=0.8)
for i, country in enumerate(country_cmd_norm.index):
    plt.annotate(country[:10], (pca_res[i, 0], pca_res[i, 1]), fontsize=8, alpha=0.7)

plt.title('국가별 전복 품목 포트폴리오 군집 분석 (K-Means Clustering)', fontsize=14, pad=12)
plt.xlabel('주성분 1 (PCA 1)', fontsize=11)
plt.ylabel('주성분 2 (PCA 2)', fontsize=11)
plt.grid(True, linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig('BIZ-Jeonbok/images/17_country_cmd_clustering.png', dpi=300)
plt.close()

print("--- ALL ADVANCED CHARTS (12~17) GENERATED SUCCESSFULLY ---")
