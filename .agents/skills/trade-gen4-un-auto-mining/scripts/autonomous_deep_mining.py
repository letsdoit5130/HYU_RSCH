"""
사람 개입 없이 GitHub Actions에서 완전 자동으로 도는 딥마이닝 버전.

trade-gen2.2-un-partner-deep-mining은 대화형 AI 세션(Claude Code 등)이 WebSearch/WebFetch로
직접 조사하는 방식이라, 컴퓨터/세션이 꺼지면 멈춘다. 이 스크립트는 그 한계를 없애기 위해
Gemini API를 Google Search grounding 도구와 함께 호출해, 서버(GitHub Actions)에서 실제로
회사를 검색하고 그 결과를 병합까지 자동으로 수행한다.

무결성 규칙은 동일하게 강제한다:
- 실제 검색으로 확인된 것만 보고하도록 시스템 프롬프트에 명시
- source_url 없는 레코드는 merge_research_findings.py가 자동 거부 (재사용, 중복 구현 없음)
- 비용 통제를 위해 한 번 실행에 --top_n 개 신규 후보국만 처리 (기본 3개)

이 스크립트 자체는 "검색 결과를 믿을지 말지" 판단하지 않는다 — 그건 여전히
merge_research_findings.py의 하드 게이트(출처 URL 필수)가 담당한다. 다만 LLM이 실제로 grounding
없이 지어낼 가능성을 줄이기 위해 grounding_metadata의 실제 인용 URL도 별도 감사 로그에 남긴다.
"""

import os
import sys
import re
import json
import time
import argparse
import datetime
import subprocess

import pandas as pd

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

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MERGE_SCRIPT = os.path.join(SKILLS_DIR, 'trade-gen2.2-un-partner-deep-mining', 'scripts', 'merge_research_findings.py')

SYSTEM_PROMPT = """당신은 무역 파트너 리서치 담당자입니다. Google Search 도구로 실제 검색한
결과에 근거해서만 답합니다.

검색 각도 (반드시 아래 각도를 모두 시도한 뒤 응답할 것 — 일반 검색 한 번만 하고 끝내지 말 것):
1. 일반 수입 디스트리뷰터/도매상 검색 (예: "{item} importer {country}")
2. LinkedIn 공개 프로필 검색 (예: "{item} broker OR agent {country} site:linkedin.com") —
   로그인 없이 공개된 프로필 URL만 대상으로 한다.
3. 현지어 및 현지 도메인(TLD) 검색 (예: 일본이면 site:.jp + 품목의 현지어 표기, 베트남이면
   site:.vn 등) — 영어 검색만으로는 현지 중소 디스트리뷰터가 잘 나오지 않으므로 반드시 시도한다.
4. 무역 전시회/협회 디렉토리 검색 (예: "{item} trade show exhibitor directory {country}",
   customs broker association directory).

이메일 확인 절차: 회사 홈페이지에 이메일이 안 보인다고 바로 빈 문자열로 넘기지 말고, 같은
도메인의 흔한 연락처 경로(/contact, /contact-us, /inquiry, /en/contact, /en/inquiry, /about)에
이메일이 있는지 1~2개 더 확인한 뒤에도 없으면 그때 빈 문자열로 남긴다.

출처 URL 확인 절차: 검색 결과에 뜬 링크라고 무조건 진짜 홈페이지로 가정하지 않는다. 그 URL이
접속되지 않거나 내용이 그 회사와 맞지 않으면, "{정확한 회사명} official site" 식으로 다시
검색해 실제로 접속되는 올바른 URL을 찾아 그것을 source_url로 쓴다. 못 찾으면 그 항목은 제외한다.

LinkedIn 등 회사 자체 홈페이지가 아닌 곳에서 회사를 발견했다면 거기서 검증을 끝내지 않는다.
회사 자체 웹사이트 URL이 확인/추정되면 그 웹사이트도 별도로 열어서 접속되는지, 연락처/문의
페이지에 이메일이 있는지 확인한다. LinkedIn 페이지만으로 source_url 요건을 채웠다고 회사 자체
사이트 확인을 생략하지 않는다. 접속을 확인하지 못한 웹사이트 URL은 website 필드에 넣지 않는다.

절대 규칙:
1. 실제로 검색해서 확인한 회사/에이전트만 보고한다. 지어내지 않는다.
2. 모든 항목에는 반드시 실제로 그 정보를 확인한 출처 URL(source_url)을 포함한다. 출처를
   특정할 수 없으면 그 항목 자체를 결과에서 제외한다.
3. 이메일/전화번호가 페이지에 공개되어 있지 않으면 절대 추측하지 않는다. 빈 문자열로 남긴다.
4. "이런 나라 회사는 보통 이런 이메일을 쓴다" 같은 패턴 기반 추정 금지.
5. 확실하지 않은 정보는 note 필드에 불확실하다고 명시한다.
6. 응답은 반드시 유효한 JSON 배열만 출력한다. 그 외 설명 텍스트는 출력하지 않는다.
   검색해도 확인 가능한 업체가 없으면 빈 배열 []을 반환한다.

각 항목은 아래 스키마를 정확히 따른다:
{
  "country": "국가명(영문, 요청받은 국가와 동일해야 함)",
  "name": "회사명 또는 에이전트 성함",
  "is_agent": true 또는 false,
  "email": "",
  "website": "",
  "linkedin": "",
  "messenger": "",
  "scope": "",
  "city": "영문 도시명",
  "country_en": "영문 국가명",
  "location_detail": "",
  "features": "실제로 확인한 취급 품목/특징",
  "coop_point": "협력 가능성 판단 근거",
  "source_url": "실제로 확인한 출처 URL (필수, http로 시작)",
  "note": ""
}"""


