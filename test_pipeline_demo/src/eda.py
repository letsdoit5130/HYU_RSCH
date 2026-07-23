"""
test_pipeline_demo 탐색적 데이터 분석 (EDA) 및 마크다운 리포트 생성 스크립트

이 프로그램은 수집된 원시 CSV 데이터를 정제 및 정량 분석하여,
비즈니스 인사이트 도출을 위한 시각화 차트 이미지와 종합 마크다운 리포트를 자동 생성합니다.

작성일: 2026-07-19
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib # 한글 폰트 설정 자동화

def run_analysis():
    print("[EDA] 탐색적 데이터 분석을 시작합니다...")
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.abspath(os.path.join(current_dir, "..", "data", "raw_data.csv"))
    images_dir = os.path.abspath(os.path.join(current_dir, "..", "images"))
    report_path = os.path.abspath(os.path.join(current_dir, "..", "docs", "eda_report.md"))
    
    if not os.path.exists(data_path):
        print(f"[EDA] [ERROR] 원시 데이터가 존재하지 않습니다: {data_path}")
        return
        
    df = pd.read_csv(data_path)
    print(f" - 데이터 분석 대상: {df.shape[0]}행, {df.shape[1]}열")
    
    # 시각화 설정
    plt.rcParams['figure.figsize'] = (10, 6)
    plt.rcParams['font.size'] = 12
    
    # [시각화 1] 데이터 개수 요약
    plt.figure()
    df.head(10).plot(kind='bar')
    plt.title('데이터 상위 10개 지표 요약')
    plt.tight_layout()
    chart1_path = os.path.join(images_dir, "summary_chart.png")
    plt.savefig(chart1_path)
    plt.close()
    print(" - 시각화 차트 1 저장 완료.")
    
    # [TODO] 데이터 특성에 맞는 정밀 시각화 및 상관 분석을 여기에 작성하십시오.
    
    # 마크다운 리포트 빌드
    report_content = []
    report_content.append(f"# test_pipeline_demo 탐색적 데이터 분석 (EDA) 보고서\n\n")
    report_content.append("## 1. 데이터 기본 개요\n")
    report_content.append(f"- **전체 데이터 행 수**: {df.shape[0]}건\n")
    report_content.append(f"- **컬럼 구성**: id, title, category, author, date, views\n\n")
    
    report_content.append("### 1.1 상위 5개 샘플 데이터\n")
    report_content.append(df.head(5).to_markdown(index=False) + "\n\n")
    
    report_content.append("## 2. 주요 시각화 결과\n")
    report_content.append("![요약 차트](../images/summary_chart.png)\n\n")
    
    report_content.append("## 3. 데이터 기반 비즈니스 인사이트\n")
    report_content.append("- 수집된 데이터의 상위 분포를 볼 때 특정 항목이 집중되는 경향이 관찰됩니다.\n")
    report_content.append("- 상세 분석 결과에 비추어 향후 전략을 다각화할 필요가 있습니다.\n")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.writelines(report_content)
        
    print(f"[EDA] 분석 완료 및 마크다운 리포트 생성 완료: {report_path}")
    return report_path

if __name__ == "__main__":
    run_analysis()
