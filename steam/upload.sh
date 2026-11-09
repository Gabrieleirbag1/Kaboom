#!/bin/bash
# Uploads the Windows and Linux builds to Steam (see docs/release.md).
#   steam/upload.sh <Kaboom-x-windows.zip> <Kaboom-x-linux.tar.gz>
# The two files are the "steam-windows" and "steam-linux" artifacts of the Build workflow.
# Needs steamcmd (https://developer.valvesoftware.com/wiki/SteamCMD) and STEAM_BUILDER: the
# Steam account allowed to upload builds (steamcmd asks for its password and Steam Guard code).
set -e
cd "$(dirname "$0")/.."

windows_zip="$1"
linux_tar="$2"
if [ ! -f "$windows_zip" ] || [ ! -f "$linux_tar" ]; then
    echo "Usage: steam/upload.sh <Kaboom-x-windows.zip> <Kaboom-x-linux.tar.gz>" >&2
    exit 1
fi
if [ -z "$STEAM_BUILDER" ]; then
    echo "Set STEAM_BUILDER to the Steam account that uploads builds" >&2
    exit 1
fi
if grep -q '"1000000"' steam/app_build.vdf; then
    echo "Put Kaboom's AppID and depot IDs in steam/*.vdf first" >&2
    exit 1
fi

rm -rf dist/windows/Kaboom dist/linux/Kaboom
mkdir -p dist/windows dist/linux
unzip -q "$windows_zip" -d dist/windows
tar -xzf "$linux_tar" -C dist/linux
test -f dist/windows/Kaboom/Kaboom.exe
test -x dist/linux/Kaboom/Kaboom

steamcmd +login "$STEAM_BUILDER" +run_app_build "$PWD/steam/app_build.vdf" +quit
echo "Uploaded. Set the build live on a branch in Steamworks: App Admin > SteamPipe > Builds"
