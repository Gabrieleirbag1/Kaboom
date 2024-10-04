current_dir=$(pwd)

#Create the virtual environment
if [ ! -d "$current_dir/venv" ]; then
    python3 -m venv "$current_dir/venv"
fi

# Activate the virtual environment
source "$current_dir/venv/bin/activate"

# Install dependencies
pip3 install -r "$current_dir/requirements.txt"

# Create Build directory only if it does not exist
if [ ! -d "$current_dir/Build" ]; then
    mkdir -p "$current_dir/Build"
fi
cd "$current_dir/Build"

# Create the executable
pyinstaller --noconfirm --onefile --windowed --icon "$current_dir/Client/images/bombe-icon.ico" --add-data "$current_dir/Client/images:images/" --add-data "$current_dir/Client/audio:audio/" --add-data "$current_dir/Client/styles:styles/" --add-data "$current_dir/Client/fonts:fonts/" --add-data "$current_dir/Client/confs:confs/" --add-data "$current_dir/Client/settings:settings/" --add-data "$current_dir/Client/logs:logs/" --distpath "$current_dir" --name "Kaboom" "$current_dir/Client/client.py"

# Deactivate the virtual environment
deactivate

# Remove the virtual environment
rm -rf "$current_dir/venv"

# Check if user is on MacOS
if [ "$(uname)" != "Darwin" ]; then
    # Create the .desktop file only if it does not exist
    desktop_file_path="$HOME/.local/share/applications/kaboom.desktop"
    if [ ! -f "$desktop_file_path" ]; then
        executable_path="$current_dir/Kaboom"
        icon_path="$current_dir/Client/images/bombe-icon.png"

        # Write the .desktop file
        echo "[Desktop Entry]" > "$desktop_file_path"
        echo "Version=1.0" >> "$desktop_file_path"
        echo "Name=Kaboom" >> "$desktop_file_path"
        echo "Exec=$executable_path" >> "$desktop_file_path"
        echo "Icon=$icon_path" >> "$desktop_file_path"
        echo "Type=Application" >> "$desktop_file_path"
        echo "Categories=Game;" >> "$desktop_file_path"

        # Make the .desktop file executable
        chmod +x "$desktop_file_path"
    fi
fi