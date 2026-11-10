# Releasing Kaboom (GitHub and Steam)

Every version of Kaboom is the **compiled game**: Python, Qt and the game's files in one folder, nothing else to install. `build.py` makes it with PyInstaller (`Kaboom.spec`) and the same folder becomes:

| Release | File | Made by |
|---|---|---|
| GitHub, Windows | `kaboom-setup-<version>.exe` (Inno Setup, `kaboom_setup.iss`) | `build.py --package` on Windows |
| GitHub, Linux | `kaboom_<version>_amd64.deb` (`create_release_package.sh`) | `build.py --package` on Linux |
| Steam, Windows | the folder `dist/windows/Kaboom` | `build.py --archive` on Windows |
| Steam, Linux | the folder `dist/linux/Kaboom` | `build.py --archive` in the Steam Runtime SDK |

The **Build** GitHub workflow (`.github/workflows/build.yml`) makes all four. Windows can't be built from Linux, so use the workflow rather than your computer for a release.

## What goes in the build

- `Client/client.py` and its modules, compiled.
- `images/` (`.png` only), `styles/`, `fonts/`, `confs/`, `settings/`.
- Only the sounds and music `Client/client_audio.py` plays. To add a sound, add it there and it is packed. Unused files in `Client/audio` stay in the repository but are not shipped.
- Not packed: `logs/`, `videos/`, the dev scripts (`*.py` in the asset folders).

`tests/test_build_files.py` checks this list.

The player's files (settings, logs, session) are never in the game folder: they are in `~/.config/kaboom` (Linux) or `%APPDATA%\Kaboom` (Windows). The install folder can be read-only, as on Steam or in `/usr/share/kaboom`.

On Linux the build uses the system's GLib, GStreamer (music), PulseAudio/ALSA, fonts and graphics libraries instead of bundled copies (`SYSTEM_LIBS` in `Kaboom.spec`): their plugins (mp3 decoder, PipeWire, graphics drivers) only load with the system's own version. The `.deb` lists them as dependencies; Steam's runtime provides them.

## 1. Set the version

Change `VERSION` in `Client/client_version.py` (e.g. `"1.2"`). The build, the `.deb`, the setup and the Windows file properties all read it from there.

## 2. Build

Push a tag with the version number, e.g. `1.2`, or run the workflow by hand (**Actions > Build > Run workflow**). It takes about 10 minutes. Both jobs build the game, start it off-screen for 20 s (`build.py --smoke`), then upload:

- `steam-windows`: `Kaboom-<version>-windows.zip`
- `steam-linux`: `Kaboom-<version>-linux.tar.gz`
- `setup-windows`: `kaboom-setup-<version>.exe`
- `deb-linux`: `kaboom_<version>_amd64.deb`

The artifacts are on the workflow run's page. GitHub zips each artifact, so unzip it once to get the file.

For a tag, the four files are also attached to a draft GitHub release (see section 3).

## 3. GitHub release

For a tag, the workflow also creates a **draft** release with four files:

| File | For |
|---|---|
| `kaboom-setup-<version>.exe` | Windows installer (GitHub users) |
| `kaboom_<version>_amd64.deb` | Linux package (GitHub users) |
| `Kaboom-<version>-windows.zip` | Steam, Windows (the game folder) |
| `Kaboom-<version>-linux.tar.gz` | Steam, Linux (the game folder) |

The two Steam packages are attached so that every file of a version is kept in one place. They are not meant for end users: when you write the release notes, say that players should use the setup or the `.deb`, or delete the two Steam files from the release before publishing if you don't want them public.

Before publishing the draft:

1. Install the `.deb` on Linux: `sudo apt install ./kaboom_<version>_amd64.deb`. Start Kaboom from the applications menu, log in, play a round, change the volume, restart (the settings are kept). Then check `sudo apt remove kaboom`.
2. Run the setup on Windows, ideally on a PC without Python and with the previous version installed: it must update it in place (same `AppId` in `kaboom_setup.iss`, never change it). Run the same checks.
3. Write the release notes and publish.

The Steam packages are checked later, through a Steam beta branch (see section 4).

## 4. Steam

### Once: Steamworks setup

1. In Steamworks, **App Admin > SteamPipe > Depots**: make two depots, one with **Operating System: Windows** and one with **Linux + SteamOS**. Put the AppID and the two depot IDs in `steam/app_build.vdf`, `steam/depot_windows.vdf` and `steam/depot_linux.vdf` (they contain 1000000 / 1000001 / 1000002 until then).
2. **Installation > General**: two launch options, `Kaboom.exe` (Operating System: Windows) and `Kaboom` (Linux).
3. **Installation > Linux Runtime**: choose **Steam Linux Runtime 3.0 (sniper)**. The Linux build is made in its SDK (`registry.gitlab.steamos.cloud/steamrt/sniper/sdk`).
4. Make a separate Steam account that can only upload builds (Users & Permissions). Install [steamcmd](https://developer.valvesoftware.com/wiki/SteamCMD) and log in with it once (`steamcmd +login <account> +quit`) to enter the Steam Guard code.

### Each version

1. Get the Steam packages: for a tag, download `Kaboom-<version>-windows.zip` and `Kaboom-<version>-linux.tar.gz` from the draft release (they are already plain files, nothing to unzip). For a manual run of the workflow, download the `steam-windows` and `steam-linux` artifacts from the run's page and unzip each once.
2. Upload them:
   ```bash
   STEAM_BUILDER=<account> steam/upload.sh Kaboom-1.2-windows.zip Kaboom-1.2-linux.tar.gz
   ```
3. In **SteamPipe > Builds**, set the new build live on a private branch (e.g. `beta`). Install it with Steam on Windows and on Linux (or a Steam Deck), and run the same checks as for GitHub. On Linux, check that the **music plays**: it uses the GStreamer of Steam's runtime.
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
kaboom_install.bat --package --smoke      # Windows: dist\windows\Kaboom + Releases\*.exe
```

Or in your own virtual environment: `pip install -r requirements-build.txt`, then `python build.py [--archive] [--package] [--smoke]`.

A Linux build made on your computer runs on systems at least as recent as yours. For the `.deb` and Steam, use the one from the workflow: it is built on an older base (Debian 11) and runs everywhere.
