# Ticketmaker - Freshdesk Ticket Creator

## Overview

The **Freshdesk Ticket Creator** is a Python application with a graphical user interface (GUI) built using Tkinter. This application allows users to create support tickets in a Freshdesk system easily. The tool integrates with the Freshdesk API to submit ticket details entered by the user directly to the Freshdesk ticketing platform.

## Features

- **User-Friendly GUI**: Intuitive fields for entering ticket details.
- **Dynamic Dropdowns**: Predefined dropdown options for Priority, Status, and Ticket Type.
- **Default Status**: The ticket status defaults to "Open."
- **Validation**: Ensures all fields are filled before submission.
- **Ticket Creation**: Submits ticket details to the Freshdesk API.
- **Clear Fields**: A convenient button to clear all fields after ticket creation.

## How It Works

1. The user fills in the required fields:
   - **Subject**: Short description of the issue.
   - **Description**: Detailed explanation of the issue.
   - **Email**: Contact email of the person reporting the issue.
   - **Priority**: Dropdown to select ticket priority (Low, Medium, High, Urgent).
   - **Status**: Dropdown to select ticket status (Open, Pending, Resolved, Closed).
   - **Type**: Dropdown to select ticket type (Alert, EDR, Problem, Task, Other).

2. On clicking "Create Ticket":
   - Validates that all fields are filled.
   - Maps dropdown values to Freshdesk's API values.
   - Submits the ticket details to the Freshdesk API.
   - Displays a success or error message based on the API response.

3. After submission, fields are cleared for the next entry.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/freshdesk-ticket-creator.git
   cd freshdesk-ticket-creator
   ```

2. **Install Dependencies**:
   Ensure you have Python 3.x installed and the required libraries:
   ```bash
   pip install requests
   ```

3. **Configure API Settings**:
   - Open the script file (`ticket_creator.py`).
   - Replace `yourdomain.freshdesk.com` with your Freshdesk domain.
   - Replace `your_api_key` with your Freshdesk API key.

4. **Run the Application**:
   ```bash
   python ticket_creator.py
   ```

## Usage

- Launch the application and fill in all required fields.
- Click "Create Ticket" to submit the ticket to Freshdesk.
- Use "Clear Fields" to reset the form if needed.

## Notes

- Ensure your Freshdesk API key has the necessary permissions to create tickets.
- Use HTTPS for secure communication with the Freshdesk API.

## Contributing

If you want to contribute to this project, feel free to fork the repository, make changes, and submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

Thank you for using the Freshdesk Ticket Creator!

