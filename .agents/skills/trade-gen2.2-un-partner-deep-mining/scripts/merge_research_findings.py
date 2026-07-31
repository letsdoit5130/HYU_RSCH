"""
trade-gen2.2-un-partner-deep-mining 스킬의 산출물(실제 WebSearch/WebFetch로 확인한 회사/에이전트 findings JSON)을
trade-gen2.1-un-sourcing가 만든 소싱 트래커(xlsx/csv/md)에 병합하는 결정적(deterministic) 병합기.

역할 분리:
- 실제 회사가 존재하는지 찾는 것(웹 검색/판단)은 이 스크립트가 하지 않는다. 그건 Claude가
  WebSearch/WebFetch로 직접 확인한 뒤 findings JSON으로 넘겨준다.
- 이 스크립트는 그 findings를 정해진 스키마로 xlsx/csv/md에 정확하게, 항상 같은 방식으로 반영하는
  역할만 한다 (사람이 손으로 엑셀을 편집하다 실수하는 것을 방지).

무결성 규칙 (필수):
- 모든 findings 레코드는 '출처 URL'이 있어야 한다. 출처 URL이 없는 레코드는 병합을 거부한다.
  (이메일/전화번호를 실제로 어디서 확인했는지 추적 불가능한 데이터는 절대 반영하지 않는다.)
"""

import os
import sys
import json
import argparse
import datetime

import pandas as pd
import openpyxl  # noqa: F401

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
else:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

PARTNER_COLUMNS = [
    '조사일 (Research Date)',
    '국가 (Country)',
    '회사명/에이전트명',
    '구분 (법인/개인 에이전트)',
    '이메일',
    '웹사이트 / LinkedIn URL',
    'Messenger/연락처',
    '조사 범위 (HS Code 표)',
    'City',
    'Country',
    '본사 위치 (상세)',
    '주요 취급 품목 및 특징',
    '잠재적 협력 포인트',
    '출처 URL (검증 근거)',
    '비고',
]

CANDIDATE_STATUS_COL = '조사 상태'
CANDIDATE_PARTNER_COL = '후보 파트너/에이전트명'
CANDIDATE_NOTE_COL = '비고/메모'
NUMERIC_CANDIDATE_COLS = {'후보 HS Code 수', '최고 순위', '우선순위 점수'}


def print_error(missing, required_by, action):
    print("[ERROR]: Invalid or missing input")
    print(f"- Missing: {missing}")
    print(f"- Required by: {required_by}")
    print(f"- Action: {action}")


