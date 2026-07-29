"""
BIZ-JB-Gathered.csv 데이터셋 기초 탐색 스크립트 (BIZ-Jeonbok 하위 전용)

이 스크립트는 BIZ-Jeonbok/data/BIZ-JB-Gathered.csv 전복 모은 데이터셋의 행/열 크기,
데이터 타입, 결측치, 중복값, 수치형/범주형 기술통계 요약을 확인하기 위해 작성되었습니다.
"""

import os
import pandas as pd
import numpy as np

file_path = "BIZ-Jeonbok/BIZ-JB-Gathered.csv"
if not os.path.exists(file_path):
    file_path = "BIZ-Jeonbok/data/BIZ-JB-Gathered.csv"

# 파일 읽기
try:
    df = pd.read_csv(file_path, encoding='utf-8-sig')
except Exception:
    try:
        df = pd.read_csv(file_path, encoding='cp949')
    except Exception:
        df = pd.read_csv(file_path, encoding='euc-kr')

print("--- DATA SHAPE ---")
print(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")

print("\n--- COLUMNS & TYPES ---")
print(df.dtypes)

print("\n--- HEAD 5 ---")
print(df.head(5))

print("\n--- TAIL 5 ---")
print(df.tail(5))

print("\n--- MISSING VALUES ---")
print(df.isnull().sum())

print("\n--- DUPLICATED ROWS ---")
print(f"Duplicated: {df.duplicated().sum()}")

print("\n--- DESCRIBE NUMERICAL ---")
print(df.describe())

print("\n--- DESCRIBE CATEGORICAL ---")
print(df.describe(include=['str', 'object', 'category']))
