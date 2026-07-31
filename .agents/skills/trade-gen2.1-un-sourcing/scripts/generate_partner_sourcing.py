"""
trade-gen1-un-eda 스킬이 만든 EDA 리포트(TOP N HS Code x TOP 10 유망국가 표)를 파싱해,
데이터 기반 "소싱 후보국가 & 파트너 리서치 트래커"를 자동/누적 생성하는 범용 스킬.

설계 원칙 (중요):
- 이 스크립트는 실제 웹 검색/실사를 수행하지 않는다. 따라서 회사명·이메일·전화번호 같은
  "실제 파트너 컨택 정보"를 지어내서 채워 넣지 않는다. 예전 버전(BIZ-Jeonbok/src/
  partner_sourcing_agent.py)은 품목과 무관하게 항상 동일한 10개 하드코딩 가상 업체를
  "실존 검증 완료"라고 표시해 저장했는데, 이는 실제로 없는 이메일/전화번호를 마치 검증된
  진짜 데이터처럼 보이게 하는 심각한 데이터 신뢰성 문제였다.
- 대신 이 스크립트가 채우는 것은 EDA 리포트에서 실제로 산출된 값(국가, HS Code, 순위,
  수입액/물량)뿐이다. 회사명/이메일/웹사이트/메신저 등 사람이 직접 조사해야 하는 필드는
  빈 값 + "조사 상태"로 시작하고, 재실행할 때마다 사용자가 채워 넣은 값은 덮어쓰지 않는다.
- 품목/프로젝트 하드코딩 없이 --item, --output_dir, --eda_report 인자로 어떤 프로젝트
  폴더에서도 재사용 가능하다.
"""

import os
import sys
import re
import argparse
import datetime
from collections import defaultdict

import pandas as pd
import openpyxl  # noqa: F401  (pd.ExcelWriter engine 의존성)

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
else:
    # 리눅스 CI 러너가 non-UTF-8 로케일일 때 한글/이모지 print()가 UnicodeEncodeError로
    # 죽는 것을 방지 (GitHub Actions 등 무인 자동화 환경 방어)
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

# EDA 리포트에서 순수 파생되는 컬럼 (재실행 시 항상 최신 데이터로 갱신)
EDA_DERIVED_COLS = [
    '데이터 수집일',
    'EDA 데이터 근거 (HS Code별 순위/수입액/물량)',
    '후보 HS Code 수',
    '최고 순위',
    '우선순위 점수',
]
# 사람이 직접 조사해 채워야 하는 컬럼 (재실행해도 기존에 입력된 값은 보존)
USER_EDITABLE_COLS = [
    '조사 상태',
    '후보 파트너/에이전트명',
    '회사 이메일',
    '웹사이트 / LinkedIn',
    'Messenger',
    '본사 위치',
    '비고/메모',
]
LEAD_COLUMNS = ['국가 (Country)'] + EDA_DERIVED_COLS + USER_EDITABLE_COLS
NEW_CANDIDATE_STATUS = '🆕 신규 후보 (미착수)'
EMPTY_EDITABLE = {
    '조사 상태': NEW_CANDIDATE_STATUS,
    '후보 파트너/에이전트명': '',
    '회사 이메일': '',
    '웹사이트 / LinkedIn': '',
    'Messenger': '',
    '본사 위치': '',
    '비고/메모': '',
}


def print_error(missing, required_by, action):
    print("[ERROR]: Required file not found or unreadable")
    print(f"- Missing: {missing}")
    print(f"- Required by: {required_by}")
    print(f"- Action: {action}")


# ---------------------------------------------------------------------------
# 1. EDA 리포트 파서
# ---------------------------------------------------------------------------

