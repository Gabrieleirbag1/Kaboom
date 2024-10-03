$current_dir = Get-Location

# Install dependencies
pip3 install -r "$current_dir\requirements.txt"

# Create dist directory only if it does not exist
if (-Not (Test-Path "$current_dir\dist")) {
    New-Item -ItemType Directory -Path "$current_dir\dist"
}
Set-Location "$current_dir\dist"

# Create the executable
pyinstaller --noconfirm --onefile --windowed --icon "$current_dir\Client\images\bombe-icon.ico" --add-data "$current_dir\Client\images;images\" --add-data "$current_dir\Client\audio;audio\" --add-data "$current_dir\Client\styles;styles\" --add-data "$current_dir\Client\fonts;fonts\" --add-data "$current_dir\Client\confs;confs\" --add-data "$current_dir\Client\settings;settings\" --add-data "$current_dir\Client\logs;logs\" --distpath "$current_dir" --name "Kaboom" "$current_dir\Client\client.py"