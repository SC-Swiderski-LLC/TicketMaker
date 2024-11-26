import sys
import os
import json
import re
import base64
import winreg
import logging
from ctypes import Structure, c_uint, POINTER, windll, create_string_buffer, byref, cast, c_void_p, string_at
from ctypes.wintypes import DWORD
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QWidget, QMessageBox, QFileDialog, QSystemTrayIcon, QMenu,
    QSplashScreen, QInputDialog
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon, QPixmap, QPalette, QColor
from freshdesk.api import API
import requests

# File paths for logs and encrypted credentials
STORAGE_PATH = r"C:\ProgramData\TicketMaker"
LOG_FILE = os.path.join(STORAGE_PATH, "ticketmaker.log")
URL_FILE = os.path.join(STORAGE_PATH, "FreshdeskURL.dat")
APIKEY_FILE = os.path.join(STORAGE_PATH, "FreshdeskAPIKey.dat")

# Set up logging to write to both a file and the console
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller."""
    # base_path = getattr(sys, "_MEIPASS", os.path.abspath(os.path.dirname(__file__)))
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS

    resolved_path = os.path.join(base_path, relative_path)

    if not os.path.exists(resolved_path):
        raise FileNotFoundError(f"Resource not found: {resolved_path}")
    return resolved_path


def get_credential(credential_name):
    """Retrieve a credential from Windows Credential Manager."""
    try:
        # Retrieve the credential from Windows Credential Manager
        credential = win32cred.CredRead(credential_name, win32cred.CRED_TYPE_GENERIC)
        if credential:
            return credential['CredentialBlob'].decode()
        else:
            logger.warning(f"Credential {credential_name} not found.")
            return None
    except Exception as e:
        logger.error(f"Error retrieving credential {credential_name}: {e}")
        return None
    

# Retrieve the Freshdesk URL and API Key
url, api_key = load_credentials()

if url and api_key:
    logger.info(f"Freshdesk URL: {url}")
    logger.info(f"Freshdesk API Key: {api_key}")
else:
    logger.critical("Failed to retrieve Freshdesk credentials. Exiting.")
    sys.exit(1)  # Exit the app if credentials are missing

def is_windows_dark_mode():
    """Detect if Windows is in dark mode."""
    try:
        reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        use_light_theme, _ = winreg.QueryValueEx(reg_key, "AppsUseLightTheme")
        return use_light_theme == 0
    except Exception as e:
        logger.warning(f"Dark mode detection failed: {e}")
        return False
    
    
def sanitize_credential(credential):
    """Clean up credentials by removing unexpected characters."""
    return credential.strip().replace("\x00", "")


# Retrieve and sanitize Freshdesk URL and API Key
url = get_credential("TicketMaker_FreshdeskURL")
api_key = get_credential("TicketMaker_APIKey")

if url and api_key:
    url = sanitize_credential(url)
    api_key = sanitize_credential(api_key)
    logger.info(f"Freshdesk URL: {url}")
    logger.info(f"Freshdesk API Key: {api_key}")
else:
    logger.critical("Failed to retrieve Freshdesk credentials. Exiting.")
    sys.exit(1)  # Exit the app if credentials are missing

# Dark mode testing

# Main App Class
class TicketCreator(QMainWindow):
    def __init__(self, config):
        super().__init__()
        self.config = config
        logger.debug(f"TicketCreator initialized with config: {self.config}")
        self.attachments = []
        self.init_ui()
        self.apply_theme()


    def init_ui(self):
        """Set up the UI."""
        self.setWindowTitle("TicketMaker")
        self.setGeometry(100, 100, 800, 850)

        # Set window icon
        icon_path = resource_path("assets/icon.ico")
        self.setWindowIcon(QIcon(icon_path))

        # Set system tray icon
        tray_icon_path = resource_path("assets/icon.ico")
        self.tray_icon = QSystemTrayIcon(QIcon(tray_icon_path), self)
        self.tray_icon.setToolTip("TicketMaker")

        # Tray Menu
        tray_menu = QMenu()
        open_action = tray_menu.addAction("Open TicketMaker")
        open_action.triggered.connect(self.show_normal)  # Adjusted to reuse show_normal()
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(self.exit_application)
        self.tray_icon.setContextMenu(tray_menu)

        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

        central_widget = QWidget()
        layout = QVBoxLayout()
        # Add additional UI initialization here
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Subject Field
        self.subject_label = QLabel("Subject: ")
        layout.addWidget(self.subject_label)
        self.subject_input = QLineEdit(placeholderText="Enter the ticket subject here")
        layout.addWidget(self.subject_input)

        # Email Field
        self.email_label = QLabel("Your Email:")
        layout.addWidget(self.email_label)
        self.email_input = QLineEdit(placeholderText="Enter your email address")
        layout.addWidget(self.email_input)

        # Rich Text Editor
        self.description_label = QLabel("Description:")
        layout.addWidget(self.description_label)
        self.editor = QWebEngineView()
        editor_path = resource_path("src/editor.html")
        if os.path.exists(editor_path):
            self.editor.setUrl(QUrl.fromLocalFile(editor_path))
        else:
            self.editor.setHtml("<h3>Editor file not found</h3>")
        layout.addWidget(self.editor)

        # Type Dropdown
        self.dropdown_type_label = QLabel("Ticket Type: ")
        layout.addWidget(self.dropdown_type_label)
        self.dropdown_type = QComboBox()
        self.dropdown_type.addItem("")
        self.dropdown_type.addItems(['Alert', 'EDR', 'Problem', 'Task', 'Sage', 'Other'])
        layout.addWidget(self.dropdown_type)
        self.dropdown_type.currentTextChanged.connect(self.handle_dropdown_type_change)

        # Classification Dropdown
        self.classification_label = QLabel("Classification: ")
        self.classification_label.hide()
        layout.addWidget(self.classification_label)
        self.dropdown_classification = QComboBox()
        self.dropdown_classification.addItem('')
        self.dropdown_classification.addItems([
            "Intacct - Support Request",
            "Intacct - Report Issue",
            "Intacct - Enhancement Request",
            "SCM - Support Request",
            "SCM - Report Issue",
            "SCM - Enhancement Request",
            "Sage - Access Request",
            "Sage - System Down",
            "Sage - General Inquiry",
            "Password Reset"
        ])
        self.dropdown_classification.hide()
        layout.addWidget(self.dropdown_classification)

        # Priority Dropdown
        layout.addWidget(QLabel("Priority:"))
        self.priority_dropdown = QComboBox()
        self.priority_dropdown.addItems(["Low", "Medium", "High", "Urgent"])
        layout.addWidget(self.priority_dropdown)

        # Status Dropdown
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

        # Clear Button
        self.clear_button = QPushButton("Clear Fields")
        self.clear_button.clicked.connect(self.clear_fields)
        layout.addWidget(self.clear_button)

        # Set Main Layout
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)


    def apply_theme(self):
        """Apply dark or light theme based on OS settings."""
        app = QApplication.instance()
        is_dark_mode = is_windows_dark_mode()

        # Set PyQt dark palette
        # palette = QPalette()

        if is_dark_mode:
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor("#2b2b2b"))
            palette.setColor(QPalette.WindowText, QColor("#ffffff"))
            palette.setColor(QPalette.Base, QColor("#1e1e1e"))
            palette.setColor(QPalette.Text, QColor("#d4d4d4"))
            palette.setColor(QPalette.Button, QColor("#3c3c3c"))
            palette.setColor(QPalette.ButtonText, QColor("#ffffff"))
            app.setPalette(palette)
            self.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")
        else:
            palette = QPalette()
            palette.setColor(QPalette.Window, QColor("#ffffff"))
            palette.setColor(QPalette.WindowText, QColor("#000000"))
            palette.setColor(QPalette.Base, QColor("#f0f0f0"))
            palette.setColor(QPalette.Text, QColor("#000000"))
            palette.setColor(QPalette.Button, QColor("#e0e0e0"))
            palette.setColor(QPalette.ButtonText, QColor("#000000"))
            app.setPalette(palette)
            self.setStyleSheet("background-color: #ffffff; color: #000000;")

            # # Apply styles to specific widgets
            # self.subject_input.setStyleSheet("background-color: #2b2b2b; color: #ffffff; border: 1px solid #555;")
            # self.email_input.setStyleSheet("background-color: #2b2b2b; color: #ffffff; border: 1px solid #555;")
            # self.dropdown_type.setStyleSheet('background-color: #2b2b2b; color: #ffffff; border: 1px solid #555;')
            # self.dropdown_classification.setStyleSheet('background-color: #2b2b2b; color: #ffffff; border: 1px solid #555;')
            # self.priority_dropdown.setStyleSheet("background-color: #2b2b2b; color: #ffffff; border: 1px solid #555;")
            # self.status_dropdown.setStyleSheet("background-color: #2b2b2b; color: #ffffff; border: 1px solid #555;")
            # self.attachment_button.setStyleSheet("background-color: #3c3c3c; color: #ffffff; border: 1px solid #555;")
            # self.submit_button.setStyleSheet("background-color: #3c3c3c; color: #ffffff; border: 1px solid #555;")
            # self.clear_button.setStyleSheet("background-color: #3c3c3c; color: #ffffff; border: 1px solid #555;")

            # # Dark mode for QMessageBox
        #     app.setStyleSheet("""
        #         QMessageBox {
        #             background-color: #2b2b2b;
        #             color: #ffffff;
        #         }
        #         QMessageBox QLabel {
        #             color: #ffffff;
        #         }
        #         QMessageBox QPushButton {
        #             background-color: #3c3c3c;
        #             color: #ffffff;
        #             border: 1px solid #555;
        #         }
        #         QMessageBox QPushButton:hover {
        #             background-color: #555;
        #         }
        #     """)

        # else:
        #     palette = app.style().standardPalette()
        #     self.subject_input.setStyleSheet("")
        #     self.email_input.setStyleSheet("")
        #     self.dropdown_type.setStyleSheet('')
        #     self.dropdown_classification.setStyleSheet('')
        #     self.priority_dropdown.setStyleSheet("")
        #     self.status_dropdown.setStyleSheet("")
        #     self.attachment_button.setStyleSheet("")
        #     self.submit_button.setStyleSheet("")
        #     self.clear_button.setStyleSheet("")

        #     # Light mode for QMessageBox
        #     app.setStyleSheet("""
        #         QMessageBox {
        #             background-color: #ffffff;
        #             color: #000000;
        #         }
        #         QMessageBox QLabel {
        #             color: #000000;
        #         }
        #         QMessageBox QPushButton {
        #             background-color: #f0f0f0;
        #             color: #000000;
        #             border: 1px solid #ccc;
        #         }
        #         QMessageBox QPushButton:hover {
        #             background-color: #e0e0e0;
        #         }
        #     """)

        # app.setPalette(palette)

        # Wait for the editor page to load before applying dark mode
        def set_editor_mode():
            self.editor.page().runJavaScript(f"setDarkMode({str(is_dark_mode).lower()});")

        self.editor.page().loadFinished.connect(set_editor_mode)


    def tray_icon_activated(self, reason):
        """Handle tray icon activation."""
        if reason == QSystemTrayIcon.DoubleClick:
            self.show()


    def handle_dropdown_type_change(self, value):
        if value == 'Sage':
            self.classification_label.show()
            self.dropdown_classification.show()
            self.dropdown_classification.setCurrentIndex(0)
        else:
            self.classification_label.hide()
            self.dropdown_classification.hide()


    def closeEvent(self, event):
        """Override close event to minimize to tray instead of exiting."""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "TicketMaker",
            "TicketMaker is running in the system tray.",
            QSystemTrayIcon.Information,
            3000
        )


    def exit_application(self):
        """Exit the application cleanly."""
        try:
            self.tray_icon.hide()
            print("Tray icon hidden. Application exiting.")
        except Exception as e:
            print(f"Error during application exit: {e}")
        
        QApplication.quit()


    def create_ticket(self):

        def validate_field(field_label, field_input, value, error_msg):
            if not value.strip():
                field_label.setStyleSheet('color: red;')
                field_input.setStyleSheet('border: 2px solid red;')
                return error_msg
            else:
                field_label.setStyleSheet('')
                field_input.setStyleSheet('')
                return None
        
        missing_fields = []

        # Append if there is a missing value
        subject_error = validate_field(self.subject_label, self.subject_input, self.subject_input.text(), 'Subject')
        if subject_error:
            missing_fields.append(subject_error)
        email_error = validate_field(self.email_label, self.email_input, self.email_input.text(), 'Email')
        if email_error:
            missing_fields.append(email_error)
        type_error = validate_field(self.dropdown_type_label, self.dropdown_type, self.dropdown_type.currentText(), 'Type')
        if type_error:
            missing_fields.append(type_error)


        # Validate the Description field asynchronously
        def validate_description(content):
            description = content.strip() if content.strip() else None
            if not description:
                self.description_label.setStyleSheet('color: red;')
                self.editor.page().runJavaScript("document.getElementById('editor').classList.add('invalid')")
                missing_fields.append('Description')
            else:
                self.description_label.setStyleSheet('')
                self.editor.page().runJavaScript("document.getElementById('editor').classList.remove('invalid')")

            # Show errors or proceed
            if missing_fields:
                QMessageBox.critical(self, 'Error', f'The following fields are required: \n{', '.join(filter(None, missing_fields))}')
            else:
                self.send_ticket(description)

        self.editor.page().runJavaScript("document.getElementById('editor').innerText", validate_description)


    def clear_fields(self):

        """Clear all input fields and reset the form."""
        self.subject_input.clear()
        self.email_input.clear()

        # Reset the editor's content without affecting its visibility
        if os.path.exists(resource_path("src/editor.html")):
            self.editor.setUrl(QUrl.fromLocalFile(resource_path("src/editor.html")))
        else:
            self.editor.setHtml("<h3>Editor file not found</h3>")

        # Reset dropdowns and attachments
        self.dropdown_type.setCurrentIndex(0)
        self.priority_dropdown.setCurrentIndex(0)
        self.status_dropdown.setCurrentIndex(0)
        self.attachments = []
        self.attachment_label.setText("Attachments:")

        self.subject_label.setStyleSheet("")
        self.subject_input.setStyleSheet("")
        self.email_label.setStyleSheet("")
        self.email_input.setStyleSheet("")
        self.dropdown_type_label.setStyleSheet("")
        self.dropdown_type.setStyleSheet("")
        self.description_label.setStyleSheet("")
        self.editor.page().runJavaScript("document.getElementById('editor').classList.remove('invalid')")


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

    def send_ticket(self, description):
        """Send the ticket data to the Freshdesk API with or without attachments."""
        try:
            logger.info("Initiating ticket creation process...")

            # Prepare ticket details
            subject = self.subject_input.text().strip()
            email = self.email_input.text().strip()
            type_field = self.dropdown_type.currentText()
            classification = self.dropdown_classification.currentText()
            priority = self.priority_dropdown.currentIndex() + 1
            status = self.status_dropdown.currentIndex() + 2

            if not subject or not email:
                logger.error("Subject or Email is missing!")
                QMessageBox.critical(self, "Error", "Subject and Email are required!")
                return

            logger.info(f"Ticket details: subject={subject}, email={email}, priority={priority}, status={status}")

            # Prepare ticket data
            data = {
                "email"        : email,
                "subject"      : subject,
                "description"  : description,
                "priority"     : priority,     # Keep as integer
                "status"       : status,       # Keep as integer
                "type"         : type_field,
                "custom_fields": {
                    "cf_classification": classification
                }
            }

            # Prepare attachments
            files = []
            has_attachments = bool(self.attachments or self.embedded_images)
            if has_attachments:
                try:
                    for attachment in self.attachments:
                        logger.info(f"Processing attachment: {attachment}")
                        files.append(("attachments[]", (os.path.basename(attachment), open(attachment, "rb"))))

                    for idx, embedded_image in enumerate(self.embedded_images):
                        file_name = f"embedded_image_{idx + 1}.png"
                        missing_padding = len(embedded_image) % 4
                        if missing_padding != 0:
                            embedded_image += "=" * (4 - missing_padding)

                        with open(file_name, "wb") as img_file:
                            img_file.write(base64.b64decode(embedded_image))
                        files.append(("attachments[]", (file_name, open(file_name, "rb"))))
                except Exception as attachment_error:
                    logger.error(f"Error processing attachments: {attachment_error}")
                    QMessageBox.warning(self, "Warning", f"Could not process attachments or embedded images:\n{attachment_error}")
                    return

            # API headers
            credentials = f"{self.config['api_key']}:X"
            encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
            headers = {
                "Authorization": f"Basic {encoded_credentials}"
            }

            logger.info(f"Headers: {headers}")

            # API URL
            api_url = f"https://{self.config['api_url'].rstrip('/')}/api/v2/tickets"
            logger.info(f"API URL: {api_url}")

            # Send API request
            response = None
            try:
                if has_attachments:
                    response = requests.post(api_url, headers=headers, data=data, files=files)
                else:
                    headers["Content-Type"] = "application/json"
                    response = requests.post(api_url, headers=headers, json=data)

                logger.info(f"Response status code: {response.status_code}")
                logger.info(f"Response body: {response.text}")

                # Handle API response
                if response.status_code == 201:
                    QMessageBox.information(self, "Success", "Ticket created successfully!")
                    self.clear_fields()
                else:
                    error_message = response.json().get("message", response.text)
                    logger.error(f"API returned an error: {error_message}")
                    QMessageBox.critical(self, "Error", f"Failed to create ticket: {error_message}")
            except Exception as request_error:
                logger.error(f"Error making API request: {request_error}")
                QMessageBox.critical(self, "Error", f"Failed to communicate with Freshdesk: {request_error}")
            finally:
                # Cleanup embedded images and file handles
                for file_path in self.embedded_images:
                    try:
                        os.remove(file_path)
                    except Exception:
                        pass
                for _, (_, file_handle) in files:
                    try:
                        file_handle.close()
                    except Exception:
                        pass
        except Exception as general_error:
            logger.critical(f"Unexpected error in send_ticket(): {general_error}")
            QMessageBox.critical(self, "Critical Error", f"An unexpected error occurred:\n{general_error}")

