"""Enrollment management module."""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

from config import *
from database import DatabaseConnection, logger


class EnrollmentOperations:
    @staticmethod
    def get_students():
        query = """
            SELECT s.student_id, u.username, u.email
            FROM students s
            JOIN users u ON s.user_id = u.user_id
            ORDER BY u.username
        """
        return DatabaseConnection.execute_query(query)

    @staticmethod
    def get_courses():
        query = """
            SELECT course_id, course_code, course_name
            FROM courses
            ORDER BY course_code
        """
        return DatabaseConnection.execute_query(query)

    @staticmethod
    def get_all_enrollments():
        query = """
            SELECT e.enrollment_id, u.username, c.course_code, c.course_name,
                   e.enrollment_date, e.status
            FROM enrollments e
            JOIN students s ON e.student_id = s.student_id
            JOIN users u ON s.user_id = u.user_id
            JOIN courses c ON e.course_id = c.course_id
            ORDER BY e.enrollment_id
        """
        return DatabaseConnection.execute_query(query)

    @staticmethod
    def search_enrollments(term):
        query = """
            SELECT e.enrollment_id, u.username, c.course_code, c.course_name,
                   e.enrollment_date, e.status
            FROM enrollments e
            JOIN students s ON e.student_id = s.student_id
            JOIN users u ON s.user_id = u.user_id
            JOIN courses c ON e.course_id = c.course_id
            WHERE u.username ILIKE %s
               OR c.course_code ILIKE %s
               OR c.course_name ILIKE %s
               OR e.status ILIKE %s
            ORDER BY e.enrollment_id
        """
        like = f"%{term}%"
        return DatabaseConnection.execute_query(query, (like, like, like, like))

    @staticmethod
    def get_enrollment_by_id(enrollment_id):
        query = """
            SELECT enrollment_id, student_id, course_id, enrollment_date, status
            FROM enrollments
            WHERE enrollment_id = %s
        """
        return DatabaseConnection.execute_fetchone(query, (enrollment_id,))

    @staticmethod
    def add_enrollment(student_id, course_id, enrollment_date, status):
        query = """
            INSERT INTO enrollments (student_id, course_id, enrollment_date, status)
            VALUES (%s, %s, %s, %s)
            RETURNING enrollment_id
        """
        conn = DatabaseConnection.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (student_id, course_id, enrollment_date, status))
            enrollment_id = cursor.fetchone()[0]
            conn.commit()
            logger.info("Enrollment added: %s", enrollment_id)
            return True, enrollment_id
        except Exception as exc:
            conn.rollback()
            logger.error("Add enrollment error: %s", exc)
            return False, str(exc)
        finally:
            cursor.close()

    @staticmethod
    def update_enrollment(enrollment_id, student_id, course_id, enrollment_date, status):
        query = """
            UPDATE enrollments
            SET student_id = %s,
                course_id = %s,
                enrollment_date = %s,
                status = %s
            WHERE enrollment_id = %s
        """
        try:
            DatabaseConnection.execute_update(
                query, (student_id, course_id, enrollment_date, status, enrollment_id)
            )
            return True, "Enrollment updated successfully"
        except Exception as exc:
            logger.error("Update enrollment error: %s", exc)
            return False, str(exc)

    @staticmethod
    def delete_enrollment(enrollment_id):
        try:
            DatabaseConnection.execute_update("DELETE FROM enrollments WHERE enrollment_id = %s", (enrollment_id,))
            return True, "Enrollment deleted successfully"
        except Exception as exc:
            logger.error("Delete enrollment error: %s", exc)
            return False, str(exc)


class EnrollmentManagementWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Enrollment Management")
        self.geometry("1000x600")
        self.config(bg=COLOR_LIGHT)
        self.parent = parent
        self.create_widgets()
        self.load_enrollments()

    def create_widgets(self):
        top = tk.Frame(self, bg=COLOR_LIGHT)
        top.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(top, text="Search:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(top, font=FONT_NORMAL, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_enrollments())
        tk.Button(top, text="Search", font=FONT_NORMAL, bg=COLOR_SECONDARY, fg="white",
                  command=self.search_enrollments).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Add Enrollment", font=FONT_NORMAL, bg=COLOR_SUCCESS, fg="white",
                  command=self.open_add).pack(side=tk.LEFT, padx=5)

        table = tk.Frame(self, bg=COLOR_LIGHT)
        table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(
            table,
            columns=("ID", "Student", "Course Code", "Course Name", "Enrollment Date", "Status"),
            show="headings"
        )
        for column, width in [("ID", 60), ("Student", 140), ("Course Code", 100),
                              ("Course Name", 230), ("Enrollment Date", 110), ("Status", 100)]:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=width, anchor=tk.W)
        scrollbar = ttk.Scrollbar(table, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind("<Double-1>", lambda e: self.edit_selected())

        bottom = tk.Frame(self, bg=COLOR_LIGHT)
        bottom.pack(fill=tk.X, padx=10, pady=10)
        tk.Button(bottom, text="Edit", font=FONT_NORMAL, bg=COLOR_SECONDARY, fg="white",
                  command=self.edit_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(bottom, text="Delete", font=FONT_NORMAL, bg=COLOR_DANGER, fg="white",
                  command=self.delete_selected).pack(side=tk.LEFT, padx=5)
        tk.Button(bottom, text="Refresh", font=FONT_NORMAL, bg=COLOR_WARNING, fg="white",
                  command=self.load_enrollments).pack(side=tk.LEFT, padx=5)

    def load_enrollments(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in EnrollmentOperations.get_all_enrollments():
            self.tree.insert("", tk.END, values=row)

    def search_enrollments(self):
        term = self.search_entry.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = EnrollmentOperations.search_enrollments(term) if term else EnrollmentOperations.get_all_enrollments()
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def _selected_id(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Selection", "Please select an enrollment first")
            return None
        return self.tree.item(selection[0], "values")[0]

    def open_add(self):
        AddEnrollmentWindow(self)

    def edit_selected(self):
        enrollment_id = self._selected_id()
        if enrollment_id:
            EditEnrollmentWindow(self, enrollment_id)

    def delete_selected(self):
        enrollment_id = self._selected_id()
        if not enrollment_id:
            return
        if messagebox.askyesno("Confirm", "Delete this enrollment?"):
            success, message = EnrollmentOperations.delete_enrollment(enrollment_id)
            if success:
                messagebox.showinfo("Success", message)
                self.load_enrollments()
            else:
                messagebox.showerror("Error", message)


class _EnrollmentFormBase(tk.Toplevel):
    def _load_students(self):
        students = EnrollmentOperations.get_students()
        self.student_map = {f"{username} ({email})": student_id for student_id, username, email in students}
        self.student_combo["values"] = list(self.student_map.keys())

    def _load_courses(self):
        courses = EnrollmentOperations.get_courses()
        self.course_map = {f"{code} - {name}": course_id for course_id, code, name in courses}
        self.course_combo["values"] = list(self.course_map.keys())

    def _common_fields(self):
        form = tk.Frame(self, bg=COLOR_LIGHT)
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(form, text="Student:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.student_combo = ttk.Combobox(form, font=FONT_NORMAL, state="readonly")
        self.student_combo.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Course:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.course_combo = ttk.Combobox(form, font=FONT_NORMAL, state="readonly")
        self.course_combo.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Enrollment Date (YYYY-MM-DD):", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.date_entry = tk.Entry(form, font=FONT_NORMAL)
        self.date_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Status:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.status_combo = ttk.Combobox(form, font=FONT_NORMAL, state="readonly")
        self.status_combo["values"] = ("Active", "Completed", "Dropped")
        self.status_combo.pack(fill=tk.X, pady=(0, 10))

        self._load_students()
        self._load_courses()

    def _buttons(self, label, command):
        buttons = tk.Frame(self, bg=COLOR_LIGHT)
        buttons.pack(fill=tk.X, padx=20, pady=10)
        tk.Button(buttons, text=label, font=FONT_NORMAL, bg=COLOR_SUCCESS, fg="white",
                  command=command).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons, text="Cancel", font=FONT_NORMAL, bg=COLOR_DANGER, fg="white",
                  command=self.destroy).pack(side=tk.LEFT, padx=5)


class AddEnrollmentWindow(_EnrollmentFormBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Enrollment")
        self.geometry("400x380")
        self.config(bg=COLOR_LIGHT)
        self.parent = parent
        self._common_fields()
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.status_combo.set("Active")
        self._buttons("Save", self.save_enrollment)

    def save_enrollment(self):
        student_key = self.student_combo.get().strip()
        course_key = self.course_combo.get().strip()
        enrollment_date = self.date_entry.get().strip()
        status = self.status_combo.get().strip()

        if not all([student_key, course_key, enrollment_date, status]):
            messagebox.showerror("Validation", MSG_FILL_FIELDS)
            return
        try:
            datetime.strptime(enrollment_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation", "Invalid enrollment date format. Use YYYY-MM-DD")
            return

        success, result = EnrollmentOperations.add_enrollment(
            self.student_map[student_key],
            self.course_map[course_key],
            enrollment_date,
            status,
        )
        if success:
            messagebox.showinfo("Success", "Enrollment added successfully")
            self.parent.load_enrollments()
            self.destroy()
        else:
            messagebox.showerror("Error", result)


class EditEnrollmentWindow(_EnrollmentFormBase):
    def __init__(self, parent, enrollment_id):
        super().__init__(parent)
        self.title("Edit Enrollment")
        self.geometry("400x380")
        self.config(bg=COLOR_LIGHT)
        self.parent = parent
        self.enrollment_id = enrollment_id
        self._common_fields()
        self._buttons("Update", self.update_enrollment)
        self._load_data()

    def _load_data(self):
        enrollment = EnrollmentOperations.get_enrollment_by_id(self.enrollment_id)
        if not enrollment:
            return
        self.student_combo.set(next((name for name, pk in self.student_map.items() if pk == enrollment[1]), ""))
        self.course_combo.set(next((name for name, pk in self.course_map.items() if pk == enrollment[2]), ""))
        self.date_entry.insert(0, enrollment[3].strftime("%Y-%m-%d") if enrollment[3] else "")
        self.status_combo.set(enrollment[4] or "Active")

    def update_enrollment(self):
        student_key = self.student_combo.get().strip()
        course_key = self.course_combo.get().strip()
        enrollment_date = self.date_entry.get().strip()
        status = self.status_combo.get().strip()

        if not all([student_key, course_key, enrollment_date, status]):
            messagebox.showerror("Validation", MSG_FILL_FIELDS)
            return
        try:
            datetime.strptime(enrollment_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation", "Invalid enrollment date format. Use YYYY-MM-DD")
            return

        success, message = EnrollmentOperations.update_enrollment(
            self.enrollment_id,
            self.student_map[student_key],
            self.course_map[course_key],
            enrollment_date,
            status,
        )
        if success:
            messagebox.showinfo("Success", message)
            self.parent.load_enrollments()
            self.destroy()
        else:
            messagebox.showerror("Error", message)