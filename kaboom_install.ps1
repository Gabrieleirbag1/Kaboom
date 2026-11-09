# Builds the compiled game (Python and Qt inside) in dist\windows\Kaboom with build.py.
#   .\kaboom_install.ps1 [build.py options: --package --archive --smoke]
#   --package also makes Releases\kaboom-setup-<version>.exe (needs Inno Setup 6)
$current_dir = $PSScriptRoot

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

# Install the game's packages and PyInstaller, then build
& "$current_dir\venv\Scripts\python.exe" -m pip install -r "$current_dir\requirements-build.txt"
if ($LASTEXITCODE -ne 0) { exit 1 }
& "$current_dir\venv\Scripts\python.exe" "$current_dir\build.py" @args
$buildResult = $LASTEXITCODE

# Remove the virtual environment
Remove-Item -Recurse -Force "$current_dir\venv"

if ($buildResult -ne 0) { exit $buildResult }
Write-Host "Kaboom build completed: $current_dir\dist\windows\Kaboom\Kaboom.exe"
