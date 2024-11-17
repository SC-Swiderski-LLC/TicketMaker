import tkinter as tk
from tkinter import messagebox
import requests
import json
import os

# Load the config file
config_path = "config.json"

if os.path.exists(config_path):
    with open(config_path, "r") as config_file:
        config = json.load(config_file)
        url = config.get("url")
        api_key = config.get("api_key")
else:
    messagebox.showerror("Error", "Configuration file not found. Please set up the app correctly.")
    exit()

def create_ticket():
    subject = entry_subject.get()
    description = text_description.get("1.0", tk.END).strip()  # Fixed here
    email = entry_email.get()
    priority = priority_var.get()
    status = status_var.get()

    # Check if any field is empty
    if not subject or not description or not email or not priority or not status:
        messagebox.showerror("Error", "All fields are required.")
        return

    # Map dropdown values to API values
    priority_mapping = {"Low": 1, "Medium": 2, "High": 3, "Urgent": 4}
    status_mapping = {"Open": 2, "Pending": 3, "Resolved": 4, "Closed": 5}

    url # Updated to use config file variable
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "subject": subject,
        "description": description,
        "email": email,
        "priority": priority_mapping[priority],
        "status": status_mapping[status]
    }
    response = requests.post(url, headers=headers, json=data, auth=(api_key, "X")) # Updated to use config file variable
    if response.status_code == 201:
        messagebox.showinfo("Ticket Created", f"Ticket with subject '{subject}' created successfully!")
    else:
        messagebox.showerror("Error", f"Failed to create ticket: {response.status_code} {response.text}")

def clear_fields():
    entry_subject.delete(0, tk.END)
    text_description.delete("1.0", tk.END)
    entry_email.delete(0, tk.END)
    priority_var.set("")
    status_var.set("")

def create_and_clear():
    create_ticket()
    clear_fields()

# Create the main window
root = tk.Tk()
root.title("TicketMaker Lite")
root.geometry("600x400") # This sets the initial size of the window
root.iconbitmap("assets/icon.ico")  # Replace with the actual path to your icon file


# Configure the grid to expand with the window size
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(1, weight=1)

# Create and place the subject label and entry
label_subject = tk.Label(root, text="Subject")
label_subject.grid(row=0, column=0, padx=10, pady=10, sticky='w')
entry_subject = tk.Entry(root)
entry_subject.grid(row=0, column=1, padx=10, pady=10, sticky='ew')

# Create and place the description label and text box with scrollbar
label_description = tk.Label(root, text="Description")
label_description.grid(row=1, column=0, padx=10, pady=10, sticky="nw")
frame_description = tk.Frame(root)
frame_description.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
text_description = tk.Text(frame_description, wrap=tk.WORD, height=10, width=40)
scrollbar_description = tk.Scrollbar(frame_description, command=text_description.yview)
text_description.config(yscrollcommand=scrollbar_description.set)
scrollbar_description.pack(side=tk.RIGHT, fill=tk.Y)
text_description.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Create and place the email label and entry
label_email = tk.Label(root, text="Email")
label_email.grid(row=2, column=0, padx=10, pady=10, sticky='w')
entry_email = tk.Entry(root)
entry_email.grid(row=2, column=1, padx=10, pady=10, sticky='ew')

# Create and place the priority label and dropdown
label_priority = tk.Label(root, text="Priority")
label_priority.grid(row=3, column=0, padx=10, pady=10, sticky='w')
priority_var = tk.StringVar(value="Low") # Default to "Low"
priority_dropdown = tk.OptionMenu(root, priority_var, "Low", "Medium", "High", "Urgent")
priority_dropdown.grid(row=3, column=1, padx=10, pady=10, sticky='ew')

# Create and place the status label and dropdown
label_status = tk.Label(root, text="Status")
label_status.grid(row=4, column=0, padx=10, pady=10, sticky='w')
status_var = tk.StringVar(value="Open") # Modified code to default to "Open" status
status_dropdown = tk.OptionMenu(root, status_var, "Open", "Pending", "Resolved", "Closed")
status_dropdown.grid(row=4, column=1, padx=10, pady=10, sticky='ew')

# Create and place the clear button
button_clear = tk.Button(root, text="Clear Fields", command=clear_fields)
button_clear.grid(row=5, column=0, padx=10, pady=20, sticky='ew')

# Create and place the submit button
button_submit = tk.Button(root, text="Create Ticket", command=create_and_clear)
button_submit.grid(row=5, column=1, padx=10, pady=20, sticky='ew')

# Run the application
root.mainloop()
