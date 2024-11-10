import tkinter as tk
from tkinter import messagebox
from freshdesk.api import API

#========================== 
# Initialize Freshdesk API
#==========================
domain = 'yourcompany.freshdesk.com'  # Replace with your Freshdesk domain
api_key = 'your_api_key'  # Replace with your Freshdesk API key
freshdesk = API(domain, api_key)

# Function to submit ticket
def submit_ticket():
    # Get input values
    subject = subject_entry.get()
    description = description_text.get("1.0", tk.END).strip()
    email = email_entry.get()
    priority = priority_entry.get()
    status = status_entry.get()

    # Validation
    if not subject or not description or not email:
        messagebox.showwarning("Input Error", "Subject, Description, and Email are required fields.")
        return

    try:
        #===========================================
        #  Create the ticket using python-freshdesk
        #===========================================
        ticket = freshdesk.tickets.create_ticket(
            subject=subject,
            description=description,
            email=email,
            priority=int(priority),
            status=int(status)
        )
        messagebox.showinfo("Success", f"Ticket created successfully with ID: {ticket.id}")
        clear_fields()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create ticket: {str(e)}")

# Function to clear fields
def clear_fields():
    subject_entry.delete(0, tk.END)
    description_text.delete("1.0", tk.END)
    email_entry.delete(0, tk.END)
    priority_entry.delete(0, tk.END)
    status_entry.delete(0, tk.END)

# Create GUI
root = tk.Tk()
root.title("Ticketmaker - Ticket Submission Tool")

# Subject
tk.Label(root, text="Subject:").grid(row=0, column=0, sticky="e")
subject_entry = tk.Entry(root, width=50)
subject_entry.grid(row=0, column=1, padx=10, pady=5)

# Description
tk.Label(root, text="Description:").grid(row=1, column=0, sticky="ne")
description_text = tk.Text(root, width=50, height=10)
description_text.grid(row=1, column=1, padx=10, pady=5)

# Email
tk.Label(root, text="Email:").grid(row=2, column=0, sticky="e")
email_entry = tk.Entry(root, width=50)
email_entry.grid(row=2, column=1, padx=10, pady=5)

# Priority
tk.Label(root, text="Priority (1-4):").grid(row=3, column=0, sticky="e")
priority_entry = tk.Entry(root, width=50)
priority_entry.grid(row=3, column=1, padx=10, pady=5)

# Status
tk.Label(root, text="Status (2-5):").grid(row=4, column=0, sticky="e")
status_entry = tk.Entry(root, width=50)
status_entry.grid(row=4, column=1, padx=10, pady=5)

# Submit button
submit_button = tk.Button(root, text="Submit Ticket", command=submit_ticket)
submit_button.grid(row=5, column=1, pady=20)

root.mainloop()
