"""Modern dashboard module."""

import tkinter as tk

from config import *
from database import DatabaseConnection


class DashboardOperations:
    @staticmethod
    def get_counts():
        query = """
            SELECT 'Departments' AS name, COUNT(*)::int AS total FROM departments
            UNION ALL SELECT 'Students' AS name, COUNT(*)::int AS total FROM students
            UNION ALL SELECT 'Lecturers' AS name, COUNT(*)::int AS total FROM lecturers
            UNION ALL SELECT 'Courses' AS name, COUNT(*)::int AS total FROM courses
            UNION ALL SELECT 'Enrollments' AS name, COUNT(*)::int AS total FROM enrollments
            UNION ALL SELECT 'Grades' AS name, COUNT(*)::int AS total FROM grades
            UNION ALL SELECT 'Payments' AS name, COUNT(*)::int AS total FROM payments
            ORDER BY name
        """
        return {name: total for name, total in DatabaseConnection.execute_query(query)}


class DashboardFrame(tk.Frame):
    def __init__(self, parent, user_data, app):
        super().__init__(parent, bg=COLOR_LIGHT)
        self.user_data = user_data
        self.app = app
        self.counts = DashboardOperations.get_counts()
        self._build_ui()

    def _build_ui(self):
        header = tk.Frame(self, bg=COLOR_PRIMARY, height=120)
        header.pack(fill=tk.X, padx=12, pady=(12, 8))
        header.pack_propagate(False)

        tk.Label(
            header,
            text=f"Welcome back, {self.user_data['username']}",
            font=("Arial", 20, "bold"),
            fg="white",
            bg=COLOR_PRIMARY
        ).pack(anchor=tk.W, padx=20, pady=(18, 0))
        tk.Label(
            header,
            text=f"Role: {self.user_data['role']}  •  University Management System",
            font=FONT_NORMAL,
            fg="#d7e3f0",
            bg=COLOR_PRIMARY
        ).pack(anchor=tk.W, padx=20, pady=(6, 0))

        stats = tk.Frame(self, bg=COLOR_LIGHT)
        stats.pack(fill=tk.X, padx=12, pady=(0, 8))
        stats_data = [
            ("Departments", self.counts.get("Departments", 0), "#2ecc71"),
            ("Students", self.counts.get("Students", 0), "#3498db"),
            ("Lecturers", self.counts.get("Lecturers", 0), "#9b59b6"),
            ("Courses", self.counts.get("Courses", 0), "#f39c12"),
        ]
        for i, (label, value, color) in enumerate(stats_data):
            card = self._stat_card(stats, label, value, color)
            card.grid(row=0, column=i, padx=6, sticky="nsew")
            stats.grid_columnconfigure(i, weight=1)

        tk.Label(
            self,
            text="Module Hub",
            font=FONT_SUBTITLE,
            fg=COLOR_PRIMARY,
            bg=COLOR_LIGHT
        ).pack(anchor=tk.W, padx=16, pady=(8, 6))

        hub = tk.Frame(self, bg=COLOR_LIGHT)
        hub.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 12))

        modules = [
            ("Departments", "Manage academic departments", "#1abc9c", self.app.open_department_management),
            ("Students", "Track student records", "#3498db", self.app.open_student_management),
            ("Lecturers", "Manage lecturer profiles", "#9b59b6", self.app.open_lecturer_management),
            ("Courses", "Organize course catalog", "#f39c12", self.app.open_course_management),
            ("Enrollments", "Register students into courses", "#e67e22", self.app.open_enrollment_management),
            ("Grades", "Record assessments", "#e74c3c", self.app.open_grade_management),
            ("Payments", "Handle tuition payments", "#16a085", self.app.open_payment_management),
            ("Reports", "View system summaries", "#34495e", self.app.open_reports),
        ]

        for index, (title, subtitle, color, action) in enumerate(modules):
            row = index // 4
            col = index % 4
            self._module_card(hub, title, subtitle, color, action).grid(
                row=row, column=col, padx=8, pady=8, sticky="nsew"
            )
            hub.grid_columnconfigure(col, weight=1)
        for row in range(2):
            hub.grid_rowconfigure(row, weight=1)

    def _stat_card(self, parent, title, value, color):
        frame = tk.Frame(parent, bg="white", highlightbackground="#dde6ef", highlightthickness=1)
        tk.Label(frame, text=title, font=FONT_NORMAL, fg=COLOR_TEXT, bg="white").pack(anchor=tk.W, padx=16, pady=(14, 0))
        tk.Label(frame, text=str(value), font=("Arial", 24, "bold"), fg=color, bg="white").pack(anchor=tk.W, padx=16, pady=(2, 14))
        return frame

    def _module_card(self, parent, title, subtitle, color, action):
        frame = tk.Frame(parent, bg="white", highlightbackground="#dde6ef", highlightthickness=1)
        tk.Frame(frame, bg=color, height=6).pack(fill=tk.X)
        body = tk.Frame(frame, bg="white")
        body.pack(fill=tk.BOTH, expand=True, padx=14, pady=14)
        tk.Label(body, text=title, font=FONT_SUBTITLE, fg=COLOR_TEXT, bg="white").pack(anchor=tk.W)
        tk.Label(body, text=subtitle, font=FONT_SMALL, fg="#66788a", bg="white", wraplength=180, justify=tk.LEFT).pack(anchor=tk.W, pady=(6, 14))
        tk.Button(body, text="Open", font=FONT_NORMAL, bg=color, fg="white", relief=tk.FLAT, command=action).pack(anchor=tk.W)
        return frame