def print_error(missing, required_by, action):
    print("[ERROR]: Required file not found or misconfigured")
    print(f"- Missing: {missing}")
    print(f"- Required by: {required_by}")
    print(f"- Action: {action}")


def build_user_prompt(item, country, hs_context):
    return f"""'{item}'을(를) 취급하는 {country} 소재 실제 수입 디스트리뷰터 또는 독립 에이전트를
Google Search로 찾아주세요.

관련 HS Code/무역 데이터 맥락 (참고용, 그대로 보고하지 말고 검색에 활용):
{hs_context}

다음 검색 각도를 모두 시도하세요 (한 가지 검색만 하고 끝내지 마세요):
1. 일반 수입 디스트리뷰터/도매상 검색: "{item} importer {country}"
2. LinkedIn 공개 프로필 검색: "{item} broker OR agent {country} site:linkedin.com"
3. {country}의 현지어/현지 도메인(TLD) 검색 — 영어 검색으로 안 나오는 현지 중소 디스트리뷰터를
   찾기 위함
4. 무역 전시회/협회 디렉토리 검색: "{item} trade show exhibitor directory {country}"

국가당 최대 3개 업체까지, 실제로 검색으로 출처를 확인할 수 있는 것만 JSON 배열로 응답하세요."""


def call_gemini(prompt, model="gemini-2.5-flash"):
    from google import genai
    from google.genai import types

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")

    client = genai.Client(api_key=api_key)
    grounding_tool = types.Tool(google_search=types.GoogleSearch())
    config = types.GenerateContentConfig(
        tools=[grounding_tool],
        system_instruction=SYSTEM_PROMPT,
        temperature=0.0,
    )

    # Gemini 서버가 일시적으로 과부하 상태(503 UNAVAILABLE)일 때가 있어, 짧게 재시도한다.
    last_error = None
    for attempt in range(3):
        try:
            response = client.models.generate_content(model=model, contents=prompt, config=config)
            break
        except Exception as e:
            last_error = e
            is_transient = '503' in str(e) or 'UNAVAILABLE' in str(e) or '429' in str(e)
            if not is_transient or attempt == 2:
                raise
            wait_s = 2 ** (attempt + 1)
            print(f"   ⏳ 일시적 오류({e}), {wait_s}초 후 재시도 ({attempt + 1}/3)...")
            time.sleep(wait_s)
    else:
        raise last_error

    text = response.text or ""

    grounded_urls = []
    try:
        candidate = response.candidates[0]
        gm = candidate.grounding_metadata
        if gm and gm.grounding_chunks:
            for chunk in gm.grounding_chunks:
                if chunk.web and chunk.web.uri:
                    grounded_urls.append(chunk.web.uri)
    except Exception:
        pass

    return text, grounded_urls


def extract_json_array(text):
    text = text.strip()
    if text.startswith("```"):
        parts = text.split("```")
        if len(parts) >= 2:
            text = parts[1]
            if text.startswith("json"):
                text = text[4:]
    start = text.find('[')
    end = text.rfind(']')
    if start == -1 or end == -1 or end < start:
        return []
    try:
        parsed = json.loads(text[start:end + 1])
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []


def select_target_countries(excel_path, top_n):
    df = pd.read_excel(excel_path, sheet_name='Sourcing_Candidates')
    if '조사 상태' not in df.columns or '우선순위 점수' not in df.columns:
        return []
    df = df[df['조사 상태'].astype(str).str.contains('신규 후보', na=False)]
    df = df.sort_values(by='우선순위 점수', ascending=False)
    return df.head(top_n).to_dict('records')


def append_audit_log(audit_path, now_str, entries):
    os.makedirs(os.path.dirname(audit_path), exist_ok=True)
    with open(audit_path, 'a', encoding='utf-8') as f:
        for entry in entries:
            entry['timestamp'] = now_str
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')


