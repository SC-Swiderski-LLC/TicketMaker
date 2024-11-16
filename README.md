# TicketMaker - Freshdesk Ticket Creator

![Application Screenshot](images/screenshotmain.png)

## Overview

**TicketMaker** is a Python application designed to simplify creating support tickets in a Freshdesk system. This repository contains two versions of the application:

1. **Full Version**: Includes a rich text editor with support for embedded and uploaded images as attachments.
2. **Lite Version**: A minimal implementation using Tkinter for a lightweight ticket creation experience.

## Full Version

### Features

- **Rich Text Editor**: Supports formatted text and embedded images in the ticket description.
- **Embedded Image Handling**: Automatically extracts embedded images and sends them as attachments.
- **File Attachments**: Users can upload additional files to include with their tickets.
- **User-Friendly GUI**: Intuitive fields for entering ticket details.
- **Dropdown Options**: Predefined dropdowns for Priority and Status fields.
- **Validation**: Ensures all required fields are filled before submission.
- **Secure API Integration**: Communicates with the Freshdesk API for ticket creation.

### How It Works

1. **Fill in Required Fields**:
   - **Subject**: Short description of the issue.
   - **Description**: Rich text description with support for images.
   - **Email**: Contact email of the requester.
   - **Priority**: Dropdown to select ticket priority (Low, Medium, High, Urgent).
   - **Status**: Dropdown to select ticket status (Open, Pending, Resolved, Closed).
   - **Attachments**: Add files to include with the ticket.

2. **Submit Ticket**:
   - The app validates the inputs and extracts embedded images.
   - Submits the ticket details and attachments to the Freshdesk API.
   - Displays a success or error message based on the API response.

   ![Full Version Screenshot](images/successmessage.png)


3. **Clear Form**:
   - The fields are reset after successful submission.
   - Embedded images saved during processing are automatically cleaned up.


## Lite Version

### Features

- **Minimal Design**: Lightweight Tkinter-based GUI.
- **Dropdown Options**: Predefined dropdowns for Priority and Status fields.
- **Validation**: Ensures all required fields are filled before submission.
- **Simple API Integration**: Communicates with the Freshdesk API for ticket creation.

### How It Works

1. **Fill in Required Fields**:
   - **Subject**: Short description of the issue.
   - **Description**: Plain text description of the issue.
   - **Email**: Contact email of the requester.
   - **Priority**: Dropdown to select ticket priority (Low, Medium, High, Urgent).
   - **Status**: Dropdown to select ticket status (Open, Pending, Resolved, Closed).

2. **Submit Ticket**:
   - The app validates the inputs and submits the ticket details to the Freshdesk API.
   - Displays a success or error message based on the API response.

3. **Clear Form**:
   - The fields are reset after submission.

![Lite Version Screenshot](images/screenshotlite.png)

## Installation

### Common Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/sargeschultz11/Ticketmaker
   cd Ticketmaker
   ```

2. **Install Dependencies**:
   Ensure you have Python 3.x installed and install the required libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Settings**:
   - Open the config file (`config.json`).
   - Replace `yourdomain.freshdesk.com` with your Freshdesk domain.
   - Replace `your_api_key` with your Freshdesk API key.

### Running the Full Version

1. **Ensure WebEngine Requirements**:
   The full version uses PyQt5 with QWebEngine, which may require additional setup for your system. Follow [PyQt5 installation documentation](https://riverbankcomputing.com/software/pyqt/intro) if needed.

2. **Run the Application**:
   ```bash
   python ticket_creator_full.py
   ```

### Running the Lite Version

1. **Run the Application**:
   ```bash
   python ticket_creator_lite.py
   ```

## Notes

- Ensure your Freshdesk API key has the necessary permissions to create tickets.
- Use HTTPS for secure communication with the Freshdesk API.
- For the full version, embedded images in the rich text editor will be extracted and attached automatically.

## Contributing

If you want to contribute to this project, feel free to fork the repository, make changes, and submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

Thank you for using Ticketmaker! Let us know if you have any questions or suggestions.
