@echo off
chcp 65001 >nul
rem Jak 1 Korean patch: extract the user's ISO, then decompile and compile the game with the patch.
setlocal
cd /d "%~dp0"
set "ISO=%~1"
if not "%ISO%"=="" goto have_iso
echo 잭 앤 덱스터 ISO 파일(NTSC-U, SCUS-97124)을 이 창에 끌어다 놓고 Enter 를 누르세요.
set /p "ISO=ISO 파일: "
:have_iso
set "ISO=%ISO:"=%"
if not exist "%ISO%" (
  echo 파일을 찾을 수 없습니다: %ISO%
  goto fail
)
echo.
echo 게임 데이터를 추출하고 한글 패치를 빌드합니다. 몇 분 걸립니다...
"%~dp0extractor.exe" -e -v -d -c --disable-ansi "%ISO%"
if errorlevel 1 goto fail
echo.
echo 설치가 끝났습니다. play.bat 으로 게임을 실행하세요.
pause
exit /b 0

:fail
echo.
echo 설치하지 못했습니다. data\log 폴더의 extractor 로그를 확인하세요.
pause
exit /b 1
