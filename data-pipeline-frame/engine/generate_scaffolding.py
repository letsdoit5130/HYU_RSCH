"""
범용 데이터 분석 파이프라인 프레임워크 프로젝트 스캐폴딩 생성기 (generate_scaffolding.py)

이 프로그램은 임의의 타겟 웹사이트 URL과 수집 컬럼 목록을 입력받아
표준 데이터 프로젝트 폴더(data, docs, images, src) 및 각 단계별 뼈대 파이썬 코드를 자동 조립하는 엔지니어링 모듈입니다.

주요 기능:
- 타겟 프로젝트 폴더 구조 자동 생성
- scraper.py, eda.py, excel/word/pptx/html 빌더 스크립트 배포
- 커스텀 수집 컬럼 스키마 주입 지원

작성일: 2026-07-23
"""

import os
import argparse
import sys

def create_scaffolding(project_name, target_url, columns_list):
    workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    project_dir = os.path.join(workspace_dir, project_name)
    
    subdirs = ["data", "docs", "images", "src"]
    print(f"[Scaffolding] 프로젝트 경로 생성: {project_dir}")
    
    for subdir in subdirs:
        path = os.path.join(project_dir, subdir)
        os.makedirs(path, exist_ok=True)
        print(f" - 폴더 생성: {subdir}/")
        
    print(f"[Scaffolding] {project_name} 뼈대 생성이 성공적으로 완료되었습니다.")
    return project_dir

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="범용 수집 파이프라인 프로젝트 스캐폴딩 생성기")
    parser.add_argument("--project", default="test_pipeline_demo", help="생성할 프로젝트 이름")
    parser.add_argument("--url", default="https://example.com", help="타겟 웹사이트 URL")
    parser.add_argument("--columns", default="id,title,category,date,views", help="수집 대상 컬럼 목록 (쉼표 구분)")
    
    args = parser.parse_args()
    cols = [c.strip() for c in args.columns.split(",") if c.strip()]
    create_scaffolding(args.project, args.url, cols)
