"""
trade-eda-generator → partner-sourcing-generator를 한 번의 명령으로 순차 실행하는 오케스트레이터.

두 스크립트 모두 결정적(deterministic) pandas 스크립트이므로 이 래퍼는 그냥 순서대로
subprocess로 호출할 뿐, 판단이나 웹 검색은 하지 않는다.

주의: 3단계(partner-deep-mining, 실제 웹 검색으로 파트너 찾기)는 여기 포함되지 않는다.
그건 AI가 WebSearch/WebFetch로 직접 수행해야 하는 작업이라 단일 CLI 명령으로 만들 수 없다
(정직하게 못 되는 걸 되는 척 자동화하지 않는다). 이 스크립트 실행 후 사용자가 자연어로
"파트너 리서치도 해줘" 라고 요청하면 그때 AI 에이전트가 3단계를 이어서 수행한다.
"""

import os
import sys
import argparse
import subprocess

if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

SKILLS_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
EDA_SCRIPT = os.path.join(SKILLS_DIR, 'trade-eda-generator', 'scripts', 'generate_trade_eda.py')
SOURCING_SCRIPT = os.path.join(SKILLS_DIR, 'partner-sourcing-generator', 'scripts', 'generate_partner_sourcing.py')


def run_step(label, cmd):
    print("=" * 60)
    print(f"▶ {label}")
    print("=" * 60)
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"❌ {label} 실패 (exit code {result.returncode}) — 파이프라인 중단")
        sys.exit(result.returncode)
    print(f"✅ {label} 완료\n")


def main():
    parser = argparse.ArgumentParser(
        description="trade-eda-generator + partner-sourcing-generator 원샷 실행"
    )
    parser.add_argument("--input", required=True, help="무역 통계 CSV 경로")
    parser.add_argument("--item", required=True, help="품목명 (예: '전복 (Abalone)')")
    parser.add_argument("--output_dir", required=True, help="프로젝트 루트 폴더")
    parser.add_argument("--item_slug", default=None, help="데이터 파일명 슬러그 (생략 시 자동 생성)")
    args = parser.parse_args()

    for path, label in [(EDA_SCRIPT, "trade-eda-generator"), (SOURCING_SCRIPT, "partner-sourcing-generator")]:
        if not os.path.exists(path):
            print(f"[ERROR]: Required file not found")
            print(f"- Missing: {path}")
            print(f"- Required by: run_pipeline.py ({label})")
            print(f"- Action: 스킬 디렉터리 구조를 확인하세요.")
            sys.exit(1)

    eda_cmd = [sys.executable, EDA_SCRIPT, "--input", args.input, "--item", args.item, "--output_dir", args.output_dir]
    run_step("1/2 trade-eda-generator (EDA 리포트 + 15개 차트 생성)", eda_cmd)

    sourcing_cmd = [sys.executable, SOURCING_SCRIPT, "--item", args.item, "--output_dir", args.output_dir]
    if args.item_slug:
        sourcing_cmd += ["--item_slug", args.item_slug]
    run_step("2/2 partner-sourcing-generator (소싱 후보국가 우선순위 산출)", sourcing_cmd)

    clean_item = args.item.split('(')[0].strip() if '(' in args.item else args.item.strip()
    print("=" * 60)
    print("🎉 1~2단계 파이프라인 완료")
    print(f"   - EDA 리포트: {args.output_dir}/reports/BIZ-{clean_item}_Gathered_EDA_Report.md")
    print(f"   - 소싱 후보국가: {args.output_dir}/reports/{clean_item}_Buyers_Lead_List.md")
    print()
    print("👉 3단계(실제 파트너 검색)는 자동화 대상이 아닙니다. AI 에이전트에게 자연어로 요청하세요:")
    print(f'   예: "{clean_item} 우선순위 상위 국가들 로컬파트너 실제로 찾아서 정리해줘"')
    print("=" * 60)


if __name__ == "__main__":
    main()
