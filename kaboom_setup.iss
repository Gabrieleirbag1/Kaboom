; Windows setup of Kaboom: installs the compiled game (dist\windows\Kaboom, made by build.py).
; Python is inside the game: nothing else to install. Build it with `python build.py --package`,
; or by hand: iscc /DMyAppVersion=1.2 kaboom_setup.iss

#ifndef MyAppVersion
  #define MyAppVersion "1.2"
#endif

[Setup]
; NOTE: The value of AppId uniquely identifies this application. Keep it: the setup then updates
; an installed Kaboom instead of installing a second one.
AppId={{YOUR-GUID-HERE}}
AppName=Kaboom
AppVersion={#MyAppVersion}
AppVerName=Kaboom {#MyAppVersion}
DefaultDirName={autopf}\Kaboom
DefaultGroupName=Kaboom
UninstallDisplayIcon={app}\Kaboom.exe
OutputDir=Releases
OutputBaseFilename=kaboom-setup-{#MyAppVersion}
SetupIconFile=Client\images\bombe-icon.ico
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[InstallDelete]
; Files of the previous version that the new one doesn't have any more
Type: filesandordirs; Name: "{app}\_internal"

[Files]
Source: "dist\windows\Kaboom\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "Client\images\bombe-icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Kaboom"; Filename: "{app}\Kaboom.exe"
Name: "{group}\{cm:UninstallProgram,Kaboom}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Kaboom"; Filename: "{app}\Kaboom.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\Kaboom"; Filename: "{app}\Kaboom.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{app}\Kaboom.exe"; Description: "{cm:LaunchProgram,Kaboom}"; Flags: nowait postinstall skipifsilent
