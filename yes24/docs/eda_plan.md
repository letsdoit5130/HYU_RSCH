1# YES24 베스트셀러 데이터 EDA 구현 계획

이 문서는 [bestsellers.csv](../data/bestsellers.csv)에 수집된 877개의 도서 데이터를 바탕으로 탐색적 데이터 분석(EDA, Exploratory Data Analysis)을 수행하고 주요 인사이트를 시각화하여 저장하기 위한 개발 계획서입니다.

---

## Goal Description

수집된 베스트셀러 데이터에 대한 다각도 분석을 통해 유의미한 시장 인사이트를 도출합니다. 분석 결과 그래프(이미지)는 프로젝트 규칙에 따라 `yes24/images/` 디렉토리에 저장하며, 분석을 수행하는 전체 코드는 `yes24/src/eda.py`로 구현합니다.

---

## User Review Required
>
> [!IMPORTANT]
> **1. 시각화 한글 폰트 설정**
> Windows 환경에서 Matplotlib 시각화 시 한글이 깨지지 않도록 시스템 폰트인 **맑은 고딕(Malgun Gothic)**을 기본 적용하겠습니다.
>
> **2. 시각화 대상 선정 및 추가 분석**
> 현재 제안하는 분석 주제(출판사 분포, 판매지수 상관관계, 태그 분석 등) 외에 특별히 보고 싶으신 지표나 통계가 있다면 말씀해 주세요.

---

## Proposed Changes

### 1. 의존성 패키지 추가 설치

EDA 진행을 위해 다음 패키지들을 공통 가상환경(`.venv`)에 추가 설치합니다.

- `matplotlib`: 차트 생성 및 시각화 기본 프레임워크
- `seaborn`: 세련된 통계 시각화 및 Heatmap 구성
- `wordcloud`: 태그(해시태그) 빈도 분석을 위한 워드클라우드 이미지 생성

### 2. 소스 코드 추가 및 변경

#### [NEW] yes24/src/eda.py

데이터 분석 및 시각화를 전담하는 스크립트를 새로 작성합니다.

```python
"""
YES24 베스트셀러 데이터 탐색적 분석 및 시각화 (EDA)

이 모듈은 수집된 도서 데이터를 읽어 들여 기초 통계 분석을 수행하고,
주요 인사이트(출판사 점유율, 상관관계, 태그 분포 등)를 시각화하여 이미지로 저장합니다.

작성일: 2026-07-12
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter
import re

def set_korean_font():
    """Matplotlib 한글 깨짐 방지를 위해 시스템 한글 폰트(맑은 고딕)를 설정합니다."""
    plt.rcParams['font.family'] = 'Malgun Gothic'
    plt.rcParams['axes.unicode_minus'] = False

def run_eda():
    """
    EDA 메인 함수: 데이터를 로드하고 정제한 뒤 다음 5가지 시각화를 진행하여 
    yes24/images/ 폴더에 이미지로 보존합니다.
    """
    # 1. 데이터 로드
    # 2. 데이터 타입 변환 및 정제 (정가, 할인가, 판매지수, 평점 등 numeric 변환)
    # 3. 시각화 진행 및 저장:
    #    - Chart 1: 베스트셀러 진입 도서 수가 많은 Top 10 출판사 (막대 그래프)
    #    - Chart 2: 판매지수, 평점, 리뷰건수, 할인가, 할인율 간 상관관계 (Heatmap)
    #    - Chart 3: 정가 및 할인가 가격 분포 (밀도 및 히스토그램)
    #    - Chart 4: 할인율 분포 분석 (파이 차트 또는 막대 그래프)
    #    - Chart 5: 도서 태그(키워드) 빈도 분석 (Word Cloud)
    pass
```

#### [NEW] 시각화 이미지 생성 (yes24/images/)

분석 결과는 다음 이미지 파일로 생성되어 저장됩니다.

- `yes24/images/top_publishers.png`: 베스트셀러 점유율 상위 10개 출판사
- `yes24/images/correlation_heatmap.png`: 주요 지표 간 상관관계 열지도
- `yes24/images/price_distribution.png`: 가격 분포 히스토그램
- `yes24/images/discount_rates.png`: 할인율 분포
- `yes24/images/tag_wordcloud.png`: 태그 빈도 워드클라우드

---

## Verification Plan

### Automated Tests

- 패키지 설치 확인: `uv pip list`를 수행하여 `matplotlib`, `seaborn`, `wordcloud`가 가상환경에 설치되어 있는지 확인합니다.
- 분석 스크립트 실행: `uv run yes24/src/eda.py` 명령어를 통해 실행 오류(타입 오류, 폰트 깨짐 등)가 없는지 검증합니다.

### Manual Verification

- `yes24/images/` 폴더에 시각화 차트 이미지 5종이 잘 생성되었는지 확인합니다.
- 차트 이미지들을 열어서 한글 깨짐 현상이 없는지, 차트 눈금과 레이블이 겹치지 않고 정상 표시되는지 검증합니다.
