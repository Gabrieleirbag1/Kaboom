# PyInstaller recipe of the compiled game, the same on Windows, Linux and macOS (#21).
# Run it with `python build.py`: it makes the folder dist/<os>/Kaboom/ (Python, Qt and the game's
# files inside). Steam ships that folder as is; the .deb and the Windows setup install it.
# On macOS it also makes dist/macos/Kaboom.app, the app bundle shipped in the .dmg and on Steam.
import os
import sys

ROOT = os.path.abspath(SPECPATH)
CLIENT = os.path.join(ROOT, "Client")
sys.path.insert(0, ROOT)
from build import VERSION, game_files  # noqa: E402


a = Analysis(
    [os.path.join(CLIENT, "client.py")],
    pathex=[CLIENT],
    datas=game_files(),
    excludes=["tkinter", "pydub", "unittest", "pydoc", "PyInstaller"],
    noarchive=False,
)

# Linux: these libraries are taken from the player's system (every desktop and Steam's runtime has
# them), not from the build machine. They load system plugins (GStreamer music decoders, PipeWire/
# PulseAudio, graphics drivers, fonts) that need the system's own version of them: an older bundled
# copy makes music or the graphics driver fail to load on newer distros.
SYSTEM_LIBS = (
    "libstdc++", "libgcc_s", "libatomic", "libmvec",                       # C/C++ runtime
    "libglib-2.0", "libgobject-2.0", "libgmodule-2.0", "libgthread-2.0", "libgio-2.0", "libpcre",
    "libgst", "liborc",                                                    # GStreamer (music)
    "libasound", "libpulse", "libsndfile", "libFLAC", "libogg", "libvorbis", "libopus",
    "libmp3lame", "libmpg123", "libasyncns",                               # audio
    "libdbus-1", "libsystemd", "libapparmor", "libgssapi", "libkrb5", "libk5crypto", "libcom_err",
    "libkeyutils",
    "libfontconfig", "libfreetype", "libpng16", "libbrotli",               # fonts
    "libGL", "libEGL", "libGLX", "libdrm", "libgbm",                       # graphics driver
)


def is_system_lib(dest: str) -> bool:
    """System libraries land at the top of the build; Qt's plugins (PyQt5/Qt5/plugins/mediaservice/
    libgstmediaplayer.so...) stay, they are part of Qt."""
    return os.path.dirname(dest) == "" and dest.startswith(SYSTEM_LIBS)


if sys.platform.startswith("linux"):
    a.binaries = [entry for entry in a.binaries if not is_system_lib(entry[0])]

# macOS: Qt's camera plugin is never used, and macOS would ask the player for camera access.
if sys.platform == "darwin":
    a.binaries = [entry for entry in a.binaries if "libqavfcamera" not in entry[0]]

pyz = PYZ(a.pure)

version_info = None
if sys.platform == "win32":
    from PyInstaller.utils.win32.versioninfo import (FixedFileInfo, StringFileInfo, StringStruct,
                                                     StringTable, VarFileInfo, VarStruct, VSVersionInfo)
    numbers = tuple((list(map(int, VERSION.split("."))) + [0, 0, 0, 0])[:4])
    version_info = VSVersionInfo(
        ffi=FixedFileInfo(filevers=numbers, prodvers=numbers),
        kids=[StringFileInfo([StringTable("040904B0", [
            StringStruct("FileDescription", "Kaboom"),
            StringStruct("FileVersion", VERSION),
            StringStruct("InternalName", "Kaboom"),
            StringStruct("OriginalFilename", "Kaboom.exe"),
            StringStruct("ProductName", "Kaboom"),
            StringStruct("ProductVersion", VERSION),
        ])]), VarFileInfo([VarStruct("Translation", [1033, 1200])])])

ICON = "bombe-icon.icns" if sys.platform == "darwin" else "bombe-icon.ico"

exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,  # a folder, not one big self-extracting file
    name="Kaboom",
    console=False,
    upx=False,  # antivirus tools often flag UPX-packed files
    icon=os.path.join(CLIENT, "images", ICON),
    version=version_info,
)
coll = COLLECT(exe, a.binaries, a.datas, name="Kaboom", upx=False)

if sys.platform == "darwin":
    # Kaboom.app: double-click in Finder, icon in Launchpad and the Dock once in /Applications.
    # build.py signs it ad hoc (Apple Silicon refuses to run unsigned code).
    app = BUNDLE(
        coll,
        name="Kaboom.app",
        icon=os.path.join(CLIENT, "images", ICON),
        bundle_identifier="net.missclick.kaboom",
        version=VERSION,
        info_plist={
            "CFBundleName": "Kaboom",
            "CFBundleDisplayName": "Kaboom",
            "CFBundleShortVersionString": VERSION,
            "CFBundleVersion": VERSION,
            "NSHighResolutionCapable": True,
            "LSMinimumSystemVersion": "11.0",
            "LSApplicationCategoryType": "public.app-category.games",
        },
    )