def parse_eda_report_tables(report_path):
    """generate_trade_eda.py(trade-gen1-un-eda 스킬)가 만든
    '### 📌 [표 N] HS ... TOP 10 유망 국가 11대 명세 표' 섹션들을 파싱해
    (table_num, hs_label, rank, country, reason) 레코드 리스트로 반환한다."""
    if not os.path.exists(report_path):
        return []

    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    header_re = re.compile(r"^###\s*(?:📌\s*)?\[표\s*(\d+)\]\s*(.+?)\s*TOP 10 유망")

    parsed = []
    current_table_num = None
    current_hs_label = None

    for line in content.split('\n'):
        header_match = header_re.match(line.strip())
        if header_match:
            current_table_num = int(header_match.group(1))
            current_hs_label = header_match.group(2).strip()
            continue

        # 다른 ## / ### 헤딩이나 구분선(---)을 만나면 표 구간을 벗어난 것으로 간주해
        # 리포트 뒤쪽의 무관한 다른 마크다운 표(FTA 매트릭스 등)가 섞여 들어가는 것을 방지
        stripped = line.strip()
        if stripped.startswith('#') or stripped == '---':
            current_table_num = None
            current_hs_label = None
            continue

        if current_table_num is None or not stripped.startswith('|'):
            continue
        if '유망순위' in stripped or ':---' in stripped:
            continue

        cols = [c.strip() for c in stripped.split('|')[1:-1]]
        if len(cols) < 3:
            continue

        rank_str = cols[0].replace('*', '').replace('위', '').strip()
        try:
            rank_num = int(rank_str)
        except ValueError:
            continue  # "- | 데이터 없음 | ..." 같은 플레이스홀더 행

        country = cols[1].replace('*', '').strip()
        if not country or country == '데이터 없음':
            continue
        reason = cols[2].strip()

        parsed.append({
            'table_num': current_table_num,
            'hs_label': current_hs_label,
            'rank': rank_num,
            'country': country,
            'reason': reason,
        })

    return parsed


# ---------------------------------------------------------------------------
# 2. 국가별 소싱 후보 집계
# ---------------------------------------------------------------------------

def build_candidate_rows(parsed_rows, now_str):
    agg = defaultdict(lambda: {'best_rank': 10 ** 9, 'appearances': []})
    for row in parsed_rows:
        a = agg[row['country']]
        a['best_rank'] = min(a['best_rank'], row['rank'])
        a['appearances'].append(row)

    records = []
    for country, a in agg.items():
        n_hs = len(a['appearances'])
        best_rank = a['best_rank']
        # 우선순위 점수: 여러 HS Code에서 동시에 상위권일수록, 순위가 높을수록(숫자가 작을수록) 가점
        priority_score = n_hs * 100 - best_rank
        reasons = "; ".join(
            f"[{r['hs_label']}] {r['rank']}위 - {r['reason']}"
            for r in sorted(a['appearances'], key=lambda x: (x['table_num'], x['rank']))
        )
        record = {
            '국가 (Country)': country,
            '데이터 수집일': now_str,
            'EDA 데이터 근거 (HS Code별 순위/수입액/물량)': reasons,
            '후보 HS Code 수': n_hs,
            '최고 순위': best_rank,
            '우선순위 점수': priority_score,
        }
        record.update(EMPTY_EDITABLE)
        records.append(record)

    records.sort(key=lambda r: -r['우선순위 점수'])
    return records


def load_existing_leads(excel_path):
    if not os.path.exists(excel_path):
        return pd.DataFrame(columns=LEAD_COLUMNS), pd.DataFrame()
    try:
        df_leads = pd.read_excel(excel_path, sheet_name='Sourcing_Candidates')
        df_history = pd.read_excel(excel_path, sheet_name='Sourcing_History')
    except Exception as e:
        print(f"⚠️ 기존 엑셀을 읽는 데 실패해 새로 시작합니다: {e}")
        return pd.DataFrame(columns=LEAD_COLUMNS), pd.DataFrame()

    if '국가 (Country)' not in df_leads.columns:
        # 구버전(회사명 하드코딩) 스키마와 호환되지 않으므로 새 스키마로 새로 시작한다.
        # (구버전 파일은 git 이력에 그대로 남아있어 필요하면 되돌릴 수 있다.)
        print("⚠️ 기존 파일이 이전 버전(회사 하드코딩) 스키마입니다. 새 스키마로 새로 시작합니다.")
        return pd.DataFrame(columns=LEAD_COLUMNS), pd.DataFrame()

    return df_leads, df_history


