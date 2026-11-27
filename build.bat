@echo off
cd /d "%~dp0"
py -3.14 -m pip install -r requirements-build.txt
if errorlevel 1 goto fail
py -3.14 -m PyInstaller --clean --noconfirm NX2FlowSender.spec
if errorlevel 1 goto fail
explorer dist
exit /b 0
:fail
echo Build failed. Review the errors above.
pause
exit /b 1
