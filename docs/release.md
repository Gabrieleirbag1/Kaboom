# Releasing Kaboom (GitHub and Steam)

Every version of Kaboom is the **compiled game**: Python, Qt and the game's files in one folder (an app bundle, `Kaboom.app`, on macOS), nothing else to install. `build.py` makes it with PyInstaller (`Kaboom.spec`) and the same folder becomes:

| Release | File | Made by |
|---|---|---|
| GitHub, Windows | `kaboom-setup-<version>.exe` (Inno Setup, `kaboom_setup.iss`) | `build.py --package` on Windows |
| GitHub, Linux | `kaboom_<version>_amd64.deb` (`create_release_package.sh`) | `build.py --package` on Linux |
| GitHub, macOS | `kaboom-<version>-macos-arm64.dmg` (Apple Silicon) and `kaboom-<version>-macos-x86_64.dmg` (Intel) | `build.py --package` on a Mac of each kind |
| Steam, Windows | the folder `dist/windows/Kaboom` | `build.py --archive` on Windows |
| Steam, Linux | the folder `dist/linux/Kaboom` | `build.py --archive` in the Steam Runtime SDK |
| Steam, macOS | `dist/macos/Kaboom.app` (Apple Silicon) | `build.py --archive` on an Apple Silicon Mac |

The **Build** GitHub workflow (`.github/workflows/build.yml`) makes all of them. Windows and macOS can't be built from Linux, so use the workflow rather than your computer for a release.

macOS needs one build per processor: Qt 5 has no "universal" package for both. The workflow builds on an Apple Silicon Mac (`macos-latest`) and an Intel Mac (`macos-15-intel`; GitHub plans to remove Intel Macs around August 2027, after which only Apple Silicon remains). Steam gets the Apple Silicon build only.

## What goes in the build

- `Client/client.py` and its modules, compiled.
- `images/` (`.png` only), `styles/`, `fonts/`, `confs/`, `settings/`.
- Only the sounds and music `Client/client_audio.py` plays. To add a sound, add it there and it is packed. Unused files in `Client/audio` stay in the repository but are not shipped.
- Not packed: `logs/`, `videos/`, the dev scripts (`*.py` in the asset folders).

`tests/test_build_files.py` checks this list.

The player's files (settings, logs, session) are never in the game folder: they are in `~/.config/kaboom` (Linux), `%APPDATA%\Kaboom` (Windows) or `~/Library/Application Support/Kaboom` (macOS). The install folder can be read-only, as on Steam, in `/usr/share/kaboom` or in `/Applications`.

On Linux the build uses the system's GLib, GStreamer (music), PulseAudio/ALSA, fonts and graphics libraries instead of bundled copies (`SYSTEM_LIBS` in `Kaboom.spec`): their plugins (mp3 decoder, PipeWire, graphics drivers) only load with the system's own version. The `.deb` lists them as dependencies; Steam's runtime provides them.

### macOS: the app and its signature

On macOS, `Kaboom.spec` also makes `Kaboom.app` (icon `Client/images/bombe-icon.icns`, bundle id `net.missclick.kaboom`, macOS 11 or newer). The `.dmg` holds `Kaboom.app` and a link to Applications: the player drags Kaboom into Applications, and it then appears in Launchpad and can be kept in the Dock, like the `.deb` does with the applications menu.

The app is **signed ad hoc** (`codesign --sign -` in `build.py`): Apple Silicon Macs only run signed code, and this signature costs nothing. It is not a Developer ID signature and the app is not notarized, so the first time a player opens Kaboom downloaded from GitHub, macOS says it can't check the developer. The player must then do one of these:

- right-click (or Control-click) Kaboom in Applications > **Open** > **Open**; on macOS 15 and later, open it once, then go to **System Settings > Privacy & Security** > **Open Anyway**;
- or in a terminal: `xattr -dr com.apple.quarantine /Applications/Kaboom.app`.

Steam doesn't trigger this check: games installed by Steam open directly. Removing the warning for GitHub players needs an Apple Developer account (Developer ID signature + notarization); that is for later, with the App Store.

## 1. Set the version

Change `VERSION` in `Client/client_version.py` (e.g. `"1.2"`). The build, the `.deb`, the setup and the Windows file properties all read it from there.

## 2. Build

Push a tag with the version number, e.g. `1.2`, or run the workflow by hand (**Actions > Build > Run workflow**). It takes about 10 minutes. Every job builds the game, starts it off-screen for 20 s (`build.py --smoke`), then uploads:

- `steam-windows`: `Kaboom-<version>-windows.zip`
- `steam-linux`: `Kaboom-<version>-linux.tar.gz`
- `steam-macos-arm64` / `steam-macos-x86_64`: `Kaboom-<version>-macos-<arch>.tar.gz` (the `.app`)
- `setup-windows`: `kaboom-setup-<version>.exe`
- `deb-linux`: `kaboom_<version>_amd64.deb`
- `dmg-macos-arm64` / `dmg-macos-x86_64`: `kaboom-<version>-macos-<arch>.dmg`

The artifacts are on the workflow run's page. GitHub zips each artifact, so unzip it once to get the file.

For a tag, the eight files are also attached to a draft GitHub release (see section 3).

## 3. GitHub release

For a tag, the workflow also creates a **draft** release with eight files:

