# login.py
"""
User Login Window
Handles authentication
"""

import tkinter as tk
from tkinter import messagebox, ttk
import re
from config import *
from database import UserOperations


class LoginWindow(tk.Tk):
    """Login window class"""

    def __init__(self):
        super().__init__()

        self.password_entry = None
        self.username_entry = None
        self.title("University Management System - Login")
        self.geometry("400x350")
        self.resizable(False, False)
        self.config(bg=COLOR_PRIMARY)

        # Center window on screen
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

        self.user_data = None
        self.create_widgets()

    def create_widgets(self):
        """Create login UI elements"""

        # Title Frame
        title_frame = tk.Frame(self, bg=COLOR_PRIMARY)
        title_frame.pack(pady=20)

        title_label = tk.Label(
            title_frame,
            text=APP_TITLE,
            font=FONT_TITLE,
            fg=COLOR_LIGHT,
            bg=COLOR_PRIMARY
        )
        title_label.pack()

        subtitle_label = tk.Label(
            title_frame,
            text="Login to Your Account",
            font=FONT_NORMAL,
            fg=COLOR_SECONDARY,
            bg=COLOR_PRIMARY
        )
        subtitle_label.pack()

        # Main Form Frame
        form_frame = tk.Frame(self, bg=COLOR_LIGHT)
        form_frame.pack(padx=30, pady=20, fill=tk.BOTH, expand=True)

        # Username
        username_label = tk.Label(
            form_frame,
            text="Username:",
            font=FONT_NORMAL,
            fg=COLOR_TEXT,
            bg=COLOR_LIGHT
        )
        username_label.pack(anchor=tk.W, pady=(0, 5))

        self.username_entry = tk.Entry(form_frame, font=FONT_NORMAL, width=30)
        self.username_entry.pack(pady=(0, 15), fill=tk.X)
        self.username_entry.bind('<Return>', lambda e: self.login())

        # Password
        password_label = tk.Label(
            form_frame,
            text="Password:",
            font=FONT_NORMAL,
            fg=COLOR_TEXT,
            bg=COLOR_LIGHT
        )
        password_label.pack(anchor=tk.W, pady=(0, 5))

        self.password_entry = tk.Entry(
            form_frame,
            font=FONT_NORMAL,
            width=30,
            show="●"
        )
        self.password_entry.pack(pady=(0, 20), fill=tk.X)
        self.password_entry.bind('<Return>', lambda e: self.login())

        # Buttons Frame
        button_frame = tk.Frame(form_frame, bg=COLOR_LIGHT)
        button_frame.pack(fill=tk.X)

        login_btn = tk.Button(
            button_frame,
            text="Login",
            font=FONT_NORMAL,
            bg=COLOR_SECONDARY,
            fg="white",
            command=self.login,
            cursor="hand2",
            width=12
        )
        login_btn.pack(side=tk.LEFT, padx=5)

        clear_btn = tk.Button(
            button_frame,
            text="Clear",
            font=FONT_NORMAL,
            bg=COLOR_WARNING,
            fg="white",
            command=self.clear_fields,
            cursor="hand2",
            width=12
        )
        clear_btn.pack(side=tk.LEFT, padx=5)

    def login(self):
        """Validate login credentials"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        # Validation
        if not username or not password:
            messagebox.showerror("Validation Error", MSG_FILL_FIELDS)
            return

        # Authenticate
        success, user_data = UserOperations.validate_login(username, password)

        if success:
            self.user_data = user_data
            messagebox.showinfo("Success", f"Welcome, {user_data['username']}!")
            self.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password!")
            self.password_entry.delete(0, tk.END)

    def clear_fields(self):
        """Clear input fields"""
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.username_entry.focus()

    def get_user_data(self):
        """Get authenticated user data"""
        return self.user_data


if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()
    if app.user_data:
        print(f"Logged in as: {app.user_data['username']}")