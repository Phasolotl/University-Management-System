# main.py
"""
University Management System - Main Application
Entry point for the application
"""

import tkinter as tk
from tkinter import messagebox
from login import LoginWindow
from config import *


class MainApplication(tk.Tk):
    """Main application class"""

    def __init__(self, user_data):
        super().__init__()

        self.user_data = user_data
        self.title(f"{APP_TITLE} - {user_data['username']}")
        self.geometry("1000x600")
        self.config(bg=COLOR_PRIMARY)

        # Center window
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

        self.current_frame = None
        self.create_menu()
        self.show_dashboard()

    def create_menu(self):
        """Create application menu"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Dashboard", command=self.show_dashboard)
        file_menu.add_separator()
        file_menu.add_command(label="Change Password", command=self.change_password)
        file_menu.add_command(label="Logout", command=self.logout)
        file_menu.add_command(label="Exit", command=self.exit_app)

        # Management Menu
        mgmt_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Management", menu=mgmt_menu)
        mgmt_menu.add_command(label="Departments", command=lambda: self.show_placeholder("Department Management"))
        mgmt_menu.add_command(label="Students", command=lambda: self.show_placeholder("Student Management"))
        mgmt_menu.add_command(label="Lecturers", command=lambda: self.show_placeholder("Lecturer Management"))
        mgmt_menu.add_command(label="Courses", command=lambda: self.show_placeholder("Course Management"))
        mgmt_menu.add_command(label="Enrollments", command=lambda: self.show_placeholder("Enrollment Management"))

        # Academic Menu
        academic_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Academic", menu=academic_menu)
        academic_menu.add_command(label="Grades", command=lambda: self.show_placeholder("Grade Management"))
        academic_menu.add_command(label="Payments", command=lambda: self.show_placeholder("Payment Management"))
        academic_menu.add_command(label="Reports", command=lambda: self.show_placeholder("Reports"))

        # Tools Menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Database Backup", command=lambda: self.show_placeholder("Database Backup"))

        # Help Menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def show_dashboard(self):
        """Show dashboard"""
        self.clear_frame()
        frame = tk.Frame(self, bg=COLOR_LIGHT)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        title = tk.Label(
            frame,
            text="Dashboard",
            font=FONT_TITLE,
            fg=COLOR_PRIMARY,
            bg=COLOR_LIGHT
        )
        title.pack(pady=20)

        welcome = tk.Label(
            frame,
            text=f"Welcome, {self.user_data['username']}!",
            font=FONT_SUBTITLE,
            fg=COLOR_TEXT,
            bg=COLOR_LIGHT
        )
        welcome.pack(pady=10)

        role = tk.Label(
            frame,
            text=f"Role: {self.user_data['role']}",
            font=FONT_NORMAL,
            fg=COLOR_SECONDARY,
            bg=COLOR_LIGHT
        )
        role.pack()

        info = tk.Label(
            frame,
            text="Use the menu above to navigate through different modules.",
            font=FONT_SMALL,
            fg=COLOR_TEXT,
            bg=COLOR_LIGHT
        )
        info.pack(pady=30)

        self.current_frame = frame

    def show_placeholder(self, title):
        """Show placeholder for modules"""
        self.clear_frame()
        frame = tk.Frame(self, bg=COLOR_LIGHT)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        label = tk.Label(
            frame,
            text=f"{title}",
            font=FONT_TITLE,
            fg=COLOR_PRIMARY,
            bg=COLOR_LIGHT
        )
        label.pack(pady=20)

        message = tk.Label(
            frame,
            text="Coming Soon...",
            font=FONT_SUBTITLE,
            fg=COLOR_WARNING,
            bg=COLOR_LIGHT
        )
        message.pack()

        self.current_frame = frame

    def change_password(self):
        """Change password dialog"""
        messagebox.showinfo("Change Password", "Feature coming soon!")

    def show_about(self):
        """Show about dialog"""
        about_text = f"{APP_TITLE}\nVersion {APP_VERSION}\n\nA comprehensive university management system built with Python and PostgreSQL."
        messagebox.showinfo("About", about_text)

    def logout(self):
        """Logout user"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.destroy()
            start_application()

    def exit_app(self):
        """Exit application"""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.destroy()

    def clear_frame(self):
        """Clear current frame"""
        if self.current_frame:
            self.current_frame.destroy()


def start_application():
    """Start the application"""
    login = LoginWindow()
    login.mainloop()

    if login.user_data:
        app = MainApplication(login.user_data)
        app.mainloop()
    else:
        messagebox.showinfo("Exit", "Thank you for using University Management System!")


if __name__ == "__main__":
    start_application()