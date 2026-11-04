$current_dir = Get-Location

# Pick Python: prefer 3.14 through the py launcher, otherwise use python on PATH
$python = "python"
$pythonArgs = @()
if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3.14 --version *> $null
    if ($LASTEXITCODE -eq 0) {
        $python = "py"
        $pythonArgs = @("-3.14")
    }
}
& $python @pythonArgs --version *> $null
if (-Not $?) {
    Write-Error "Python 3 is not installed or not on PATH."
    exit 1
}
Write-Host "Using $(& $python @pythonArgs --version)"

# Create the virtual environment
if (-Not (Test-Path "$current_dir\venv")) {
    & $python @pythonArgs -m venv "$current_dir\venv"
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