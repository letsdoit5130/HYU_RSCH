#!/bin/bash
echo "======================================================="
echo "[Harness] test_pipeline_demo 수집-분석-리포팅 파이프라인 실행"
echo "======================================================="

PYTHON_EXE="../.venv/bin/python"
if [ ! -f "$PYTHON_EXE" ]; then
    PYTHON_EXE="python3"
fi

echo "- 사용 인터프리터: $PYTHON_EXE"
echo "- 파이프라인 시작..."

$PYTHON_EXE ../.agents/skills/crawler-analysis/scripts/run_pipeline.py --project test_pipeline_demo --url "https://news.naver.com"

echo "======================================================="
echo "[Harness] 실행이 완료되었습니다."
echo "======================================================="
