[Setup]
AppName=TicketMaker
AppVersion=0.3.0
DefaultDirName={pf}\TicketMaker
DefaultGroupName=TicketMaker
UninstallDisplayIcon={app}\TicketMaker.exe
OutputBaseFilename=TicketMakerInstaller
Compression=lzma
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
AppPublisher=TicketMaker Community Project
AppPublisherURL=https://github.com/TicketMaker-Community-Project/
AppSupportURL=https://github.com/TicketMaker-Community-Project/TicketMaker/issues
AppUpdatesURL=https://github.com/TicketMaker-Community-Project/TicketMaker/releases
UninstallDisplayName=TicketMaker


[Files]
Source: "TicketMaker.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "requirements.txt"; DestDir: "{tmp}"; Flags: ignoreversion
Source: "install_dependencies.ps1"; DestDir: "{tmp}"; Flags: ignoreversion

[Icons]
Name: "{group}\TicketMaker"; Filename: "{app}\TicketMaker.exe"
Name: "{group}\Uninstall TicketMaker"; Filename: "{uninstallexe}"
Name: "{commondesktop}\TicketMaker"; Filename: "{app}\TicketMaker.exe"

[Registry]
Root: HKCU; Subkey: "Software\TicketMaker"; ValueType: string; ValueName: "URL"; ValueData: "{code:GetURL}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\TicketMaker"; ValueType: string; ValueName: "APIKey"; ValueData: "{code:GetAPIKey}"; Flags: uninsdeletevalue
Root: HKCU; Subkey: "Software\TicketMaker"; Flags: uninsdeletekey

[Run]
Filename: "{app}\TicketMaker.exe"; Description: "Launch TicketMaker"; Flags: nowait postinstall skipifsilent

[Code]
var
  FreshdeskURL: string;
  FreshdeskAPIKey: string;
  CustomPage: TInputQueryWizardPage;

function IsPythonInstalled(): Boolean;
var
  PythonPath: string;
begin
  Result := RegQueryStringValue(HKLM, 'Software\Python\PythonCore\3.12\InstallPath', '', PythonPath);
end;

procedure InstallDependencies();
var
  PowerShellPath: string;
  ScriptPath: string;
  TempDirPath: string;
  ErrorCode: Integer;
begin
  PowerShellPath := ExpandConstant('{sys}\WindowsPowerShell\v1.0\powershell.exe');
  TempDirPath := ExpandConstant('{tmp}');
  ScriptPath := TempDirPath + '\install_dependencies.ps1';

  if FileExists(ScriptPath) then
  begin
    MsgBox('Installing Python dependencies...', mbInformation, MB_OK);
    Exec(PowerShellPath, '-ExecutionPolicy Bypass -File "' + ScriptPath + '" -TempDirPath "' + TempDirPath + '"', '', SW_SHOW, ewWaitUntilTerminated, ErrorCode);
    if ErrorCode <> 0 then
      MsgBox('Failed to install Python dependencies. Check log for details.', mbError, MB_OK);
  end
  else
  begin
    MsgBox('Dependency installer script not found: ' + ScriptPath, mbError, MB_OK);
  end;
end;

function GetURL(Param: string): string;
begin
  Result := FreshdeskURL;
end;

function GetAPIKey(Param: string): string;
begin
  Result := FreshdeskAPIKey;
end;

procedure CreateCustomPage();
begin
  CustomPage := CreateInputQueryPage(wpWelcome,
    'Freshdesk Configuration',
    'Please provide your Freshdesk URL and API Key.',
    'These values are required to configure the application.');

  CustomPage.Add('Freshdesk URL:', False);
  CustomPage.Add('Freshdesk API Key:', False);
end;

procedure ValidateCustomPage();
begin
  FreshdeskURL := CustomPage.Values[0];
  FreshdeskAPIKey := CustomPage.Values[1];

  if (FreshdeskURL = '') or (FreshdeskAPIKey = '') then
  begin
    MsgBox('Both Freshdesk URL and API Key are required to proceed.', mbError, MB_OK);
    RaiseException('Validation failed.'); // Stop installation if validation fails
  end;
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpWelcome then
    CreateCustomPage();
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    if not IsPythonInstalled() then
    begin
      MsgBox('Python 3.12 is not installed. Please install Python 3.12 or later before proceeding.', mbError, MB_OK);
      RaiseException('Python not installed.');
    end;
    InstallDependencies();
  end;
end;
