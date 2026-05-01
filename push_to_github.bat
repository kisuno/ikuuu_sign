@echo off
setlocal
cd /d "%~dp0"

set TOKEN=%GITHUB_TOKEN%
set USER=kisuno

if "%TOKEN%"=="" (
    echo Please set GITHUB_TOKEN environment variable first!
    echo   set GITHUB_TOKEN=ghp_xxxxxxxxxxxx
    echo Or paste your token below:
    set /p TOKEN="Token: "
)

echo ========================================
echo   Push ikuuu_sign to GitHub
echo ========================================

REM Find Git
for %%g in ("C:\Program Files\Git\bin\git.exe" "C:\Program Files (x86)\Git\bin\git.exe") do (
    if exist %%g set GIT=%%g
)
if not defined GIT (
    echo Git not found!
    pause & exit /b 1
)

REM Commit
%GIT% add -A
%GIT% commit -m "Update: Linux/macOS CI, credit DeepSeek V4 Pro" 2>nul

REM Tag
%GIT% tag -f v1.0.0

REM Remote
%GIT% remote remove origin 2>nul
%GIT% remote add origin https://%USER%:%TOKEN%@github.com/%USER%/ikuuu_sign.git

REM Push with retry
set RETRY=0
:push
%GIT% push -u origin main --tags --force
if %errorlevel% equ 0 goto done
set /a RETRY+=1
if %RETRY% lss 5 (
    echo Retry %RETRY%/5...
    timeout /t 5 >nul
    goto push
)
echo FAILED. Check your network/proxy.
pause & exit /b 1

:done
echo SUCCESS! https://github.com/%USER%/ikuuu_sign
pause
