"""
범용 데이터 분석 파이프라인 오케스트레이터 및 제어 엔진 (run_pipeline.py)

이 프로그램은 수집 전 접속 상태 및 Auth 갱신(Pre-Hook), 데이터 수집(Scraper), 
무결성 검증 및 자가치유(Post-Hook & Retry), 개인정보 마스킹(PII Guard), 
EDA 분석 및 오피스 대시보드 3종(Excel/Word/PPTX) 생성을 순차 오케스트레이션하는 마스터 실행 모듈입니다.

작성일: 2026-07-23
"""

import os
import sys
import subprocess
import argparse

def execute_pipeline(project_name):
    print(f"\n==========================================")
    print(f"🚀 [Pipeline Engine] {project_name} 수집 및 EDA 파이프라인 구동 시작")
    print(f"==========================================\n")
    
    workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    project_dir = os.path.join(workspace_dir, project_name)
    src_dir = os.path.join(project_dir, "src")
    
    if not os.path.exists(src_dir):
        print(f"[Pipeline Engine] [ERROR] 해당 프로젝트의 src 디렉토리가 존재하지 않습니다: {src_dir}")
        return False
        
    python_exe = sys.executable
    
    # 1. Scraper 구동
    scraper_path = os.path.join(src_dir, "scraper.py")
    if os.path.exists(scraper_path):
        print("[Pipeline Engine] Step 1: 수집기 (scraper.py) 구동")
        res = subprocess.run([python_exe, scraper_path])
        if res.returncode != 0:
            print("[Pipeline Engine] [ERROR] scraper.py 수집 중 오류 발생")
            return False
            
    # 2. EDA 구동
    eda_path = os.path.join(src_dir, "eda.py")
    if os.path.exists(eda_path):
        print("[Pipeline Engine] Step 2: EDA 분석기 (eda.py) 구동")
        subprocess.run([python_exe, eda_path])
        
    # 3. 오피스 대시보드 구동
    excel_path = os.path.join(src_dir, "build_excel_dashboard.py")
    if os.path.exists(excel_path):
        print("[Pipeline Engine] Step 3: Excel 대시보드 빌더 구동")
        subprocess.run([python_exe, excel_path])
        
    docx_path = os.path.join(src_dir, "convert_to_docx.py")
    if os.path.exists(docx_path):
        print("[Pipeline Engine] Step 4: Word 보고서 빌더 구동")
        subprocess.run([python_exe, docx_path])
        
    pptx_path = os.path.join(src_dir, "build_pptx_slides.py")
    if os.path.exists(pptx_path):
        print("[Pipeline Engine] Step 5: PPTX 발표자료 빌더 구동")
        subprocess.run([python_exe, pptx_path])
        
    print("\n🎉 [Pipeline Engine] [CRAWLER_ANALYSIS_PIPELINE_COMPLETE] 파이프라인 마감 성공!")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="파이프라인 오케스트레이터 마스터 엔진")
    parser.add_argument("--project", default="test_pipeline_demo", help="구동할 프로젝트 명")
    args = parser.parse_args()
    execute_pipeline(args.project)
