"""
trade-gen1-un-eda가 만든 EDA 리포트(우선 개척시장 3선, 삼국무역 우선 개척 조합 3선,
월별 계절성)를 파싱해, 체크박스 기반으로 체크하며 이어갈 수 있는 "실행 로드맵
(Action Plan)"을 자동 생성하는 스킬.

설계 원칙 (trade-gen2.1-un-sourcing과 동일한 철학):
- 이 스크립트는 실제 웹 검색/실사를 수행하지 않는다. 파트너/서류 요건 등 정성적 필드는
  업계 표준 템플릿 + "실사 확인 필요" 표기로 시작하며, 지어내지 않는다.
- EDA 리포트에 실제로 산출된 값(시장명, 근거, 마진갭, 매입/판매가, 계절성)만 그대로 인용한다.
- 각 스텝은 "이유 → 행동 → 목표기한(계절성 기반) → 실패 시 대안(Plan B) → 다음 스텝 조건"을
  전부 갖춰야 한다 (사용자 피드백 6가지 반영: 타임라인/Plan B/자금회수/샘플게이트/갱신트리거/
  사전서류체크리스트).
- 재실행해도 "완료" 표시가 있는 스텝은 덮어쓰지 않는다 (trade-gen2.1의 재실행 안전성 원칙과 동일).
"""

import os
import re
import sys
import argparse
import datetime

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

SEASONALITY_LEAD_MONTHS = 3  # 소싱→선적→통관 표준 리드타임 가정치 (품목별 실제 리드타임은 별도 확인)


def print_error(missing, required_by, action):
    print("[ERROR]: Required file not found or unreadable")
    print(f"- Missing: {missing}")
    print(f"- Required by: {required_by}")
    print(f"- Action: {action}")


# ---------------------------------------------------------------------------
# 1. EDA 리포트 파서
# ---------------------------------------------------------------------------

def extract_section(content, start_pattern, end_pattern=None):
    """start_pattern에 매칭되는 첫 줄부터, end_pattern(또는 다음 '## ' 헤딩)
    직전까지의 구간을 반환한다."""
    lines = content.split('\n')
    start_re = re.compile(start_pattern)
    end_re = re.compile(end_pattern) if end_pattern else re.compile(r'^## ')

    start_idx = None
    for i, line in enumerate(lines):
        if start_re.match(line.strip()):
            start_idx = i + 1
            break
    if start_idx is None:
        return ""

    end_idx = len(lines)
    for i in range(start_idx, len(lines)):
        if end_re.match(lines[i].strip()):
            end_idx = i
            break
    return "\n".join(lines[start_idx:end_idx])


def _field(block, label):
    m = re.search(rf'^-\s*\*\*{re.escape(label)}\*\*:\s*(.+)$', block, re.MULTILINE)
    return m.group(1).strip() if m else None


def parse_market_picks(content):
    """'## 🎯 1. 1인 종합상사 최적 우선 개척 시장 3선' 섹션에서 ①②③ 블록을 파싱."""
    section = extract_section(content, r'^## 🎯 1\.')
    if not section:
        return []
    header_re = re.compile(r'^###\s*([①②③])\s*시장\s*\d+:\s*(.+?)\s*—\s*\[(.+?)\]\s*$')
    blocks = re.split(r'(?=^###\s*[①②③])', section, flags=re.MULTILINE)
    picks = []
    for b in blocks:
        m = header_re.match(b.strip().split('\n')[0])
        if not m:
            continue
        picks.append({
            'mark': m.group(1),
            'market': m.group(2).strip(),
            'label': m.group(3).strip(),
            'reason': _field(b, '선정 근거') or '(근거 파싱 실패 — 리포트 형식 확인 필요)',
            'item_rec': _field(b, '추천 품목') or '데이터 없음',
        })
    return picks


