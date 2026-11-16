; Inno Setup script for nfe2pdf installer
; Compile with: iscc scripts/build_installer.iss
;
; Requirements:
; - Inno Setup 6.2+
; - Built executable at dist/nfe2pdf.exe
; - LGPL-3.0.txt and config.yaml.example in project root

#define MyAppName "nfe2pdf"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Adriano Lucas"
#define MyAppURL "https://github.com/adrianolucasdc/nfe-xml-to-pdf"
#define MyAppExeName "nfe2pdf.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=..\LICENSE
OutputDir=..\installer_output
OutputBaseFilename=nfe2pdf_setup_v{#MyAppVersion}
; SetupIconFile=..\src\nfe2pdf\assets\logo.png  ; Requires .ico format
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "fileassoc"; Description: "Associar arquivos .xml (NF-e) ao nfe2pdf"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\LGPL-3.0.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\config.yaml.example"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Registry]
; .xml -> nfe2pdf (HKCU, sem admin). OBS: o Windows 10/11 ignora isto se o usuario ja
; tiver uma escolha propria (UserChoice); por isso tambem registramos o app em
; "Abrir com" e abrimos as Configuracoes de apps padrao ao final.
Root: HKCU; Subkey: "Software\Classes\.xml"; ValueType: string; ValueData: "nfe2pdf.xml"; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\.xml\OpenWithProgids"; ValueType: string; ValueName: "nfe2pdf.xml"; ValueData: ""; Flags: uninsdeletevalue; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\nfe2pdf.xml"; ValueType: string; ValueData: "NF-e XML Document"; Flags: uninsdeletekey; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\nfe2pdf.xml\DefaultIcon"; ValueType: string; ValueData: "{app}\{#MyAppExeName},0"; Flags: uninsdeletekey; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\nfe2pdf.xml\shell\open\command"; ValueType: string; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Flags: uninsdeletekey; Tasks: fileassoc
; Aplicativo listado em "Abrir com..."
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}"; ValueType: string; ValueName: "FriendlyAppName"; ValueData: "{#MyAppName}"; Flags: uninsdeletekey; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\SupportedTypes"; ValueType: string; ValueName: ".xml"; ValueData: ""; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\Applications\{#MyAppExeName}\shell\open\command"; ValueType: string; ValueData: """{app}\{#MyAppExeName}"" ""%1"""; Tasks: fileassoc

[Run]
Filename: "{app}\{#MyAppExeName}"; Parameters: "install"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
Filename: "ms-settings:defaultapps"; Description: "Abrir Configuracoes para definir o nfe2pdf como padrao para arquivos .xml"; Flags: shellexec postinstall skipifsilent unchecked; Tasks: fileassoc

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
procedure SHChangeNotify(wEventId: Integer; uFlags: Integer; dwItem1: Integer; dwItem2: Integer);
  external 'SHChangeNotify@shell32.dll stdcall';

// Avisa o Windows que as associacoes de arquivo mudaram (SHCNE_ASSOCCHANGED)
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    SHChangeNotify($08000000, 0, 0, 0);
end;
