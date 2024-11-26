[Setup]
AppName=TicketMaker
AppVersion=0.3.5
AppPublisher=S.C. Swiderski IT Department
AppPublisherURL=https://github.com/SC-Swiderski-LLC/TicketMaker
AppSupportURL=https://github.com/SC-Swiderski-LLC/TicketMaker/issues
AppUpdatesURL=https://github.com/SC-Swiderski-LLC/TicketMaker/releases
DefaultDirName={pf64}\TicketMaker
DefaultGroupName=TicketMaker
OutputBaseFilename=TicketMaker_Installer
PrivilegesRequired=admin
Compression=lzma
SolidCompression=yes
WizardImageFile=TicketMakerLogo.bmp
WizardSmallImageFile=TicketMakerLogoSmall.bmp
UninstallDisplayName=TicketMaker
UninstallDisplayIcon={app}\icon.ico

[Files]
Source: "TicketMaker.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "encrypt.ps1"; DestDir: "{tmp}"; Flags: deleteafterinstall
Source: "icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Registry]
Root: HKLM; Subkey: "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"; \
ValueName: "TicketMaker"; ValueType: string; ValueData: """{app}\TicketMaker.exe"""; Flags: uninsdeletevalue

[InstallDelete]
Type: filesandordirs; Name: "{app}"
Type: filesandordirs; Name: "{commonappdata}\TicketMaker"

[UninstallDelete]
Type: filesandordirs; Name: "{commonappdata}\TicketMaker"

[Icons]
Name: "{group}\TicketMaker"; Filename: "{app}\TicketMaker.exe"

[Code]
var
  FreshdeskURL: string;
  FreshdeskAPIKey: string;
  InputPage: TInputQueryWizardPage;

// Function to check if running silently
function IsSilentInstall: Boolean;
begin
  Result := WizardSilent;
end;

// Parse command-line parameters
function GetParamValue(const ParamName: string): string;
var
  I: Integer;
  Param, Prefix: string;
begin
  Prefix := '/' + ParamName + '=';
  Result := '';
  for I := 1 to ParamCount do
  begin
    Param := ParamStr(I);
    if Pos(Prefix, Param) = 1 then
    begin
      Result := Copy(Param, Length(Prefix) + 1, MaxInt);
      Break;
    end;
  end;
end;

// Initialize wizard
procedure InitializeWizard;
begin
  if IsSilentInstall then
  begin
    FreshdeskURL := GetParamValue('FreshdeskURL');
    FreshdeskAPIKey := GetParamValue('FreshdeskApiKey');

    // Validate parameters
    if (FreshdeskURL = '') or (FreshdeskAPIKey = '') then
    begin
      MsgBox('Silent install requires both /FreshdeskURL and /FreshdeskApiKey parameters.', mbError, MB_OK);
      Abort(); // Abort if parameters are missing
    end;
  end
  else
  begin
    InputPage := CreateInputQueryPage(wpWelcome,
      'Freshdesk Credentials',
      'Enter Freshdesk URL and API Key',
      'This information will be securely stored.');

    InputPage.Add('Freshdesk URL:', False);
    InputPage.Add('API Key:', True);
  end;
end;

// Handle Next button click
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;

  if not IsSilentInstall and Assigned(InputPage) and (CurPageID = InputPage.ID) then
  begin
    FreshdeskURL := Trim(InputPage.Values[0]);
    FreshdeskAPIKey := Trim(InputPage.Values[1]);

    if (FreshdeskURL = '') or (FreshdeskAPIKey = '') then
    begin
      MsgBox('Both Freshdesk URL and API Key are required.', mbError, MB_OK);
      Result := False;
    end;
  end;
end;

// Handle silent parameters
procedure InitializeSilentInstall;
begin
  FreshdeskURL := GetParamValue('FreshdeskURL');
  FreshdeskAPIKey := GetParamValue('FreshdeskApiKey');

  if (FreshdeskURL = '') or (FreshdeskAPIKey = '') then
  begin
    MsgBox('Silent install requires both /FreshdeskURL and /FreshdeskApiKey parameters.', mbError, MB_OK);
    Abort();
  end;
end;

// Encrypt credentials
procedure CurStepChanged(CurStep: TSetupStep);
var
  PowerShellScriptPath: string;
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    PowerShellScriptPath := ExpandConstant('{tmp}\encrypt.ps1');
    if not Exec('powershell.exe',
                '-NoProfile -ExecutionPolicy Bypass -File "' + PowerShellScriptPath +
                '" -FreshdeskURL "' + FreshdeskURL +
                '" -FreshdeskApiKey "' + FreshdeskAPIKey + '"',
                '', SW_HIDE, ewWaitUntilTerminated, ResultCode) then
    begin
      MsgBox('Failed to execute PowerShell script.', mbError, MB_OK);
    end
    else if ResultCode <> 0 then
    begin
      MsgBox('PowerShell script failed with exit code ' + IntToStr(ResultCode), mbError, MB_OK);
    end;
  end;
end;

