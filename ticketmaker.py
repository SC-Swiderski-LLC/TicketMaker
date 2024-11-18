import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QWidget, QMessageBox, QFileDialog, QSystemTrayIcon, QMenu
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon
import requests
import base64
import re
import win32serviceutil
import win32service
import win32event
import servicemanager
import winreg

def add_to_startup(app_name, app_path):
    """Add the application to Windows startup."""
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
    except Exception as e:
        print(f"Failed to add to startup: {e}")

def remove_from_startup(app_name):
    """Remove the application from Windows startup."""
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, app_name)
    except FileNotFoundError:
        pass  # The app was not in startup
    except Exception as e:
        print(f"Failed to remove from startup: {e}")

def get_registry_value(key, subkey, value_name):
    try:
        registry_key = winreg.OpenKey(key, subkey, 0, winreg.KEY_READ)
        value, _ = winreg.QueryValueEx(registry_key, value_name)
        winreg.CloseKey(registry_key)
        return value
    except FileNotFoundError:
        return None

# Registry constants
REGISTRY_PATH = r"SOFTWARE\\TicketMaker"

# Retrieve URL and API key from the registry
url = get_registry_value(winreg.HKEY_LOCAL_MACHINE, REGISTRY_PATH, "URL")
api_key = get_registry_value(winreg.HKEY_LOCAL_MACHINE, REGISTRY_PATH, "APIKey")

