@echo off
chcp 65001 > nul
echo =======================================================
echo [Harness] test_pipeline_demo 수집-분석-리포팅 파이프라인 실행
echo =======================================================

set PYTHON_EXE=..\.venv\Scripts\python.exe
if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=python
)

echo - 사용 인터프리터: %PYTHON_EXE%
echo - 파이프라인 시작...

"%PYTHON_EXE%" ..\.agents\skills\crawler-analysis\scripts\run_pipeline.py --project test_pipeline_demo --url "https://news.naver.com"

echo =======================================================
echo [Harness] 실행이 완료되었습니다.
echo =======================================================
pause
