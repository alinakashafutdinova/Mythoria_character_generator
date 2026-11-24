@echo off
cd /d "%~dp0"
where py >nul 2>&1
if errorlevel 1 (echo Install Python 3 from python.org & pause & exit /b 1)
if not exist .venv\Scripts\python.exe py -3 -m venv .venv
.venv\Scripts\python.exe -c "import flask, waitress" >nul 2>&1
if errorlevel 1 .venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe tools\start.py
pause