# Validate that the values are retrieved successfully
if not url or not api_key:
    raise RuntimeError("URL or APIKey is missing from the registry. Please reinstall and configure TicketMaker.")


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller. """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# GUI Application Class
class TicketCreator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TicketMaker")
        self.setGeometry(100, 100, 800, 850)
        self.setWindowIcon(QIcon(resource_path("assets/icon.ico")))

        # Main widget and layout
        central_widget = QWidget()
        layout = QVBoxLayout()

        # Subject
        self.subject_label = QLabel("Subject:")
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Enter the ticket subject here")
        layout.addWidget(self.subject_label)
        layout.addWidget(self.subject_input)

        # Email field
        self.email_label = QLabel("Your Email:")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email address")
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)

        # Web-based editor
        self.editor = QWebEngineView()
        self.editor.setUrl(QUrl.fromLocalFile(resource_path("editor.html")))
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.editor)

        # Enable additional WebEngine settings
        self.editor.settings().setAttribute(QWebEngineSettings.PluginsEnabled, True)
        self.editor.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)

        # Priority dropdown
        self.priority_label = QLabel("Priority:")
        self.priority_dropdown = QComboBox()
        self.priority_dropdown.addItems(["Low", "Medium", "High", "Urgent"])
        layout.addWidget(self.priority_label)
        layout.addWidget(self.priority_dropdown)

        # Status dropdown
        self.status_label = QLabel("Status:")
        self.status_dropdown = QComboBox()
        self.status_dropdown.addItems(["Open", "Pending", "Resolved", "Closed"])
        layout.addWidget(self.status_label)
        layout.addWidget(self.status_dropdown)

        # Attachment selection
        self.attachment_label = QLabel("Attachments:")
        self.attachment_button = QPushButton("Add Attachments")
        self.attachment_button.setFixedHeight(50)
        self.attachment_button.clicked.connect(self.add_attachments)
        self.attachments = []
        layout.addWidget(self.attachment_label)
        layout.addWidget(self.attachment_button)

        # Buttons
        self.submit_button = QPushButton("Create Ticket")
        self.submit_button.setFixedHeight(50)
        self.submit_button.clicked.connect(self.create_ticket)
        layout.addWidget(self.submit_button)

        self.clear_button = QPushButton("Clear Fields")
        self.clear_button.clicked.connect(self.clear_fields)
        layout.addWidget(self.clear_button)

        # Set layout
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # System Tray Icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(resource_path("assets/icon.ico")))

        tray_menu = QMenu()
        open_action = tray_menu.addAction("Open TicketMaker")
        open_action.triggered.connect(self.show)
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(self.exit_application)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.show)
        self.tray_icon.show()

    def closeEvent(self, event):
        """Override the close event to hide the window instead of quitting."""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "TicketMaker",
            "TicketMaker is still running in the system tray.",
            QSystemTrayIcon.Information,
            3000
        )

    def exit_application(self):
        """Exit the application cleanly."""
        self.tray_icon.hide()
        QApplication.quit()

    def add_attachments(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Attachments")
        if files:
            self.attachments.extend(files)
            self.attachment_label.setText(f"{len(self.attachments)} attachment(s) added")

    def get_description_content(self):
        self.editor.page().runJavaScript("getContent()", self.handle_description_content)

    def handle_description_content(self, description):
        self.description = description
        self.embedded_images = self.extract_embedded_images(description)
        self.send_ticket()

    def extract_embedded_images(self, description):
        embedded_images = []
        img_matches = re.findall(r'<img src="data:image/(.*?);base64,(.*?)"', description)
        for idx, (img_type, img_data) in enumerate(img_matches):
            file_name = f"embedded_image_{idx + 1}.{img_type}"
            file_path = os.path.join(os.getcwd(), file_name)
            with open(file_path, "wb") as img_file:
                img_file.write(base64.b64decode(img_data))
            embedded_images.append(file_path)
        return embedded_images

    def create_ticket(self):
        self.get_description_content()

    def send_ticket(self):
        subject = self.subject_input.text().strip()
        description = self.description or "No description provided"
        email = self.email_input.text().strip()
        priority = self.priority_dropdown.currentText()
        status = self.status_dropdown.currentText()

        # Check required fields
        if not subject or not description or not email:
            QMessageBox.critical(self, "Error", "Subject, description, and email are required.")
            return

        # Map dropdown values
        priority_mapping = {"Low": 1, "Medium": 2, "High": 3, "Urgent": 4}
        status_mapping = {"Open": 2, "Pending": 3, "Resolved": 4, "Closed": 5}

        # API payload
        data = {
            "email": self.email_input.text().strip(),
            "subject": self.subject_input.text().strip(),
            "description": description,
            "priority": priority_mapping.get(self.priority_dropdown.currentText(), 1),
            "status": status_mapping.get(self.status_dropdown.currentText(), 2)
        }

        try:
            files = [
                ("attachments[]", (os.path.basename(f), open(f, "rb")))
                for f in self.attachments
            ]
            files.extend([
                ("attachments[]", (os.path.basename(f), open(f, "rb")))
                for f in self.embedded_images
            ])

            if files:
                response = requests.post(
                    f"{url}/api/v2/tickets",
                    data=data,
                    files=files,
                    auth=(api_key, "X")
                )
                for _, f in files:
                    f[1].close()
                for file_path in self.embedded_images:
                    if os.path.exists(file_path):
                        os.remove(file_path)
            else:
                headers = {"Content-Type": "application/json"}
                response = requests.post(
                    f"{url}/api/v2/tickets",
                    headers=headers,
                    json=data,
                    auth=(api_key, "X")
                )

            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Ticket created successfully!")
                self.clear_fields()
            else:
                QMessageBox.critical(self, "Error", f"Failed to create ticket. Status code: {response.status_code}\nResponse: {response.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")

    def clear_fields(self):
        self.subject_input.clear()
        self.email_input.clear()
        self.editor.page().runJavaScript("setContent('')")
        self.priority_dropdown.setCurrentIndex(0)
        self.status_dropdown.setCurrentIndex(0)
        self.attachments = []
        self.embedded_images = []
        self.attachment_label.setText("Attachments:")


class TicketMakerService(win32serviceutil.ServiceFramework):
    _svc_name_ = "TicketMakerService"
    _svc_display_name_ = "TicketMaker Application Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogInfoMsg("TicketMaker Service is starting...")
        app = QApplication([])
        window = TicketCreator()
        window.hide()  # Service starts with GUI hidden
        app.exec_()


if __name__ == "__main__":
    app_path = os.path.abspath(__file__)
    add_to_startup("TicketMaker", app_path)  # Add app to startup

    if len(sys.argv) > 1 and sys.argv[1] in ["install", "remove", "start", "stop"]:
        win32serviceutil.HandleCommandLine(TicketMakerService)
    else:
        app = QApplication(sys.argv)
        window = TicketCreator()
        window.show()

        try:
            sys.exit(app.exec_())
        except SystemExit:
            print("Application closed cleanly.")

