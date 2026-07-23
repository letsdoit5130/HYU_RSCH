"""
탐색적 데이터 분석(EDA) 및 마크다운 리포트 생성 스크립트 (eda.py)

이 프로그램은 수집된 원시 CSV 데이터를 정제 및 정량 분석하여,
비즈니스 인사이트 도출을 위한 시각화 차트 이미지와 종합 마크다운 리포트를 자동 생성합니다.

작성일: 2026-07-23
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib

def run_analysis(data_csv_path: str = "data/raw_data.csv", output_report_path: str = "docs/eda_report.md"):
    print("[EDA] 탐색적 데이터 분석을 시작합니다...")
    if not os.path.exists(data_csv_path):
        print(f"[EDA ERROR] 원시 데이터가 존재하지 않습니다: {data_csv_path}")
        return
        
    df = pd.read_csv(data_csv_path, encoding="utf-8-sig")
    print(f" - 데이터 분석 대상: {df.shape[0]}행, {df.shape[1]}열")
    
    images_dir = os.path.join(os.path.dirname(output_report_path), "..", "images")
    os.makedirs(images_dir, exist_ok=True)
    chart_path = os.path.join(images_dir, "summary_chart.png")
    
    plt.figure(figsize=(10, 6))
    plt.title("수집 데이터 요약 분포 차트")
    plt.bar(["전체 데이터 수"], [len(df)], color="#0284c7")
    plt.savefig(chart_path, dpi=300, bbox_inches="tight")
    plt.close()
    
    os.makedirs(os.path.dirname(output_report_path), exist_ok=True)
    with open(output_report_path, "w", encoding="utf-8") as f:
        f.write("# 📊 탐색적 데이터 분석(EDA) 및 비즈니스 리포트\n\n")
        f.write(f"- **총 수집 건수**: {len(df)}건\n")
        f.write(f"- **컬럼 목록**: {list(df.columns)}\n\n")
        f.write("## 시각화 요약\n\n")
        f.write("![요약 차트](../images/summary_chart.png)\n")
        
    print(f"[EDA COMPLETED] 분석 리포트 및 이미지 저장 완료 -> {output_report_path}")

if __name__ == "__main__":
    run_analysis()