def load_findings(findings_path):
    if not os.path.exists(findings_path):
        print_error(findings_path, "merge_research_findings.py", "먼저 findings JSON 파일을 생성하세요.")
        return None
    with open(findings_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not isinstance(data, list):
        print_error("findings JSON 최상위는 리스트여야 함", "merge_research_findings.py",
                     "형식: [{country, name, ..., source_url}, ...]")
        return None

    rejected = []
    valid = []
    for rec in data:
        if not rec.get('source_url') or not str(rec.get('source_url')).strip().startswith('http'):
            rejected.append(rec)
            continue
        if not rec.get('country') or not rec.get('name'):
            rejected.append(rec)
            continue
        valid.append(rec)

    if rejected:
        print(f"⚠️ 출처 URL/필수 필드가 없어 {len(rejected)}건을 반영하지 않고 건너뜁니다:")
        for r in rejected:
            print(f"   - {r.get('country', '?')} / {r.get('name', '?')} (source_url 없음 또는 형식 오류)")

    return valid


def build_partner_rows(findings, now_str):
    rows = []
    for rec in findings:
        rows.append({
            '조사일 (Research Date)': now_str,
            '국가 (Country)': rec['country'],
            '회사명/에이전트명': rec['name'],
            '구분 (법인/개인 에이전트)': '개인 에이전트' if rec.get('is_agent') else '법인',
            '이메일': rec.get('email', '') or '',
            '웹사이트 / LinkedIn URL': rec.get('website', '') or rec.get('linkedin', '') or '',
            'Messenger/연락처': rec.get('messenger', '') or '',
            '조사 범위 (HS Code 표)': rec.get('scope', '') or '',
            'City': rec.get('city', '') or '',
            'Country': rec.get('country_en', '') or rec['country'],
            '본사 위치 (상세)': rec.get('location_detail', '') or rec.get('location', '') or '',
            '주요 취급 품목 및 특징': rec.get('features', '') or '',
            '잠재적 협력 포인트': rec.get('coop_point', '') or '',
            '출처 URL (검증 근거)': rec['source_url'],
            '비고': rec.get('note', '') or '',
        })
    return rows


def merge_partner_sheet(existing_df, new_rows):
    key = lambda r: (r['국가 (Country)'].strip().lower(), r['회사명/에이전트명'].strip().lower())
    combined = {}
    if existing_df is not None and not existing_df.empty:
        # Excel 왕복으로 빈 칸이 NaN이 되어있을 수 있으므로 실제 빈 문자열로 되돌린다
        # (안 그러면 재병합 시 마크다운에 "nan" 문자열로 렌더링됨).
        for _, row in existing_df.fillna('').iterrows():
            combined[key(row.to_dict())] = row.to_dict()
    added, updated = 0, 0
    for row in new_rows:
        k = key(row)
        if k in combined:
            updated += 1
        else:
            added += 1
        combined[k] = row
    df = pd.DataFrame(list(combined.values()), columns=PARTNER_COLUMNS)
    df = df.sort_values(by=['국가 (Country)', '회사명/에이전트명'])
    return df, added, updated


def update_candidate_status(df_candidates, names_by_country):
    if df_candidates is None or df_candidates.empty:
        return df_candidates
    # Excel 왕복 후 전부 빈 문자열이던 컬럼은 pandas가 float64(NaN)로 추론해 읽어오는 경우가
    # 있어, 그 상태에서 문자열을 대입하면 TypeError가 난다. object dtype으로 고정하고, 빈 칸이
    # "nan" 문자열로 렌더링되지 않도록 실제 빈 문자열로 채워 넣는다.
    df = df_candidates.astype(object).copy()
    text_cols = [c for c in df.columns if c not in NUMERIC_CANDIDATE_COLS]
    df[text_cols] = df[text_cols].fillna('')
    for idx, row in df.iterrows():
        country = row.get('국가 (Country)')
        names = names_by_country.get(country)
        if not names:
            continue
        df.at[idx, CANDIDATE_STATUS_COL] = f"🔍 조사 완료 ({len(names)}개사 발견)"
        shown = names[:2]
        more = len(names) - len(shown)
        summary = ", ".join(shown) + (f" 외 {more}개사" if more > 0 else "")
        df.at[idx, CANDIDATE_PARTNER_COL] = summary
        df.at[idx, CANDIDATE_NOTE_COL] = "상세 내역은 'Verified_Partners' 시트 참고"
    return df


def render_markdown(clean_item, df_candidates, df_partners, df_history, md_report_path, now_str):
    status_md = (
        df_candidates[CANDIDATE_STATUS_COL].value_counts().to_frame(name='국가 수').to_markdown()
        if df_candidates is not None and not df_candidates.empty else "데이터 없음"
    )
    partners_md = df_partners.to_markdown(index=False) if not df_partners.empty else "아직 검증된 파트너가 없습니다."
    candidates_md = df_candidates.to_markdown(index=False) if df_candidates is not None and not df_candidates.empty else "데이터 없음"
    history_md = df_history.to_markdown(index=False) if df_history is not None and not df_history.empty else "데이터 없음"

    md_content = f"""# 🌐 한국산 {clean_item} 소싱 후보국가 & 파트너 리서치 트래커

- **최종 자동 업데이트 일시**: {now_str}
- **검증된 파트너/에이전트 수**: `{len(df_partners)}건` (출처 URL 필수)

> ⚠️ "Verified_Partners" 섹션의 모든 행은 실제 WebSearch/WebFetch로 확인된 출처 URL을 가지고 있습니다.
> 출처 URL이 없는 정보는 이 문서에 절대 반영되지 않습니다. 그 외 "미조사" 상태인 국가의
> 파트너 정보는 아직 조사되지 않은 것이며, 지어낸 값이 아닙니다.

---

## 📊 1. 조사 상태별 현황

{status_md}

---

## 🔍 2. 검증된 파트너/에이전트 목록 (출처 URL 포함)

{partners_md}

---

## 📋 3. 소싱 후보국가 리스트 (우선순위 점수 순)

{candidates_md}

---

## 📈 4. 수집 실행 히스토리 로그

{history_md}

---
*"검증된 파트너" 섹션은 사람 또는 실시간 웹 검색이 가능한 에이전트가 직접 확인한 결과만 포함합니다.
출처 URL을 클릭해 원본 정보를 재확인한 뒤 컨택하세요.*
"""
    with open(md_report_path, 'w', encoding='utf-8') as f:
        f.write(md_content)


def merge(findings_path, output_dir, item, item_slug=None):
    import re

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clean_item = item.split('(')[0].strip() if '(' in item else item.strip()
    slug = (item_slug or re.sub(r'[^a-zA-Z0-9]+', '_', item).strip('_').lower() or 'item')

    data_dir = os.path.join(output_dir, 'data')
    reports_dir = os.path.join(output_dir, 'reports')
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(reports_dir, exist_ok=True)
    excel_path = os.path.join(data_dir, f'{slug}_buyers_leads.xlsx')
    md_report_path = os.path.join(reports_dir, f'{clean_item}_Buyers_Lead_List.md')

    if not os.path.exists(excel_path):
        print_error(
            excel_path, "merge_research_findings.py",
            "먼저 trade-gen2.1-un-sourcing 스킬로 소싱 후보국가 트래커를 생성하세요.",
        )
        return None

    findings = load_findings(findings_path)
    if findings is None:
        return None
    if not findings:
        print("병합할 유효한 findings가 없습니다 (모두 출처 URL 누락으로 거부됨).")
        return None

    df_candidates = pd.read_excel(excel_path, sheet_name='Sourcing_Candidates')
    df_history = pd.read_excel(excel_path, sheet_name='Sourcing_History')
    try:
        df_partners_existing = pd.read_excel(excel_path, sheet_name='Verified_Partners')
    except Exception:
        df_partners_existing = pd.DataFrame(columns=PARTNER_COLUMNS)

    new_rows = build_partner_rows(findings, now_str)
    df_partners, added, updated = merge_partner_sheet(df_partners_existing, new_rows)

    names_by_country = {}
    for row in df_partners.to_dict('records'):
        names_by_country.setdefault(row['국가 (Country)'], []).append(row['회사명/에이전트명'])

    df_candidates = update_candidate_status(df_candidates, names_by_country)

    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        df_candidates.to_excel(writer, sheet_name='Sourcing_Candidates', index=False)
        df_partners.to_excel(writer, sheet_name='Verified_Partners', index=False)
        df_history.to_excel(writer, sheet_name='Sourcing_History', index=False)

    render_markdown(clean_item, df_candidates, df_partners, df_history, md_report_path, now_str)

    print(f"✅ 파트너 리서치 결과 병합 완료: 신규 {added}건, 갱신 {updated}건 (누적 {len(df_partners)}건)")
    print(f"📌 엑셀 DB: {excel_path} (Verified_Partners 시트)")
    print(f"📌 마크다운 리포트: {md_report_path}")
    return df_partners


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="WebSearch/WebFetch로 확인된 파트너 findings를 소싱 트래커에 병합"
    )
    parser.add_argument("--findings", type=str, required=True, help="findings JSON 파일 경로")
    parser.add_argument("--item", type=str, required=True, help="품목명")
    parser.add_argument("--output_dir", type=str, required=True, help="프로젝트 루트 폴더")
    parser.add_argument("--item_slug", type=str, default=None, help="데이터 파일명 슬러그")
    args = parser.parse_args()

    result = merge(args.findings, args.output_dir, args.item, args.item_slug)
    sys.exit(0 if result is not None else 1)
