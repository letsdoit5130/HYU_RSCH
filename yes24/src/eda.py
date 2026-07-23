"""
YES24 베스트셀러 데이터 탐색적 데이터 분석 (EDA) 및 시각화

이 모듈은 수집된 YES24 베스트셀러 데이터인 bestsellers.csv 파일을 로드하여
데이터 전처리를 수행하고, 다양한 비즈니스 인사이트를 도출하기 위한 시각화 그래프들을 생성합니다.
시각화 결과 이미지는 yes24/images 디렉토리에 저장됩니다.

- 분석 및 시각화 항목:
  1. 베스트셀러 점유율 상위 10개 출판사 분석 (막대 그래프)
  2. 수치형 데이터(정가, 할인가, 할인율, 판매지수, 리뷰건수, 평점) 간의 상관관계 분석 (상관관계 열지도)
  3. 도서 정가 및 할인가 분포 분석 (히스토그램 및 밀도)
  4. 할인율 유형 분포 분석 (막대 그래프)
  5. 도서 태그 키워드 빈도 분석 (워드클라우드)

작성일: 2026-07-12
"""

import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter

def set_korean_font():
    """Matplotlib 한글 깨짐 방지를 위해 시스템 한글 폰트(맑은 고딕)를 설정합니다."""
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False
    # 그래프 스타일 설정
    sns.set_theme(style="whitegrid", font="Malgun Gothic")

