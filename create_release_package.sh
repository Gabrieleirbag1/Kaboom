#!/bin/bash

# Ask for the version
read -p "Enter the version (e.g., 1.0): " version

# Define paths
base_dir="Releases/kaboom_${version}_all"
debian_dir="$base_dir/DEBIAN"
usr_local_bin_dir="$base_dir/usr/local/bin"
usr_share_applications_dir="$base_dir/usr/share/applications"
usr_share_icons_dir="$base_dir/usr/share/icons/hicolor/512x512/apps"
usr_share_kaboom_dir="$base_dir/usr/share/kaboom"

# Create directories
mkdir -p "$debian_dir"
mkdir -p "$usr_local_bin_dir"
mkdir -p "$usr_share_applications_dir"
mkdir -p "$usr_share_icons_dir"
mkdir -p "$usr_share_kaboom_dir"

# Create the control file
cat <<EOL > "$debian_dir/control"
Package: kaboom
Version: $version
Section: base
Priority: optional
Architecture: all
Depends: python3, python3-pip
Maintainer: GARRONE Gabriel gabrielgarrone670@gmail.com
Description: Kaboom - The online multiplayer video game
 Kaboom is an online multiplayer video game. It is a clone of the famous game
 Bomberman. The game is written in Python and uses the Pygame library.
EOL

# Create the postinst file
cat <<'EOL' > "$debian_dir/postinst"
#!/bin/bash
set -e

# Get the current user and their home directory
current_user=$(logname)
user_home=$(eval echo "~$current_user")

# Install the required packages
sudo -u "$current_user" pip3 install --user -r /usr/share/kaboom/requirements.txt 

# Make the .desktop file executable
chmod +x /usr/share/applications/kaboom.desktop

# Create the .desktop file only if it does not exist
desktop_file_path="$user_home/.local/share/applications/kaboom.desktop"
if [ ! -f "$desktop_file_path" ]; then
    executable_path="/usr/local/bin/Kaboom"
    icon_path="/usr/share/icons/hicolor/512x512/apps/bombe-icon.png"

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

# Update desktop database
if command -v update-desktop-database > /dev/null 2>&1; then
    update-desktop-database
fi

exit 0
EOL

# Create the kaboom.desktop file
cat <<'EOL' > "$usr_share_applications_dir/kaboom.desktop"
[Desktop Entry]
Version=1.0
Name=Kaboom
Exec=/usr/bin/kaboom
Icon=/usr/share/icons/hicolor/512x512/apps/bombe-icon.png
Type=Application
Categories=Game;
EOL

# Make the postinst script executable
chmod +x "$debian_dir/postinst"

# Create an empty requirements.txt file
touch "$usr_share_kaboom_dir/requirements.txt"

# Create an empty Kaboom file
touch "$usr_local_bin_dir/Kaboom"

# Create an empty bombe-icon.png file
touch "$usr_share_icons_dir/bombe-icon.png"

echo "Directory structure successfully created for version $version."