def parse_triangular_picks(content):
    """'### 🏆 삼국무역 우선 개척 조합 3선' 섹션에서 ①②③ 블록을 파싱."""
    section = extract_section(content, r'^###\s*🏆\s*삼국무역 우선 개척 조합 3선', r'^###\s*📋')
    if not section:
        return []
    header_re = re.compile(r'^###\s*([①②③])\s*조합\s*\d+\s*—\s*(.+?):\s*(.+?)\s*→\s*(.+?)\s*—\s*\[(.+?)\]\s*$')
    blocks = re.split(r'(?=^###\s*[①②③])', section, flags=re.MULTILINE)
    picks = []
    for b in blocks:
        m = header_re.match(b.strip().split('\n')[0])
        if not m:
            continue
        picks.append({
            'mark': m.group(1),
            'criterion': m.group(2).strip(),
            'b_country': m.group(3).strip(),
            'c_country': m.group(4).strip(),
            'hs_label': m.group(5).strip(),
            'reason': _field(b, '선정 근거') or '(근거 파싱 실패)',
            'buy_price': _field(b, '권장 매입가') or '데이터 없음',
            'sell_price': _field(b, '권장 판매가') or '데이터 없음',
            'verdict': _field(b, '판정') or '',
        })
    return picks


def parse_seasonality(content):
    """'### 5. 월별 수출입 계절성 분석' 표를 (월:무역액) 딕셔너리로 파싱.
    데이터 없거나 헤더가 달라도, 첫 컬럼이 1~12 범위 정수인 2컬럼 표는 전부 인식한다."""
    section = extract_section(content, r'^###\s*5\.\s*월별', r'^###\s*6\.')
    if not section or '데이터 없음' in section:
        return {}
    result = {}
    for line in section.split('\n'):
        stripped = line.strip()
        if not stripped.startswith('|') or ':---' in stripped:
            continue
        cols = [c.strip() for c in stripped.split('|')[1:-1]]
        if len(cols) < 2:
            continue
        try:
            month = int(re.sub(r'[^0-9]', '', cols[0]))
            value = float(re.sub(r'[^0-9.\-]', '', cols[1]))
        except (ValueError, TypeError):
            continue
        if 1 <= month <= 12:
            result[month] = value
    return result


def compute_target_month(peak_month, lead_months=SEASONALITY_LEAD_MONTHS):
    """피크월 - 리드타임을 계산해 '가장 가까운 미래' 목표월(YYYY년 MM월)을 반환한다."""
    today = datetime.date.today()
    target_month = ((peak_month - lead_months - 1) % 12) + 1
    target_year = today.year if target_month >= today.month else today.year + 1
    return f"{target_year}년 {target_month}월", target_month


# ---------------------------------------------------------------------------
# 2. 액션플랜 조립
# ---------------------------------------------------------------------------

PRE_DEPARTURE_CHECKLIST = """## 0️⃣ 사전 준비 서류 체크리스트 (모든 스텝 시작 전 1회 준비)

> ⚠️ 아래는 업계 일반 표준 서류 목록입니다. 품목/타겟국가별 정확한 요건은 반드시 현지 리서치로
> 재확인하세요 *(실사 확인 필요)*.

- [ ] 원산지증명서(Certificate of Origin) 발급 경로 확인 (대한상공회의소 또는 세관)
- [ ] 위생증명서(Health/Sanitary Certificate) — 식품/농수산물인 경우 필수, 발급기관 사전 확인
- [ ] HACCP / ISO22000 등 위생안전 인증 사본 준비
- [ ] 시험성적서(COA, Certificate of Analysis) 최신본 확보
- [ ] Sales Contract 템플릿 준비 (결제조건/인코텀즈 조항 포함)
- [ ] Proforma Invoice(P/I) 템플릿 준비
- [ ] Commercial B2B Offer Sheet 준비 (아래 "TOP HS Code별 유망 타겟시장 표" 부록의 오퍼서 참고)
- [ ] 사업자등록증/수출자 등록 확인 (관세청 통관고유부호 등)
- [ ] K-SURE 국외기업 신용조사 서비스 이용 여부 결정 (2단계 계약 협상 전 권장)

---
"""


