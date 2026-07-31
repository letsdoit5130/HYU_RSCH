"""
해유 김 수출 데이터(HaeYu-Laver-EXP.csv) 기초 탐색 및 데이터 파악 스크립트.

주요 기능:
- 데이터 로드 (인코딩 자동 감지)
- 데이터 크기, Head/Tail, Info, 결측치, 중복값 확인
- 수치형 및 범주형 기술통계 확인
"""
import pandas as pd
import numpy as np

# 데이터 로드
file_path = 'BIZ-laver/data/HaeYu-Laver-EXP.csv'

# encoding 테스트 및 로드
try:
    df = pd.read_csv(file_path, encoding='utf-8')
except UnicodeDecodeError:
    try:
        df = pd.read_csv(file_path, encoding='cp949')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='euc-kr')

print("=== 1. DATA SHAPE ===")
print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

print("\n=== 2. HEAD 5 ===")
print(df.head())

print("\n=== 3. TAIL 5 ===")
print(df.tail())

print("\n=== 4. INFO ===")
df.info()

print("\n=== 5. MISSING VALUES ===")
print(df.isnull().sum())

print("\n=== 6. DUPLICATES ===")
print(f"Duplicated rows: {df.duplicated().sum()}")

print("\n=== 7. NUMERICAL DESCRIBE ===")
print(df.describe())

print("\n=== 8. CATEGORICAL DESCRIBE ===")
categorical_cols = df.select_dtypes(include=['object', 'category']).columns
if len(categorical_cols) > 0:
    print(df.describe(include=['object', 'category']))
else:
    print("No categorical columns found by default type.")

print("\n=== 9. UNIQUE VALUES PER COLUMN ===")
for col in df.columns:
    print(f"{col}: {df[col].nunique()} unique values, sample: {df[col].unique()[:5]}")
