@echo off
setlocal

cd /d "%~dp0"

set "REPO_URL=https://github.com/Turnstone7512/CPI_Dashboard.git"
set "BRANCH=main"
set "GIT_TERMINAL_PROMPT=0"

where git >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Git was not found. Please install Git for Windows first.
  pause
  exit /b 1
)

if not exist ".git" (
  git init
  if errorlevel 1 goto failed
)

git branch -M %BRANCH%
if errorlevel 1 goto failed

git config user.name "Turnstone7512"
if errorlevel 1 goto failed

git config user.email "Turnstone7512@users.noreply.github.com"
if errorlevel 1 goto failed

git remote get-url origin >nul 2>nul
if errorlevel 1 (
  git remote add origin %REPO_URL%
) else (
  git remote set-url origin %REPO_URL%
)
if errorlevel 1 goto failed

git add index.html README.md .nojekyll .gitignore Python push-to-github.cmd
if errorlevel 1 goto failed

git diff --cached --quiet
if errorlevel 1 (
  git commit -m "Deploy static CPI dashboard"
  if errorlevel 1 goto failed
) else (
  echo [INFO] No file changes to commit.
)

git fetch origin %BRANCH%
if not errorlevel 1 (
  git merge --allow-unrelated-histories -X ours --no-edit origin/%BRANCH%
  if errorlevel 1 goto failed
)

git push -u origin %BRANCH%
if errorlevel 1 goto failed

echo.
echo [OK] Uploaded to %REPO_URL%
echo [OK] Set GitHub Pages to branch main and folder /root.
pause
exit /b 0

:failed
echo.
echo [ERROR] Upload failed.
echo If this is an authentication error, sign in with Git Credential Manager first.
echo If you want a no-prompt token version, provide a GitHub Personal Access Token.
pause
exit /b 1
