# Using Configurator.exe Outside the Installation Process

`configurator.exe` is a versatile tool that goes beyond its primary role during the installation of **TicketMaker**. It can be used by IT administrators and advanced users to manage and update the application's Freshdesk API configuration at any time.

## Key Features of Configurator.exe
1. **Interactive Configuration**:
   - Launch `configurator.exe` without any arguments to open a GUI.
   - The GUI allows users to manually update the Freshdesk URL and API key stored in the registry.
   - Ideal for reconfiguring the application after installation.

2. **Silent Command-Line Updates**:
   - `configurator.exe` supports command-line arguments for silent updates to the registry.
   - This feature is useful for IT administrators who need to quickly update settings across multiple systems without user interaction.

## Command-Line Usage
Run the following command in a terminal or PowerShell to pass parameters to `configurator.exe`:

```bash
configurator.exe <Freshdesk_URL> <API_Key>
```

### Example
To update the Freshdesk URL and API key:
```bash
configurator.exe "https://examplecompany.freshdesk.com" "NewAPIKey123"
```
- This command updates the registry with the provided Freshdesk URL and API key.
- No GUI is launched, making it suitable for automated scripts or remote updates.

## PowerShell Command
In PowerShell, use the following command to achieve the same:
```powershell
Start-Process -FilePath "C:\Path\To\configurator.exe" -ArgumentList '"https://examplecompany.freshdesk.com" "NewAPIKey123"' -Wait
```

## Practical Use Cases
1. **Post-Installation Configuration**:
   - Reconfigure the application if the Freshdesk account details change after installation.
   - Update settings on user systems without needing to reinstall the application.

2. **Centralized IT Management**:
   - Integrate `configurator.exe` into deployment scripts for enterprise environments.
   - Apply updates remotely using silent command-line functionality.

3. **Troubleshooting**:
   - Quickly reset the API configuration in case of connection issues with Freshdesk.
   - Ensure registry entries are correctly set without manual registry editing.

## Notes
- Ensure the `configurator.exe` file is accessible on the target system when using it for updates.
- Administrator privileges may be required to modify registry entries.
- Always verify the provided Freshdesk URL and API key for accuracy before applying changes.

`configurator.exe` is a valuable addition to IT toolkits, simplifying the management of critical application settings with its dual interactive and command-line capabilities.
```
