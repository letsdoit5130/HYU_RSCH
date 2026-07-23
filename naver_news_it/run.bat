@echo off
chcp 65001 > nul
echo =======================================================
echo [Harness] naver_news_it 수집-분석-리포팅 파이프라인 실행
echo =======================================================

REM 공통 가상환경 파이썬 확인
set PYTHON_EXE=..\.venv\Scripts\python.exe
if not exist "%PYTHON_EXE%" (
    set PYTHON_EXE=python
)

echo - 사용 인터프리터: %PYTHON_EXE%
echo - 파이프라인 시작...

"%PYTHON_EXE%" ..\.agents\skills\crawler-analysis\scripts\run_pipeline.py --project naver_news_it --url "https://news.naver.com/section/105"

echo =======================================================
echo [Harness] 실행이 완료되었습니다.
echo =======================================================
pause
