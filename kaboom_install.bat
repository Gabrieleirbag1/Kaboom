@echo off
setlocal

set "current_dir=%cd%"

:: Create the virtual environment
if not exist "%current_dir%\venv" (
    python -m venv "%current_dir%\venv"
)

:: Activate the virtual environment
call "%current_dir%\venv\Scripts\activate.bat"

:: Install dependencies
pip install -r "%current_dir%\requirements.txt"

:: Create Build directory only if it does not exist
if not exist "%current_dir%\Build" (
    mkdir "%current_dir%\Build"
)
cd /d "%current_dir%\Build"

:: Create the executable
pyinstaller --noconfirm --onefile --windowed --icon "%current_dir%\Client\images\bombe-icon.ico" --add-data "%current_dir%\Client\images;images" --add-data "%current_dir%\Client\audio;audio" --add-data "%current_dir%\Client\styles;styles" --add-data "%current_dir%\Client\fonts;fonts" --add-data "%current_dir%\Client\confs;confs" --add-data "%current_dir%\Client\settings;settings" --add-data "%current_dir%\Client\logs;logs" --distpath "%current_dir%" --name "Kaboom" "%current_dir%\Client\client.py"

:: Deactivate the virtual environment
call deactivate

:: Remove the virtual environment
rd /s /q "%current_dir%\venv"

:: Return to the original directory
cd /d "%current_dir%"

endlocal