"""
완도 전복 글로벌 무역 EDA, 바이어 DB 수집 및 5대 산출물 자동 갱신 통합 파이프라인 스크립트

이 스크립트는 매일 자정 GitHub Actions 또는 수동 실행 시:
1. crawler_buyer.py를 통해 8대 컬럼 스키마 글로벌 바이어 DB 수집/갱신
2. make_xlsx_data.py를 통해 Excel 데이터북 6개 시트 갱신
3. make_html_dashboard.py를 통해 반응형 HTML 대시보드 UI 갱신
4. make_full_docx_report.py를 통해 통합 DOCX 보고서 갱신
5. make_pptx_deck.py를 통해 PowerPoint 16:9 발표자료 덱을 순차적으로 갱신합니다.
"""

import os
import subprocess
import sys

def run_script(script_path):
    print(f"\n==================================================")
    print(f">> EXECUTING: {script_path}")
    print(f"==================================================")
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, encoding='utf-8')
    if result.returncode == 0:
        print(result.stdout)
        print(f"[SUCCESS] {script_path}")
    else:
        print(f"[ERROR] in {script_path}:\n{result.stderr}")
        sys.exit(result.returncode)

def main():
    base_dir = os.path.join("BIZ-Jeonbok", "src")
    
    scripts = [
        os.path.join("BIZ-Jeonbok", "src", "crawler_buyer.py"),
        os.path.join("BIZ-Jeonbok", "src", "verify_real_web.py"),
        os.path.join("BIZ-Jeonbok", "src", "verify_buyers.py"),
        os.path.join("BIZ-Jeonbok", "src", "make_xlsx_data.py"),
        os.path.join("BIZ-Jeonbok", "src", "make_html_dashboard.py"),
        os.path.join("BIZ-Jeonbok", "src", "make_full_docx_report.py"),
        os.path.join("BIZ-Jeonbok", "src", "make_pptx_deck.py")
    ]
    
    for s in scripts:
        if os.path.exists(s):
            run_script(s)
        else:
            print(f"⚠ Warning: Script {s} not found.")

    print("\n[COMPLETE] ALL PIPELINE STEPS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    main()
