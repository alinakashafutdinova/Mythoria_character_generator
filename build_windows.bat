@echo off
cd /d "%~dp0"
py -3 -m pip install -r requirements-dev.txt
py -3 -m PyInstaller --noconfirm mythoria.spec
if errorlevel 1 (echo Build failed & exit /b 1)
echo Ready: dist\Mythoria\Mythoria.exe
