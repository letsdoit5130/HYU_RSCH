"""
교보문고 베스트셀러 탐색적 데이터 분석 (EDA) 및 시각화 (py-eda 스킬 규칙 준수 버전)

이 모듈은 수집된 교보문고 베스트셀러 데이터인 bestsellers.csv 파일을 로드하여
데이터 전처리를 수행하고, 데이터 기반의 다양한 인사이트를 시각화 이미지로 생성합니다.
koreanize-matplotlib를 사용하여 한글 폰트를 연동하고,
Seaborn 전역 테마 설정을 사용하지 않고 차트별 세부 설정을 수행합니다.

분석 및 시각화 항목:
1. 베스트셀러 점유율 상위 10개 출판사 분석 (막대 그래프)
2. 수치형 지표(정가, 할인가, 할인율, 리뷰건수, 평점) 간의 상관관계 (상관관계 열지도)
3. 도서 가격 분포 분석 (정가 vs 할인가 히스토그램)
4. 도서 할인율 빈도 분포 (막대 그래프)
5. 도서 분야(태그) 키워드 빈도 분석 (워드클라우드)
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib  # py-eda 한글 폰트 연동 규칙 준수
from wordcloud import WordCloud
from collections import Counter
import io

def run_eda():
    # 경로 설정
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(current_dir)
    data_path = os.path.join(project_dir, "data", "bestsellers.csv")
    images_dir = os.path.join(project_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    if not os.path.exists(data_path):
        print(f"데이터 파일이 존재하지 않습니다: {data_path}")
        return
        
    print("1. 데이터를 불러오는 중...")
    df = pd.read_csv(data_path, encoding="utf-8-sig")
    
    # -------------------------------------------------------------
    # py-eda 규칙 2: 데이터 탐색 기초 출력 및 무결성 진단
    # -------------------------------------------------------------
    print("\n" + "="*50)
    print(" py-eda 데이터 탐색 기초 진단 보고")
    print("="*50)
    print(f"- 데이터 크기 (행/열): {df.shape[0]}행 {df.shape[1]}열")
    print(f"- 중복된 데이터 행 수: {df.duplicated().sum()}건")
    
    print("\n[기본 정보 (info())]")
    buffer = io.StringIO()
    df.info(buf=buffer)
    print(buffer.getvalue())
    
    print("\n[원시 데이터 프리뷰 (상위 3행)]")
    print(df.head(3).to_string())
    print("\n[원시 데이터 프리뷰 (하위 3행)]")
    print(df.tail(3).to_string())
    
    # 2. 데이터 전처리 및 수치형 변환
    df['정가'] = pd.to_numeric(df['정가'], errors='coerce').fillna(0)
    df['할인가'] = pd.to_numeric(df['할인가'], errors='coerce').fillna(0)
    df['할인율'] = pd.to_numeric(df['할인율'], errors='coerce').fillna(0)
    df['리뷰건수'] = pd.to_numeric(df['리뷰건수'], errors='coerce').fillna(0)
    df['평점'] = pd.to_numeric(df['평점'], errors='coerce').fillna(0.0)
    
    # -------------------------------------------------------------
    # 시각화 1: Top 10 출판사 분석
    # -------------------------------------------------------------
    print("\n3-1. Top 10 출판사 시각화 작성 중...")
    plt.figure(figsize=(12, 6))
    top_publishers = df['출판사'].value_counts().head(10)
    
    # sns.set_theme() 전역 테마 설정을 호출하지 않고, 개별 차트 디테일 조정
    sns.barplot(x=top_publishers.values, y=top_publishers.index, hue=top_publishers.index, palette="viridis", legend=False)
    plt.title("교보문고 베스트셀러 점유율 상위 10개 출판사", fontsize=16, fontweight='bold', pad=15)
    plt.xlabel("베스트셀러 등록 도서 수 (권)", fontsize=12)
    plt.ylabel("출판사명", fontsize=12)
    plt.grid(True, axis='x', linestyle='--', alpha=0.5)  # 개별 그리드 조정
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
    numeric_cols = ['정가', '할인가', '할인율', '리뷰건수', '평점']
    corr_matrix = df[numeric_cols].corr()
    
    sns.heatmap(corr_matrix, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, annot_kws={"size": 10})
    plt.title("교보문고 베스트셀러 주요 지표 간 상관관계", fontsize=14, fontweight='bold', pad=15)
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
    
    # 아웃라이어(비정상 가격 도서) 제외를 위해 10만원 이하 데이터 중심 분석
    filtered_prices = df[(df['정가'] <= 100000) & (df['정가'] > 0)]
    
    sns.histplot(data=filtered_prices, x='정가', kde=True, color='skyblue', label='정가', alpha=0.6, bins=25)
    sns.histplot(data=filtered_prices, x='할인가', kde=True, color='salmon', label='할인가', alpha=0.6, bins=25)
    
    plt.title("도서 가격 분포 분석 (정가 vs 할인가)", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("가격 (원)", fontsize=12)
    plt.ylabel("도서 빈도 수 (권)", fontsize=12)
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
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
    
    discount_counts = df['할인율'].dropna().value_counts().sort_index()
    
    sns.barplot(x=discount_counts.index.astype(int), y=discount_counts.values, hue=discount_counts.index.astype(int), palette="crest", legend=False)
    plt.title("교보문고 베스트셀러 도서 할인율 빈도", fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("할인율 (%)", fontsize=12)
    plt.ylabel("도서 수 (권)", fontsize=12)
    plt.grid(True, axis='y', linestyle='--', alpha=0.5)
    
    # 각 막대 위에 값 표시
    for i, val in enumerate(discount_counts.values):
        plt.text(i, val + 0.2, f"{val}권", ha='center', fontsize=9)
        
    plt.tight_layout()
    
    discount_chart_path = os.path.join(images_dir, "discount_rates.png")
    plt.savefig(discount_chart_path, dpi=300)
    plt.close()
    print(f"할인율 차트 저장 완료: {discount_chart_path}")
    
    # -------------------------------------------------------------
    # 시각화 5: 분야(태그) 워드클라우드
    # -------------------------------------------------------------
    print("3-5. 도서 분야(태그) 빈도 분석 및 워드클라우드 작성 중...")
    
    all_tags = []
    for tag_str in df['태그'].dropna():
        tags = [t.strip() for t in tag_str.split(',') if t.strip()]
        all_tags.extend(tags)
        
    tag_counts = Counter(all_tags)
    
    if len(tag_counts) > 0:
        # Windows 기본 한글 폰트 경로 (맑은 고딕)
        font_path = "C:/Windows/Fonts/malgun.ttf"
        if not os.path.exists(font_path):
            font_path = "C:/Windows/Fonts/malgunbd.ttf"
            
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
        plt.title("교보문고 베스트셀러 주요 도서 분야(카테고리)", fontsize=16, fontweight='bold', pad=15)
        plt.tight_layout()
        
        wc_chart_path = os.path.join(images_dir, "tag_wordcloud.png")
        plt.savefig(wc_chart_path, dpi=300)
        plt.close()
        print(f"워드클라우드 저장 완료: {wc_chart_path}")
    else:
        print("분석할 태그 데이터가 없어 워크클라우드 생성을 건너뜁니다.")
        
    print("\n[성공] 모든 시각화 결과물이 KyoBooks/images 디렉토리에 성공적으로 저장되었습니다.")

if __name__ == "__main__":
    run_eda()