def build_market_step(idx, pick, next_pick, seasonality, item_label):
    step_no = idx + 1
    target_txt = "계절성 데이터 없음 — 가능한 빨리 착수 권장 (표준 리드타임 참고)"
    if seasonality:
        peak_month = max(seasonality, key=seasonality.get)
        target_str, _ = compute_target_month(peak_month)
        target_txt = (
            f"**{target_str}**까지 오퍼 완료 권장 (이 품목은 {peak_month}월이 계절성 피크 — "
            f"리드타임 {SEASONALITY_LEAD_MONTHS}개월 역산)"
        )

    fallback = (
        f"**{next_pick['market']} — [{next_pick['label']}]**로 전환 (다음 우선순위 시장, 추천 품목: {next_pick['item_rec']})"
        if next_pick else "더 이상 대체 시장 후보가 없습니다 — 신시장 개척 TOP5 섹션에서 추가 후보를 확인하세요."
    )

    return f"""## {step_no}️⃣ [{pick['mark']}] {pick['market']} 개척 — [{pick['label']}]

- [ ] **행동**: `{item_label}` 품목을 `{pick['market']}` 시장에 오퍼. 추천 품목: {pick['item_rec']}
- **이유**: {pick['reason']}
- **목표 완료일**: {target_txt}
- **자금 계획**: 결제조건 `T/T 30% Deposit + 70% against B/L` 기준, 계약금(30%) 지급 시점부터 잔금 회수(B/L 발행)까지
  통상 LCL 30~45일 / FCL 45~60일 자금이 묶입니다. 이 기간의 운전자금을 미리 확보하세요.
- **⚠️ 샘플/품질 검증 게이트 (계약 전 필수, 생략 금지)**:
  - [ ] 샘플 요청 및 인수
  - [ ] 규격/사이즈 확인
  - [ ] HACCP/COA 등 인증서 원본 확인
  - [ ] 위 3개 항목 통과 전에는 본계약(대량 오더) 진행 금지
- **실패 시 대안(Plan B)**: 바이어 반응이 없거나(3주 이상 무응답) 조건이 안 맞으면 → {fallback}
- **다음 스텝 조건**: 샘플 검증 통과 + 최소 1개 바이어 회신 확보 시 다음 스텝 진행
"""


def build_triangular_step(idx, pick, next_pick, offset):
    step_no = offset + idx + 1
    fallback = (
        f"**{next_pick['b_country']} → {next_pick['c_country']}** 조합으로 전환 (다음 우선순위, {next_pick['criterion']} 기준)"
        if next_pick else "더 이상 대체 조합 후보가 없습니다 — HS Code별 전체 후보 목록에서 추가 조합을 확인하세요."
    )
    return f"""## {step_no}️⃣ [{pick['mark']}] 삼국무역: {pick['b_country']} 소싱 → {pick['c_country']} 판매 — [{pick['criterion']}]

- [ ] **행동**: `{pick['b_country']}`의 컨택 파트너 리스트업(trade-gen2.2/4) → 매입 협상 → `{pick['c_country']}` 바이어 오퍼
- **이유**: {pick['reason']} (품목: {pick['hs_label']})
- **권장 매입가**: {pick['buy_price']}
- **권장 판매가**: {pick['sell_price']}
- **판정**: {pick['verdict']}
- **자금 계획**: 매입(B국)과 판매(C/D국) 결제조건이 어긋나면(예: B에는 선지급, C/D에서는 후지급) 이중으로
  자금이 묶입니다 — 계약 전 양쪽 결제조건을 반드시 맞춰보고 필요 시 back-to-back L/C를 검토하세요.
- **⚠️ 필수 확인 (중계무역 특성)**:
  - [ ] 한국 미개입이므로 한국 FTA 협정세율 미적용 확인
  - [ ] 외국환거래법상 중계무역 신고 절차(외국인수수입/외국인도수출) 확인
  - [ ] `{pick['b_country']}`/`{pick['c_country']}` 제재 대상국 여부 확인
  - [ ] 샘플 검증 통과 전 본계약 금지 (위 시장 개척 스텝과 동일 원칙)
- **실패 시 대안(Plan B)**: 매입 협상 결렬 또는 마진 붕괴 시 → {fallback}
- **다음 스텝 조건**: 매입처 확정 + 샘플 검증 통과 시 다음 스텝 진행
"""