if __name__ == "__main__":
    import traceback

    app = QApplication(sys.argv)

    try:
        # Load credentials using DPAPI
        url, api_key = load_credentials()

        if url and api_key:
            config = {
                "api_url": url,
                "api_key": api_key
            }

            logger.info(f"Configuration loaded: {config}")
        else:
            logger.critical("Failed to retrieve Freshdesk credentials. Exiting.")
            QMessageBox.critical(None, "Error", "Failed to load configuration. Please check your setup.")
            sys.exit(1)

        # Show splash screen
        splash_logo_path = resource_path("assets\\splash_logo.png")
        print("Resolved splash logo path:", splash_logo_path)  # Debugging line to verify path
        splash_pix = QPixmap(splash_logo_path)

        if splash_pix.isNull():
            logger.error(f"Failed to load splash logo: {splash_logo_path}")

        splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
        splash.setWindowFlag(Qt.FramelessWindowHint)
        splash.show()

        # Launch the main window
        try:
            window = TicketCreator(config)
            logger.info("Main window initialized successfully.")
        except Exception as e:
            logger.critical(f"Failed to initialize TicketCreator: {e}")
            error_details = traceback.format_exc()
            QMessageBox.critical(None, "Critical Error", f"An error occurred while initializing the application:\n\n{error_details}")
            sys.exit(1)

        splash.finish(window)  # Finish the splash, but do not call window.show()

    except Exception as e:
        # Log and display any unexpected errors
        error_details = traceback.format_exc()
        logger.critical(f"Unexpected error during application startup: {error_details}")
        QMessageBox.critical(None, "Critical Error", f"An unexpected error occurred:\n\n{error_details}")
        sys.exit(1)

    # Start the app
    try:
        sys.exit(app.exec_())
    except Exception as e:
        error_details = traceback.format_exc()
        logger.critical(f"Runtime error: {error_details}")
        QMessageBox.critical(None, "Critical Error", f"A fatal error occurred during app execution:\n\n{error_details}")
        sys.exit(1)

