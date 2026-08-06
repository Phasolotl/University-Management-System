# main.py
"""
University Management System - Main Application
Entry point for the application
"""

import logging
import tkinter as tk
from tkinter import messagebox
from login import LoginWindow
from routes.dashboard import DashboardFrame
from routes.department import DepartmentManagementWindow
from routes.student import StudentManagementWindow
from routes.lecturer import LecturerManagementWindow
from routes.course import CourseManagementWindow
from routes.enrollment import EnrollmentManagementWindow
from routes.grade import GradeManagementWindow
from routes.payment import PaymentManagementWindow
from routes.report import ReportWindow
from config import *

logger = logging.getLogger(__name__)


class MainApplication(tk.Tk):
    """Main application class"""

    def __init__(self, user_data):
        super().__init__()

        self.user_data = user_data
        self.title(f"{APP_TITLE} - {user_data['username']}")
        self.geometry("1280x780")
        self.minsize(1180, 700)
        self.config(bg=COLOR_PRIMARY)
        self.report_callback_exception = self._handle_exception

        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

        self.current_frame = None
        self.create_menu()
        self.show_dashboard()

    def _handle_exception(self, exc_type, exc_value, exc_traceback):
        logger.error("Unhandled app error", exc_info=(exc_type, exc_value, exc_traceback))
        messagebox.showerror(
            "Unexpected Error",
            "The app hit a problem.\n\n"
            f"{exc_value}\n\nPlease try again or reopen the screen."
        )

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
        mgmt_menu.add_command(label="Departments", command=self.open_department_management)
        mgmt_menu.add_command(label="Students", command=self.open_student_management)
        mgmt_menu.add_command(label="Lecturers", command=self.open_lecturer_management)
        mgmt_menu.add_command(label="Courses", command=self.open_course_management)
        mgmt_menu.add_command(label="Enrollments", command=self.open_enrollment_management)

        # Academic Menu
        academic_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Academic", menu=academic_menu)
        academic_menu.add_command(label="Grades", command=self.open_grade_management)
        academic_menu.add_command(label="Payments", command=self.open_payment_management)
        academic_menu.add_command(label="Reports", command=self.open_reports)

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
        self.current_frame = DashboardFrame(self, self.user_data, self)
        self.current_frame.pack(fill=tk.BOTH, expand=True)

    def _open_window(self, creator, title):
        try:
            creator()
        except Exception as exc:
            logger.exception("Failed to open %s", title)
            messagebox.showerror(
                "Unable to Open Module",
                f"We couldn't open {title}.\n\n{exc}"
            )

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

    def open_student_management(self):
        """Open student management window"""
        self._open_window(lambda: StudentManagementWindow(self), "Students")

    def open_department_management(self):
        """Open department management window"""
        self._open_window(lambda: DepartmentManagementWindow(self), "Departments")

    def open_lecturer_management(self):
        """Open lecturer management window"""
        self._open_window(lambda: LecturerManagementWindow(self), "Lecturers")

    def open_course_management(self):
        """Open course management window"""
        self._open_window(lambda: CourseManagementWindow(self), "Courses")

    def open_enrollment_management(self):
        """Open enrollment management window"""
        self._open_window(lambda: EnrollmentManagementWindow(self), "Enrollments")

    def open_grade_management(self):
        """Open grade management window"""
        self._open_window(lambda: GradeManagementWindow(self), "Grades")

    def open_payment_management(self):
        """Open payment management window"""
        self._open_window(lambda: PaymentManagementWindow(self), "Payments")

    def open_reports(self):
        """Open reports window"""
        self._open_window(lambda: ReportWindow(self), "Reports")

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
    try:
        login = LoginWindow()
        login.mainloop()

        if login.user_data:
            app = MainApplication(login.user_data)
            app.mainloop()
        else:
            messagebox.showinfo("Exit", "Thank you for using University Management System!")
    except Exception as exc:
        logger.exception("Application startup failed")
        messagebox.showerror(
            "Startup Error",
            f"The app could not start correctly.\n\n{exc}"
        )


if __name__ == "__main__":
    start_application()