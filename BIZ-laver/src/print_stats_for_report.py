"""
생성된 통계 CSV 파일들을 읽어 마크다운 보고서에 삽입할 텍스트 표와 숫자 수치를 출력하는 스크립트.
"""

import os
import pandas as pd

DOCS_DIR = 'BIZ-laver/docs'

for filename in sorted(os.listdir(DOCS_DIR)):
    if filename.endswith('.csv'):
        filepath = os.path.join(DOCS_DIR, filename)
        print(f"\n==================== {filename} ====================")
        df = pd.read_csv(filepath)
        print(df.to_markdown(index=False))

with open(os.path.join(DOCS_DIR, 'initial_exploration_summary.txt'), 'r', encoding='utf-8') as f:
    print("\n==================== initial_exploration_summary.txt ====================")
    print(f.read())