REFRESH_TRIGGER_NOTE = """---

## 🔄 로드맵 갱신 트리거

이 액션플랜은 생성 시점의 EDA 데이터 기준 스냅샷입니다. 아래 조건 중 하나라도 해당하면
`trade-gen1-un-eda`부터 다시 실행해 이 문서를 재생성하세요:

- [ ] 마지막 생성일로부터 **3개월 경과**
- [ ] 원본 무역통계 CSV를 **재수집**한 경우 (특히 최신 연도 보고지연이 해소된 경우)
- [ ] 바이어 협상에서 **가격/마진갭이 리포트 수치와 크게 어긋난다**고 확인된 경우
- [ ] 경쟁국의 신규 진입 등 **시장 구조 변화**를 감지한 경우

재생성해도 아래 체크박스 중 이미 `[x]`로 표시된 항목은 유지되므로(재실행 안전성), 진행 상황을
잃지 않고 최신 데이터로 갱신할 수 있습니다.
"""


def preserve_checked_items(old_content, new_content):
    """이전 실행에서 사람이 이미 [x]로 체크한 라인을, 같은 텍스트의 새 라인에도 반영한다
    (텍스트가 완전히 동일한 체크박스 라인만 매칭 — 완료 표시를 잃지 않기 위함)."""
    if not old_content:
        return new_content
    checked_lines = set()
    for line in old_content.split('\n'):
        s = line.strip()
        if s.startswith('- [x]'):
            checked_lines.add(s[5:].strip())
    if not checked_lines:
        return new_content
    out_lines = []
    for line in new_content.split('\n'):
        s = line.strip()
        if s.startswith('- [ ]') and s[5:].strip() in checked_lines:
            indent = line[:len(line) - len(line.lstrip())]
            out_lines.append(f"{indent}- [x]{line.lstrip()[5:]}")
        else:
            out_lines.append(line)
    return "\n".join(out_lines)


