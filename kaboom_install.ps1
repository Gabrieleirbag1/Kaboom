$current_dir = Get-Location

# Create the virtual environment
if (-Not (Test-Path "$current_dir\venv")) {
    python -m venv "$current_dir\venv"
}

# Activate the virtual environment
& "$current_dir\venv\Scripts\Activate.ps1"

# Install dependencies
pip install -r "$current_dir\requirements.txt"

# Create Build directory only if it does not exist
if (-Not (Test-Path "$current_dir\Build")) {
    New-Item -ItemType Directory -Path "$current_dir\Build"
}
Set-Location "$current_dir\Build"

# Create the executable
pyinstaller --noconfirm --onefile --windowed --icon "$current_dir\Client\images\bombe-icon.ico" --add-data "$current_dir\Client\images;images" --add-data "$current_dir\Client\audio;audio" --add-data "$current_dir\Client\styles;styles" --add-data "$current_dir\Client\fonts;fonts" --add-data "$current_dir\Client\confs;confs" --add-data "$current_dir\Client\settings;settings" --add-data "$current_dir\Client\logs;logs" --distpath "$current_dir" --name "Kaboom" "$current_dir\Client\client.py"

# Deactivate the virtual environment
deactivate

# Remove the virtual environment
Remove-Item -Recurse -Force "$current_dir\venv"

# Return to the original directory
Set-Location $current_dir