def merge_candidates(df_existing, new_records):
    existing_by_country = {}
    if not df_existing.empty:
        for _, row in df_existing.iterrows():
            existing_by_country[row['국가 (Country)']] = row.to_dict()

    new_countries = set()
    merged = []
    newly_added = 0

    for rec in new_records:
        country = rec['국가 (Country)']
        new_countries.add(country)
        combined = dict(rec)
        old = existing_by_country.get(country)
        if old is None:
            newly_added += 1
        else:
            # 사용자가 이미 조사해 채워 넣은 값은 보존한다.
            for col in USER_EDITABLE_COLS:
                old_val = old.get(col)
                if pd.notna(old_val) and str(old_val).strip() not in ('', NEW_CANDIDATE_STATUS):
                    combined[col] = old_val
        merged.append(combined)

    # 이번 실행의 TOP 10 순위에서는 빠졌지만 과거에 발견된 후보국은 이력 보존을 위해 유지
    for country, old in existing_by_country.items():
        if country not in new_countries:
            merged.append(old)

    df_merged = pd.DataFrame(merged, columns=LEAD_COLUMNS)
    df_merged = df_merged.sort_values(by='우선순위 점수', ascending=False, na_position='last')
    return df_merged, newly_added


# ---------------------------------------------------------------------------
# 3. 메인 파이프라인
# ---------------------------------------------------------------------------

