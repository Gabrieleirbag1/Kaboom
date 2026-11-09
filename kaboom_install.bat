@echo off
:: Builds the compiled game (Python and Qt inside) in dist\windows\Kaboom with build.py.
::   kaboom_install.bat [build.py options: --package --archive --smoke]
::   --package also makes Releases\kaboom-setup-<version>.exe (needs Inno Setup 6)
setlocal

set "current_dir=%~dp0"
if "%current_dir:~-1%"=="\" set "current_dir=%current_dir:~0,-1%"

:: Pick Python: prefer 3.14 through the py launcher, otherwise use python on PATH
set "PYTHON=python"
py -3.14 --version >nul 2>&1
if not errorlevel 1 set "PYTHON=py -3.14"
%PYTHON% --version >nul 2>&1
if errorlevel 1 (
    echo Python 3 is not installed or not on PATH.
    exit /b 1
)
for /f "delims=" %%v in ('%PYTHON% --version') do echo Using %%v

:: Create the virtual environment
if not exist "%current_dir%\venv" (
    %PYTHON% -m venv "%current_dir%\venv"
)

:: Install the game's packages and PyInstaller, then build
"%current_dir%\venv\Scripts\python.exe" -m pip install -r "%current_dir%\requirements-build.txt"
if errorlevel 1 exit /b 1
"%current_dir%\venv\Scripts\python.exe" "%current_dir%\build.py" %*
set "build_result=%errorlevel%"

:: Remove the virtual environment
rd /s /q "%current_dir%\venv"

if not "%build_result%"=="0" exit /b %build_result%
echo Kaboom build completed: %current_dir%\dist\windows\Kaboom\Kaboom.exe
endlocal
