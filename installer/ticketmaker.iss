[Setup]
AppName=TicketMaker
AppVersion=0.3.5
DefaultDirName={localappdata}\TicketMaker
DefaultGroupName=TicketMaker
OutputBaseFilename=TicketMaker_InteractiveInstaller
PrivilegesRequired=lowest
Compression=lzma
SolidCompression=yes
WizardImageFile=TicketMakerLogo.bmp
WizardSmallImageFile=TicketMakerLogoSmall.bmp
UninstallDisplayName=TicketMaker
UninstallDisplayIcon=icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "TicketMaker.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "SaveCredentials.cmd"; DestDir: "{app}"; Flags: ignoreversion

[Code]
// Variables to hold user input
var
  FreshdeskURL: string;
  FreshdeskAPIKey: string;
  InputPage: TInputQueryWizardPage;

// Check if the installer is running silently
function IsSilentInstall: Boolean;
begin
  // Use WizardSilent to detect silent mode
  Result := WizardSilent;
end;

// Function to parse command-line parameters
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

// Initialize the wizard and add custom input page (only for interactive installs)
procedure InitializeWizard;
begin
  if not IsSilentInstall then
  begin
    // Create a custom input page for Freshdesk credentials
    InputPage := CreateInputQueryPage(wpWelcome,
      'Freshdesk Credentials',
      'Please enter your Freshdesk URL and API Key',
      'This information will be securely stored in Windows Credential Manager.');

    // Add input fields
    InputPage.Add('Freshdesk URL:', False);  // Regular text field
    InputPage.Add('API Key:', True);        // Masked password field
  end;
end;

// Validate user input before moving to the next page
function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True; // Allow navigation by default

  // Validate input on the custom page (interactive installs only)
  if not IsSilentInstall and (CurPageID = InputPage.ID) then
  begin
    FreshdeskURL := InputPage.Values[0];
    FreshdeskAPIKey := InputPage.Values[1];

    // Ensure fields are not empty
    if (FreshdeskURL = '') or (FreshdeskAPIKey = '') then
    begin
      MsgBox('Both fields are required.', mbError, MB_OK);
      Result := False; // Prevent navigation to the next page
    end;
  end;
end;

// Retrieve command-line parameters for silent install
procedure InitializeSilentInstall;
var
  LogFile: string;
begin
  LogFile := ExpandConstant('{localappdata}\TicketMaker\SilentInstallDebug.log');
  SaveStringToFile(LogFile, 'Starting Silent Installation...' + #13#10, True);

  // Retrieve parameters
  FreshdeskURL := GetParamValue('FreshdeskURL');
  FreshdeskAPIKey := GetParamValue('FreshdeskAPIKey');

  SaveStringToFile(LogFile, 'FreshdeskURL: ' + FreshdeskURL + #13#10, True);
  SaveStringToFile(LogFile, 'FreshdeskAPIKey: ' + FreshdeskAPIKey + #13#10, True);

  // Ensure required parameters are provided
  if (FreshdeskURL = '') or (FreshdeskAPIKey = '') then
  begin
    SaveStringToFile(LogFile, 'Error: Missing parameters. Installation aborted.' + #13#10, True);
    MsgBox('Error: Missing parameters for silent install. Provide FreshdeskURL and FreshdeskAPIKey.', mbError, MB_OK);
    Abort();
  end;

  SaveStringToFile(LogFile, 'Parameters validated successfully.' + #13#10, True);
end;

// Run PowerShell script to save credentials
function SaveCredentials: Boolean;
var
  ResultCode: Integer;
  CmdCommand, LogFile, ErrorLog: string;
begin
  // Log file for debugging
  LogFile := ExpandConstant('{localappdata}\TicketMaker\SilentInstallDebug.log');
  ErrorLog := ExpandConstant('{localappdata}\TicketMaker\CmdError.log');

  // Build the CMD command with named parameters
  CmdCommand := '"' + ExpandConstant('{app}\SaveCredentials.cmd') + '" FreshdeskURL="' +
                FreshdeskURL + '" FreshdeskAPIKey="' + FreshdeskAPIKey + '"';

  // Log the CMD command
  SaveStringToFile(LogFile, 'Executing CMD command: ' + CmdCommand + #13#10, True);

  // Execute the CMD script
  Result := Exec('cmd.exe', '/C ' + CmdCommand, '', SW_HIDE, ewWaitUntilTerminated, ResultCode);

  // Log the result
  if not Result or (ResultCode <> 0) then
  begin
    SaveStringToFile(LogFile, 'Failed to execute CMD script. ResultCode: ' + IntToStr(ResultCode) + #13#10, True);
    MsgBox('Failed to save credentials. Please check the log file for details.', mbError, MB_OK);
    Result := False;
  end
  else
  begin
    SaveStringToFile(LogFile, 'CMD script executed successfully.' + #13#10, True);
    Result := True;
  end;
end;

// Post-installation tasks
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssInstall then
  begin
    // Initialize input for silent installs
    if IsSilentInstall then
      InitializeSilentInstall;

    // Save credentials
    if not SaveCredentials then
      Abort(); // Cancel installation if credentials fail to save
  end;
end;
