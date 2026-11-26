#!/bin/bash
# Uploads the Windows, Linux and macOS builds to Steam (see docs/release.md).
#   steam/upload.sh <Kaboom-x-windows.zip> <Kaboom-x-linux.tar.gz> [Kaboom-x-macos-arm64.tar.gz]
# The files are the "steam-windows", "steam-linux" and "steam-macos-arm64" artifacts of the Build
# workflow (or the files of the draft release). Without the macOS file, its depot is not updated.
# Needs steamcmd (https://developer.valvesoftware.com/wiki/SteamCMD) and STEAM_BUILDER: the
# Steam account allowed to upload builds (steamcmd asks for its password and Steam Guard code).
set -e
cd "$(dirname "$0")/.."

windows_zip="$1"
linux_tar="$2"
macos_tar="$3"
if [ ! -f "$windows_zip" ] || [ ! -f "$linux_tar" ] || { [ -n "$macos_tar" ] && [ ! -f "$macos_tar" ]; }; then
    echo "Usage: steam/upload.sh <Kaboom-x-windows.zip> <Kaboom-x-linux.tar.gz> [Kaboom-x-macos-arm64.tar.gz]" >&2
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

rm -rf dist/windows/Kaboom dist/linux/Kaboom dist/macos
mkdir -p dist/windows dist/linux dist/macos
unzip -q "$windows_zip" -d dist/windows
tar -xzf "$linux_tar" -C dist/linux
test -f dist/windows/Kaboom/Kaboom.exe
test -x dist/linux/Kaboom/Kaboom

app_build="$PWD/steam/app_build.vdf"
if [ -n "$macos_tar" ]; then
    tar -xzf "$macos_tar" -C dist/macos
    test -x dist/macos/Kaboom.app/Contents/MacOS/Kaboom
else
    # Same build without the macOS depot (next to app_build.vdf: its paths are relative to it)
    app_build="$PWD/steam/.app_build_no_macos.vdf"
    trap 'rm -f "$app_build"' EXIT
    grep -v 'depot_macos.vdf' steam/app_build.vdf > "$app_build"
    echo "No macOS build given: its depot is not updated"
fi

steamcmd +login "$STEAM_BUILDER" +run_app_build "$app_build" +quit
echo "Uploaded. Set the build live on a branch in Steamworks: App Admin > SteamPipe > Builds"