def run_eda():
    """YES24 베스트셀러 데이터를 로드하여 전처리 및 EDA 시각화를 수행합니다."""
    # 1. 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, "..", "data", "bestsellers.csv")
    images_dir = os.path.join(current_dir, "..", "images")
    os.makedirs(images_dir, exist_ok=True)
    
    if not os.path.exists(data_path):
        print(f"데이터 파일이 존재하지 않습니다: {data_path}")
        return
        
    print("1. 데이터를 불러오는 중...")
    df = pd.read_csv(data_path, encoding="utf-8-sig")
    print(f"데이터 로드 완료: 총 {len(df)}개 도서 정보")
    
    # 2. 데이터 전처리 및 수치형 변환
    print("2. 데이터 전처리 수행 중...")
    df['정가'] = pd.to_numeric(df['정가'], errors='coerce')
    df['할인가'] = pd.to_numeric(df['할인가'], errors='coerce')
    df['할인율'] = pd.to_numeric(df['할인율'], errors='coerce')
    df['판매지수'] = pd.to_numeric(df['판매지수'], errors='coerce')
    df['리뷰건수'] = pd.to_numeric(df['리뷰건수'], errors='coerce').fillna(0)
    df['평점'] = pd.to_numeric(df['평점'], errors='coerce').fillna(0.0)
    
    # 한글 폰트 설정 적용
    set_korean_font()
    
    # -------------------------------------------------------------
    # 시각화 1: Top 10 출판사 분석
    # -------------------------------------------------------------
    print("3-1. Top 10 출판사 시각화 작성 중...")
    plt.figure(figsize=(12, 6))
    top_publishers = df['출판사'].value_counts().head(10)
    
    sns.barplot(x=top_publishers.values, y=top_publishers.index, palette="viridis")
    plt.title("YES24 베스트셀러 점유율 상위 10개 출판사", fontsize=16, fontweight='bold', pad=15)
    plt.xlabel("베스트셀러 등록 도서 수 (권)", fontsize=12)
    plt.ylabel("출판사명", fontsize=12)
    plt.tight_layout()
    
    pub_chart_path = os.path.join(images_dir, "top_publishers.png")
    plt.savefig(pub_chart_path, dpi=300)
    plt.close()
    print(f"출판사 차트 저장 완료: {pub_chart_path}")
    
    # -------------------------------------------------------------
    # 시각화 2: 수치형 변수 간 상관관계 열지도 (Heatmap)
    # -------------------------------------------------------------
    print("3-2. 수치형 지표 상관관계 열지도 작성 중...")
    plt.figure(figsize=(8, 6))
    numeric_cols = ['정가', '할인가', '할인율', '판매지수', '리뷰건수', '평점']
    corr_matrix = df[numeric_cols].corr()
    
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, annot_kws={"size": 10})
    plt.title("YES24 베스트셀러 주요 지표 간 상관관계", fontsize=14, fontweight='bold', pad=15)
    plt.tight_layout()
    
    heatmap_chart_path = os.path.join(images_dir, "correlation_heatmap.png")
    plt.savefig(heatmap_chart_path, dpi=300)
    plt.close()
    print(f"상관관계 열지도 저장 완료: {heatmap_chart_path}")
    
    # -------------------------------------------------------------
    # 시각화 3: 가격 분포 분석 (정가 및 할인가 비교)
    # -------------------------------------------------------------
    print("3-3. 도서 가격 분포 차트 작성 중...")
    plt.figure(figsize=(10, 6))
    
    # 아웃라이어(비정상 가격 도서) 제외를 위해 5만원 이하 데이터 중심 분석
    filtered_prices = df[(df['정가'] <= 50000) & (df['정가'] > 0)]
    
    sns.histplot(data=filtered_prices, x='정가', kde=True, color='skyblue', label='정가', alpha=0.6, bins=30)
    sns.histplot(data=filtered_prices, x='할인가', kde=True, color='salmon', label='할인가', alpha=0.6, bins=30)
    
    plt.title("도서 가격 분포 분석 (정가 vs 할인가, 5만원 이하)", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("가격 (원)", fontsize=12)
    plt.ylabel("도서 빈도 수 (권)", fontsize=12)
    plt.legend()
    plt.tight_layout()
    
    price_chart_path = os.path.join(images_dir, "price_distribution.png")
    plt.savefig(price_chart_path, dpi=300)
    plt.close()
    print(f"가격 분포 차트 저장 완료: {price_chart_path}")

    # -------------------------------------------------------------
    # 시각화 4: 할인율 분포 분석
    # -------------------------------------------------------------
    print("3-4. 할인율 분포 차트 작성 중...")
    plt.figure(figsize=(8, 5))
    
    # 할인율을 문자형으로 변환하여 범주형 그래프로 표현 (0, 5, 10 등 명확한 할인율 위주)
    discount_counts = df['할인율'].dropna().value_counts().sort_index()
    
    sns.barplot(x=discount_counts.index.astype(int), y=discount_counts.values, palette="crest")
    plt.title("YES24 베스트셀러 도서 할인율 빈도", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("할인율 (%)", fontsize=12)
    plt.ylabel("도서 수 (권)", fontsize=12)
    
    # 각 막대 위에 값 표시
    for i, val in enumerate(discount_counts.values):
        plt.text(i, val + 5, f"{val}권", ha='center', fontsize=9)
        
    plt.tight_layout()
    
    discount_chart_path = os.path.join(images_dir, "discount_rates.png")
    plt.savefig(discount_chart_path, dpi=300)
    plt.close()
    print(f"할인율 차트 저장 완료: {discount_chart_path}")

    # -------------------------------------------------------------
    # 시각화 5: 태그(해시태그) 워드클라우드
    # -------------------------------------------------------------
    print("3-5. 태그 빈도 분석 및 워드클라우드 작성 중...")
    
    # 태그 컬럼에서 해시태그 키워드 추출
    all_tags = []
    for tag_str in df['태그'].dropna():
        # '#태그명' 형태 분할
        tags = [t.strip().replace('#', '') for t in tag_str.split(',') if t.strip()]
        all_tags.extend(tags)
        
    tag_counts = Counter(all_tags)
    
    if len(tag_counts) > 0:
        # Windows 기본 한글 폰트 경로 (맑은 고딕)
        font_path = "C:/Windows/Fonts/malgun.ttf"
        if not os.path.exists(font_path):
            font_path = "C:/Windows/Fonts/malgunbd.ttf"  # 맑은 고딕 Bold
            
        wc = WordCloud(
            font_path=font_path,
            width=800,
            height=400,
            background_color="white",
            colormap="Dark2",
            max_words=100
        ).generate_from_frequencies(tag_counts)
        
        plt.figure(figsize=(12, 6))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.title("YES24 베스트셀러 도서 주요 태그 키워드", fontsize=16, fontweight='bold', pad=15)
        plt.tight_layout()
        
        wc_chart_path = os.path.join(images_dir, "tag_wordcloud.png")
        plt.savefig(wc_chart_path, dpi=300)
        plt.close()
        print(f"워드클라우드 저장 완료: {wc_chart_path}")
    else:
        print("분석할 태그 데이터가 없어 워크클라우드 생성을 건너뜁니다.")
        
    print("\n[성공] 모든 시각화 결과물이 yes24/images 디렉토리에 성공적으로 저장되었습니다.")

if __name__ == "__main__":
    run_eda()
