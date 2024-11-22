
# TicketMaker - Freshdesk Ticket Creator

![Application Screenshot](images/screenshotmain.png)

## Overview

**TicketMaker** is a standalone Windows application designed to simplify creating support tickets in a Freshdesk system. This repository contains the full version of the application.

### Features

- **Rich Text Editor**: Supports formatted text and embedded images in the ticket description.
- **Embedded Image Handling**: Automatically extracts embedded images and sends them as attachments.
- **File Attachments**: Users can upload additional files to include with their tickets.
- **User-Friendly GUI**: Intuitive fields for entering ticket details.
- **Dropdown Options**: Predefined dropdowns for Priority and Status fields.
- **Validation**: Ensures all required fields are filled before submission.
- **Secure API Integration**: Communicates with the Freshdesk API for ticket creation.
- **Standalone Portable Application**: Runs as a single `.exe` file with no installation required.

---

## How It Works

1. **First Launch**:
   - Upon the first launch, the app prompts for your Freshdesk API URL and API key.
   - These details are stored temporarily in a `config.json` file until the app is exited.

2. **Fill in Required Fields**:
   - **Subject**: Short description of the issue.
   - **Description**: Rich text description with support for images.
   - **Email**: Contact email of the requester.
   - **Priority**: Dropdown to select ticket priority (Low, Medium, High, Urgent).
   - **Status**: Dropdown to select ticket status (Open, Pending, Resolved, Closed).
   - **Attachments**: Add files to include with the ticket.

3. **Submit Ticket**:
   - The app validates the inputs and extracts embedded images.
   - Submits the ticket details and attachments to the Freshdesk API.
   - Displays a success or error message based on the API response.

4. **Config Cleanup**:
   - On exit, the `config.json` file is cleared to avoid storing sensitive data.

---

## Packaging the Application

Use the following PyInstaller command to create the standalone executable for `ticketmaker.py`:

```bash
pyinstaller --clean --onefile --noconsole --icon="assets/icon.ico" --add-data "assets;assets" --add-data "editor.html;." --hidden-import "PyQt5.QtWidgets" --hidden-import "PyQt5.QtWebEngineWidgets" --hidden-import "PyQt5.QtCore" --hidden-import "PyQt5.QtGui" --hidden-import "PyQt5.QtWebEngine" --hidden-import "PyQt5.QtWebEngineCore" --hidden-import "PyQt5.QtWebEngineQuick" --hidden-import "freshdesk.api" ticketmaker.py
```

---

## Future Developments

The following features are planned for future versions:
- **Deployable for Managed Intune Environments**: Ability to easily distribute via Microsoft Intune.
- **Installer Option**: MSI installer tailored for managed environments.
- **Menu Items**: Enhanced menu options for additional functionality.
- **Dark Mode Support**: A dark mode option for better user experience.
- **Custom Branding**: Ability to apply custom branding to the app.

---

## Credits

- **Python-Freshdesk Library Wrapper**: [Freshdesk API Python Wrapper](https://github.com/rschulz600/freshdesk-api-wrapper).
- **Support Ticket Icon**: <a href="https://www.flaticon.com/free-icons/support-ticket" title="support ticket icons">Support ticket icons created by syafii5758 - Flaticon</a>.
- **Advanced Installer**: <a href="https://www.advancedinstaller.com/" title="advanced installer homepage">Windows Installer Packaging Tool for Developers, ISVs & Enterprises</a>.

---

## Contributing

If you want to contribute to this project, feel free to fork the repository, make changes, and submit a pull request.

---

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

Thank you for using TicketMaker! Let us know if you have any questions or suggestions.

