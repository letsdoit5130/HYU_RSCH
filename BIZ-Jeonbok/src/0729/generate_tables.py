"""
BIZ-JB-Gathered.csv EDA 통계표 및 표 데이터 수집 스크립트 (BIZ-Jeonbok 하위 전용)

이 스크립트는 BIZ-Jeonbok 하위의 EDA 리포트(BIZ-Jeonbok/reports/EDA_Report.md) 작성을 위해
각 차트 및 기술통계에 해당하는 정확한 피봇테이블, 교차표,
기술통계 요약 수치, TF-IDF 상위 30개 키워드 표를 출력합니다.
"""

import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

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
df['cifvalue_num'] = df['cifvalue'].apply(clean_currency)
df['fobvalue_num'] = df['fobvalue'].apply(clean_currency)
df['netWgt_num'] = df['netWgt'].apply(clean_currency)
unit_price_col = [c for c in df.columns if 'Unit Price' in c][0]
df['unit_price_num'] = df[unit_price_col].apply(clean_currency)

print("=== 1. 수치형 기술통계 (df.describe()) ===")
num_cols = ['refYear', 'primaryValue_num', 'netWgt_num', 'grossWgt', 'unit_price_num', 'cifvalue_num', 'fobvalue_num']
print(df[num_cols].describe().to_markdown())

print("\n=== 2. 범주형 기술통계 (df.describe(include=['str', 'object'])) ===")
cat_cols = ['reporterDesc', 'partnerDesc', 'flowDesc', 'cmdCode', 'cmdDesc', 'qtyUnitAbbr']
print(df[cat_cols].astype(str).describe().to_markdown())
