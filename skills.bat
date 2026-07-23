@echo off
chcp 65001 > nul
rem 워크스페이스 가상환경의 python.exe를 사용하여 .agents/list_skills.py를 실행합니다.
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0.agents\list_skills.py" %*
) else (
    python "%~dp0.agents\list_skills.py" %*
)
