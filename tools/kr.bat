@echo off
rem Windows entry point: loads the VS 2022 C++ environment, then runs the Git Bash scripts.
rem usage: tools\kr.bat setup C:\Games\jak1.iso   (OpenGOAL build + ISO extract, once)
rem        tools\kr.bat build [dev^|release]       (Korean font + translations)
rem        tools\kr.bat run                        (start the game)
rem        tools\kr.bat package ^<version^>        (prebuilt patch zip in dist\, after build release)
setlocal
set "ROOT=%~dp0.."
set "GK=%ROOT%\jak-project\out\build\Release\bin\gk.exe"

if /i "%~1"=="run" (
  if not exist "%GK%" echo gk.exe not found: run "tools\kr.bat setup" first & exit /b 1
  pushd "%ROOT%\jak-project"
  start "" "%GK%" -- -boot -fakeiso
  popd
  exit /b 0
)
if /i "%~1"=="setup" (set "SCRIPT=tools/setup_opengoal.sh") else if /i "%~1"=="build" (set "SCRIPT=tools/build_kr.sh") else if /i "%~1"=="package" (set "SCRIPT=tools/package_kr.sh") else (
  echo usage: tools\kr.bat setup ^<jak1.iso^> ^| build [dev^|release] ^| package ^<version^> ^| run
  exit /b 1
)

set "VSWHERE=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer\vswhere.exe"
if not exist "%VSWHERE%" echo Visual Studio 2022 C++ tools not found (see README) & exit /b 1
set "VS="
for /f "usebackq delims=" %%i in (`"%VSWHERE%" -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath`) do set "VS=%%i"
if not defined VS echo Visual Studio 2022 C++ tools not found (see README) & exit /b 1
rem vcvars64 calls vswhere itself
set "PATH=%ProgramFiles(x86)%\Microsoft Visual Studio\Installer;%PATH%"
call "%VS%\VC\Auxiliary\Build\vcvars64.bat" >nul || exit /b 1

rem winget does not put LLVM and NASM on PATH
if exist "%ProgramFiles%\LLVM\bin" set "PATH=%ProgramFiles%\LLVM\bin;%PATH%"
if exist "%LOCALAPPDATA%\bin\NASM" set "PATH=%LOCALAPPDATA%\bin\NASM;%PATH%"
if exist "%ProgramFiles%\NASM" set "PATH=%ProgramFiles%\NASM;%PATH%"

set "BASH=%ProgramFiles%\Git\bin\bash.exe"
if not exist "%BASH%" set "BASH=%USERPROFILE%\scoop\apps\git\current\bin\bash.exe"
if not exist "%BASH%" echo Git Bash not found (install Git for Windows) & exit /b 1

cd /d "%ROOT%"
rem Git Bash's /usr/bin/link would shadow MSVC link.exe, so put cl's directory first
"%BASH%" -c "export PATH=\"$(dirname \"$(command -v cl)\"):$PATH\"; exec \"$0\" \"$@\"" %SCRIPT% %2
