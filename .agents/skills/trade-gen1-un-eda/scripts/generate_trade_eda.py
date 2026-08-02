"""
UN Comtrade 등 무역 통계 CSV를 입력받아 15개 데이터 기반 시각화 차트와
TOP 10 HS Code별 TOP 10 유망국가 11대 명세 분석표, 1인 상사 시장개척 전략을
자동 산출하는 범용 무역 EDA 엔진.

설계 원칙:
- 입력 CSV의 컬럼명이 raw UN Comtrade 스키마든, 단순화된 수집기 스키마든 모두 인식한다.
- 품목(item)에 대한 하드코딩된 가정(HS Code, 국가, 가격)을 두지 않고, 실제 데이터에서
  동적으로 산출한다. 데이터로 뒷받침되지 않는 정성적 필드는 "확인 필요"로 명시한다.
- 컬럼 부족/데이터 부족 시 전체 파이프라인이 죽지 않도록 차트 단위로 방어하고,
  치명적 결함(필수 컬럼 전무)에 한해서만 구조화된 [ERROR]를 출력하고 중단한다.
"""

import os
import re
import sys
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib  # noqa: F401  (한글 폰트 자동 적용)

# Windows 콘솔 인코딩 방어
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

plt.rcParams['axes.unicode_minus'] = False


# ---------------------------------------------------------------------------
# 공통 유틸리티
# ---------------------------------------------------------------------------

def pick_col(df, candidates):
    """candidates 중 df에 실제 존재하는 첫 번째 컬럼명을 반환. 없으면 None."""
    for c in candidates:
        if c in df.columns:
            return c
    return None


def print_error(missing, required_by, action):
    print("[ERROR]: Required file is empty or missing critical columns")
    print(f"- Missing: {missing}")
    print(f"- Required by: {required_by}")
    print(f"- Action: {action}")


def normalize_columns(df):
    """comtrade_api_collector.py의 단순화 스키마(year/exporter/importer/hs_code/
    trade_value/trade_weight)를 raw UN Comtrade 스키마 이름으로 매핑해
    두 스키마 모두 이 스크립트가 그대로 처리할 수 있게 한다."""
    alias_map = {
        'year': 'refYear',
        'exporter': 'reporterDesc',
        'importer': 'partnerDesc',
        'hs_code': 'cmdCode',
        'trade_value': 'primaryValue',
        'trade_weight': 'netWgt',
    }
    rename = {src: dst for src, dst in alias_map.items() if src in df.columns and dst not in df.columns}
    if rename:
        df = df.rename(columns=rename)
    return df


def save_placeholder(img_path, title, message="유효한 데이터가 부족하여 이 차트를 생략합니다."):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.text(0.5, 0.5, message, ha='center', va='center', fontsize=13, color='gray')
    ax.set_title(title, fontsize=14, pad=15)
    ax.axis('off')
    fig.tight_layout()
    fig.savefig(img_path, dpi=200)
    plt.close(fig)


def run_chart(label, fn):
    """개별 차트 생성 함수를 안전하게 실행. 실패해도 전체 파이프라인은 계속된다."""
    try:
        return fn()
    except Exception as e:
        print(f"⚠️ [{label}] 차트 생성 중 오류 발생, 플레이스홀더로 대체합니다: {e}")
        return None


def df_to_md(obj, empty_msg="데이터 없음"):
    if obj is None:
        return empty_msg
    if hasattr(obj, 'empty') and obj.empty:
        return empty_msg
    try:
        return obj.to_markdown()
    except Exception:
        return str(obj)


# ---------------------------------------------------------------------------
# 메인 엔진
# ---------------------------------------------------------------------------

