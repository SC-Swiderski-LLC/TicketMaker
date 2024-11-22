import sys
import os
import json
import re
import base64
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QWidget, QMessageBox, QFileDialog, QSystemTrayIcon, QMenu,
    QSplashScreen, QInputDialog
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon, QPixmap
from freshdesk.api import API  # Add this here
import argparse


# Paths and Constants
CONFIG_PATH = os.path.expandvars(r"%PROGRAMDATA%\TicketMaker\config.json")


# Utility Functions
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


def load_config():
    """Load configuration from JSON."""
    try:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as file:
                return json.load(file)
    except Exception as e:
        print(f"Error loading configuration: {e}")
    return None


def save_config(api_url, api_key):
    """Save configuration to JSON in a readable format."""
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, "w") as file:
            json.dump({"api_url": api_url, "api_key": api_key}, file, indent=4)  # Add indent for pretty-printing
        print(f"Configuration saved to {CONFIG_PATH}")
    except Exception as e:
        print(f"Error saving configuration: {e}")


def run_configurator():
    """Prompt user for API URL and Key."""
    try:
        app = QApplication.instance() or QApplication(sys.argv)
        api_url, ok_url = QInputDialog.getText(None, "Configuration", "Enter API URL:")
        if not ok_url or not api_url.strip():
            QMessageBox.warning(None, "Error", "API URL is required!")
            return None

        api_key, ok_key = QInputDialog.getText(None, "Configuration", "Enter API Key:")
        if not ok_key or not api_key.strip():
            QMessageBox.warning(None, "Error", "API Key is required!")
            return None

        save_config(api_url.strip(), api_key.strip())
        return {"api_url": api_url.strip(), "api_key": api_key.strip()}
    except Exception as e:
        print(f"Error in configurator: {e}")
        return None


def setup_config(args):
    """Main configuration setup."""
    if args.config:
        print("Running configurator...")
        return run_configurator()

    config = load_config()
    if not config:
        print("No configuration found. Launching configurator...")
        return run_configurator()

    return config


