@echo off
cd /d "%~dp0"
echo Creating daily check-in task (08:00)...

schtasks /delete /tn "ikuuu_daily_checkin" /f >nul 2>&1

schtasks /create /tn "ikuuu_daily_checkin" ^
    /tr "\"%~dp0dist\ikuuu_sign.exe\" -s" ^
    /sc daily /st 08:00 /ru "%USERNAME%" /f

if %errorlevel% equ 0 (
    echo [OK] Runs daily at 08:00.
) else (
    echo [FAIL] Run as Administrator!
)
pause
