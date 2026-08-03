"""
UN Comtrade 등 무역 통계 CSV를 입력받아 17개 데이터 기반 시각화 차트와
TOP 10 HS Code별 TOP 10 유망 타겟시장 11대 명세 분석표, 자국(--home_country) 수출
포지션 벤치마크, 신시장 개척 TOP 5, 적정 수출단가 산출, 1인 상사 시장개척 전략을
자동 산출하는 범용 무역 EDA 엔진.

설계 원칙:
- 입력 CSV의 컬럼명이 raw UN Comtrade 스키마든, 단순화된 수집기 스키마든 모두 인식한다.
- flowDesc(Import/Export)를 반드시 구분해서 처리한다. Import 행에서 reporter는 "수입국
  (타겟시장 후보)", partner는 "원산지(경쟁 수출국)"이고, Export 행은 그 반대다. 이 둘을
  구분 없이 섞으면 "TOP 10 수출국/수입국" 랭킹이 실제로는 뒤바뀐 값을 보여주는 치명적
  오류로 이어진다 (실사용 데이터에서 확인된 문제).
- primaryValue는 Comtrade 정의상 Export 행=FOB, Import 행=CIF 값이 이미 자동 반영되어
  있으므로 별도 fob/cif 컬럼 추출 없이 unit_price를 그대로 가격 비교에 사용할 수 있다.
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

# 자체 수입 통계를 신뢰도 있게 보고하지 않거나, 물류/재수출 허브 특성상 최종 소비지가
# 아닐 가능성이 높아 "유망시장"으로 오판하기 쉬운 국가. 데이터에서 제외하지는 않고
# 표에 경고 배지만 붙인다 (실제로 물류 거점 역할을 하는 진짜 시장일 수도 있으므로).
RE_EXPORT_HUBS = {'Hong Kong', 'Singapore', 'Netherlands', 'United Arab Emirates', 'Belgium', 'Panama'}


def flag_hub(name):
    return f"{name} ⚠️재수출허브" if name in RE_EXPORT_HUBS else name


def cagr_pct(first, last, n_years):
    """연평균복합성장률(CAGR, %). 관측 기간이 다른 시장을 같은 기준으로 비교하려면
    단순 누적성장률((마지막-첫)/첫) 대신 CAGR을 써야 한다 — 2년치 데이터의 300% 성장과
    5년치 데이터의 300% 성장은 전혀 다른 의미이기 때문이다."""
    if n_years is None or n_years <= 0:
        return np.nan
    if pd.isna(first) or pd.isna(last) or first <= 0:
        return np.nan
    return (((last / first) ** (1.0 / n_years)) - 1) * 100


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

def generate_trade_eda(csv_input, item_name, output_dir, item_slug=None, home_country="Korea"):
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

    # =====================================================================
    # ⭐ flowDesc 기반 분리 — 이 스킬의 핵심 수정 사항
    # Import 행: reporter=수입국(타겟시장 후보), partner=원산지(경쟁 수출국)
    # Export 행: reporter=수출국, partner=목적지. 실무에서는 대개 reporter가
    # home_country(자국) 단독이거나(자국 벤치마크 전용 수집) 전세계(reporter=all,
    # 진짜 글로벌 수출 통계)로 수집된다 — 아래 로직은 둘 다 지원한다.
    # =====================================================================
    flow_present = flow_col != '_flow_fallback'
    if flow_present:
        flow_low = df[flow_col].astype(str).str.lower()
        imp_df = df[flow_low.str.contains('import', na=False)].copy()
        exp_df = df[flow_low.str.contains('export', na=False)].copy()
    else:
        imp_df = df.copy()
        exp_df = df.iloc[0:0].copy()

    flow_split_ok = flow_present and not imp_df.empty
    if not flow_split_ok:
        imp_df = df.copy()
        flow_warning_md = (
            "> ⚠️ 입력 CSV에 `flowDesc`(Import/Export) 컬럼이 없어 수출입 방향을 구분하지 못했습니다. "
            "아래 시장/국가 분석은 방향 구분 없이 전체 데이터를 대상으로 한 참고용 결과이며, "
            "실제 수출국/수입국 라벨이 뒤바뀌어 있을 수 있습니다. `flowDesc` 컬럼이 포함된 "
            "UN Comtrade 원본 CSV를 사용하시길 권장합니다."
        )
    else:
        flow_warning_md = (
            f"> ℹ️ 데이터 처리 방식: 전체 {len(df):,}행 중 Import {len(imp_df):,}행 / Export {len(exp_df):,}행으로 "
            "분리해 처리했습니다. **Import 행은 reporter=수입국(타겟시장 후보), partner=원산지(경쟁 수출국)**로, "
            f"**Export 행은 reporter=수출국, partner=목적지**로 해석합니다."
        )

    # ---- 최신 연도 보고 지연(under-reporting) 감지: 순위/성장률 계산에서만 제외 ----
    imp_df_ranked = imp_df
    excluded_year_note = None
    if year_col and not imp_df.empty:
        reporters_per_year = imp_df.groupby(year_col)[reporter_col].nunique().sort_index()
        if len(reporters_per_year) >= 2:
            last_y, prev_y = reporters_per_year.index[-1], reporters_per_year.index[-2]
            if reporters_per_year.loc[last_y] < reporters_per_year.loc[prev_y] * 0.6:
                imp_df_ranked = imp_df[imp_df[year_col] != last_y]
                excluded_year_note = (
                    f"⚠️ **{last_y}년은 보고국 수가 {int(reporters_per_year.loc[last_y])}개국**으로 직전연도"
                    f"({prev_y}년, {int(reporters_per_year.loc[prev_y])}개국) 대비 급감했습니다. "
                    "UN Comtrade 특성상 최근 연도일수록 보고가 늦게 들어오는 시차 때문이며, "
                    "실제 수요 감소가 아닐 가능성이 높습니다. 이 연도는 TOP 시장 순위·성장률 계산에서 "
                    "제외했고(01번 연도별 추이 차트에는 참고용으로만 표시), 최신 시장 동향은 재수집 시 "
                    "다시 확인하시길 권장합니다."
                )

    # ---- 타겟 시장(수입국) 랭킹: Import 행의 reporter_col 기준 (핵심 방향 수정) ----
    # home_country 자신은 "내가 개척해야 할 타겟시장"이 될 수 없으므로 EXCLUDE_AGG와
    # 함께 제외한다 (수출국 랭킹(comp_grp)에는 그대로 남겨야 하므로 별도 리스트로 관리).
    home_match_names = {
        v for v in pd.concat([df[reporter_col], df[partner_col]]).dropna().astype(str).unique()
        if home_country.lower() in v.lower()
    }
    EXCLUDE_TARGET = EXCLUDE_AGG + list(home_match_names)
    mkt_grp = imp_df_ranked.groupby(reporter_col)['clean_value'].agg(sum_million=lambda x: x.sum() / 1e6, count='count')
    mkt_grp = mkt_grp[~mkt_grp.index.isin(EXCLUDE_TARGET)].sort_values(by='sum_million', ascending=False)
    top_market_df = mkt_grp.head(10)
    top5_markets = top_market_df.head(5).index.tolist()
    top8_markets = top_market_df.head(8).index.tolist()

    # ---- 글로벌 경쟁 수출국: Export가 reporter=all로 수집됐으면 직접, 아니면 Import의
    # partner(원산지) 집계로 간접 추정 (간접 추정임을 반드시 명시 — 데이터 조작 금지 원칙) ----
    exp_reporter_multi = (not exp_df.empty) and exp_df[reporter_col].nunique() > 1
    if exp_reporter_multi:
        comp_grp = exp_df.groupby(reporter_col)['clean_value'].agg(sum_million=lambda x: x.sum() / 1e6, count='count')
        comp_grp = comp_grp[~comp_grp.index.isin(EXCLUDE_AGG)].sort_values(by='sum_million', ascending=False).head(10)
        comp_source_note = "각 국가가 스스로 신고한 수출 실적 (Export를 reporter=all로 수집한 경우 — 직접 신고 기준, 신뢰도 높음)."
    else:
        comp_grp = imp_df_ranked.groupby(partner_col)['clean_value'].agg(sum_million=lambda x: x.sum() / 1e6, count='count')
        comp_grp = comp_grp[~comp_grp.index.isin(EXCLUDE_AGG)].sort_values(by='sum_million', ascending=False).head(10)
        comp_source_note = (
            "⚠️ **간접 추정치**입니다 — 각 수입국이 신고한 원산지(partner) 데이터를 합산한 것이며, "
            "경쟁 수출국 스스로의 수출 신고가 아닙니다. 정확도를 높이려면 Export 데이터를 "
            "`reporter=all`로 재수집하세요 (comtrade_api_collector.py의 `--reporter_code all` 옵션)."
        )

    # ---- 자국(home_country) 벤치마크: exp_df 직접 신고 우선, 없으면 imp_df 미러로 대체 추정 ----
    home_by = None
    home_source_note = None
    if not exp_df.empty and reporter_col in exp_df.columns:
        home_mask = exp_df[reporter_col].astype(str).str.contains(home_country, case=False, na=False)
        home_exp = exp_df[home_mask]
    else:
        home_exp = exp_df.iloc[0:0]

    if not home_exp.empty:
        home_by = home_exp.groupby(partner_col)  # partner = 수출 목적지
        home_source_note = f"`{home_country}`가 스스로 신고한 Export 데이터 기준 (직접 신고)."
    else:
        mirror_mask = imp_df[partner_col].astype(str).str.contains(home_country, case=False, na=False)
        home_mirror = imp_df[mirror_mask]
        if not home_mirror.empty:
            home_by = home_mirror.groupby(reporter_col)  # reporter = 상대국(수입국) = 목적지
            home_source_note = (
                f"`{home_country}` 자체 Export 신고가 없어, 상대국들이 \"`{home_country}`에서 수입했다\"고 "
                "신고한 Import 미러 데이터로 대체 추정한 결과입니다 (mirror statistics)."
            )
        else:
            home_source_note = (
                f"`{home_country}`에 대한 Export 신고 또는 Import 미러 데이터를 찾지 못했습니다. "
                f"--home_country 파라미터가 CSV의 국가명 표기와 일치하는지 확인하세요."
            )

    home_destinations = set(home_by.groups.keys()) if home_by is not None else set()

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
        title_suffix = ' (최신연도는 보고 지연 가능성 있음)' if excluded_year_note else ''
        ax.set_title(f'01. {clean_item} 연도별/거래유형별 무역액 추이 ($M){title_suffix}', fontsize=14, pad=15)
        ax.set_ylabel('무역액 (USD M)')
        ax.set_xlabel('연도')
        ax.grid(axis='y', linestyle='--', alpha=0.5)
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return piv

    charts_md['01'] = df_to_md(run_chart('01', chart_01))

    # =====================================================================
    # 02. TOP 10 글로벌 경쟁 수출국
    # =====================================================================
    def chart_02():
        path = os.path.join(img_dir, '02_top_exporter_ranking.png')
        if comp_grp.empty:
            save_placeholder(path, f'02. {clean_item} TOP 10 글로벌 경쟁 수출국')
            return None
        fig, ax = plt.subplots(figsize=(10, 5))
        comp_grp['sum_million'].plot(kind='barh', ax=ax, color='#2ca02c')
        ax.invert_yaxis()
        ax.set_title(f'02. {clean_item} TOP 10 글로벌 경쟁 수출국 ($M)', fontsize=14, pad=15)
        ax.set_xlabel('무역액 (USD M)')
        ax.grid(axis='x', linestyle='--', alpha=0.5)
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return comp_grp

    charts_md['02'] = df_to_md(run_chart('02', chart_02)) + f"\n\n{comp_source_note}"

    # =====================================================================
    # 03. TOP 10 유망 타겟 시장 (수입국)
    # =====================================================================
    def chart_03():
        path = os.path.join(img_dir, '03_top_importer_ranking.png')
        if top_market_df.empty:
            save_placeholder(path, f'03. {clean_item} TOP 10 유망 타겟시장')
            return None
        fig, ax = plt.subplots(figsize=(10, 5))
        top_market_df['sum_million'].plot(kind='barh', ax=ax, color='#ff7f0e')
        ax.invert_yaxis()
        ax.set_title(f'03. {clean_item} TOP 10 유망 타겟시장(수입국) 무역액 ($M)', fontsize=14, pad=15)
        ax.set_xlabel('무역액 (USD M)')
        ax.grid(axis='x', linestyle='--', alpha=0.5)
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return top_market_df

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
    # 08. TOP 5 유망 타겟시장 연도별 추이 (CAGR)
    # =====================================================================
    def chart_08():
        path = os.path.join(img_dir, '08_top5_importer_growth.png')
        if not year_col or not top5_markets:
            save_placeholder(path, f'08. {clean_item} TOP5 타겟시장 연도별 추이', "연도 정보 또는 타겟시장 데이터가 부족합니다.")
            return None
        piv = imp_df_ranked[imp_df_ranked[reporter_col].isin(top5_markets)].pivot_table(
            index=year_col, columns=reporter_col, values='clean_value', aggfunc='sum', fill_value=0
        ) / 1e6
        if piv.shape[0] < 2:
            save_placeholder(path, f'08. {clean_item} TOP5 타겟시장 연도별 추이', "추이를 그리기에 연도 수가 부족합니다.")
            return None
        fig, ax = plt.subplots(figsize=(10, 5))
        piv.plot(kind='line', marker='o', ax=ax)
        ax.set_title(f'08. {clean_item} TOP 5 유망 타겟시장 연도별 무역액 추이 ($M)', fontsize=14, pad=15)
        ax.set_ylabel('무역액 (USD M)')
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        n_years = piv.index.max() - piv.index.min()
        cagr = pd.Series({c: cagr_pct(piv[c].iloc[0], piv[c].iloc[-1], n_years) for c in piv.columns}).round(1)
        return pd.DataFrame({'시작년도($M)': piv.iloc[0], '최종년도($M)': piv.iloc[-1], 'CAGR(%)': cagr})

    charts_md['08'] = df_to_md(run_chart('08', chart_08))

    # =====================================================================
    # 09. 시장 집중도 파레토 차트 (80/20)
    # =====================================================================
    def chart_09():
        path = os.path.join(img_dir, '09_market_concentration_pareto.png')
        if top_market_df.empty:
            save_placeholder(path, f'09. {clean_item} 시장 집중도 파레토')
            return None
        p_sum = top_market_df['sum_million']
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
    # 10. 주요 타겟시장별/연도별 단가 변화 히트맵
    # =====================================================================
    def chart_10():
        path = os.path.join(img_dir, '10_export_price_heatmap.png')
        if not year_col or not top5_markets:
            save_placeholder(path, f'10. {clean_item} 타겟시장별/연도별 단가 히트맵', "연도 정보 또는 타겟시장 데이터가 부족합니다.")
            return None
        sub = imp_df_ranked[imp_df_ranked[reporter_col].isin(top5_markets) & imp_df_ranked['unit_price'].notna()
                             & np.isfinite(imp_df_ranked['unit_price'])]
        piv = sub.pivot_table(index=reporter_col, columns=year_col, values='unit_price', aggfunc='mean')
        if piv.empty:
            save_placeholder(path, f'10. {clean_item} 타겟시장별/연도별 단가 히트맵')
            return None
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.heatmap(piv, annot=True, fmt=".1f", cmap='YlOrRd', ax=ax)
        ax.set_title(f'10. {clean_item} 주요 타겟시장별/연도별 평균 수입단가 변화 ($/kg)', fontsize=14, pad=15)
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
            # flow 구분이 없으면 상위 5개 타겟시장의 무역액 기여도를 누적 폭포수로 표현
            top5 = top_market_df.head(5)['sum_million']
            if top5.empty:
                save_placeholder(path, f'11. {clean_item} 무역 수지 폭포수')
                return None
            labels = top5.index.tolist()
            values = top5.values
            title_suffix = '(TOP5 타겟시장 누적 기여도)'

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
    # 12. 타겟시장별 단가 변동성 박스플롯
    # =====================================================================
    def chart_12():
        path = os.path.join(img_dir, '12_country_price_boxplot.png')
        sub = imp_df_ranked[imp_df_ranked[reporter_col].isin(top8_markets) & imp_df_ranked['unit_price'].notna()
                             & np.isfinite(imp_df_ranked['unit_price'])]
        if sub.empty:
            save_placeholder(path, f'12. {clean_item} 타겟시장별 단가 변동성')
            return None
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.boxplot(data=sub, x=reporter_col, y='unit_price', hue=reporter_col,
                    order=top8_markets, palette='Set2', legend=False, ax=ax)
        ax.set_title(f'12. {clean_item} TOP 8 타겟시장 수입단가($/kg) 변동성 박스플롯', fontsize=14, pad=15)
        ax.tick_params(axis='x', rotation=30)
        ax.set_xlabel('')
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return sub.groupby(reporter_col)['unit_price'].agg(['mean', 'std', 'median', 'max']).loc[
            [c for c in top8_markets if c in sub[reporter_col].unique()]
        ]

    charts_md['12'] = df_to_md(run_chart('12', chart_12))

    # =====================================================================
    # 13. 수요 집중도(HHI Index) 연도별 추이 — 소수 타겟시장에 수요가 쏠려있는가
    # =====================================================================
    def chart_13():
        path = os.path.join(img_dir, '13_hhi_index_trend.png')
        if not year_col:
            save_placeholder(path, f'13. {clean_item} 수요 집중도(HHI) 추이', "연도 컬럼이 없어 생략합니다.")
            return None
        piv = imp_df.pivot_table(index=year_col, columns=reporter_col, values='clean_value', aggfunc='sum', fill_value=0)
        if piv.empty:
            save_placeholder(path, f'13. {clean_item} 수요 집중도(HHI) 추이')
            return None
        row_sum = piv.sum(axis=1)
        hhi_s = piv.div(row_sum.replace(0, np.nan), axis=0).pow(2).sum(axis=1) * 10000
        hhi_s = hhi_s.dropna()
        if hhi_s.empty:
            save_placeholder(path, f'13. {clean_item} 수요 집중도(HHI) 추이')
            return None
        fig, ax = plt.subplots(figsize=(10, 5))
        hhi_s.plot(kind='line', marker='s', color='darkblue', ax=ax)
        ax.set_title(f'13. {clean_item} 타겟시장 수요 집중도(HHI Index) 연도별 추이', fontsize=14, pad=15)
        ax.set_ylabel('HHI Index (소수 시장 쏠림 정도)')
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return hhi_s.round(0).to_frame(name='HHI_Index')

    charts_md['13'] = df_to_md(run_chart('13', chart_13))

    # =====================================================================
    # 14. 데이터 기반 가격대(4분위) 구조 — 실제 사이즈/규격 데이터는 아님
    # =====================================================================
    def chart_14():
        path = os.path.join(img_dir, '14_size_pricing_structure.png')
        prices = df['unit_price'].replace([np.inf, -np.inf], np.nan).dropna()
        if len(prices) < 4:
            save_placeholder(path, f'14. {clean_item} 가격대(4분위) 구조', "단가 표본이 부족하여 구간을 나눌 수 없습니다.")
            return None
        try:
            tiers = pd.qcut(prices, 4, labels=['Economy(하위 25%)', 'Standard(25~50%)', 'Premium(50~75%)', 'Ultra-Premium(상위 25%)'])
        except ValueError:
            save_placeholder(path, f'14. {clean_item} 가격대(4분위) 구조', "단가 값의 분산이 낮아 4분위 구간을 나눌 수 없습니다.")
            return None
        tier_avg = prices.groupby(tiers, observed=True).mean().sort_values()
        fig, ax = plt.subplots(figsize=(10, 5))
        tier_avg.plot(kind='barh', color='#bcbd22', ax=ax)
        ax.set_title(f'14. {clean_item} 단가 기준 가격대(4분위) 구조 ($/kg)', fontsize=14, pad=15)
        ax.set_xlabel('평균 단가 ($/kg, 데이터 산출값 — 실제 사이즈/규격 데이터 아님)')
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return tier_avg.to_frame(name='평균단가($/kg)')

    charts_md['14'] = df_to_md(run_chart('14', chart_14))

    # =====================================================================
    # 15. 유망 타겟시장 성장성 vs 단가 포지셔닝 매트릭스
    # =====================================================================
    def chart_15():
        path = os.path.join(img_dir, '15_promising_country_matrix.png')
        candidates = top_market_df.head(5).index.tolist()
        if not candidates:
            save_placeholder(path, f'15. {clean_item} 유망 타겟시장 매트릭스')
            return None
        avg_price = imp_df_ranked[imp_df_ranked[reporter_col].isin(candidates)].groupby(reporter_col)['unit_price'].mean()
        growth = pd.Series(0.0, index=candidates)
        if year_col:
            piv = imp_df_ranked[imp_df_ranked[reporter_col].isin(candidates)].pivot_table(
                index=year_col, columns=reporter_col, values='clean_value', aggfunc='sum', fill_value=0
            )
            if piv.shape[0] >= 2:
                n_years = piv.index.max() - piv.index.min()
                growth = pd.Series({c: cagr_pct(piv[c].iloc[0], piv[c].iloc[-1], n_years) for c in piv.columns}).reindex(candidates)
        result = pd.DataFrame({
            'CAGR(%)': growth.round(1),
            '평균단가($/kg)': avg_price.reindex(candidates).round(1),
        }).dropna(how='all')
        result['CAGR(%)'] = result['CAGR(%)'].fillna(0)
        result['평균단가($/kg)'] = result['평균단가($/kg)'].fillna(0)
        fig, ax = plt.subplots(figsize=(10, 5))
        colors = plt.cm.tab10.colors
        ax.scatter(result['CAGR(%)'], result['평균단가($/kg)'], s=500,
                   c=[colors[i % len(colors)] for i in range(len(result))], alpha=0.7)
        for i, (name, row) in enumerate(result.iterrows()):
            ax.annotate(str(name), (row['CAGR(%)'], row['평균단가($/kg)']),
                        fontsize=11, weight='bold', xytext=(5, 5), textcoords='offset points')
        ax.set_title(f'15. {clean_item} 유망 타겟시장 성장성(CAGR) vs 단가 포지셔닝', fontsize=14, pad=15)
        ax.set_xlabel('CAGR (연평균복합성장률, %)')
        ax.set_ylabel('평균 단가 ($/kg)')
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return result

    charts_md['15'] = df_to_md(run_chart('15', chart_15))

    # =====================================================================
    # 16. (신규) home_country 수출단가 vs 시장평균 수입단가 포지셔닝
    # =====================================================================
    def chart_16():
        path = os.path.join(img_dir, '16_home_price_positioning.png')
        if home_by is None:
            save_placeholder(path, f'16. {home_country} 가격 포지셔닝', "Export/미러 데이터가 없어 산출할 수 없습니다.")
            return None
        targets = list(dict.fromkeys(top5_markets + [m for m in home_destinations if m in top_market_df.index][:5]))[:6]
        rows = []
        for m in targets:
            mkt_sub = imp_df_ranked[imp_df_ranked[reporter_col] == m]
            mkt_price = mkt_sub['unit_price'].replace([np.inf, -np.inf], np.nan).dropna().mean()
            home_price = np.nan
            if m in home_by.groups:
                hp = home_by.get_group(m)['unit_price'].replace([np.inf, -np.inf], np.nan).dropna()
                if not hp.empty:
                    home_price = hp.mean()
            if pd.notna(mkt_price) or pd.notna(home_price):
                rows.append({'시장': m, f'{home_country} 단가': home_price, '시장평균 단가': mkt_price})
        if not rows:
            save_placeholder(path, f'16. {home_country} 가격 포지셔닝', "비교 가능한 단가 데이터가 부족합니다.")
            return None
        pos_df = pd.DataFrame(rows).set_index('시장')
        fig, ax = plt.subplots(figsize=(10, 5))
        pos_df.plot(kind='bar', ax=ax, color=['#1f77b4', '#d62728'])
        ax.set_title(f'16. {home_country} 수출단가 vs 시장평균 수입단가 포지셔닝 ($/kg)', fontsize=14, pad=15)
        ax.set_ylabel('단가 ($/kg)')
        ax.tick_params(axis='x', rotation=20)
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        return pos_df.round(1)

    charts_md['16'] = df_to_md(run_chart('16', chart_16))
    if home_source_note:
        charts_md['16'] += f"\n\n{home_source_note}"

    # =====================================================================
    # 17. (신규) TOP 유망시장 공급국 집중도(HHI) — 레드오션/블루오션 판별
    # =====================================================================
    def market_supplier_hhi(market_name):
        sub = imp_df_ranked[imp_df_ranked[reporter_col] == market_name]
        supplier_val = sub.groupby(partner_col)['clean_value'].sum()
        supplier_val = supplier_val[~supplier_val.index.isin(EXCLUDE_AGG)]
        total = supplier_val.sum()
        if total <= 0 or supplier_val.empty:
            return np.nan, None
        shares = supplier_val / total
        hhi = (shares ** 2).sum() * 10000
        top_supplier = supplier_val.sort_values(ascending=False).index[0]
        return hhi, top_supplier

    def chart_17():
        path = os.path.join(img_dir, '17_market_supplier_hhi.png')
        if top_market_df.empty:
            save_placeholder(path, f'17. {clean_item} 타겟시장 공급국 집중도(HHI)')
            return None
        rows = []
        for m in top_market_df.index:
            hhi_val, top_sup = market_supplier_hhi(m)
            rows.append({'시장': m, 'HHI': hhi_val, '최대 공급국': top_sup})
        hhi_df_local = pd.DataFrame(rows).dropna(subset=['HHI']).set_index('시장')
        if hhi_df_local.empty:
            save_placeholder(path, f'17. {clean_item} 타겟시장 공급국 집중도(HHI)', "공급국 데이터가 부족합니다.")
            return None

        def band_color(v):
            return '#d62728' if v >= 2500 else ('#ff7f0e' if v >= 1500 else '#2ca02c')

        fig, ax = plt.subplots(figsize=(10, 5))
        colors = [band_color(v) for v in hhi_df_local['HHI']]
        ax.barh(hhi_df_local.index, hhi_df_local['HHI'], color=colors)
        ax.invert_yaxis()
        ax.axvline(2500, color='red', linestyle='--', alpha=0.4, linewidth=1)
        ax.axvline(1500, color='orange', linestyle='--', alpha=0.4, linewidth=1)
        ax.set_title(f'17. {clean_item} TOP 유망시장 공급국 집중도(HHI) — 레드오션(≥2500) / 중간(1500~2500) / 블루오션(<1500)', fontsize=12, pad=15)
        ax.set_xlabel('HHI Index (공급국 쏠림 정도, 높을수록 소수 국가 과점)')
        fig.tight_layout()
        fig.savefig(path, dpi=200)
        plt.close(fig)
        hhi_df_local['판정'] = hhi_df_local['HHI'].apply(
            lambda v: '🔴레드오션(과점)' if v >= 2500 else ('🟠중간' if v >= 1500 else '🟢블루오션(분산)')
        )
        hhi_df_local['최대 공급국'] = hhi_df_local['최대 공급국'].apply(flag_hub)
        return hhi_df_local.round(0)

    charts_md['17'] = df_to_md(run_chart('17', chart_17))

    plt.close('all')

    # =====================================================================
    # 동적 TOP-N HS Code별 유망 타겟시장 11대 명세 표
    # ⭐ 기존에는 partner_col(원산지)로 잘못 그룹핑되던 것을 reporter_col(타겟시장)로 수정
    # =====================================================================
    def build_country_table(hs_code):
        sub = imp_df_ranked[imp_df_ranked['hs_clean'] == hs_code]
        tot = sub['clean_value'].sum()
        if sub.empty or tot <= 0:
            return "| - | 데이터 없음 | 해당 HS 분류의 유효 거래 데이터가 없습니다 | - | - | - | - | - | - | - | - |\n"
        grp = sub.groupby(reporter_col).agg(val=('clean_value', 'sum'), wgt=('clean_wgt', 'sum'), price=('unit_price', 'mean'))
        grp = grp[~grp.index.isin(EXCLUDE_TARGET)].sort_values(by='val', ascending=False).head(10)
        rows = ""
        for rank, (country, row) in enumerate(grp.iterrows(), 1):
            v_m = row['val'] / 1e6
            w_t = row['wgt'] / 1e3 if pd.notna(row['wgt']) else 0
            share = (row['val'] / tot * 100) if tot else 0
            price = row['price']
            if pd.isna(price) or not np.isfinite(price):
                price = (row['val'] / row['wgt']) if row['wgt'] else np.nan
            price_txt = f"${price:.1f}/kg" if pd.notna(price) and np.isfinite(price) else "산출불가(중량 데이터 부족)"

            explored_tag = f"{home_country} 기수출★" if country in home_destinations else "미개척☆"
            reason = f"수입액 ${v_m:,.1f}M ({share:.1f}%), 물량 {w_t:,.0f}톤 · {explored_tag}"
            country_label = flag_hub(country)
            partner = f"{country} 현지 {clean_item} 전문 수입 도매상/식품 유통 벤더 *(실사 확인 필요)*"
            comp_price = f"현지 평균 도매가 {price_txt} 수준 *(경쟁 제품 벤치마크는 데이터 미포함, 별도 조사 필요)*"
            hscode_tariff = f"HS {hs_code} — {hs_desc(hs_code)[:40]} *(관세율은 부록의 FTA 매트릭스 참고, 최신 협정세율 별도 확인)*"
            cert = "HACCP, ISO22000 등 위생안전 인증 및 시험성적서(COA) *(품목별 요건 별도 확인)*"
            non_tariff = "SPS(위생검역) 증명서, 현지어 라벨링 규정 등 *(비관세장벽 사전 확인 필요)*"
            channel = f"{country} 식품 도매시장, 전문 유통망, 대형 리테일 벤더 *(현지 조사 권장)*"
            margin = "중간 유통상 마진 15~25%, 소매 마진 25~40% *(업계 평균 추정치)*"
            logistics = "냉장/냉동 콜드체인 해상 또는 항공 운송 *(품목 특성별 별도 검토)*"

            rows += (f"| **{rank}위** | **{country_label}** | {reason} | {partner} | {comp_price} | {hscode_tariff} | "
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
        f"### 📌 [표 {i}] {hs_labels[i]} TOP 10 유망 타겟시장 11대 명세 표\n\n"
        f"| 유망순위 | 국가명 | 구체적 근거 (수입액/물량/{home_country} 진출여부) | 컨택해야 할 로컬 파트너 | 경쟁 제품/가격대 (도매가) | HS Code 및 관세율 | 필수 인증 및 허가 | 비관세 장벽 (SPS/라벨링) | 주요 유통 채널 | 중간 유통상 생태계 & 마진율 | 물류 및 콜드체인 인프라 |\n"
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
        grp = imp_df_ranked.groupby(reporter_col).agg(val=('clean_value', 'sum'), price=('unit_price', 'mean'))
        grp = grp[~grp.index.isin(EXCLUDE_TARGET)].sort_values(by='val', ascending=False)
        if grp.empty:
            return "데이터 부족으로 시장 전략을 산출할 수 없습니다. CSV의 reporterDesc/importer 컬럼을 확인하세요."

        volume_market = grp.index[0]
        if grp['price'].notna().any():
            premium_market = grp[grp['price'].notna()].sort_values(by='price', ascending=False).index[0]
        else:
            premium_market = volume_market

        growth_market = None
        if year_col:
            candidates = grp.head(15).index.tolist()
            piv = imp_df_ranked[imp_df_ranked[reporter_col].isin(candidates)].pivot_table(
                index=year_col, columns=reporter_col, values='clean_value', aggfunc='sum', fill_value=0
            )
            if piv.shape[0] >= 2:
                n_years = piv.index.max() - piv.index.min()
                g = pd.Series({c: cagr_pct(piv[c].iloc[0], piv[c].iloc[-1], n_years) for c in piv.columns}).dropna()
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

### ③ 시장 3: {growth_market} — [고성장 시장 (CAGR 기준)]
- **선정 근거**: 관측 기간 중 연평균복합성장률(CAGR)이 가장 두드러진 시장입니다. 신규 진입 시 선점 효과를 기대할 수 있습니다.

> ⚠️ 위 3대 시장은 무역 통계의 정량적 산출 결과이며, 실제 진출 전 현지 바이어 리서치, 인증/규제 요건, FTA 협정세율은 별도로 확인이 필요합니다."""

    market_3star_text = build_market_strategy()

    # =====================================================================
    # (신규) home_country 포지션 벤치마크 표
    # =====================================================================
    if home_by is not None and home_destinations:
        home_rows = []
        for dest, sub in home_by:
            if dest in EXCLUDE_AGG:
                continue
            val_sum = sub['clean_value'].sum()
            price_avg = sub['unit_price'].replace([np.inf, -np.inf], np.nan).dropna().mean()
            cagr_txt = "-"
            if year_col:
                yv = sub.groupby(year_col)['clean_value'].sum()
                if len(yv) >= 2:
                    n_years = yv.index.max() - yv.index.min()
                    c = cagr_pct(yv.iloc[0], yv.iloc[-1], n_years)
                    cagr_txt = f"{c:.1f}%" if pd.notna(c) else "-"
            home_rows.append({
                '목적지': flag_hub(dest),
                f'{home_country} 수출액($M)': round(val_sum / 1e6, 2),
                '평균단가($/kg)': round(price_avg, 1) if pd.notna(price_avg) else '산출불가',
                'CAGR': cagr_txt,
            })
        home_bench_df = pd.DataFrame(home_rows).sort_values(by=f'{home_country} 수출액($M)', ascending=False).head(15).set_index('목적지')
        home_benchmark_md = df_to_md(home_bench_df) + f"\n\n{home_source_note}"
    else:
        home_benchmark_md = f"데이터 없음. {home_source_note or ''}"

    # =====================================================================
    # (신규) 신시장 개척 TOP 5 — 유망 타겟시장 중 home_country 실적이 없는 곳을
    # 시장규모 순으로 최대 5개까지 선정 (top_market_df가 이미 시장규모 내림차순이므로
    # 순서 그대로 head(5)만 취하면 됨)
    # =====================================================================
    TOP_N_NEW_MARKET = 5
    unexplored_markets_all = [m for m in top_market_df.index if m not in home_destinations]
    unexplored_markets = unexplored_markets_all[:TOP_N_NEW_MARKET]
    if unexplored_markets:
        unexplored_rows = []
        for m in unexplored_markets:
            hhi_val, top_sup = market_supplier_hhi(m)
            unexplored_rows.append({
                '신시장 후보': flag_hub(m),
                '시장규모($M)': round(top_market_df.loc[m, 'sum_million'], 1),
                '현재 최대 공급국': flag_hub(top_sup) if top_sup else '확인불가',
                '공급국 집중도(HHI)': round(hhi_val, 0) if pd.notna(hhi_val) else '확인불가',
            })
        unexplored_md = df_to_md(pd.DataFrame(unexplored_rows).set_index('신시장 후보'))
        remaining_n = len(unexplored_markets_all) - len(unexplored_markets)
        remaining_note = f" (이 외에도 시장규모 기준 하위 미개척 시장 {remaining_n}곳 추가 존재)" if remaining_n > 0 else ""
        unexplored_md += (
            f"\n\n> 위 5곳은 TOP 유망 타겟시장 중 `{home_country}`의 수출 실적이 (직접 신고 또는 미러 데이터 기준) "
            f"확인되지 않은 곳을 시장규모 순으로 선정한 것입니다{remaining_note}. HHI가 낮을수록(공급국이 "
            "분산돼 있을수록) 신규 진입 장벽이 상대적으로 낮습니다."
        )
    else:
        unexplored_md = f"TOP 유망 타겟시장 전부에서 `{home_country}`의 수출 실적이 확인되어, 별도의 신시장 후보가 없습니다."

    # =====================================================================
    # (신규) 적정 수출단가(Target Price) 산출 표
    # =====================================================================
    price_rows = []
    for m in top_market_df.head(8).index:
        sub = imp_df_ranked[imp_df_ranked[reporter_col] == m]
        prices = sub['unit_price'].replace([np.inf, -np.inf], np.nan).dropna()
        if prices.empty:
            continue
        mkt_avg, mkt_std = prices.mean(), prices.std(ddof=0)
        home_val = np.nan
        if home_by is not None and m in home_by.groups:
            hp = home_by.get_group(m)['unit_price'].replace([np.inf, -np.inf], np.nan).dropna()
            if not hp.empty:
                home_val = hp.mean()
        low, high = max(mkt_avg - (mkt_std or 0), 0), mkt_avg + (mkt_std or 0)
        position_txt = "데이터 없음(미개척 또는 미러 없음)"
        if pd.notna(home_val) and mkt_avg > 0:
            diff_pct = (home_val - mkt_avg) / mkt_avg * 100
            position_txt = f"{'▲시장평균보다 비쌈' if diff_pct > 0 else '▼시장평균보다 저렴'} ({diff_pct:+.0f}%)"
        price_rows.append({
            '타겟시장': flag_hub(m),
            '시장평균 수입단가($/kg)': round(mkt_avg, 1),
            '권장 오퍼밴드($/kg)': f"${low:.1f} ~ ${high:.1f}",
            f'{home_country} 현재단가($/kg)': round(home_val, 1) if pd.notna(home_val) else '데이터없음',
            '포지션': position_txt,
        })
    if price_rows:
        price_band_md = df_to_md(pd.DataFrame(price_rows).set_index('타겟시장'))
        price_band_md += (
            "\n\n> 권장 오퍼밴드는 해당 시장의 수입단가 평균 ± 표준편차 구간입니다. "
            f"`{home_country}` 현재단가가 이 구간보다 높으면 인증/품질/브랜드로 프리미엄을 정당화해야 하고, "
            "낮으면 원가 경쟁력을 활용한 물량 확대 전략이 유리합니다. `primaryValue`는 Comtrade 정의상 "
            "Export 행=FOB, Import 행=CIF가 이미 반영된 값이므로 별도 환산 없이 그대로 비교했습니다."
        )
    else:
        price_band_md = "적정단가를 산출할 수 있는 유효 데이터가 부족합니다."

    # =====================================================================
    # (신규) 삼국무역(중계무역) 후보 매트릭스
    # home_country(A국) 소싱이 여의치 않을 때, 대체 소싱국(B) → 판매 타겟국(C/D)
    # 조합을 마진갭 기준으로 자동 랭킹한다. home_country는 이 거래에 끼지 않으므로
    # B/C/D 후보 모두에서 제외한다.
    # =====================================================================
    def origin_price_estimate(country):
        """country의 평균 판매(수출)단가 추정치와 신뢰도 라벨을 반환.
        Export가 reporter=all로 직접 신고돼 있으면 그 값을, 아니면 상대국들이
        '이 나라에서 수입했다'고 신고한 Import 미러 단가로 근사한다."""
        if exp_reporter_multi and country in exp_df[reporter_col].values:
            p = exp_df[exp_df[reporter_col] == country]['unit_price'].replace([np.inf, -np.inf], np.nan).dropna()
            if not p.empty:
                return p.mean(), '직접신고(FOB)'
        p2 = imp_df_ranked[imp_df_ranked[partner_col] == country]['unit_price'].replace([np.inf, -np.inf], np.nan).dropna()
        if not p2.empty:
            return p2.mean(), '간접추정(상대국 CIF 기준)'
        return np.nan, None

    def supplier_share_in_market(market, supplier):
        sub = imp_df_ranked[imp_df_ranked[reporter_col] == market]
        tot = sub['clean_value'].sum()
        if tot <= 0:
            return np.nan
        sup_val = sub[sub[partner_col] == supplier]['clean_value'].sum()
        return sup_val / tot * 100

    triangular_B = [c for c in comp_grp.index if c not in home_match_names][:5]
    triangular_C = [m for m in top_market_df.index][:5]

    tri_rows = []
    for b in triangular_B:
        b_price, b_conf = origin_price_estimate(b)
        if pd.isna(b_price) or b_price <= 0:
            continue
        for c in triangular_C:
            if b == c:
                continue
            c_sub = imp_df_ranked[imp_df_ranked[reporter_col] == c]
            c_prices = c_sub['unit_price'].replace([np.inf, -np.inf], np.nan).dropna()
            if c_prices.empty:
                continue
            c_price = c_prices.mean()
            margin_pct = (c_price - b_price) / b_price * 100
            b_share = supplier_share_in_market(c, b)
            if pd.isna(b_share) or b_share < 5:
                verdict = '🟢 화이트스페이스(B 미진출)' if margin_pct > 0 else '⚠️ 마진 근거 부족'
            else:
                verdict = f'🟡 이미 B 진출({b_share:.0f}%)' if margin_pct > 0 else '⚠️ 마진 근거 부족'
            tri_rows.append({
                'B(소싱국)': flag_hub(b),
                'C/D(판매국)': flag_hub(c),
                f'B 판매단가($/kg, {b_conf})': round(b_price, 1),
                'C/D 시장평균단가($/kg)': round(c_price, 1),
                '마진갭(%)': round(margin_pct, 0),
                'B의 현재 C/D 점유율(%)': round(b_share, 1) if pd.notna(b_share) else '0(미진출)',
                '판정': verdict,
            })

    if tri_rows:
        tri_df = pd.DataFrame(tri_rows).sort_values(by='마진갭(%)', ascending=False).head(10)
        triangular_md = df_to_md(tri_df.set_index(['B(소싱국)', 'C/D(판매국)']))
        triangular_md += (
            "\n\n> ⚠️ **반드시 확인 후 실행**: 위 표는 무역통계상 가격 갭만 보여줄 뿐, 실제 기회는 대부분 "
            "① B-C/D 간 신용/금융 공백, ② MOQ 미스매치, ③ 신뢰 중개 필요성에서 나옵니다 — 가격 갭만 "
            "보고 뛰어들면 이미 B가 직접 더 싸게 팔고 있는 시장일 수 있습니다. 또한 (1) 한국이 거래에 "
            f"끼지 않으므로 한국 FTA 협정세율이 전혀 적용되지 않고, (2) 외국환거래법상 **중계무역**은 "
            "일반 수출과 다른 별도 신고 절차(외국인수수입/외국인도수출)와 K-SURE 상품이 필요하며, "
            "(3) B/C/D가 제재 대상국인지 반드시 사전 확인해야 합니다. (4) 위 단가는 데이터셋에 포함된 "
            "전체 HS Code를 블렌딩한 평균입니다 — 광범위한 catch-all 코드가 섞여 있으면 왜곡될 수 있으니 "
            "위 \"TOP HS Code별 유망 타겟시장 11대 명세 표\"의 HS Code별 단가와 교차 확인하세요."
        )
    else:
        triangular_md = (
            "삼국무역 후보를 산출할 수 있는 데이터가 부족합니다 (경쟁 수출국/타겟시장 단가 데이터 필요). "
            "Export를 `reporter=all`로 수집하면 B의 판매단가가 간접추정이 아닌 직접신고 기준으로 정확해집니다."
        )

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

    caveats_md = flow_warning_md
    if excluded_year_note:
        caveats_md += f"\n>\n> {excluded_year_note}"

    full_md = f"""# 🌊 {input_basename} — {clean_item} 무역 데이터 종합 EDA 및 글로벌 영업전략 리포트

## 📌 Executive Summary

본 리포트는 `{input_basename}` {clean_item} 무역 데이터셋(총 {total_rec:,}행)을 대상으로 데이터 기반
**1인 종합상사 최적 개척 시장 3선 전략**, 무역액 기준 **동적 산출 TOP {TOP_N_HS} HS Code**별 **TOP 10 유망
타겟시장 11대 명세 분석표**, **`{home_country}` 포지션 벤치마크**, **신시장 개척 TOP 5**, **적정 수출단가 산출**,
**삼국무역(중계무역) 후보 매트릭스**, 그리고 **[TOP 5 실전 무역 고도화 패키지]**를 산출한 EDA 보고서입니다.

{caveats_md}

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

## 2. 세부 탐색적 데이터 분석 및 시각화 (17대 핵심 분석)

### 1. 연도별 글로벌 {clean_item} 수출입 거래 총액 추이
![1. 연도별 무역 추이](../images/01_annual_trade_trend.png)
**[분석 해석]**: 데이터셋 전체 누적 무역액은 ${total_val_m}M입니다. 연도별/거래유형별 세부 수치는 아래 표를 참고하세요.
{charts_md['01']}

### 2. TOP 10 글로벌 경쟁 수출국 분석
![2. TOP 10 경쟁 수출국](../images/02_top_exporter_ranking.png)
{charts_md['02']}

### 3. TOP 10 유망 타겟시장(수입국) 분석
![3. TOP 10 유망 타겟시장](../images/03_top_importer_ranking.png)
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

### 8. TOP 5 유망 타겟시장 연도별 무역액 추이 (CAGR)
![8. TOP5 타겟시장 추이](../images/08_top5_importer_growth.png)
{charts_md['08']}

### 9. 시장 집중도 파레토 (80/20)
![9. 파레토](../images/09_market_concentration_pareto.png)
{charts_md['09']}

### 10. 주요 타겟시장별/연도별 단가 변화 히트맵
![10. 히트맵](../images/10_export_price_heatmap.png)
{charts_md['10']}

### 11. 무역 수지 폭포수 차트
![11. 폭포수](../images/11_trade_balance_waterfall.png)
{charts_md['11']}

### 12. 타겟시장별 단가 변동성 박스플롯
![12. 박스플롯](../images/12_country_price_boxplot.png)
{charts_md['12']}

### 13. 연도별 수요 집중도(HHI) 추이
![13. HHI](../images/13_hhi_index_trend.png)
{charts_md['13']}

### 14. 데이터 기반 가격대(4분위) 구조
![14. 가격구조](../images/14_size_pricing_structure.png)
{charts_md['14']}

### 15. 유망 타겟시장 성장성(CAGR) vs 단가 포지셔닝 Matrix
![15. 유망시장](../images/15_promising_country_matrix.png)
{charts_md['15']}

### 16. {home_country} 수출단가 vs 시장평균 수입단가 포지셔닝 (가격 경쟁력)
![16. 가격 포지셔닝](../images/16_home_price_positioning.png)
{charts_md['16']}

### 17. TOP 유망시장 공급국 집중도(HHI) — 레드오션/블루오션 판별
![17. 공급국 HHI](../images/17_market_supplier_hhi.png)
{charts_md['17']}

---

# 👔 [특별 부록] 1인 종합상사 창업자를 위한 {clean_item} 글로벌 신시장 개척 실전 전략서

## 🇰🇷 {home_country} 포지션 벤치마크 (실측)

{home_country}가 현재 어느 시장에 실제로 얼마나, 어떤 단가로 수출하고 있는지의 벤치마크입니다.

{home_benchmark_md}

---

## 🆕 신시장 개척 TOP 5 (유망 타겟시장 중 {home_country} 미진출 상위 5개국)

{unexplored_md}

---

## 💰 적정 수출단가(Target Price) 산출

{price_band_md}

---

## 🔀 삼국무역(중계무역) 후보 매트릭스 — B국 소싱 → C/D국 판매

`{home_country}` 소싱이 여의치 않을 경우를 대비한 대안 전략입니다. `{home_country}`가 거래에 직접
끼지 않고, 대체 소싱국(B)의 물건을 타겟시장(C/D)에 중개하는 조합을 마진갭 기준으로 자동 랭킹합니다.

{triangular_md}

---

## 🎯 1. 1인 종합상사 최적 우선 개척 시장 3선 (데이터 기반 산출)

1인 기업의 한계(리스크 관리, 물류 부담, 자금 회수 주기)와 강점(빠른 의사결정, 맞춤형 바이어 대응)을 고려해
실제 무역 데이터에서 산출한 **Top 3 타깃 시장**은 다음과 같습니다:

{market_3star_text}

---

## 🗺️ 동적 산출 TOP {TOP_N_HS} HS Code별 TOP 10 유망 타겟시장 분석 표 (11대 명세 필드)

> ⚠️ 아래 표의 "구체적 근거", "경쟁 제품/가격대"는 데이터 산출값이며, 그 외 정성적 필드(파트너/인증/유통채널 등)는
> 업계 일반 템플릿으로 *(확인 필요)* 표기된 항목은 반드시 현지 리서치로 검증해야 합니다. ⚠️재수출허브 표기 국가는
> 최종 소비지가 아닐 수 있으니 우선순위 해석에 주의하세요.

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
*(품목별 상세 스펙/단가는 위 TOP {TOP_N_HS} HS Code 표 및 "적정 수출단가 산출" 표의 데이터 산출값을 참고해 채워 넣으세요.)*

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
    parser.add_argument("--home_country", type=str, default="Korea",
                         help="벤치마크 기준이 되는 자국(수출국) 이름. CSV의 reporterDesc/partnerDesc 표기에 포함되는 "
                              "부분 문자열이면 됨 (예: 'Korea'는 'Rep. of Korea'와 매칭)")
    args = parser.parse_args()

    ok = generate_trade_eda(args.input, args.item, args.output_dir, args.item_slug, args.home_country)
    sys.exit(0 if ok else 1)
