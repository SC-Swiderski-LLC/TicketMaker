import tkinter as tk
from tkinter import messagebox
import winreg
from pathlib import Path
import sys

def save_to_registry(api_url, api_key):
    try:
        registry_path = r"Software\TicketMaker"
        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE, registry_path)
        winreg.SetValueEx(key, "URL", 0, winreg.REG_SZ, api_url)
        winreg.SetValueEx(key, "API_KEY", 0, winreg.REG_SZ, api_key)
        winreg.CloseKey(key)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to write to the registry: {e}")
        return False

def handle_cli_args():
    """Process CLI arguments for direct registry update."""
    if len(sys.argv) >= 3:
        api_url = sys.argv[1]
        api_key = sys.argv[2]

        if save_to_registry(api_url, api_key):
            print("API URL and Key saved successfully via CLI.")
        else:
            print("Failed to save API URL and Key via CLI.")
        sys.exit(0)

def submit():
    api_url = url_entry.get()
    api_key = key_entry.get()

    # Ensure placeholders are replaced with valid inputs
    if api_url == "https://yourcompany.freshdesk.com" or not api_url:
        messagebox.showwarning("Input Error", "Please enter a valid Freshdesk URL!")
        return
    if api_key == "Your Freshdesk API key" or not api_key:
        messagebox.showwarning("Input Error", "Please enter your Freshdesk API key!")
        return

    if save_to_registry(api_url, api_key):
        messagebox.showinfo("Success", "API URL and Key saved successfully!")
        root.destroy()

def set_placeholder(entry, placeholder_text):
    """Add placeholder text to an Entry widget."""
    entry.insert(0, placeholder_text)
    entry.config(fg="grey")

    def on_focus_in(event):
        if entry.get() == placeholder_text:
            entry.delete(0, "end")
            entry.config(fg="black")

    def on_focus_out(event):
        if not entry.get():
            set_placeholder(entry, placeholder_text)

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

# Handle CLI arguments for silent updates
handle_cli_args()

# Determine the path to the icon
if hasattr(sys, "_MEIPASS"):
    # Path inside the PyInstaller temp folder
    icon_path = Path(sys._MEIPASS) / "assets" / "icon.ico"
else:
    # Path during development
    icon_path = Path("assets/icon.ico")

# Interactive mode: show GUI
root = tk.Tk()
root.title("TicketMaker Configuration")

# Add the window icon
if icon_path.exists():
    root.iconbitmap(icon_path)
else:
    messagebox.showwarning("Warning", f"Icon file '{icon_path}' not found!")

instructions = (
    "Please enter your Freshdesk URL and API key below to complete the TicketMaker setup."
)
tk.Label(root, text=instructions, justify="left", wraplength=400, fg="blue").grid(row=0, column=0, columnspan=2, padx=10, pady=(10, 20))

# API URL
tk.Label(root, text="Freshdesk URL:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
url_entry = tk.Entry(root, width=40)
url_entry.grid(row=1, column=1, padx=10, pady=10)
set_placeholder(url_entry, "https://yourcompany.freshdesk.com")

# API Key
tk.Label(root, text="Freshdesk API Key:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
key_entry = tk.Entry(root, width=40)
key_entry.grid(row=2, column=1, padx=10, pady=10)
set_placeholder(key_entry, "Your Freshdesk API key")

# Submit button
submit_button = tk.Button(root, text="Save", command=submit)
submit_button.grid(row=3, column=0, columnspan=2, pady=(10, 20))

root.mainloop()
