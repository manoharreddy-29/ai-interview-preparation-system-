@echo off
title Push to GitHub
echo ======================================================================
echo    Pushing AI-Based Student Answer Evaluation System to GitHub
echo ======================================================================
echo.

set "PATH=C:\Program Files\Microsoft SQL Server Management Studio 22\Release\Common7\IDE\CommonExtensions\Microsoft\TeamFoundation\Team Explorer\Git\cmd;%PATH%"

git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================================================
    echo  [SUCCESS] Code successfully pushed to GitHub!
    echo  View repository: https://github.com/manoharreddy-29/ai-interview-preparation-system-
    echo ======================================================================
) else (
    echo.
    echo ======================================================================
    echo  [NOTICE] If GitHub requires sign-in:
    echo  Please log in using your GitHub credentials in the browser window
    echo  or provide a GitHub Personal Access Token.
    echo ======================================================================
)
echo.
pause
