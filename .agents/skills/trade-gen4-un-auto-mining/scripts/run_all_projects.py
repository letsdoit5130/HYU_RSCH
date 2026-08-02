"""
`autonomous_deep_mining.py`를 저장소 전체의 프로젝트에 대해 자동으로 찾아 반복 실행하는 래퍼.

새 품목(BIZ-* 프로젝트)이 생겨도 이 스크립트나 GitHub Actions 워크플로우를 수정할 필요가
없도록 하기 위한 것이다: `trade-gen1-un-eda` → `trade-gen2.1-un-sourcing`을 한 번이라도 거쳐
`{slug}_buyers_leads.xlsx`에 `Sourcing_Candidates` 시트가 생긴 프로젝트는 다음 실행부터
자동으로 이 스크립트에 발견되어 처리된다.

`--item`/`--output_dir`/`--item_slug`를 모두 명시하면 발견 로직을 건너뛰고 그 프로젝트
하나만 처리한다 (workflow_dispatch로 단일 프로젝트만 온디맨드 실행할 때 사용).
"""

import os
import sys
import glob
import argparse

import openpyxl

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import autonomous_deep_mining as adm

BUYERS_LEADS_SUFFIX = '_buyers_leads.xlsx'


def discover_projects():
    """저장소 루트 기준으로 BIZ-*/data/*_buyers_leads.xlsx를 스캔해, 실제로
    `trade-gen2.1-un-sourcing`을 거쳐 `Sourcing_Candidates` 시트가 있는 파일만 프로젝트로
    인정한다. 구버전 포맷(예: Buyer_Leads/Overall_Breakdown 시트만 있는 파일)은 제외된다."""
    projects = []
    for path in sorted(glob.glob(os.path.join('BIZ-*', 'data', f'*{BUYERS_LEADS_SUFFIX}'))):
        filename = os.path.basename(path)
        item_slug = filename[:-len(BUYERS_LEADS_SUFFIX)]
        output_dir = path.split(os.sep)[0]

        try:
            wb = openpyxl.load_workbook(path, read_only=True)
        except Exception as e:
            print(f"⚠️ {path} 열기 실패, 건너뜀: {e}")
            continue

        if 'Sourcing_Candidates' not in wb.sheetnames:
            print(f"— {path}: Sourcing_Candidates 시트 없음 (구버전 포맷으로 추정), 건너뜀")
            continue

        item = item_slug.replace('_', ' ').title()
        projects.append({'item': item, 'output_dir': output_dir, 'item_slug': item_slug})

    return projects


def run_all(projects, top_n, model):
    if not projects:
        print("발견된 프로젝트가 없습니다 (BIZ-*/data/*_buyers_leads.xlsx 중 Sourcing_Candidates가 있는 파일 없음).")
        return 0

    print(f"📋 발견된 프로젝트 ({len(projects)}개): {[p['item_slug'] for p in projects]}")

    results = {}
    for project in projects:
        print("\n" + "=" * 60)
        print(f"▶ 프로젝트: {project['item_slug']} ({project['output_dir']})")
        print("=" * 60)
        try:
            code = adm.run(project['item'], project['output_dir'], project['item_slug'], top_n, model)
        except Exception as e:
            print(f"⚠️ {project['item_slug']} 처리 중 예외 발생 (다음 프로젝트로 계속): {e}")
            code = 1
        results[project['item_slug']] = code

    print("\n" + "=" * 60)
    print("📊 전체 실행 요약")
    for slug, code in results.items():
        print(f"  - {slug}: {'✅ 성공' if code == 0 else '⚠️ 실패'}")
    print("=" * 60)

    # 하나라도 성공했으면 커밋할 변경 사항이 있을 수 있으므로 워크플로우 전체를 실패로 처리하지
    # 않는다. 전부 실패한 경우에만 비정상 종료로 보고한다.
    return 0 if any(code == 0 for code in results.values()) else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="전 프로젝트 자동 발견 + 딥마이닝 반복 실행")
    parser.add_argument("--item", type=str, default=None, help="지정 시 이 프로젝트만 처리 (발견 로직 건너뜀)")
    parser.add_argument("--output_dir", type=str, default=None, help="--item과 함께 지정")
    parser.add_argument("--item_slug", type=str, default=None, help="--item과 함께 지정")
    parser.add_argument("--top_n", type=int, default=10000, help="프로젝트당 조사할 신규 후보국 수")
    parser.add_argument("--model", type=str, default="gemini-2.5-flash", help="사용할 Gemini 모델")
    args = parser.parse_args()

    if args.item and args.output_dir and args.item_slug:
        target_projects = [{'item': args.item, 'output_dir': args.output_dir, 'item_slug': args.item_slug}]
    else:
        target_projects = discover_projects()

    sys.exit(run_all(target_projects, args.top_n, args.model))
