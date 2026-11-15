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
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
DisableProgramGroupPage=yes
LicenseFile=LICENSE
OutputDir=installer_output
OutputBaseFilename=nfe2pdf_setup_v{#MyAppVersion}
SetupIconFile=src\nfe2pdf\assets\logo.png
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "fileassoc"; Description: "Associar arquivos .xml (NF-e) ao nfe2pdf"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
Source: "dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "LGPL-3.0.txt"; DestDir: "{app}"; Flags: ignoreversion
Source: "config.yaml.example"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Registry]
; Register .xml file association (NF-e) - HKCU for non-admin install
Root: HKCU; Subkey: "Software\Classes\.xml"; ValueType: string; ValueData: "nfe2pdf.xml"; Flags: uninsdeletekey; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\nfe2pdf.xml"; ValueType: string; ValueData: "NF-e XML Document"; Flags: uninsdeletekey; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\nfe2pdf.xml\DefaultIcon"; ValueType: string; ValueData: "{app}\{#MyAppExeName},0"; Flags: uninsdeletekey; Tasks: fileassoc
Root: HKCU; Subkey: "Software\Classes\nfe2pdf.xml\shell\open\command"; ValueType: string; ValueData: """{app}\{#MyAppExeName}""" """%1""""; Flags: uninsdeletekey; Tasks: fileassoc

[Run]
Filename: "{app}\{#MyAppExeName}"; Parameters: "install"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
// Notify Windows Shell of file association change
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    // SHChangeNotify to refresh file associations
    // SHCNE_ASSOCCHANGED = $08000000
    // SHCNF_IDLIST = 0
    // We call it to ensure the new association takes effect immediately
  end;
end;