def run(item, output_dir, item_slug, top_n, model):
    """단일 프로젝트를 조사한다. sys.exit()를 직접 호출하지 않고 종료 코드(int)를 반환한다 —
    run_all_projects.py가 여러 프로젝트에 대해 이 함수를 반복 호출할 때 한 프로젝트의 오류로
    전체 프로세스가 죽지 않도록 하기 위함. CLI 단독 실행 시의 종료 코드 처리는 하단
    `if __name__ == "__main__":` 블록이 담당한다."""
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    clean_item = item.split('(')[0].strip() if '(' in item else item.strip()
    slug = (item_slug or re.sub(r'[^a-zA-Z0-9]+', '_', item).strip('_').lower() or 'item')

    data_dir = os.path.join(output_dir, 'data')
    excel_path = os.path.join(data_dir, f'{slug}_buyers_leads.xlsx')

    print("=" * 60)
    print(f"🤖 완전 자동 딥마이닝 가동 (Gemini + Search Grounding): {item}")
    print("=" * 60)

    if not os.environ.get("GEMINI_API_KEY"):
        print_error(
            "GEMINI_API_KEY 환경변수",
            "autonomous_deep_mining.py",
            "GitHub Secrets(또는 로컬 환경변수)에 GEMINI_API_KEY를 설정하세요.",
        )
        return 1

    if not os.path.exists(excel_path):
        print_error(
            excel_path,
            "autonomous_deep_mining.py",
            "먼저 trade-gen2.1-un-sourcing으로 소싱 후보국가 트래커를 생성하세요.",
        )
        return 1

    targets = select_target_countries(excel_path, top_n)
    if not targets:
        print("조사할 신규 후보국이 없습니다 (모두 조사 완료 상태이거나 후보 없음). 종료합니다.")
        return 0

    print(f"이번 실행 대상 ({len(targets)}개국): {[t.get('국가 (Country)') for t in targets]}")

    all_findings = []
    audit_entries = []
    for row in targets:
        country = row.get('국가 (Country)')
        hs_context = row.get('EDA 데이터 근거 (HS Code별 순위/수입액/물량)', '')
        prompt = build_user_prompt(clean_item, country, hs_context)
        print(f"🔍 {country} 조사 중...")

        try:
            text, grounded_urls = call_gemini(prompt, model=model)
        except Exception as e:
            print(f"⚠️ {country} 조사 실패 (건너뜀): {e}")
            audit_entries.append({'country': country, 'error': str(e)})
            continue

        records = extract_json_array(text)
        valid = [r for r in records if r.get('source_url', '').strip().startswith('http')]
        rejected = len(records) - len(valid)
        if rejected:
            print(f"   ⚠️ 출처 URL 없어 {rejected}건 자동 제외")

        all_findings.extend(valid)
        audit_entries.append({
            'country': country,
            'raw_response': text,
            'grounded_urls': grounded_urls,
            'accepted': len(valid),
            'rejected': rejected,
        })
        print(f"   ✅ {len(valid)}건 확보")

    audit_path = os.path.join(data_dir, f'{slug}_auto_mining_log.jsonl')
    append_audit_log(audit_path, now_str, audit_entries)
    print(f"📄 감사 로그: {audit_path}")

    if not all_findings:
        print("확보된 findings가 없습니다 (전부 미확인/출처없음으로 제외됨). 병합 생략.")
        return 0

    tmp_findings_path = os.path.join(data_dir, f'.tmp_{slug}_auto_findings.json')
    with open(tmp_findings_path, 'w', encoding='utf-8') as f:
        json.dump(all_findings, f, ensure_ascii=False, indent=2)

    merge_cmd = [sys.executable, MERGE_SCRIPT, '--findings', tmp_findings_path, '--item', item, '--output_dir', output_dir]
    if item_slug:
        merge_cmd += ['--item_slug', item_slug]

    result = subprocess.run(merge_cmd)

    try:
        os.remove(tmp_findings_path)
    except OSError:
        pass

    return result.returncode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="완전 자동 딥마이닝 (Gemini API + Google Search grounding)")
    parser.add_argument("--item", type=str, required=True, help="품목명")
    parser.add_argument("--output_dir", type=str, required=True, help="프로젝트 루트 폴더")
    parser.add_argument("--item_slug", type=str, default=None, help="데이터 파일명 슬러그")
    parser.add_argument("--top_n", type=int, default=3, help="이번 실행에서 조사할 신규 후보국 수 (비용 통제, 기본 3)")
    parser.add_argument("--model", type=str, default="gemini-2.5-flash", help="사용할 Gemini 모델")
    args = parser.parse_args()

    sys.exit(run(args.item, args.output_dir, args.item_slug, args.top_n, args.model))
