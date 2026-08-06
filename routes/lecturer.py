"""Lecturer management module."""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

from config import *
from database import DatabaseConnection, logger


class LecturerOperations:
    @staticmethod
    def get_departments():
        return DatabaseConnection.execute_query(
            "SELECT department_id, department_name FROM departments ORDER BY department_name"
        )

    @staticmethod
    def get_available_users():
        query = """
            SELECT u.user_id, u.username, u.email
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
            WHERE r.role_name = 'Lecturer'
              AND NOT EXISTS (
                  SELECT 1 FROM lecturers l WHERE l.user_id = u.user_id
              )
            ORDER BY u.username
        """
        return DatabaseConnection.execute_query(query)

    @staticmethod
    def get_all_lecturers():
        query = """
            SELECT l.lecturer_id, u.username, u.email, d.department_name,
                   l.qualification, l.phone, l.office_location, l.hire_date
            FROM lecturers l
            JOIN users u ON l.user_id = u.user_id
            JOIN departments d ON l.department_id = d.department_id
            ORDER BY l.lecturer_id
        """
        return DatabaseConnection.execute_query(query)

    @staticmethod
    def search_lecturers(term):
        query = """
            SELECT l.lecturer_id, u.username, u.email, d.department_name,
                   l.qualification, l.phone, l.office_location, l.hire_date
            FROM lecturers l
            JOIN users u ON l.user_id = u.user_id
            JOIN departments d ON l.department_id = d.department_id
            WHERE u.username ILIKE %s
               OR u.email ILIKE %s
               OR d.department_name ILIKE %s
               OR COALESCE(l.qualification, '') ILIKE %s
            ORDER BY l.lecturer_id
        """
        like = f"%{term}%"
        return DatabaseConnection.execute_query(query, (like, like, like, like))

    @staticmethod
    def get_lecturer_by_id(lecturer_id):
        query = """
            SELECT l.lecturer_id, l.user_id, u.username, u.email, l.department_id,
                   d.department_name, l.qualification, l.phone, l.office_location, l.hire_date
            FROM lecturers l
            JOIN users u ON l.user_id = u.user_id
            JOIN departments d ON l.department_id = d.department_id
            WHERE l.lecturer_id = %s
        """
        return DatabaseConnection.execute_fetchone(query, (lecturer_id,))

    @staticmethod
    def add_lecturer(user_id, department_id, qualification, phone, office_location, hire_date):
        query = """
            INSERT INTO lecturers (user_id, department_id, qualification, phone, office_location, hire_date)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING lecturer_id
        """
        conn = DatabaseConnection.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (user_id, department_id, qualification, phone, office_location, hire_date))
            lecturer_id = cursor.fetchone()[0]
            conn.commit()
            logger.info("Lecturer added: %s", lecturer_id)
            return True, lecturer_id
        except Exception as exc:
            conn.rollback()
            logger.error("Add lecturer error: %s", exc)
            return False, str(exc)
        finally:
            cursor.close()

    @staticmethod
    def update_lecturer(lecturer_id, department_id, qualification, phone, office_location, hire_date):
        query = """
            UPDATE lecturers
            SET department_id = %s,
                qualification = %s,
                phone = %s,
                office_location = %s,
                hire_date = %s
            WHERE lecturer_id = %s
        """
        try:
            DatabaseConnection.execute_update(
                query, (department_id, qualification, phone, office_location, hire_date, lecturer_id)
            )
            return True, "Lecturer updated successfully"
        except Exception as exc:
            logger.error("Update lecturer error: %s", exc)
            return False, str(exc)

    @staticmethod
    def delete_lecturer(lecturer_id):
        try:
            DatabaseConnection.execute_update("DELETE FROM lecturers WHERE lecturer_id = %s", (lecturer_id,))
            return True, "Lecturer deleted successfully"
        except Exception as exc:
            logger.error("Delete lecturer error: %s", exc)
            return False, str(exc)


class LecturerManagementWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Lecturer Management")
        self.geometry("1100x600")
        self.config(bg=COLOR_LIGHT)
        self.parent = parent
        self.create_widgets()
        self.load_lecturers()

    def create_widgets(self):
        top = tk.Frame(self, bg=COLOR_LIGHT)
        top.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(top, text="Search:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(top, font=FONT_NORMAL, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_lecturers())

        tk.Button(top, text="Search", font=FONT_NORMAL, bg=COLOR_SECONDARY, fg="white",
                  command=self.search_lecturers).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Add Lecturer", font=FONT_NORMAL, bg=COLOR_SUCCESS, fg="white",
                  command=self.open_add).pack(side=tk.LEFT, padx=5)

        table = tk.Frame(self, bg=COLOR_LIGHT)
        table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(
            table,
            columns=("ID", "Username", "Email", "Department", "Qualification", "Phone", "Office", "Hire Date"),
            show="headings"
        )
        headings = [
            ("ID", 60), ("Username", 120), ("Email", 180), ("Department", 140),
            ("Qualification", 140), ("Phone", 110), ("Office", 120), ("Hire Date", 90)
        ]
        for column, width in headings:
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
                  command=self.load_lecturers).pack(side=tk.LEFT, padx=5)

    def load_lecturers(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in LecturerOperations.get_all_lecturers():
            self.tree.insert("", tk.END, values=row)

    def search_lecturers(self):
        term = self.search_entry.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = LecturerOperations.search_lecturers(term) if term else LecturerOperations.get_all_lecturers()
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def _selected_id(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Selection", "Please select a lecturer first")
            return None
        return self.tree.item(selection[0], "values")[0]

    def open_add(self):
        AddLecturerWindow(self)

    def edit_selected(self):
        lecturer_id = self._selected_id()
        if lecturer_id:
            EditLecturerWindow(self, lecturer_id)

    def delete_selected(self):
        lecturer_id = self._selected_id()
        if not lecturer_id:
            return
        if messagebox.askyesno("Confirm", "Delete this lecturer?"):
            success, message = LecturerOperations.delete_lecturer(lecturer_id)
            if success:
                messagebox.showinfo("Success", message)
                self.load_lecturers()
            else:
                messagebox.showerror("Error", message)


class _LecturerFormBase(tk.Toplevel):
    def _load_departments(self):
        departments = LecturerOperations.get_departments()
        self.department_map = {name: dept_id for dept_id, name in departments}
        self.department_combo["values"] = list(self.department_map.keys())

    def _load_users(self):
        users = LecturerOperations.get_available_users()
        self.user_map = {f"{username} ({email})": user_id for user_id, username, email in users}
        self.user_combo["values"] = list(self.user_map.keys())

    def _common_fields(self):
        form = tk.Frame(self, bg=COLOR_LIGHT)
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(form, text="User:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.user_combo = ttk.Combobox(form, font=FONT_NORMAL, state="readonly")
        self.user_combo.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Department:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.department_combo = ttk.Combobox(form, font=FONT_NORMAL, state="readonly")
        self.department_combo.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Qualification:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.qualification_entry = tk.Entry(form, font=FONT_NORMAL)
        self.qualification_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Phone:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.phone_entry = tk.Entry(form, font=FONT_NORMAL)
        self.phone_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Office Location:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.office_entry = tk.Entry(form, font=FONT_NORMAL)
        self.office_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Hire Date (YYYY-MM-DD):", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.hire_date_entry = tk.Entry(form, font=FONT_NORMAL)
        self.hire_date_entry.pack(fill=tk.X, pady=(0, 10))

        self._load_users()
        self._load_departments()

    def _buttons(self, label, command):
        buttons = tk.Frame(self, bg=COLOR_LIGHT)
        buttons.pack(fill=tk.X, padx=20, pady=10)
        tk.Button(buttons, text=label, font=FONT_NORMAL, bg=COLOR_SUCCESS, fg="white",
                  command=command).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons, text="Cancel", font=FONT_NORMAL, bg=COLOR_DANGER, fg="white",
                  command=self.destroy).pack(side=tk.LEFT, padx=5)


class AddLecturerWindow(_LecturerFormBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Lecturer")
        self.geometry("420x500")
        self.config(bg=COLOR_LIGHT)
        self.parent = parent
        self._common_fields()
        self._buttons("Save", self.save_lecturer)

    def save_lecturer(self):
        user_key = self.user_combo.get().strip()
        department_key = self.department_combo.get().strip()
        qualification = self.qualification_entry.get().strip()
        phone = self.phone_entry.get().strip()
        office = self.office_entry.get().strip()
        hire_date = self.hire_date_entry.get().strip()

        if not all([user_key, department_key, qualification, phone, office, hire_date]):
            messagebox.showerror("Validation", MSG_FILL_FIELDS)
            return
        try:
            datetime.strptime(hire_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation", "Invalid hire date format. Use YYYY-MM-DD")
            return

        success, result = LecturerOperations.add_lecturer(
            self.user_map[user_key],
            self.department_map[department_key],
            qualification,
            phone,
            office,
            hire_date,
        )
        if success:
            messagebox.showinfo("Success", "Lecturer added successfully")
            self.parent.load_lecturers()
            self.destroy()
        else:
            messagebox.showerror("Error", result)


class EditLecturerWindow(_LecturerFormBase):
    def __init__(self, parent, lecturer_id):
        super().__init__(parent)
        self.title("Edit Lecturer")
        self.geometry("420x500")
        self.config(bg=COLOR_LIGHT)
        self.parent = parent
        self.lecturer_id = lecturer_id
        self._common_fields()
        self._buttons("Update", self.update_lecturer)
        self._load_data()

    def _load_data(self):
        lecturer = LecturerOperations.get_lecturer_by_id(self.lecturer_id)
        if not lecturer:
            return
        user_label = f"{lecturer[2]} ({lecturer[3]})"
        self.user_combo["values"] = (user_label,)
        self.user_combo.set(user_label)
        self.department_combo.set(lecturer[5])
        self.qualification_entry.insert(0, lecturer[6] or "")
        self.phone_entry.insert(0, lecturer[7] or "")
        self.office_entry.insert(0, lecturer[8] or "")
        self.hire_date_entry.insert(0, lecturer[9].strftime("%Y-%m-%d") if lecturer[9] else "")

    def update_lecturer(self):
        department_key = self.department_combo.get().strip()
        qualification = self.qualification_entry.get().strip()
        phone = self.phone_entry.get().strip()
        office = self.office_entry.get().strip()
        hire_date = self.hire_date_entry.get().strip()

        if not all([department_key, qualification, phone, office, hire_date]):
            messagebox.showerror("Validation", MSG_FILL_FIELDS)
            return
        try:
            datetime.strptime(hire_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation", "Invalid hire date format. Use YYYY-MM-DD")
            return

        success, message = LecturerOperations.update_lecturer(
            self.lecturer_id,
            self.department_map[department_key],
            qualification,
            phone,
            office,
            hire_date,
        )
        if success:
            messagebox.showinfo("Success", message)
            self.parent.load_lecturers()
            self.destroy()
        else:
            messagebox.showerror("Error", message)