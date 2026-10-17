@echo off
chcp 65001 >nul
rem Start the game. --portable keeps settings and saves next to gk.exe, apart from other OpenGOAL installs.
cd /d "%~dp0"
if not exist "data\out\jak1" (
  echo 먼저 install.bat 으로 설치하세요.
  pause
  exit /b 1
)
start "" "%~dp0gk.exe" --portable -- -boot -fakeiso
