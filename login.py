# login.py
"""
User Login Window
Handles authentication and registration
"""

import logging
import re
import traceback
import tkinter as tk
from tkinter import messagebox, ttk

from config import *
from database import UserOperations

logger = logging.getLogger(__name__)


class LoginWindow(tk.Tk):
    """Login window class"""

    def __init__(self):
        super().__init__()

        self.password_entry = None
        self.username_entry = None
        self.title(f"{APP_TITLE} - Login")
        self.geometry("520x430")
        self.resizable(False, False)
        self.config(bg=COLOR_PRIMARY)
        self.report_callback_exception = self._handle_exception

        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

        self.user_data = None
        self.create_widgets()

    def _handle_exception(self, exc_type, exc_value, exc_traceback):
        """Show a friendly crash prompt for unexpected UI errors."""
        logger.error("Unhandled UI error", exc_info=(exc_type, exc_value, exc_traceback))
        messagebox.showerror(
            "Unexpected Error",
            "Something went wrong while using the app.\n\n"
            f"{exc_value}\n\nPlease try again."
        )

    def create_widgets(self):
        """Create login UI elements"""
        shell = tk.Frame(self, bg=COLOR_PRIMARY)
        shell.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        hero = tk.Frame(shell, bg=COLOR_PRIMARY)
        hero.pack(fill=tk.X, pady=(0, 14))

        tk.Label(
            hero,
            text=APP_TITLE,
            font=("Arial", 20, "bold"),
            fg=COLOR_LIGHT,
            bg=COLOR_PRIMARY
        ).pack(anchor=tk.W)

        tk.Label(
            hero,
            text="Sign in or create a student/lecturer account",
            font=FONT_NORMAL,
            fg="#c9d8e8",
            bg=COLOR_PRIMARY
        ).pack(anchor=tk.W, pady=(4, 0))

        card = tk.Frame(shell, bg=COLOR_LIGHT, highlightbackground="#d6dee8", highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            card,
            text="Welcome back",
            font=FONT_TITLE,
            fg=COLOR_PRIMARY,
            bg=COLOR_LIGHT
        ).pack(anchor=tk.W, padx=22, pady=(20, 4))

        tk.Label(
            card,
            text="Log in to continue",
            font=FONT_NORMAL,
            fg=COLOR_SECONDARY,
            bg=COLOR_LIGHT
        ).pack(anchor=tk.W, padx=22, pady=(0, 16))

        form = tk.Frame(card, bg=COLOR_LIGHT)
        form.pack(fill=tk.BOTH, expand=True, padx=22, pady=(0, 18))

        tk.Label(form, text="Username", font=FONT_NORMAL, bg=COLOR_LIGHT, fg=COLOR_TEXT).pack(anchor=tk.W)
        self.username_entry = tk.Entry(form, font=FONT_NORMAL, relief=tk.FLAT, highlightthickness=1,
                                       highlightbackground="#cfd8e3", highlightcolor=COLOR_SECONDARY)
        self.username_entry.pack(fill=tk.X, pady=(4, 12), ipady=6)
        self.username_entry.bind("<Return>", lambda e: self.login())

        tk.Label(form, text="Password", font=FONT_NORMAL, bg=COLOR_LIGHT, fg=COLOR_TEXT).pack(anchor=tk.W)
        self.password_entry = tk.Entry(
            form,
            font=FONT_NORMAL,
            show="●",
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground="#cfd8e3",
            highlightcolor=COLOR_SECONDARY
        )
        self.password_entry.pack(fill=tk.X, pady=(4, 16), ipady=6)
        self.password_entry.bind("<Return>", lambda e: self.login())

        button_row = tk.Frame(form, bg=COLOR_LIGHT)
        button_row.pack(fill=tk.X, pady=(4, 8))

        tk.Button(
            button_row,
            text="Login",
            font=FONT_NORMAL,
            bg=COLOR_SECONDARY,
            fg="white",
            command=self.login,
            cursor="hand2",
            relief=tk.FLAT,
            padx=14,
            pady=6
        ).pack(side=tk.LEFT)

        tk.Button(
            button_row,
            text="Register",
            font=FONT_NORMAL,
            bg=COLOR_SUCCESS,
            fg="white",
            command=self.open_registration,
            cursor="hand2",
            relief=tk.FLAT,
            padx=14,
            pady=6
        ).pack(side=tk.LEFT, padx=8)

        tk.Button(
            button_row,
            text="Clear",
            font=FONT_NORMAL,
            bg=COLOR_WARNING,
            fg="white",
            command=self.clear_fields,
            cursor="hand2",
            relief=tk.FLAT,
            padx=14,
            pady=6
        ).pack(side=tk.LEFT)

        tk.Label(
            form,
            text="New students and lecturers can create accounts here.",
            font=FONT_SMALL,
            fg="#6f7f91",
            bg=COLOR_LIGHT
        ).pack(anchor=tk.W, pady=(10, 0))

    def login(self):
        """Validate login credentials"""
        try:
            username = self.username_entry.get().strip()
            password = self.password_entry.get()

            if not username or not password:
                messagebox.showerror("Validation Error", MSG_FILL_FIELDS)
                return

            success, user_data = UserOperations.validate_login(username, password)

            if success:
                self.user_data = user_data
                messagebox.showinfo("Success", f"Welcome, {user_data['username']}!")
                self.destroy()
            else:
                messagebox.showerror("Login Failed", "We couldn't verify that username and password.")
                self.password_entry.delete(0, tk.END)
        except Exception as exc:
            self._handle_runtime_error("login", exc)

    def open_registration(self):
        """Open registration window."""
        RegistrationWindow(self)

    def clear_fields(self):
        """Clear input fields"""
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.username_entry.focus()

    def get_user_data(self):
        """Get authenticated user data"""
        return self.user_data

    def _handle_runtime_error(self, action, exc):
        logger.exception("Login window %s failed", action)
        messagebox.showerror(
            "Error",
            f"Something went wrong while trying to {action}.\n\n{exc}"
        )


