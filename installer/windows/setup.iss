; installer/windows/setup.iss
[Setup]
AppName=ViScriber
AppVersion=1.0.0
AppPublisher=ViScriber
DefaultDirName={autopf}\ViScriber
DefaultGroupName=ViScriber
OutputDir=dist
OutputBaseFilename=ViScriber-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\VideoTranscriber.exe
SetupIconFile=..\..\resources\icon.ico

[Files]
Source: "..\..\dist\VideoTranscriber.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\ViScriber"; Filename: "{app}\VideoTranscriber.exe"
Name: "{commondesktop}\ViScriber"; Filename: "{app}\VideoTranscriber.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Run]
Filename: "{app}\VideoTranscriber.exe"; Description: "{cm:LaunchProgram,ViScriber}"; Flags: nowait postinstall skipifsilent
