"""Reports module."""

import tkinter as tk
from tkinter import ttk

from config import *
from database import DatabaseConnection


class ReportOperations:
    @staticmethod
    def get_counts():
        query = """
            SELECT 'Departments' AS name, COUNT(*)::int AS total FROM departments
            UNION ALL
            SELECT 'Students' AS name, COUNT(*)::int AS total FROM students
            UNION ALL
            SELECT 'Lecturers' AS name, COUNT(*)::int AS total FROM lecturers
            UNION ALL
            SELECT 'Courses' AS name, COUNT(*)::int AS total FROM courses
            UNION ALL
            SELECT 'Enrollments' AS name, COUNT(*)::int AS total FROM enrollments
            UNION ALL
            SELECT 'Grades' AS name, COUNT(*)::int AS total FROM grades
            UNION ALL
            SELECT 'Payments' AS name, COUNT(*)::int AS total FROM payments
            ORDER BY name
        """
        return DatabaseConnection.execute_query(query)


class ReportWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Reports")
        self.geometry("500x400")
        self.config(bg=COLOR_LIGHT)
        self.create_widgets()
        self.load_counts()

    def create_widgets(self):
        title = tk.Label(self, text="System Summary", font=FONT_TITLE, bg=COLOR_LIGHT, fg=COLOR_PRIMARY)
        title.pack(pady=20)

        frame = tk.Frame(self, bg=COLOR_LIGHT)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        self.tree = ttk.Treeview(frame, columns=("Module", "Total"), show="headings", height=12)
        self.tree.heading("Module", text="Module")
        self.tree.heading("Total", text="Total")
        self.tree.column("Module", width=250, anchor=tk.W)
        self.tree.column("Total", width=100, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def load_counts(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in ReportOperations.get_counts():
            self.tree.insert("", tk.END, values=row)