class RegistrationWindow(tk.Toplevel):
    """Account registration window"""

    def __init__(self, parent):
        super().__init__(parent)
        self.title(f"{APP_TITLE} - Register")
        self.geometry("540x560")
        self.resizable(False, False)
        self.config(bg=COLOR_PRIMARY)
        self.report_callback_exception = self._handle_exception
        self.parent = parent

        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

        self._build_ui()

    def _handle_exception(self, exc_type, exc_value, exc_traceback):
        logger.error("Unhandled registration error", exc_info=(exc_type, exc_value, exc_traceback))
        messagebox.showerror(
            "Unexpected Error",
            "Registration could not be completed.\n\n"
            f"{exc_value}\n\nPlease try again."
        )

    def _build_ui(self):
        shell = tk.Frame(self, bg=COLOR_PRIMARY)
        shell.pack(fill=tk.BOTH, expand=True, padx=18, pady=18)

        tk.Label(
            shell,
            text="Create Account",
            font=("Arial", 20, "bold"),
            fg=COLOR_LIGHT,
            bg=COLOR_PRIMARY
        ).pack(anchor=tk.W)

        tk.Label(
            shell,
            text="Register as a student or lecturer",
            font=FONT_NORMAL,
            fg="#c9d8e8",
            bg=COLOR_PRIMARY
        ).pack(anchor=tk.W, pady=(4, 14))

        card = tk.Frame(shell, bg=COLOR_LIGHT, highlightbackground="#d6dee8", highlightthickness=1)
        card.pack(fill=tk.BOTH, expand=True)

        form = tk.Frame(card, bg=COLOR_LIGHT)
        form.pack(fill=tk.BOTH, expand=True, padx=22, pady=22)

        self.entries = {}
        fields = [
            ("Username", "username"),
            ("Email", "email"),
            ("Password", "password"),
            ("Confirm Password", "confirm_password"),
        ]

        for label_text, key in fields:
            tk.Label(form, text=label_text, font=FONT_NORMAL, bg=COLOR_LIGHT, fg=COLOR_TEXT).pack(anchor=tk.W)
            entry = tk.Entry(
                form,
                font=FONT_NORMAL,
                show="●" if "password" in key else "",
                relief=tk.FLAT,
                highlightthickness=1,
                highlightbackground="#cfd8e3",
                highlightcolor=COLOR_SECONDARY
            )
            entry.pack(fill=tk.X, pady=(4, 12), ipady=6)
            self.entries[key] = entry

        tk.Label(form, text="Account Type", font=FONT_NORMAL, bg=COLOR_LIGHT, fg=COLOR_TEXT).pack(anchor=tk.W)
        self.role_combo = ttk.Combobox(form, font=FONT_NORMAL, state="readonly")
        self.role_combo["values"] = (ROLE_STUDENT, ROLE_LECTURER)
        self.role_combo.pack(fill=tk.X, pady=(4, 16))

        button_row = tk.Frame(form, bg=COLOR_LIGHT)
        button_row.pack(fill=tk.X)

        tk.Button(
            button_row,
            text="Create Account",
            font=FONT_NORMAL,
            bg=COLOR_SUCCESS,
            fg="white",
            command=self.register_account,
            cursor="hand2",
            relief=tk.FLAT,
            padx=14,
            pady=6
        ).pack(side=tk.LEFT)

        tk.Button(
            button_row,
            text="Cancel",
            font=FONT_NORMAL,
            bg=COLOR_DANGER,
            fg="white",
            command=self.destroy,
            cursor="hand2",
            relief=tk.FLAT,
            padx=14,
            pady=6
        ).pack(side=tk.LEFT, padx=8)

    def register_account(self):
        """Create a new student or lecturer account."""
        try:
            username = self.entries["username"].get().strip()
            email = self.entries["email"].get().strip()
            password = self.entries["password"].get()
            confirm_password = self.entries["confirm_password"].get()
            role_name = self.role_combo.get().strip()

            if not all([username, email, password, confirm_password, role_name]):
                messagebox.showerror("Validation Error", MSG_FILL_FIELDS)
                return

            if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                messagebox.showerror("Validation Error", MSG_INVALID_EMAIL)
                return

            if len(password) < 6:
                messagebox.showerror("Validation Error", MSG_INVALID_PASSWORD)
                return

            if password != confirm_password:
                messagebox.showerror("Validation Error", "Passwords do not match.")
                return

            success, result = UserOperations.register_account(username, email, password, role_name)
            if success:
                messagebox.showinfo(
                    "Success",
                    f"Account created for {role_name.lower()} '{username}'. You can log in now."
                )
                self.destroy()
            else:
                messagebox.showerror("Registration Failed", result)
        except Exception as exc:
            logger.exception("Registration failed")
            messagebox.showerror(
                "Registration Error",
                f"We couldn't create the account.\n\n{exc}"
            )


if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()
    if app.user_data:
        print(f"Logged in as: {app.user_data['username']}")
