#!/bin/bash
# Makes the Linux package Releases/kaboom_<version>_amd64.deb from the compiled game
# (dist/linux/Kaboom, made by build.py). Python is inside the game: the package doesn't need it.
#   ./create_release_package.sh [version]     (default: the version in Client/client_version.py)
# Usually run by `python build.py --package`.
set -e
cd "$(dirname "$0")"

version="$1"
if [ -z "$version" ]; then
    version=$(sed -n 's/^VERSION = "\(.*\)"/\1/p' Client/client_version.py)
fi
if [ -z "$version" ]; then
    read -p "Enter the version (e.g., 1.2): " version
fi

game_dir="dist/linux/Kaboom"
if [ ! -x "$game_dir/Kaboom" ]; then
    echo "The compiled game is missing ($game_dir): run python build.py first" >&2
    exit 1
fi

# Define paths
base_dir="Releases/kaboom_${version}_amd64"
debian_dir="$base_dir/DEBIAN"
usr_local_bin_dir="$base_dir/usr/local/bin"
usr_share_applications_dir="$base_dir/usr/share/applications"
usr_share_icons_dir="$base_dir/usr/share/icons/hicolor/512x512/apps"
usr_share_kaboom_dir="$base_dir/usr/share/kaboom"

# Start from an empty folder: no file of a previous build left in the package
rm -rf "$base_dir"
mkdir -p "$debian_dir" "$usr_local_bin_dir" "$usr_share_applications_dir" "$usr_share_icons_dir"

# The game: /usr/share/kaboom, started by /usr/local/bin/Kaboom (same command as before 1.2)
cp -a "$game_dir" "$usr_share_kaboom_dir"
ln -s /usr/share/kaboom/Kaboom "$usr_local_bin_dir/Kaboom"
cp "Client/images/bombe-icon.png" "$usr_share_icons_dir/bombe-icon.png"

installed_size=$(du -sk "$base_dir" | cut -f1)

# Create the control file. The game uses the system's GLib, GStreamer (music), audio, fonts and
# graphics libraries (see SYSTEM_LIBS in Kaboom.spec).
cat <<EOL > "$debian_dir/control"
Package: kaboom
Version: $version
Section: games
Priority: optional
Architecture: amd64
Installed-Size: $installed_size
Depends: libglib2.0-0 | libglib2.0-0t64, libgstreamer1.0-0, gstreamer1.0-plugins-base, libpulse0, libasound2 | libasound2t64, libfontconfig1, libfreetype6, libgl1, libdbus-1-3
Recommends: gstreamer1.0-plugins-good
Maintainer: GARRONE Gabriel gabrielgarrone670@gmail.com
Description: Kaboom - The online multiplayer word game
 Kaboom is an online multiplayer word game: type a word containing the
 syllable before the bomb explodes. The game is written in Python and uses
 PyQt5; Python and Qt are included in the package.

EOL

# Create the postinst file
cat <<'EOL' > "$debian_dir/postinst"
#!/bin/bash
set -e

# Get the current user and their home directory
current_user=$(logname 2>/dev/null || echo "${SUDO_USER:-root}")
user_home=$(eval echo "~$current_user")

# Make the .desktop file executable
chmod +x /usr/share/applications/kaboom.desktop

# Create the .desktop file only if it does not exist
desktop_file_path="$user_home/.local/share/applications/kaboom.desktop"
if [ -d "$user_home/.local/share/applications" ] && [ ! -f "$desktop_file_path" ]; then
    executable_path="/usr/local/bin/Kaboom"
    icon_path="/usr/share/icons/hicolor/512x512/apps/bombe-icon.png"

    # Write the .desktop file
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

# Update desktop database
if command -v update-desktop-database > /dev/null 2>&1; then
    update-desktop-database
fi

exit 0
EOL

# Create the kaboom.desktop file
cat <<'EOL' > "$usr_share_applications_dir/kaboom.desktop"
[Desktop Entry]
Version=1.1
Name=Kaboom
Exec=/usr/local/bin/Kaboom
Icon=/usr/share/icons/hicolor/512x512/apps/bombe-icon.png
Type=Application
Categories=Game;
EOL

# Make the postinst script executable
chmod +x "$debian_dir/postinst"

# rwxr-xr-x folders and executables, rw-r--r-- files (whatever the umask of the build)
chmod -R u=rwX,go=rX "$base_dir"

dpkg-deb --build --root-owner-group "$base_dir" "Releases/kaboom_${version}_amd64.deb"
echo "Package created: Releases/kaboom_${version}_amd64.deb"