def generate_trade_eda(csv_input, item_name, output_dir, item_slug=None):
    print("=" * 60)
    print(f"🚀 범용 무역 EDA 엔진 가동: {item_name}")
    print("=" * 60)

    if not os.path.exists(csv_input):
        print_error(csv_input, "generate_trade_eda.py", "올바른 --input CSV 경로를 지정하세요.")
        return False

    try:
        df = pd.read_csv(csv_input, low_memory=False)
    except Exception as e:
        print_error(f"{csv_input} (로드 실패: {e})", "generate_trade_eda.py", "CSV 파일 인코딩/형식을 확인하세요.")
        return False

    if df.empty:
        print_error(f"{csv_input} (0 rows)", "generate_trade_eda.py", "유효한 행이 포함된 CSV를 다시 수집하세요.")
        return False

    df = normalize_columns(df)

    val_col = pick_col(df, ['primaryValue', 'cifvalue', 'fobvalue'])
    wgt_col = pick_col(df, ['netWgt', 'qty', 'grossWgt'])
    year_col = pick_col(df, ['refYear', 'period'])
    month_col = pick_col(df, ['refMonth'])
    freq_col = pick_col(df, ['freqCode'])
    reporter_col = pick_col(df, ['reporterDesc'])
    partner_col = pick_col(df, ['partnerDesc'])
    flow_col = pick_col(df, ['flowDesc'])
    cmd_code_col = pick_col(df, ['cmdCode'])
    cmd_desc_col = pick_col(df, ['cmdDesc'])

    if val_col is None or partner_col is None:
        print_error(
            f"value column(one of primaryValue/cifvalue/fobvalue/trade_value)={val_col}, "
            f"partner column(partnerDesc/importer)={partner_col}",
            "generate_trade_eda.py",
            "UN Comtrade 원본 컬럼(primaryValue, partnerDesc 등) 또는 "
            "comtrade_api_collector.py 산출 컬럼(trade_value, importer 등)을 포함한 CSV를 사용하세요.",
        )
        return False

    df['clean_value'] = pd.to_numeric(
        df[val_col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False),
        errors='coerce',
    )
    df['clean_wgt'] = (
        pd.to_numeric(df[wgt_col].astype(str).str.replace(',', '', regex=False), errors='coerce')
        if wgt_col else pd.Series(np.nan, index=df.index)
    )
    df['unit_price'] = np.where(df['clean_wgt'] > 0, df['clean_value'] / df['clean_wgt'], np.nan)

    if reporter_col is None:
        df['_reporter_fallback'] = 'N/A'
        reporter_col = '_reporter_fallback'
    if flow_col is None:
        df['_flow_fallback'] = 'Trade'
        flow_col = '_flow_fallback'

    # HS Code 정제: mojibake가 섞인 "030781 (��)" 같은 원본에서도
    # 선행 숫자 코드만 안정적으로 추출해 동일 HS Code를 하나의 그룹으로 묶는다.
    if cmd_code_col:
        hs_extracted = df[cmd_code_col].astype(str).str.extract(r'(\d+)')[0]
        df['hs_clean'] = hs_extracted.fillna(df[cmd_code_col].astype(str))
    elif cmd_desc_col:
        df['hs_clean'] = df[cmd_desc_col].astype(str)
    else:
        df['hs_clean'] = item_name

    img_dir = os.path.join(output_dir, 'images')
    rep_dir = os.path.join(output_dir, 'reports')
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(rep_dir, exist_ok=True)

    clean_item = item_name.split('(')[0].strip() if '(' in item_name else item_name.strip()
    slug = (item_slug or re.sub(r'[^a-zA-Z0-9]+', '_', item_name).strip('_').lower() or 'item')
    slug_title = '_'.join(w.capitalize() for w in slug.split('_'))  # 파일명용 — 공백 없이 단어 경계만 유지 (예: power_take_off -> Power_Take_Off)

    EXCLUDE_AGG = ['World', 'Free Zones', 'Areas, nes', 'Special Categories']
    plt.rcParams['font.size'] = 10

    # ---- 데이터가 실제 월별 해상도를 가지는지 판별 (freqCode='A'면 refMonth는 sentinel) ----
    has_monthly_data = False
    if month_col:
        valid_months = pd.to_numeric(df[month_col], errors='coerce')
        valid_months = valid_months[(valid_months >= 1) & (valid_months <= 12)]
        if freq_col:
            has_monthly_data = (df[freq_col].astype(str).str.upper().isin(['M'])).any() and valid_months.nunique() > 1
        else:
            has_monthly_data = valid_months.nunique() > 1

    # ---- 동적 TOP-N HS Code 산출 (하드코딩 금지) ----
    TOP_N_HS = 10
    hs_totals = df.groupby('hs_clean')['clean_value'].sum().sort_values(ascending=False)
    top_hs_list = hs_totals.head(TOP_N_HS).index.tolist()

    def hs_desc(code):
        if cmd_desc_col:
            sub = df[df['hs_clean'] == code][cmd_desc_col].dropna()
            if not sub.empty:
                return str(sub.mode().iloc[0])[:80]
        return str(code)

    # ---- 상위 수입국 (여러 차트에서 재사용) ----
    imp_grp = df.groupby(partner_col)['clean_value'].agg(sum_million=lambda x: x.sum() / 1e6, count='count')
    imp_grp = imp_grp[~imp_grp.index.isin(EXCLUDE_AGG)].sort_values(by='sum_million', ascending=False)
    top_imp_df = imp_grp.head(10)
    top5_partners = top_imp_df.head(5).index.tolist()

    charts_md = {}

    # =====================================================================
    # 01. 연도별 무역 규모 및 수출입 추이
    # =====================================================================
    def chart_01():
        path = os.path.join(img_dir, '01_annual_trade_trend.png')
        if not year_col:
            save_placeholder(path, f'01. {clean_item} 연도별 무역액 추이', "연도 컬럼(refYear/year)이 없어 생략합니다.")
            return None
        piv = df.pivot_table(index=year_col, columns=flow_col, values='clean_value', aggfunc='sum', fill_value=0) / 1e6
        if piv.empty:
            save_placeholder(path, f'01. {clean_item} 연도별 무역액 추이')
            return None
        fig, ax = plt.subplots(figsize=(10, 5))
        piv.plot(kind='bar', ax=ax, colormap='tab10')
        ax.set_title(f'01. {clean_item} 연도별/거래유형별 무역액 추이 ($M)', fontsize=14, pad=15)
        ax.set_ylabel('무역액 (USD M)')
        ax.set_xlabel('연도')
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return piv

    charts_md['01'] = df_to_md(run_chart('01', chart_01))

    # =====================================================================
    # 02. TOP 10 주요 수출국
    # =====================================================================
    def chart_02():
        path = os.path.join(img_dir, '02_top_exporter_ranking.png')
        exp_grp = df.groupby(reporter_col)['clean_value'].agg(sum_million=lambda x: x.sum() / 1e6, count='count')
        exp_grp = exp_grp[~exp_grp.index.isin(EXCLUDE_AGG)].sort_values(by='sum_million', ascending=False).head(10)
        if exp_grp.empty:
            save_placeholder(path, f'02. {clean_item} TOP 10 주요 수출국')
            return None
        fig, ax = plt.subplots(figsize=(10, 5))
        exp_grp['sum_million'].plot(kind='barh', ax=ax, color='#2ca02c')
        ax.invert_yaxis()
        ax.set_title(f'02. {clean_item} TOP 10 주요 수출국 무역액 ($M)', fontsize=14, pad=15)
        ax.set_xlabel('무역액 (USD M)')
        ax.grid(axis='x', linestyle='--', alpha=0.5)
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return exp_grp

    charts_md['02'] = df_to_md(run_chart('02', chart_02))

    # =====================================================================
    # 03. TOP 10 주요 수입국
    # =====================================================================
    def chart_03():
        path = os.path.join(img_dir, '03_top_importer_ranking.png')
        if top_imp_df.empty:
            save_placeholder(path, f'03. {clean_item} TOP 10 주요 수입국')
            return None
        fig, ax = plt.subplots(figsize=(10, 5))
        top_imp_df['sum_million'].plot(kind='barh', ax=ax, color='#ff7f0e')
        ax.invert_yaxis()
        ax.set_title(f'03. {clean_item} TOP 10 주요 수입국 무역액 ($M)', fontsize=14, pad=15)
        ax.set_xlabel('무역액 (USD M)')
        ax.grid(axis='x', linestyle='--', alpha=0.5)
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return top_imp_df

    charts_md['03'] = df_to_md(run_chart('03', chart_03))

    # =====================================================================
    # 04. 단가($/kg) 분포 히스토그램
    # =====================================================================
    def chart_04():
        path = os.path.join(img_dir, '04_unit_price_distribution.png')
        prices = df['unit_price'].replace([np.inf, -np.inf], np.nan).dropna()
        if prices.empty:
            save_placeholder(path, f'04. {clean_item} 단가 분포', "단가를 계산할 수 있는 유효한 값/중량 데이터가 없습니다.")
            return None
        # 극단 이상치로 인해 분포가 뭉개지는 것을 방지 (상위 1% 클리핑)
        clip_upper = prices.quantile(0.99)
        clipped = prices[prices <= clip_upper]
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(clipped, bins=30, color='#4c72b0', edgecolor='white')
        ax.set_title(f'04. {clean_item} 단가($/kg) 분포 히스토그램 (상위 1% 이상치 제외)', fontsize=14, pad=15)
        ax.set_xlabel('단가 ($/kg)')
        ax.set_ylabel('거래 건수')
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return prices.describe().to_frame(name='unit_price_usd_kg')

    charts_md['04'] = df_to_md(run_chart('04', chart_04))

    # =====================================================================
    # 05. 월별 수출입 계절성 분석
    # =====================================================================
    def chart_05():
        path = os.path.join(img_dir, '05_monthly_seasonality.png')
        if not has_monthly_data:
            save_placeholder(
                path, f'05. {clean_item} 월별 계절성',
                "데이터가 연간(Annual) 집계 단위라 월별 계절성을 산출할 수 없습니다.",
            )
            return None
        m = pd.to_numeric(df[month_col], errors='coerce')
        m_val = df.loc[(m >= 1) & (m <= 12)].groupby(m)['clean_value'].sum() / 1e6
        fig, ax = plt.subplots(figsize=(10, 5))
        m_val.plot(kind='line', marker='o', color='green', linewidth=2, ax=ax)
        ax.set_title(f'05. {clean_item} 월별 수출입 계절성 추이', fontsize=14, pad=15)
        ax.set_xlabel('월')
        ax.set_ylabel('무역액 (USD M)')
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return m_val.to_frame(name='무역액($M)')

    charts_md['05'] = df_to_md(run_chart('05', chart_05))

    # =====================================================================
    # 06. HS Code별 무역 점유율 파이 차트
    # =====================================================================
    def chart_06():
        path = os.path.join(img_dir, '06_hs_code_share.png')
        share = hs_totals[hs_totals > 0]
        if share.empty:
            save_placeholder(path, f'06. {clean_item} HS Code별 무역 점유율')
            return None
        top6 = share.head(6)
        other = share.iloc[6:].sum()
        pie_s = top6.copy()
        if other > 0:
            pie_s['기타'] = other
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(pie_s, labels=[hs_desc(i)[:20] if i in top6.index else '기타' for i in pie_s.index],
               autopct='%1.1f%%', startangle=90)
        ax.set_title(f'06. {clean_item} HS Code별 무역 점유율', fontsize=14, pad=15)
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return (pie_s / 1e6).to_frame(name='무역액($M)')

    charts_md['06'] = df_to_md(run_chart('06', chart_06))

    # =====================================================================
    # 07. 단가 vs 물량 산점도 (Correlation)
    # =====================================================================
    def chart_07():
        path = os.path.join(img_dir, '07_price_vs_weight_scatter.png')
        valid = df.dropna(subset=['clean_wgt', 'unit_price'])
        valid = valid[(valid['clean_wgt'] > 0) & np.isfinite(valid['unit_price'])]
        if len(valid) < 3:
            save_placeholder(path, f'07. {clean_item} 단가 vs 물량 산점도', "상관관계를 계산하기에 유효 표본이 부족합니다.")
            return None
        sample_n = min(300, len(valid))
        sample = valid.sample(sample_n, random_state=42)
        corr = valid['clean_wgt'].corr(valid['unit_price'])
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.scatter(sample['clean_wgt'] / 1e3, sample['unit_price'], alpha=0.5, color='crimson')
        ax.set_title(f'07. {clean_item} 물량(톤) vs 단가($/kg) 산점도 (r={corr:.2f})', fontsize=14, pad=15)
        ax.set_xlabel('순중량 (천 톤)')
        ax.set_ylabel('단가 ($/kg)')
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return pd.DataFrame({'상관계수(물량 vs 단가)': [round(corr, 3)], '표본수': [len(valid)]})

    charts_md['07'] = df_to_md(run_chart('07', chart_07))

    # =====================================================================
    # 08. TOP 5 주요 수입국 연도별 성장률(추이)
    # =====================================================================
    def chart_08():
        path = os.path.join(img_dir, '08_top5_importer_growth.png')
        if not year_col or not top5_partners:
            save_placeholder(path, f'08. {clean_item} TOP5 수입국 연도별 추이', "연도 정보 또는 수입국 데이터가 부족합니다.")
            return None
        piv = df[df[partner_col].isin(top5_partners)].pivot_table(
            index=year_col, columns=partner_col, values='clean_value', aggfunc='sum', fill_value=0
        ) / 1e6
        if piv.shape[0] < 2:
            save_placeholder(path, f'08. {clean_item} TOP5 수입국 연도별 추이', "추이를 그리기에 연도 수가 부족합니다.")
            return None
        fig, ax = plt.subplots(figsize=(10, 5))
        piv.plot(kind='line', marker='o', ax=ax)
        ax.set_title(f'08. {clean_item} TOP 5 주요 수입국 연도별 무역액 추이 ($M)', fontsize=14, pad=15)
        ax.set_ylabel('무역액 (USD M)')
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        growth = ((piv.iloc[-1] - piv.iloc[0]) / piv.iloc[0].replace(0, np.nan) * 100).round(1)
        return pd.DataFrame({'시작년도($M)': piv.iloc[0], '최종년도($M)': piv.iloc[-1], '누적성장률(%)': growth})

    charts_md['08'] = df_to_md(run_chart('08', chart_08))

    # =====================================================================
    # 09. 시장 집중도 파레토 차트 (80/20)
    # =====================================================================
    def chart_09():
        path = os.path.join(img_dir, '09_market_concentration_pareto.png')
        if top_imp_df.empty:
            save_placeholder(path, f'09. {clean_item} 시장 집중도 파레토')
            return None
        p_sum = top_imp_df['sum_million']
        cum_pct = (p_sum.cumsum() / p_sum.sum()) * 100
        fig, ax1 = plt.subplots(figsize=(10, 5))
        ax1.bar(p_sum.index, p_sum, color='skyblue')
        ax1.set_ylabel('수입액 (USD M)')
        ax1.tick_params(axis='x', rotation=30)
        ax2 = ax1.twinx()
        ax2.plot(p_sum.index, cum_pct, color='red', marker='o')
        ax2.set_ylabel('누적 점유율 (%)')
        ax1.set_title(f'09. {clean_item} 글로벌 수입 시장 누적 집중도 파레토 (80/20)', fontsize=14, pad=15)
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return pd.DataFrame({'수입액($M)': p_sum, '누적점유율(%)': cum_pct.round(1)})

    charts_md['09'] = df_to_md(run_chart('09', chart_09))

    # =====================================================================
    # 10. 주요 국가별/연도별 단가 변화 히트맵
    # =====================================================================
    def chart_10():
        path = os.path.join(img_dir, '10_export_price_heatmap.png')
        if not year_col or not top5_partners:
            save_placeholder(path, f'10. {clean_item} 국가별/연도별 단가 히트맵', "연도 정보 또는 수입국 데이터가 부족합니다.")
            return None
        sub = df[df[partner_col].isin(top5_partners) & df['unit_price'].notna() & np.isfinite(df['unit_price'])]
        piv = sub.pivot_table(index=partner_col, columns=year_col, values='unit_price', aggfunc='mean')
        if piv.empty:
            save_placeholder(path, f'10. {clean_item} 국가별/연도별 단가 히트맵')
            return None
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.heatmap(piv, annot=True, fmt=".1f", cmap='YlOrRd', ax=ax)
        ax.set_title(f'10. {clean_item} 주요국별/연도별 평균 단가 변화 ($/kg)', fontsize=14, pad=15)
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return piv

    charts_md['10'] = df_to_md(run_chart('10', chart_10))

    # =====================================================================
    # 11. 무역 수지 폭포수 차트
    # =====================================================================
    def chart_11():
        path = os.path.join(img_dir, '11_trade_balance_waterfall.png')
        flow_vals = df[flow_col].astype(str).str.lower()
        has_flow_info = flow_vals.isin(['export', 'import']).sum() > 0 and flow_vals.nunique() > 1
        if year_col and has_flow_info:
            exp_y = df[flow_vals == 'export'].groupby(year_col)['clean_value'].sum()
            imp_y = df[flow_vals == 'import'].groupby(year_col)['clean_value'].sum()
            balance = ((exp_y.reindex(sorted(set(exp_y.index) | set(imp_y.index)), fill_value=0)
                        - imp_y.reindex(sorted(set(exp_y.index) | set(imp_y.index)), fill_value=0)) / 1e6)
            title_suffix = '(연도별, 수출-수입)'
            labels = balance.index.astype(str).tolist()
            values = balance.values
        else:
            # flow 구분이 없으면 상위 5개국의 무역액 기여도를 누적 폭포수로 표현
            top5 = top_imp_df.head(5)['sum_million']
            if top5.empty:
                save_placeholder(path, f'11. {clean_item} 무역 수지 폭포수')
                return None
            labels = top5.index.tolist()
            values = top5.values
            title_suffix = '(TOP5 수입국 누적 기여도)'

        if len(values) == 0:
            save_placeholder(path, f'11. {clean_item} 무역 수지 폭포수')
            return None

        cum = np.cumsum(values)
        starts = np.insert(cum[:-1], 0, 0)
        colors = ['#2ca02c' if v >= 0 else '#d62728' for v in values]
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(labels, values, bottom=starts, color=colors)
        ax.axhline(0, color='black', linewidth=0.8)
        ax.set_title(f'11. {clean_item} 무역 수지 폭포수 차트 {title_suffix}', fontsize=14, pad=15)
        ax.set_ylabel('금액 (USD M)')
        ax.tick_params(axis='x', rotation=30)
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return pd.DataFrame({'값($M)': values, '누적($M)': cum}, index=labels)

    charts_md['11'] = df_to_md(run_chart('11', chart_11))

    # =====================================================================
    # 12. 국가별 단가 변동성 박스플롯
    # =====================================================================
    def chart_12():
        path = os.path.join(img_dir, '12_country_price_boxplot.png')
        top8 = top_imp_df.head(8).index.tolist()
        sub = df[df[partner_col].isin(top8) & df['unit_price'].notna() & np.isfinite(df['unit_price'])]
        if sub.empty:
            save_placeholder(path, f'12. {clean_item} 국가별 단가 변동성')
            return None
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.boxplot(data=sub, x=partner_col, y='unit_price', hue=partner_col,
                    order=top8, palette='Set2', legend=False, ax=ax)
        ax.set_title(f'12. {clean_item} TOP 8 수입국 단가($/kg) 변동성 박스플롯', fontsize=14, pad=15)
        ax.tick_params(axis='x', rotation=30)
        ax.set_xlabel('')
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return sub.groupby(partner_col)['unit_price'].agg(['mean', 'std', 'median', 'max']).loc[
            [c for c in top8 if c in sub[partner_col].unique()]
        ]

    charts_md['12'] = df_to_md(run_chart('12', chart_12))

    # =====================================================================
    # 13. 허핀달-허쉬만 시장 집중도(HHI Index) 추이
    # =====================================================================
    def chart_13():
        path = os.path.join(img_dir, '13_hhi_index_trend.png')
        if not year_col:
            save_placeholder(path, f'13. {clean_item} HHI 지수 추이', "연도 컬럼이 없어 생략합니다.")
            return None
        piv = df.pivot_table(index=year_col, columns=partner_col, values='clean_value', aggfunc='sum', fill_value=0)
        if piv.empty:
            save_placeholder(path, f'13. {clean_item} HHI 지수 추이')
            return None
        row_sum = piv.sum(axis=1)
        hhi_s = piv.div(row_sum.replace(0, np.nan), axis=0).pow(2).sum(axis=1) * 10000
        hhi_s = hhi_s.dropna()
        if hhi_s.empty:
            save_placeholder(path, f'13. {clean_item} HHI 지수 추이')
            return None
        fig, ax = plt.subplots(figsize=(10, 5))
        hhi_s.plot(kind='line', marker='s', color='darkblue', ax=ax)
        ax.set_title(f'13. {clean_item} 시장 집중도 (HHI Index) 연도별 추이', fontsize=14, pad=15)
        ax.set_ylabel('HHI Index')
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return hhi_s.round(0).to_frame(name='HHI_Index')

    charts_md['13'] = df_to_md(run_chart('13', chart_13))

    # =====================================================================
    # 14. 품목/HS Code별 단가 구간(규격 추정) 가격 구조
    # =====================================================================
    def chart_14():
        path = os.path.join(img_dir, '14_size_pricing_structure.png')
        prices = df['unit_price'].replace([np.inf, -np.inf], np.nan).dropna()
        if len(prices) < 4:
            save_placeholder(path, f'14. {clean_item} 가격 구간별 구조', "단가 표본이 부족하여 구간을 나눌 수 없습니다.")
            return None
        try:
            tiers = pd.qcut(prices, 4, labels=['Economy(하위 25%)', 'Standard(25~50%)', 'Premium(50~75%)', 'Ultra-Premium(상위 25%)'])
        except ValueError:
            save_placeholder(path, f'14. {clean_item} 가격 구간별 구조', "단가 값의 분산이 낮아 4분위 구간을 나눌 수 없습니다.")
            return None
        tier_avg = prices.groupby(tiers, observed=True).mean().sort_values()
        fig, ax = plt.subplots(figsize=(10, 5))
        tier_avg.plot(kind='barh', color='#bcbd22', ax=ax)
        ax.set_title(f'14. {clean_item} 데이터 기반 가격 구간(4분위) 구조 ($/kg)', fontsize=14, pad=15)
        ax.set_xlabel('평균 단가 ($/kg, 데이터 산출값)')
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return tier_avg.to_frame(name='평균단가($/kg)')

    charts_md['14'] = df_to_md(run_chart('14', chart_14))

    # =====================================================================
    # 15. 유망국가 성장성 vs 단가 포지셔닝 매트릭스
    # =====================================================================
    def chart_15():
        path = os.path.join(img_dir, '15_promising_country_matrix.png')
        candidates = top_imp_df.head(5).index.tolist()
        if not candidates:
            save_placeholder(path, f'15. {clean_item} 유망국가 매트릭스')
            return None
        avg_price = df[df[partner_col].isin(candidates)].groupby(partner_col)['unit_price'].mean()
        growth = pd.Series(0.0, index=candidates)
        if year_col:
            piv = df[df[partner_col].isin(candidates)].pivot_table(
                index=year_col, columns=partner_col, values='clean_value', aggfunc='sum', fill_value=0
            )
            if piv.shape[0] >= 2:
                growth = ((piv.iloc[-1] - piv.iloc[0]) / piv.iloc[0].replace(0, np.nan) * 100).reindex(candidates)
        result = pd.DataFrame({
            '연평균 성장률(%)': growth.round(1),
            '평균단가($/kg)': avg_price.reindex(candidates).round(1),
        }).dropna(how='all')
        result['연평균 성장률(%)'] = result['연평균 성장률(%)'].fillna(0)
        result['평균단가($/kg)'] = result['평균단가($/kg)'].fillna(0)
        fig, ax = plt.subplots(figsize=(10, 5))
        colors = plt.cm.tab10.colors
        ax.scatter(result['연평균 성장률(%)'], result['평균단가($/kg)'], s=500,
                   c=[colors[i % len(colors)] for i in range(len(result))], alpha=0.7)
        for i, (name, row) in enumerate(result.iterrows()):
            ax.annotate(str(name), (row['연평균 성장률(%)'], row['평균단가($/kg)']),
                        fontsize=11, weight='bold', xytext=(5, 5), textcoords='offset points')
        ax.set_title(f'15. {clean_item} 주요 수입국 성장성 vs 단가 포지셔닝 (데이터 산출)', fontsize=14, pad=15)
        ax.set_xlabel('관측기간 누적 성장률 (%)')
        ax.set_ylabel('평균 단가 ($/kg)')
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return result

    charts_md['15'] = df_to_md(run_chart('15', chart_15))

    plt.close('all')

    # =====================================================================
    # 동적 TOP-N HS Code별 유망국가 11대 명세 표
    # =====================================================================
    def build_country_table(hs_code):
        sub = df[df['hs_clean'] == hs_code]
        tot = sub['clean_value'].sum()
        if sub.empty or tot <= 0:
            return "| - | 데이터 없음 | 해당 HS 분류의 유효 거래 데이터가 없습니다 | - | - | - | - | - | - | - | - |\n"
        grp = sub.groupby(partner_col).agg(val=('clean_value', 'sum'), wgt=('clean_wgt', 'sum'), price=('unit_price', 'mean'))
        grp = grp[~grp.index.isin(EXCLUDE_AGG)].sort_values(by='val', ascending=False).head(10)
        rows = ""
        for rank, (country, row) in enumerate(grp.iterrows(), 1):
            v_m = row['val'] / 1e6
            w_t = row['wgt'] / 1e3 if pd.notna(row['wgt']) else 0
            share = (row['val'] / tot * 100) if tot else 0
            price = row['price']
            if pd.isna(price) or not np.isfinite(price):
                price = (row['val'] / row['wgt']) if row['wgt'] else np.nan
            price_txt = f"${price:.1f}/kg" if pd.notna(price) and np.isfinite(price) else "산출불가(중량 데이터 부족)"

            reason = f"수입액 ${v_m:,.1f}M ({share:.1f}%), 물량 {w_t:,.0f}톤"
            partner = f"{country} 현지 {clean_item} 전문 수입 도매상/식품 유통 벤더 *(실사 확인 필요)*"
            comp_price = f"현지 평균 도매가 {price_txt} 수준 *(경쟁 제품 벤치마크는 데이터 미포함, 별도 조사 필요)*"
            hscode_tariff = f"HS {hs_code} — {hs_desc(hs_code)[:40]} *(관세율은 부록의 FTA 매트릭스 참고, 최신 협정세율 별도 확인)*"
            cert = "HACCP, ISO22000 등 위생안전 인증 및 시험성적서(COA) *(품목별 요건 별도 확인)*"
            non_tariff = "SPS(위생검역) 증명서, 현지어 라벨링 규정 등 *(비관세장벽 사전 확인 필요)*"
            channel = f"{country} 식품 도매시장, 전문 유통망, 대형 리테일 벤더 *(현지 조사 권장)*"
            margin = "중간 유통상 마진 15~25%, 소매 마진 25~40% *(업계 평균 추정치)*"
            logistics = "냉장/냉동 콜드체인 해상 또는 항공 운송 *(품목 특성별 별도 검토)*"

            rows += (f"| **{rank}위** | **{country}** | {reason} | {partner} | {comp_price} | {hscode_tariff} | "
                     f"{cert} | {non_tariff} | {channel} | {margin} | {logistics} |\n")
        return rows

    hs_tables = {}
    for idx, hs_code in enumerate(top_hs_list, 1):
        hs_tables[idx] = build_country_table(hs_code)
    while len(hs_tables) < TOP_N_HS:
        hs_tables[len(hs_tables) + 1] = "| - | 데이터 없음 | 데이터셋에 해당 순위의 HS Code가 존재하지 않습니다 | - | - | - | - | - | - | - | - |\n"

    hs_labels = {i: (f"HS {top_hs_list[i-1]} ({hs_desc(top_hs_list[i-1])[:40]})" if i <= len(top_hs_list) else "N/A")
                 for i in range(1, TOP_N_HS + 1)}

    hs_summary_lines = "\n".join(
        f"  - {i}순위 `{hs_labels[i]}`: 총 무역액 "
        f"${(df[df['hs_clean'] == top_hs_list[i-1]]['clean_value'].sum() / 1e6):,.1f}M"
        for i in range(1, len(top_hs_list) + 1)
    ) or "  - 산출 가능한 HS Code가 없습니다."

    hs_tables_section_md = "\n\n".join(
        f"### 📌 [표 {i}] {hs_labels[i]} TOP 10 유망 국가 11대 명세 표\n\n"
        f"| 유망순위 | 국가명 | 구체적 근거 (수입액/물량) | 컨택해야 할 로컬 파트너 | 경쟁 제품/가격대 (도매가) | HS Code 및 관세율 | 필수 인증 및 허가 | 비관세 장벽 (SPS/라벨링) | 주요 유통 채널 | 중간 유통상 생태계 & 마진율 | 물류 및 콜드체인 인프라 |\n"
        f"| :---: | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
        f"{hs_tables[i]}"
        for i in range(1, TOP_N_HS + 1)
    )

    # =====================================================================
    # 데이터 기초 정보
    # =====================================================================
    preview_cols = [c for c in [year_col, month_col, reporter_col, flow_col, partner_col, cmd_desc_col, 'clean_value'] if c]
    head_txt = df.head(5)[preview_cols].to_string() if preview_cols else "미리보기 컬럼 없음"
    tail_txt = df.tail(5)[preview_cols].to_string() if preview_cols else "미리보기 컬럼 없음"
    desc_txt = df[['clean_value', 'clean_wgt', 'unit_price']].describe().to_string()

    total_val_m = round(df['clean_value'].sum() / 1e6, 2)
    total_rec = len(df)

    # 결측치 정제 내역 (SKILL.md "데이터 개요 및 정제 보고" 항목)
    na_value_n = int(df['clean_value'].isna().sum())
    na_wgt_n = int(df['clean_wgt'].isna().sum())
    na_price_n = int(df['unit_price'].isna().sum())
    cleaning_report = (
        f"- `{val_col}` → `clean_value` 숫자 변환 실패/결측: {na_value_n:,}행 ({na_value_n/total_rec*100:.1f}%)\n"
        f"- `{wgt_col or 'N/A'}` → `clean_wgt` 숫자 변환 실패/결측: {na_wgt_n:,}행 ({na_wgt_n/total_rec*100:.1f}%)\n"
        f"- `unit_price` 산출 불가(중량 0 또는 결측): {na_price_n:,}행 ({na_price_n/total_rec*100:.1f}%)"
    )

    # =====================================================================
    # 1인 상사 최적 개척 시장 3선 (데이터 기반 산출, 품목 하드코딩 없음)
    # =====================================================================
    def build_market_strategy():
        grp = df.groupby(partner_col).agg(val=('clean_value', 'sum'), price=('unit_price', 'mean'))
        grp = grp[~grp.index.isin(EXCLUDE_AGG)].sort_values(by='val', ascending=False)
        if grp.empty:
            return "데이터 부족으로 시장 전략을 산출할 수 없습니다. CSV의 partnerDesc/importer 컬럼을 확인하세요."

        volume_market = grp.index[0]
        if grp['price'].notna().any():
            premium_market = grp[grp['price'].notna()].sort_values(by='price', ascending=False).index[0]
        else:
            premium_market = volume_market

        growth_market = None
        if year_col:
            candidates = grp.head(15).index.tolist()
            piv = df[df[partner_col].isin(candidates)].pivot_table(
                index=year_col, columns=partner_col, values='clean_value', aggfunc='sum', fill_value=0
            )
            if piv.shape[0] >= 2:
                g = ((piv.iloc[-1] - piv.iloc[0]) / piv.iloc[0].replace(0, np.nan) * 100).dropna()
                g = g[g.index != volume_market].sort_values(ascending=False)
                if not g.empty:
                    growth_market = g.index[0]
        if not growth_market:
            growth_market = grp.index[1] if len(grp) > 1 else volume_market

        premium_price = grp.loc[premium_market, 'price']
        premium_price_txt = f"${premium_price:.1f}/kg" if pd.notna(premium_price) else "산출불가"

        return f"""### ① 시장 1: {volume_market} — [최대 거래 규모 시장]
- **선정 근거**: 데이터 기준 누적 수입액 1위 (${grp.loc[volume_market, 'val']/1e6:,.1f}M). 가장 안정적인 기반 매출(Base Revenue) 확보가 가능한 시장으로 우선 개척을 권장합니다.

### ② 시장 2: {premium_market} — [최고 단가/프리미엄 시장]
- **선정 근거**: 평균 단가 기준 최상위 시장 (평균 {premium_price_txt} 수준, 데이터 산출값). 고마진 프리미엄 포지셔닝에 유리합니다.

### ③ 시장 3: {growth_market} — [고성장 시장]
- **선정 근거**: 관측 기간 중 수입액 성장세가 가장 두드러진 시장입니다. 신규 진입 시 선점 효과를 기대할 수 있습니다.

> ⚠️ 위 3대 시장은 무역 통계의 정량적 산출 결과이며, 실제 진출 전 현지 바이어 리서치, 인증/규제 요건, FTA 협정세율은 별도로 확인이 필요합니다."""

    market_3star_text = build_market_strategy()

    # =====================================================================
    # TOP 5 실전 무역 고도화 패키지 (품목 파라미터화)
    # =====================================================================
    pro_advanced_package_text = f"""
## 🚀 [TOP 5 실전 무역 고도화 패키지] 1인 상사 전용 시장개척 파이프라인

### 1. 📑 주요 타깃국가별 FTA 협정 관세율 프레임워크 (Tariff Benefit Matrix)

> ⚠️ 아래 관세율은 일반적인 한국 체결 FTA 프레임워크 참고용 템플릿입니다. HS Code·품목별 실제 협정세율은
> 관세청 FTA포털(fta.customs.go.kr) 또는 K-SURE를 통해 반드시 재확인하세요.

| 타깃 국가 / 지역 | 적용 FTA 협정 명칭 | 협정 혜택 개요 | 바이어 오퍼 포인트 |
| :--- | :--- | :--- | :--- |
| **미국 (USA)** | 한-미 FTA (K-US FTA) | 대다수 품목 무관세 적용 | *"K-US FTA 협정관세 적용으로 관세 부담 최소화 오퍼"* |
| **일본 (Japan)** | RCEP | 품목별 단계적 관세 인하 | *"RCEP 원산지 증명서 발급으로 협정 관세 혜택 적용"* |
| **중국 (China)** | 한-중 FTA | 품목별 협정세율 적용 | *"한-중 FTA 협정관세 적용으로 현지 유통상 마진 확보"* |
| **동남아 (태국/베트남)** | 한-아세안 FTA (AKFTA) | Form AK 제출 시 관세 절감 | *"AKFTA Form AK 제출로 수입 관세 절감 오퍼"* |
| **유럽연합** | 한-EU FTA | 인증수출자 활용 시 무관세 다수 | *"한-EU FTA 인증수출자 적용으로 서유럽 바이어 비용 절감"* |

---

### 2. 🚢 물류 수송 형태별 MOQ 및 CBM/운임 산정 가이드 (Logistics & MOQ)

| 수송 방식 (Logistics) | 적재 단위 및 컨테이너 규격 | 추천 MOQ (최소 주문 수량) | kg/CBM당 추정 물류비 | 1인 상사 물류 실행 가이드 |
| :--- | :--- | :--- | :---: | :--- |
| **해상 LCL (소량 혼적)** | 1~3 Pallets (전용 팰릿 포장) | **50 ~ 100 Cartons** | $0.8 ~ $1.5 / kg | 초도 샘플 및 마트 테스트 물량에 적합 |
| **해상 FCL (20ft Reefer/Dry)** | 20ft 컨테이너 (약 1,000 Cartons) | **1 x 20ft Container** | $0.3 ~ $0.6 / kg | **메인 B2B 주력 물량**, 운임 효율 극대화 |
| **해상 FCL (40ft HQ Reefer)** | 40ft HQ 컨테이너 (약 2,200 Cartons) | **1 x 40ft HQ Container** | $0.2 ~ $0.4 / kg | 대형 유통 벤더 대량 계약 |
| **항공 직송 (Air Freight)** | 항공 ULD 전용 팰릿 (Express) | **10 ~ 20 Cartons** | $3.5 ~ $6.0 / kg | 초신선/고부가 프리미엄 채널 출하 |

*(물류비는 품목 부피/중량비, 유가, 계약 조건에 따라 변동되는 일반 참고치입니다.)*

---

### 3. 🛡️ 해외 바이어 신용 리스크 방어 & K-SURE 무역보험 체크리스트

- **[1단계] 바이어 사전 신용 조사**: K-SURE **국외기업 신용조사 서비스** 활용 사전 검증.
- **[2단계] 대금 결제 조건 준수**: `Irrevocable L/C at sight` 또는 `T/T 30% Deposit + 70% against B/L Copy` 준수.
- **[3단계] 단기수출보험 가입**: K-SURE 단기수출보험으로 **수출 대금 보상 안전망** 구축.

---

### 4. 🏷️ 현지 식품/제품 인증 및 라벨링(Labeling) 규제 체크리스트

1. **미국 시장**: FDA FFR 등록 및 영문 영양성분표(FDA Nutrition Facts Panel) 외포장 인쇄 필수.
2. **유럽 시장**: EU 성분 표시 및 유기농 인증(EU Organic) 여부 확인.
3. **동남아/중동 시장**: 할랄 인증(HALAL) 필요 여부 사전 확인.
4. **품질 검사성적서**: HACCP, ISO 및 공인 시험기관의 COA 성적서 상시 비치.

*(품목별 정확한 인증 요건은 대한무역투자진흥공사(KOTRA) 및 현지 수입 규정을 반드시 재확인하세요.)*

---

### 5. ⚔️ 경쟁국 대응 1인 상사 오퍼 배틀카드 (Competitive Battlecard) 템플릿

```text
[상황 1] 저가 경쟁국 대비 가격 압박 ☞ "HACCP/COA 등 공인 인증으로 위생·안전성을 입증하며 품질 프리미엄 오퍼"
[상황 2] 프리미엄 브랜드 대비 가격 열위 ☞ "동급 품질 유지, 가성비 오퍼로 바이어 마진 확보 지원"
[상황 3] MOQ 완화 요청 ☞ "초도 LCL 소량 혼적 승인, 완판 후 FCL 컨테이너 단위 2차 계약 제시"
```
"""

    # =====================================================================
    # 최종 마크다운 리포트 조립
    # =====================================================================
    input_basename = os.path.basename(csv_input)
    report_file = os.path.join(rep_dir, f"BIZ-{slug_title}_Gathered_EDA_Report.md")

    full_md = f"""# 🌊 {input_basename} — {clean_item} 무역 데이터 종합 EDA 및 글로벌 영업전략 리포트

## 📌 Executive Summary

본 리포트는 `{input_basename}` {clean_item} 무역 데이터셋(총 {total_rec:,}행)을 대상으로 데이터 기반
**1인 종합상사 최적 개척 시장 3선 전략**, 무역액 기준 **동적 산출 TOP {TOP_N_HS} HS Code**별 **TOP 10 유망국가
11대 명세 분석표**, 그리고 **[TOP 5 실전 무역 고도화 패키지]**를 산출한 EDA 보고서입니다.

---

## 1. 데이터 파악 및 기초 탐색 (Data Exploration)

- **데이터 규모**: 행 수: {total_rec:,}개, 열 수: {len(df.columns)}개
- **동적 산출 TOP {TOP_N_HS} HS Code** (무역액 기준):
{hs_summary_lines}

### 결측치 정제 내역
{cleaning_report}

### 원시 데이터 상위 5행 및 하위 5행
```
[Head 5 Rows]
{head_txt}

[Tail 5 Rows]
{tail_txt}
```

### 기술통계 요약 (Descriptive Statistics)
```
[수치형 변수 기술통계]
{desc_txt}
```

---

## 2. 세부 탐색적 데이터 분석 및 시각화 (15대 핵심 분석)

### 1. 연도별 글로벌 {clean_item} 수출입 거래 총액 추이
![1. 연도별 무역 추이](../images/01_annual_trade_trend.png)
**[분석 해석]**: 데이터셋 전체 누적 무역액은 ${total_val_m}M입니다. 연도별/거래유형별 세부 수치는 아래 표를 참고하세요.
{charts_md['01']}

### 2. TOP 10 주요 수출국 분석
![2. TOP 10 수출국](../images/02_top_exporter_ranking.png)
{charts_md['02']}

### 3. TOP 10 주요 수입국 분석
![3. TOP 10 수입국](../images/03_top_importer_ranking.png)
{charts_md['03']}

### 4. 단가($/kg) 분포 히스토그램
![4. 단가 분포](../images/04_unit_price_distribution.png)
{charts_md['04']}

### 5. 월별 수출입 계절성 분석
![5. 계절성](../images/05_monthly_seasonality.png)
{charts_md['05']}

### 6. HS Code별 무역 점유율
![6. HS Code 점유율](../images/06_hs_code_share.png)
{charts_md['06']}

### 7. 단가 vs 물량 산점도 (Correlation)
![7. 산점도](../images/07_price_vs_weight_scatter.png)
{charts_md['07']}

### 8. TOP 5 주요 수입국 연도별 무역액 추이
![8. TOP5 수입국 추이](../images/08_top5_importer_growth.png)
{charts_md['08']}

### 9. 시장 집중도 파레토 (80/20)
![9. 파레토](../images/09_market_concentration_pareto.png)
{charts_md['09']}

### 10. 주요국별/연도별 단가 변화 히트맵
![10. 히트맵](../images/10_export_price_heatmap.png)
{charts_md['10']}

### 11. 무역 수지 폭포수 차트
![11. 폭포수](../images/11_trade_balance_waterfall.png)
{charts_md['11']}

### 12. 국가별 단가 변동성 박스플롯
![12. 박스플롯](../images/12_country_price_boxplot.png)
{charts_md['12']}

### 13. 연도별 HHI 시장 집중도 추이
![13. HHI](../images/13_hhi_index_trend.png)
{charts_md['13']}

### 14. 데이터 기반 가격 구간(4분위) 구조
![14. 가격구조](../images/14_size_pricing_structure.png)
{charts_md['14']}

### 15. 유망국가 성장성 vs 단가 포지셔닝 Matrix
![15. 유망국가](../images/15_promising_country_matrix.png)
{charts_md['15']}

---

# 👔 [특별 부록] 1인 종합상사 창업자를 위한 {clean_item} 글로벌 신시장 개척 실전 전략서

## 🎯 1. 1인 종합상사 최적 우선 개척 시장 3선 (데이터 기반 산출)

1인 기업의 한계(리스크 관리, 물류 부담, 자금 회수 주기)와 강점(빠른 의사결정, 맞춤형 바이어 대응)을 고려해
실제 무역 데이터에서 산출한 **Top 3 타깃 시장**은 다음과 같습니다:

{market_3star_text}

---

## 🗺️ 동적 산출 TOP {TOP_N_HS} HS Code별 TOP 10 유망 국가 분석 표 (11대 명세 필드)

> ⚠️ 아래 표의 "구체적 근거", "경쟁 제품/가격대"는 데이터 산출값이며, 그 외 정성적 필드(파트너/인증/유통채널 등)는
> 업계 일반 템플릿으로 *(확인 필요)* 표기된 항목은 반드시 현지 리서치로 검증해야 합니다.

{hs_tables_section_md}

---

{pro_advanced_package_text}

---

## 🎁 3대 특별 부록 (1인 상사 실전 무역 영업 패키지)

### 📄 부록 1. 1인 상사 실전 B2B 오퍼서 (Commercial B2B Offer Sheet) 초안
```
======================================================================
                  COMMERCIAL B2B OFFER SHEET
======================================================================
Exporter: (Your Company Name), South Korea
Target Item: {clean_item}
Price Term: FOB Busan / CIF Target Port
MOQ: 50~100 Cartons per Spec (초도 기준, 데이터 기반 TOP HS Code 참고)
Payment Term: Irrevocable L/C at sight or T/T 30% Deposit, 70% against B/L

Valid Until: 30 Days from Issue Date
======================================================================
```
*(품목별 상세 스펙/단가는 위 TOP {TOP_N_HS} HS Code 표의 데이터 산출값을 참고해 채워 넣으세요.)*

### ✉️ 부록 2. 해외 바이어 콜드 어프로치 파이프라인 (Cold Email Template)
```text
Subject: [Direct Offer] Premium Korean {clean_item} Supply for {{Target Country}} Market

Dear Procurement Manager,

I am writing to introduce our company, a Korean exporter of premium {clean_item}.
Based on UN Comtrade trade statistics, we identified {{Target Country}} as one of the
most promising markets for this product category.

Would you be open for a short 10-minute introduction call next week to discuss a
tailored B2B offer?

Best regards,
Export Manager
```

### 🗓️ 부록 3. 글로벌 수산/식품 전시회 & 박람회 참고 캘린더
| 박람회 명칭 | 통상 개최 시기 | 개최 도시 / 국가 | 타깃 바이어 성격 |
| :--- | :--- | :--- | :--- |
| **Seafood Expo North America** | 매년 3월경 | 미국 보스턴 | 북미 대형 유통 벤더, 아시안 마트 수입상 |
| **Seafood Expo Global** | 매년 4~5월경 | 스페인 바르셀로나 | 유럽 전역 수산물 디스트리뷰터 |
| **서울국제식품산업대전 (SEOUL FOOD)** | 매년 5월경 | 대한민국 일산 KINTEX | 글로벌 수산물 해외 바이어 초청상담회 |

*(정확한 일정/장소는 매년 변경되므로 개최기관 공식 홈페이지에서 반드시 재확인하세요.)*
"""

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(full_md)

    print(f"🎉 데이터 기반 범용 EDA 리포트 생성 완료: {report_file}")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="범용 무역 EDA 엔진")
    parser.add_argument("--input", type=str, required=True, help="취합된 무역 CSV 파일 경로")
    parser.add_argument("--item", type=str, default="품목", help="품목명")
    parser.add_argument("--output_dir", type=str, default="output", help="출력 프로젝트 폴더")
    parser.add_argument("--item_slug", type=str, default=None, help="데이터/리포트 파일명 슬러그 (생략 시 --item에서 자동 생성)")
    args = parser.parse_args()

    ok = generate_trade_eda(args.input, args.item, args.output_dir, args.item_slug)
    sys.exit(0 if ok else 1)