def generate_partner_sourcing(item, output_dir, eda_report=None, item_slug=None):
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    clean_item = item.split('(')[0].strip() if '(' in item else item.strip()
    slug = (item_slug or re.sub(r'[^a-zA-Z0-9]+', '_', item).strip('_').lower() or 'item')

    data_dir = os.path.join(output_dir, 'data')
    reports_dir = os.path.join(output_dir, 'reports')
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)

    if not eda_report:
        eda_report = os.path.join(reports_dir, f"BIZ-{clean_item}_Gathered_EDA_Report.md")

    print("=" * 60)
    print(f"🌐 소싱 후보국가 & 파트너 리서치 트래커 가동: {item}")
    print(f"📄 참조 EDA 리포트: {eda_report}")
    print("=" * 60)

    if not os.path.exists(eda_report):
        print_error(
            eda_report,
            "generate_partner_sourcing.py",
            "먼저 trade-gen1-un-eda 스킬(generate_trade_eda.py)로 해당 품목의 EDA 리포트를 생성하세요.",
        )
        return None

    parsed_rows = parse_eda_report_tables(eda_report)
    if not parsed_rows:
        print_error(
            f"{eda_report} 내 파싱 가능한 HS Code 유망국가 표 없음",
            "generate_partner_sourcing.py",
            "trade-gen1-un-eda의 최신 버전으로 리포트를 재생성했는지 확인하세요 "
            "(리포트 헤딩 형식이 '### 📌 [표 N] ... TOP 10 유망 국가' 여야 합니다).",
        )
        return None

    excel_path = os.path.join(data_dir, f'{slug}_buyers_leads.xlsx')
    csv_path = os.path.join(data_dir, f'{slug}_sourcing_history.csv')
    md_report_path = os.path.join(reports_dir, f'{clean_item}_Buyers_Lead_List.md')

    new_records = build_candidate_rows(parsed_rows, now_str)
    df_existing_leads, df_existing_history = load_existing_leads(excel_path)
    df_combined_leads, newly_added = merge_candidates(df_existing_leads, new_records)

    hs_tables_seen = sorted(set(r['table_num'] for r in parsed_rows))
    history_entry = {
        '수집 구동 시기 (Execution Timestamp)': now_str,
        '참조 HS Code 표 수': len(hs_tables_seen),
        '이번 실행 발견 국가 수': len(new_records),
        '신규 후보국 수 (New)': newly_added,
        '누적 총 후보국 수 (Total Accumulated)': len(df_combined_leads),
        '상태 (Status)': '정상 완료 (Success)',
    }
    df_new_history = pd.DataFrame([history_entry])
    df_combined_history = (
        pd.concat([df_existing_history, df_new_history], ignore_index=True)
        if df_existing_history is not None and not df_existing_history.empty
        else df_new_history
    )

    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_combined_leads.to_excel(writer, sheet_name='Sourcing_Candidates', index=False)
        df_combined_history.to_excel(writer, sheet_name='Sourcing_History', index=False)

    df_combined_history.to_csv(csv_path, index=False, encoding='utf-8-sig')

    status_counts = df_combined_leads['조사 상태'].value_counts()
    status_md = status_counts.to_frame(name='국가 수').to_markdown()

    md_content = f"""# 🌐 한국산 {clean_item} 소싱 후보국가 & 파트너 리서치 트래커

- **최종 자동 업데이트 일시**: {now_str}
- **참조 EDA 리포트**: `{os.path.basename(eda_report)}`
- **현재 누적 후보국 수**: `{len(df_combined_leads)}개국`

> ⚠️ 이 문서는 실제 웹 검색/실사를 수행하지 않습니다. "국가/EDA 데이터 근거/순위/우선순위 점수"는
> trade-gen1-un-eda가 산출한 실제 무역 통계 기반값이며, "후보 파트너/에이전트명·이메일·웹사이트"는
> 사람이 직접 조사해 채워 넣어야 하는 빈 칸입니다. 재실행해도 이미 채워 넣은 조사 결과는 덮어쓰지 않습니다.

---

## 📈 1. 수집 실행 히스토리 로그 (Execution History Log)

{df_combined_history.to_markdown(index=False)}

---

## 📊 2. 조사 상태별 현황

{status_md}

---

## 📋 3. 소싱 후보국가 리스트 (우선순위 점수 순)

{df_combined_leads.to_markdown(index=False)}

---
*이 리스트는 실제 무역 데이터(EDA 리포트) 기반으로 우선순위가 매겨진 "조사 대상 후보"입니다.
실제 바이어/에이전트 컨택 정보는 현지 리서치, 무역관 조회, 전시회 등을 통해 직접 확인 후 입력하세요.*
"""

    with open(md_report_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"✅ [{clean_item}] 소싱 후보국가 트래커 갱신 완료 (신규 {newly_added}개국 추가, 누적 {len(df_combined_leads)}개국)")
    print(f"📌 마크다운 리포트: {md_report_path}")
    print(f"📌 엑셀 DB: {excel_path}")
    print(f"📌 CSV 히스토리: {csv_path}")

    return df_combined_leads, excel_path, md_report_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="trade-gen1-un-eda 리포트 기반 범용 소싱 후보국가 & 파트너 리서치 트래커 생성기"
    )
    parser.add_argument("--item", type=str, required=True, help="품목명 (예: '전복 (Abalone)', '김 (Laver)')")
    parser.add_argument("--output_dir", type=str, required=True, help="프로젝트 루트 폴더 (data/, reports/ 하위 생성)")
    parser.add_argument("--eda_report", type=str, default=None,
                         help="참조할 EDA 리포트 경로 (생략 시 {output_dir}/reports/BIZ-{품목}_Gathered_EDA_Report.md)")
    parser.add_argument("--item_slug", type=str, default=None,
                         help="데이터 파일명에 쓸 영문 슬러그 (생략 시 --item에서 자동 생성)")
    args = parser.parse_args()

    result = generate_partner_sourcing(args.item, args.output_dir, args.eda_report, args.item_slug)
    sys.exit(0 if result is not None else 1)
