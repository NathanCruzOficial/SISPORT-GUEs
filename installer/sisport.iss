#define MyAppName "SISPORT"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "SISPORT"
#define MyAppURL "https://github.com/NathanCruzOficial/SISPORT-GUEs"
#define MyAppExeName "SISPORT.exe"

[Setup]
AppId={{2A4D6B4A-7E1F-4B7A-9A5F-2A2E1E8B8A11}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
OutputBaseFilename=SISPORTSetup
Compression=lzma
SolidCompression=yes

; Isso garante que o instalador não aceite instalar por cima enquanto o app estiver aberto
CloseApplications=yes
RestartApplications=no

[Files]
; Copia TUDO do PyInstaller (onedir)
Source: "..\dist\SISPORT\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Tasks]
Name: "desktopicon"; Description: "Criar atalho na Área de Trabalho"; Flags: unchecked

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir {#MyAppName}"; Flags: nowait postinstall skipifsilent
