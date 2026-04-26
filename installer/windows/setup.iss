; installer/windows/setup.iss
[Setup]
AppName=Video Transcriber
AppVersion=1.0.0
AppPublisher=VideoTranscriber
DefaultDirName={autopf}\VideoTranscriber
DefaultGroupName=Video Transcriber
OutputDir=dist
OutputBaseFilename=VideoTranscriber-Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
UninstallDisplayIcon={app}\VideoTranscriber.exe
SetupIconFile=..\..\resources\icon.ico

[Files]
Source: "..\..\dist\VideoTranscriber.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Video Transcriber"; Filename: "{app}\VideoTranscriber.exe"
Name: "{commondesktop}\Video Transcriber"; Filename: "{app}\VideoTranscriber.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Run]
Filename: "{app}\VideoTranscriber.exe"; Description: "{cm:LaunchProgram,Video Transcriber}"; Flags: nowait postinstall skipifsilent
