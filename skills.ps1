# 워크스페이스 가상환경의 python.exe를 사용하여 .agents/list_skills.py를 실행합니다.
$PythonPath = "$PSScriptRoot\.venv\Scripts\python.exe"
if (Test-Path $PythonPath) {
    & $PythonPath "$PSScriptRoot\.agents\list_skills.py" $args
} else {
    & python "$PSScriptRoot\.agents\list_skills.py" $args
}
