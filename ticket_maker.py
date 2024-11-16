import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QWidget, QMessageBox, QFileDialog
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl
import requests
import base64
import re

# Load config file
config_path = "config.json"
if os.path.exists(config_path):
    with open(config_path, "r") as config_file:
        config = json.load(config_file)
        url = config.get("url")
        api_key = config.get("api_key")
else:
    print("Configuration file not found.")
    sys.exit(1)

class TicketCreator(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TicketMaker")
        self.setGeometry(100, 100, 800, 850)

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
        self.editor.setUrl(QUrl.fromLocalFile(os.path.abspath("editor.html")))
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(self.editor)

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
        self.submit_button.setFixedHeight(50)  # Adjust the height
        self.submit_button.clicked.connect(self.create_ticket)
        layout.addWidget(self.submit_button)

        self.clear_button = QPushButton("Clear Fields")
        self.clear_button.clicked.connect(self.clear_fields)
        layout.addWidget(self.clear_button)

        # Set layout
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def add_attachments(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Attachments")
        if files:
            self.attachments.extend(files)
            self.attachment_label.setText(f"{len(self.attachments)} attachment(s) added")

    def get_description_content(self):
        # Fetch HTML content from the editor
        self.editor.page().runJavaScript("getContent()", self.handle_description_content)

    def handle_description_content(self, description):
        # Extract and handle embedded images
        self.description = description
        self.embedded_images = self.extract_embedded_images(description)
        self.send_ticket()

    def extract_embedded_images(self, description):
        # Find base64-encoded images in the HTML content
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
            "email": email,
            "subject": subject,
            "description": description,
            "priority": priority_mapping.get(priority, 1),
            "status": status_mapping.get(status, 2)
        }

        try:
            # Handle embedded images as attachments
            files = [("attachments[]", (os.path.basename(f), open(f, "rb"))) for f in self.attachments]
            files.extend([("attachments[]", (os.path.basename(f), open(f, "rb"))) for f in self.embedded_images])

            # Send multipart/form-data if there are attachments
            if files:
                response = requests.post(
                    f"{url}/api/v2/tickets",
                    data=data,
                    files=files,
                    auth=(api_key, "X")
                )
                for _, f in files:
                    f[1].close()  # Close files after sending

                # Clean up temporary embedded image files
                for file_path in self.embedded_images:
                    if os.path.exists(file_path):
                        os.remove(file_path)
            else:
                # Send as JSON if no attachments
                headers = {"Content-Type": "application/json"}
                response = requests.post(
                    f"{url}/api/v2/tickets",
                    headers=headers,
                    json=data,
                    auth=(api_key, "X")
                )

            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Ticket created successfully!")
                self.clear_fields()  # Clear fields after success
            else:
                QMessageBox.critical(
                    self, "Error",
                    f"Failed to create ticket. Status code: {response.status_code}\nResponse: {response.text}"
                )
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TicketCreator()
    window.show()
    sys.exit(app.exec_())