# Main App Class
class TicketCreator(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.attachments = []
        self.embedded_images = []
        self.setWindowTitle("TicketMaker")
        self.setGeometry(100, 100, 800, 850)
        self.setWindowIcon(QIcon(resource_path("assets/icon.ico")))

        # System Tray Icon
        self.tray_icon = QSystemTrayIcon(QIcon(resource_path("assets/icon.ico")), self)
        self.tray_icon.setToolTip("TicketMaker")

        # Tray Menu
        tray_menu = QMenu()
        open_action = tray_menu.addAction("Open TicketMaker")
        open_action.triggered.connect(self.show)
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(self.exit_application)
        self.tray_icon.setContextMenu(tray_menu)

        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

        # Main Layout and Widgets
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Subject
        layout.addWidget(QLabel("Subject:"))
        self.subject_input = QLineEdit(placeholderText="Enter the ticket subject here")
        layout.addWidget(self.subject_input)

        # Email field
        layout.addWidget(QLabel("Your Email:"))
        self.email_input = QLineEdit(placeholderText="Enter your email address")
        layout.addWidget(self.email_input)

        # Editor
        self.editor = QWebEngineView()
        editor_path = resource_path("editor.html")
        if os.path.exists(editor_path):
            self.editor.setUrl(QUrl.fromLocalFile(editor_path))
        else:
            self.editor.setHtml("<h3>Editor file not found</h3>")
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.editor)

        # Priority dropdown
        layout.addWidget(QLabel("Priority:"))
        self.priority_dropdown = QComboBox()
        self.priority_dropdown.addItems(["Low", "Medium", "High", "Urgent"])
        layout.addWidget(self.priority_dropdown)

        # Status dropdown
        layout.addWidget(QLabel("Status:"))
        self.status_dropdown = QComboBox()
        self.status_dropdown.addItems(["Open", "Pending", "Resolved", "Closed"])
        layout.addWidget(self.status_dropdown)

        # Attachments
        self.attachment_label = QLabel("Attachments:")
        self.attachment_button = QPushButton("Add Attachments")
        self.attachment_button.clicked.connect(self.add_attachments)
        layout.addWidget(self.attachment_label)
        layout.addWidget(self.attachment_button)

        # Submit Button
        self.submit_button = QPushButton("Create Ticket")
        self.submit_button.clicked.connect(self.create_ticket)
        layout.addWidget(self.submit_button)

        # Clear Fields Button
        self.clear_button = QPushButton("Clear Fields")
        self.clear_button.clicked.connect(self.clear_fields)
        layout.addWidget(self.clear_button)

        # Set the layout for the central widget
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "TicketMaker",
            "TicketMaker is running in the system tray.",
            QSystemTrayIcon.Information,
            3000
        )

    def exit_application(self):
        """Exit the application cleanly and remove the config file for portability."""
        try:
            if os.path.exists(CONFIG_PATH):
                os.remove(CONFIG_PATH)
                print(f"Configuration file {CONFIG_PATH} removed.")
        except Exception as e:
            print(f"Failed to remove configuration file: {e}")
        
        self.tray_icon.hide()
        QApplication.quit()

    def create_ticket(self):
        subject = self.subject_input.text().strip()
        email = self.email_input.text().strip()
        if not subject or not email:
            QMessageBox.critical(self, "Error", "Subject and Email are required!")
            return
        self.editor.page().runJavaScript("getContent()", self.handle_description_content)

    def clear_fields(self):
        """Clear all input fields and reset the form."""
        self.subject_input.clear()
        self.email_input.clear()

        # Reset the editor's content without affecting its visibility
        if os.path.exists(resource_path("editor.html")):
            self.editor.setUrl(QUrl.fromLocalFile(resource_path("editor.html")))
        else:
            self.editor.setHtml("<h3>Editor file not found</h3>")

        # Reset dropdowns and attachments
        self.priority_dropdown.setCurrentIndex(0)
        self.status_dropdown.setCurrentIndex(0)
        self.attachments = []
        self.attachment_label.setText("Attachments:")

    def handle_description_content(self, description):
        self.description = description
        self.embedded_images = self.extract_embedded_images(description)
        self.send_ticket()

    def add_attachments(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Attachments")
        if files:
            self.attachments.extend(files)
            self.attachment_label.setText(f"{len(self.attachments)} attachment(s) added")

    def extract_embedded_images(self, description):
        embedded_images = []
        matches = re.findall(r'<img src="data:image/(.*?);base64,(.*?)"', description)
        for idx, (img_type, img_data) in enumerate(matches):
            file_name = f"embedded_image_{idx + 1}.{img_type}"
            file_path = os.path.join(os.getcwd(), file_name)
            with open(file_path, "wb") as img_file:
                img_file.write(base64.b64decode(img_data))
            embedded_images.append(file_path)
        return embedded_images

    def send_ticket(self):
        """Send the ticket data to the Freshdesk API with attachments."""
        try:
            # Prepare ticket details
            subject = self.subject_input.text().strip()
            email = self.email_input.text().strip()
            description = self.description or "No description provided"
            priority = self.priority_dropdown.currentIndex() + 1
            status = self.status_dropdown.currentIndex() + 2

            if not subject or not email:
                QMessageBox.critical(self, "Error", "Subject and Email are required!")
                return

            # Prepare ticket data for multipart/form-data
            data = {
                "email": email,
                "subject": subject,
                "description": description,
                "priority": str(priority),  # Strings for multipart/form-data
                "status": str(status)
            }

            # Prepare attachments
            files = []
            for f in self.attachments:
                try:
                    files.append(("attachments[]", (os.path.basename(f), open(f, "rb"))))
                except Exception as e:
                    QMessageBox.warning(self, "Warning", f"Could not open attachment: {f}\n{e}")

            for f in self.embedded_images:
                try:
                    files.append(("attachments[]", (os.path.basename(f), open(f, "rb"))))
                except Exception as e:
                    QMessageBox.warning(self, "Warning", f"Could not open embedded image: {f}\n{e}")

            # Prepare API headers
            credentials = f"{self.config['api_key']}:X"
            encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
            headers = {
                "Authorization": f"Basic {encoded_credentials}"
            }

            # API URL
            api_url = f"https://{self.config['api_url'].rstrip('/')}/api/v2/tickets"

            # Send API request
            response = requests.post(api_url, headers=headers, data=data, files=files)

            # Cleanup embedded images
            for file_path in self.embedded_images:
                try:
                    os.remove(file_path)
                except Exception:
                    pass

            # Handle API response
            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Ticket created successfully!")
                self.clear_fields()
            else:
                error_message = response.json().get("message", "Unknown error")
                QMessageBox.critical(self, "Error", f"Failed to create ticket: {error_message}")

            # Close file handles
            for _, (_, file_handle) in files:
                file_handle.close()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while creating the ticket: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TicketMaker")
    parser.add_argument("--config", action="store_true", help="Launch configuration window")
    parser.add_argument("--subject", type=str, help="Subject of the ticket")
    parser.add_argument("--email", type=str, help="Your email address")
    parser.add_argument("--description", type=str, help="Description of the ticket")
    parser.add_argument("--priority", type=int, choices=[1, 2, 3, 4], help="Priority (1=Low, 2=Medium, 3=High, 4=Urgent)")
    parser.add_argument("--status", type=int, choices=[2, 3, 4, 5], help="Status (2=Open, 3=Pending, 4=Resolved, 5=Closed)")
    parser.add_argument("--attachments", nargs="*", help="File paths for attachments")
    args = parser.parse_args()

    app = QApplication(sys.argv)

    try:
        config = setup_config(args)
        if not config:
            QMessageBox.critical(None, "Error", "Configuration setup failed. Exiting.")
            sys.exit(1)

        # CLI Ticket Creation
        if args.subject and args.email and args.description:
            print("Creating ticket from CLI...")
            data = {
                "email": args.email,
                "subject": args.subject,
                "description": args.description,
                "priority": args.priority or 1,
                "status": args.status or 2
            }
            files = []
            if args.attachments:
                for f in args.attachments:
                    try:
                        files.append(("attachments[]", (os.path.basename(f), open(f, "rb"))))
                    except Exception as e:
                        print(f"Error with attachment {f}: {e}")
                        sys.exit(1)

            # Send ticket
            api_url = f"https://{config['api_url'].rstrip('/')}/api/v2/tickets"
            credentials = f"{config['api_key']}:X"
            encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
            headers = {"Authorization": f"Basic {encoded_credentials}"}

            response = requests.post(api_url, headers=headers, data=data, files=files)
            if response.status_code == 201:
                print("Ticket created successfully!")
            else:
                print(f"Failed to create ticket: {response.text}")

            # Cleanup
            for _, (_, file_handle) in files:
                file_handle.close()

            sys.exit(0)

        # GUI Launch
        splash_pix = QPixmap(resource_path("assets/splash_logo.png"))
        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.setWindowFlag(Qt.FramelessWindowHint)
        splash.show()
        window = TicketCreator(config)
        splash.finish(window)
        window.show()
    except Exception as e:
        QMessageBox.critical(None, "Error", f"An error occurred:\n{str(e)}")
        sys.exit(1)

    sys.exit(app.exec_())