def generate_action_plan(item, output_dir, eda_report=None, item_slug=None, home_country="Korea"):
    clean_item = item.split('(')[0].strip() if '(' in item else item.strip()
    slug = (item_slug or re.sub(r'[^a-zA-Z0-9]+', '_', item).strip('_').lower() or 'item')
    slug_title = '_'.join(w.capitalize() for w in slug.split('_'))

    reports_dir = os.path.join(output_dir, 'reports')
    os.makedirs(reports_dir, exist_ok=True)

    if not eda_report:
        eda_report = os.path.join(reports_dir, f"BIZ-{slug_title}_Gathered_EDA_Report.md")

    print("=" * 60)
    print(f"🗺️  실행 로드맵(Action Plan) 생성: {item}")
    print(f"📄 참조 EDA 리포트: {eda_report}")
    print("=" * 60)

    if not os.path.exists(eda_report):
        print_error(
            eda_report,
            "generate_action_plan.py",
            "먼저 trade-gen1-un-eda 스킬로 해당 품목의 EDA 리포트를 생성하세요.",
        )
        return None

    with open(eda_report, 'r', encoding='utf-8') as f:
        content = f.read()

    market_picks = parse_market_picks(content)
    tri_picks = parse_triangular_picks(content)
    seasonality = parse_seasonality(content)

    if not market_picks and not tri_picks:
        print_error(
            f"{eda_report} 내 파싱 가능한 '우선 개척 시장 3선'/'삼국무역 우선 개척 조합 3선' 없음",
            "generate_action_plan.py",
            "trade-gen1-un-eda 최신 버전으로 리포트를 재생성했는지 확인하세요.",
        )
        return None

    plan_path = os.path.join(reports_dir, f'{slug_title}_Action_Plan.md')
    old_content = None
    if os.path.exists(plan_path):
        with open(plan_path, 'r', encoding='utf-8') as f:
            old_content = f.read()

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    market_steps_md = "\n".join(
        build_market_step(i, p, market_picks[i + 1] if i + 1 < len(market_picks) else None, seasonality, clean_item)
        for i, p in enumerate(market_picks)
    ) if market_picks else "우선 개척 시장 3선 데이터가 없어 이 구간을 생략합니다.\n"

    tri_steps_md = "\n".join(
        build_triangular_step(i, p, tri_picks[i + 1] if i + 1 < len(tri_picks) else None, len(market_picks))
        for i, p in enumerate(tri_picks)
    ) if tri_picks else "삼국무역 우선 개척 조합 3선 데이터가 없어 이 구간을 생략합니다.\n"

    seasonality_note = (
        f"이 품목은 월별 계절성 데이터가 확인되어, 스텝별 목표 완료일에 자동 반영했습니다 "
        f"(리드타임 가정: {SEASONALITY_LEAD_MONTHS}개월)."
        if seasonality else
        "이 EDA 리포트에는 월별 계절성 데이터가 없어(연간 집계 데이터), 스텝별 목표일은 "
        "\"가능한 빨리\" 기준으로 표시했습니다. 계절성이 중요한 품목이면 월별 데이터로 재수집을 권장합니다."
    )

    md_content = f"""# 🗺️ {clean_item} 실행 로드맵 (Action Plan)

- **최종 생성 일시**: {now_str}
- **참조 EDA 리포트**: `{os.path.basename(eda_report)}`
- **자국(home_country)**: `{home_country}`

> 이 문서는 `trade-gen1-un-eda`가 산출한 실제 데이터(우선 개척 시장 3선, 삼국무역 우선 개척 조합 3선,
> 계절성)만 인용해 만든 실행 순서입니다. 체크박스(`- [ ]`)를 진행 상황에 맞춰 직접 체크하시거나,
> "N번 끝났어" / "다음 스텝 진행해줘"라고 말씀해주시면 이 파일을 다시 읽어 다음 미체크 스텝을
> 안내해 드립니다. {seasonality_note}

---

{PRE_DEPARTURE_CHECKLIST}
# 🎯 파트 1. 우선 개척 시장 3선 실행 스텝

{market_steps_md}

---

# 🔀 파트 2. 삼국무역 우선 개척 조합 3선 실행 스텝

{tri_steps_md}

{REFRESH_TRIGGER_NOTE}
"""

    if old_content:
        md_content = preserve_checked_items(old_content, md_content)

    with open(plan_path, 'w', encoding='utf-8') as f:
        f.write(md_content)

    print(f"✅ 실행 로드맵 생성 완료: {plan_path}")
    print(f"📌 시장 개척 스텝 {len(market_picks)}개, 삼국무역 스텝 {len(tri_picks)}개")
    return plan_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="trade-gen1-un-eda 리포트 기반 실행 로드맵(Action Plan) 생성기"
    )
    parser.add_argument("--item", type=str, required=True, help="품목명 (예: '전복 (Abalone)', '김 (Laver)')")
    parser.add_argument("--output_dir", type=str, required=True, help="프로젝트 루트 폴더 (reports/ 하위 생성)")
    parser.add_argument("--eda_report", type=str, default=None,
                         help="참조할 EDA 리포트 경로 (생략 시 {output_dir}/reports/BIZ-{품목}_Gathered_EDA_Report.md)")
    parser.add_argument("--item_slug", type=str, default=None,
                         help="파일명에 쓸 영문 슬러그 (생략 시 --item에서 자동 생성)")
    parser.add_argument("--home_country", type=str, default="Korea", help="자국(수출국) 표기")
    args = parser.parse_args()

    result = generate_action_plan(args.item, args.output_dir, args.eda_report, args.item_slug, args.home_country)
    sys.exit(0 if result is not None else 1)