| File | For |
|---|---|
| `kaboom-setup-<version>.exe` | Windows installer (GitHub users) |
| `kaboom_<version>_amd64.deb` | Linux package (GitHub users) |
| `kaboom-<version>-macos-arm64.dmg` | macOS, Apple Silicon (M1 and later) (GitHub users) |
| `kaboom-<version>-macos-x86_64.dmg` | macOS, Intel (GitHub users) |
| `Kaboom-<version>-windows.zip` | Steam, Windows (the game folder) |
| `Kaboom-<version>-linux.tar.gz` | Steam, Linux (the game folder) |
| `Kaboom-<version>-macos-arm64.tar.gz` | Steam, macOS (`Kaboom.app`) |
| `Kaboom-<version>-macos-x86_64.tar.gz` | not used by Steam (Intel `.app`, kept with the release) |

The Steam packages are attached so that every file of a version is kept in one place. They are not meant for end users: when you write the release notes, say that players should use the setup, the `.deb` or the `.dmg` (and the Gatekeeper step above for macOS), or delete the `.zip` / `.tar.gz` files from the release before publishing if you don't want them public.

Before publishing the draft:

1. Install the `.deb` on Linux: `sudo apt install ./kaboom_<version>_amd64.deb`. Start Kaboom from the applications menu, log in, play a round, change the volume, restart (the settings are kept). Then check `sudo apt remove kaboom`.
2. Run the setup on Windows, ideally on a PC without Python and with the previous version installed: it must update it in place (same `AppId` in `kaboom_setup.iss`, never change it). Run the same checks.
3. On a Mac, open the `.dmg` of its processor and drag Kaboom into Applications. Open it from Launchpad (the first time: right-click > Open, see "macOS: the app and its signature"). Run the same checks; the settings are kept in `~/Library/Application Support/Kaboom`. Then uninstall it by moving Kaboom from Applications to the Bin.
4. Write the release notes and publish.

The Steam packages are checked later, through a Steam beta branch (see section 4).

## 4. Steam

### Once: Steamworks setup

1. In Steamworks, **App Admin > SteamPipe > Depots**: make three depots, with **Operating System: Windows**, **Linux + SteamOS** and **macOS**. Put the AppID and the three depot IDs in `steam/app_build.vdf`, `steam/depot_windows.vdf`, `steam/depot_linux.vdf` and `steam/depot_macos.vdf` (they contain 1000000 / 1000001 / 1000002 / 1000003 until then).
2. **Installation > General**: three launch options, `Kaboom.exe` (Operating System: Windows), `Kaboom` (Linux) and `Kaboom.app` (macOS).
3. **Installation > Linux Runtime**: choose **Steam Linux Runtime 3.0 (sniper)**. The Linux build is made in its SDK (`registry.gitlab.steamos.cloud/steamrt/sniper/sdk`).
4. Make a separate Steam account that can only upload builds (Users & Permissions). Install [steamcmd](https://developer.valvesoftware.com/wiki/SteamCMD) and log in with it once (`steamcmd +login <account> +quit`) to enter the Steam Guard code.

### Each version

1. Get the Steam packages: for a tag, download `Kaboom-<version>-windows.zip`, `Kaboom-<version>-linux.tar.gz` and `Kaboom-<version>-macos-arm64.tar.gz` from the draft release (they are already plain files, nothing to unzip). For a manual run of the workflow, download the `steam-windows`, `steam-linux` and `steam-macos-arm64` artifacts from the run's page and unzip each once.
2. Upload them (without the third file, the macOS depot keeps its previous build):
   ```bash
   STEAM_BUILDER=<account> steam/upload.sh Kaboom-1.2-windows.zip Kaboom-1.2-linux.tar.gz Kaboom-1.2-macos-arm64.tar.gz
   ```
3. In **SteamPipe > Builds**, set the new build live on a private branch (e.g. `beta`). Install it with Steam on Windows, on Linux (or a Steam Deck) and on a Mac, and run the same checks as for GitHub. On Linux, check that the **music plays**: it uses the GStreamer of Steam's runtime.
4. Set the build live on the `default` branch.

Steam only downloads the files that changed, so a patch that doesn't touch the images is small.

## Before the first Steam upload: rights

Steam is a commercial store. Check that the licenses allow shipping:

- `Client/fonts/Game On_PersonalUseOnly.ttf` and `Client/fonts/Bubble Love Demo.otf` (personal-use and demo fonts);
- `Client/audio/Sound/WindowsXP.wav` and `Ubuntu.wav` (operating system sounds);
- the three shipped musics: `Energy_Wave.mp3`, `Sakura_Jazzy.mp3`, `jazz_funky.mp3`.

## Building on your computer

```bash
./kaboom_install.sh --package --smoke     # Linux: dist/linux/Kaboom + Releases/*.deb
./kaboom_install.sh --package --smoke     # macOS: dist/macos/Kaboom.app + Releases/*.dmg
kaboom_install.bat --package --smoke      # Windows: dist\windows\Kaboom + Releases\*.exe
```

On a Mac, install Python 3.14 first (from [python.org](https://www.python.org/downloads/macos/) or `brew install python@3.14`). The build is for the Mac's own processor.

Or in your own virtual environment: `pip install -r requirements-build.txt`, then `python build.py [--archive] [--package] [--smoke]`.

A Linux build made on your computer runs on systems at least as recent as yours. For the `.deb` and Steam, use the one from the workflow: it is built on an older base (Debian 11) and runs everywhere.
