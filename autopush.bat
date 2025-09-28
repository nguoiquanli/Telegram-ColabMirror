@echo off
cd /d "%~dp0"

if exist ".git\index.lock" (
  attrib -r -s -h ".git\index.lock" >nul 2>&1
  del /f /q ".git\index.lock"
)

git add -A

set MSG=%*
if "%MSG%"=="" (
  for /f "tokens=1-4 delims=/ " %%a in ("%date%") do set TODAY=%%a-%%b-%%c
  set MSG=auto-push !TODAY! %time%
)
git commit -m "%MSG%"

git push origin main