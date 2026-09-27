@echo off
setlocal

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\launch.ps1"

if errorlevel 1 (
    echo.
    echo Une erreur s'est produite. Voir le detail ci-dessus.
    pause
) else (
    echo.
    echo Interface lancee. Cette fenetre peut etre fermee.
    timeout /t 3 >nul
)
