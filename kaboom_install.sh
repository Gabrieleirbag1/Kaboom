#!/bin/bash
# Builds the compiled game (Python and Qt inside) in dist/linux/Kaboom with build.py.
#   ./kaboom_install.sh [--desktop|-d] [build.py options: --package --archive --smoke]
#   --desktop: also add Kaboom to the applications menu of this user
set -e

current_dir=$(cd "$(dirname "$0")" && pwd)

# Parse command line arguments
create_desktop=false
build_args=()
for arg in "$@"
do
    if [ "$arg" == "--desktop" ] || [ "$arg" == "-d" ]; then
        create_desktop=true
    else
        build_args+=("$arg")
    fi
done

if command -v dpkg > /dev/null 2>&1; then
    # Install the venv package matching the system python3 (e.g. python3.14-venv) if not installed
    venv_pkg="python$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')-venv"
    if ! dpkg -l | grep -q "$venv_pkg"; then
        echo "Installing $venv_pkg..."
        sudo apt-get install -y "$venv_pkg"
    else
        echo "$venv_pkg is already installed."
    fi

    # Check if binutils is installed (provides objdump, used by PyInstaller)
    if ! dpkg -l | grep -q binutils; then
        echo "Installing binutils (required for objdump)..."
        sudo apt-get install -y binutils
    else
        echo "binutils is already installed."
    fi
fi

# Create the virtual environment
if [ ! -d "$current_dir/venv" ]; then
    python3 -m venv "$current_dir/venv"
fi

# Install the game's packages and PyInstaller, then build
"$current_dir/venv/bin/pip" install -r "$current_dir/requirements-build.txt"
"$current_dir/venv/bin/python" "$current_dir/build.py" "${build_args[@]}"

# Remove the virtual environment
rm -rf "$current_dir/venv"

# Check if user is on MacOS and if --desktop or -d option is provided
if [ "$(uname)" != "Darwin" ] && [ "$create_desktop" = true ]; then
    # Create the .desktop file only if it does not exist
    desktop_file_path="$HOME/.local/share/applications/kaboom.desktop"
    if [ ! -f "$desktop_file_path" ]; then
        executable_path="$current_dir/dist/linux/Kaboom/Kaboom"
        icon_path="$current_dir/Client/images/bombe-icon.png"

        # Write the .desktop file
        mkdir -p "$(dirname "$desktop_file_path")"
        echo "[Desktop Entry]" > "$desktop_file_path"
        echo "Version=1.1" >> "$desktop_file_path"
        echo "Name=Kaboom" >> "$desktop_file_path"
        echo "Exec=$executable_path" >> "$desktop_file_path"
        echo "Icon=$icon_path" >> "$desktop_file_path"
        echo "Type=Application" >> "$desktop_file_path"
        echo "Categories=Game;" >> "$desktop_file_path"

        # Make the .desktop file executable
        chmod +x "$desktop_file_path"
    fi
fi

echo "Kaboom build completed: $current_dir/dist/linux/Kaboom/Kaboom"
