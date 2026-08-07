"""Department management module."""

import tkinter as tk
from tkinter import messagebox, ttk

from config import *
from database import DatabaseConnection, logger


class DepartmentOperations:
    @staticmethod
    def get_all_departments():
        query = """
            SELECT department_id, department_name, department_code, COALESCE(head_of_department, ''), created_at
            FROM departments
            ORDER BY department_name
        """
        return DatabaseConnection.execute_query(query)

    @staticmethod
    def search_departments(term):
        query = """
            SELECT department_id, department_name, department_code, COALESCE(head_of_department, ''), created_at
            FROM departments
            WHERE department_name ILIKE %s
               OR department_code ILIKE %s
               OR COALESCE(head_of_department, '') ILIKE %s
            ORDER BY department_name
        """
        like = f"%{term}%"
        return DatabaseConnection.execute_query(query, (like, like, like))

    @staticmethod
    def get_department_by_id(department_id):
        query = """
            SELECT department_id, department_name, department_code, COALESCE(head_of_department, '')
            FROM departments
            WHERE department_id = %s
        """
        return DatabaseConnection.execute_fetchone(query, (department_id,))

    @staticmethod
    def add_department(name, code, head):
        query = """
            INSERT INTO departments (department_name, department_code, head_of_department)
            VALUES (%s, %s, %s)
            RETURNING department_id
        """
        conn = DatabaseConnection.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (name, code, head))
            department_id = cursor.fetchone()[0]
            conn.commit()
            logger.info("Department added: %s", department_id)
            return True, department_id
        except Exception as exc:
            conn.rollback()
            logger.error("Add department error: %s", exc)
            return False, str(exc)
        finally:
            cursor.close()

    @staticmethod
    def update_department(department_id, name, code, head):
        query = """
            UPDATE departments
            SET department_name = %s,
                department_code = %s,
                head_of_department = %s
            WHERE department_id = %s
        """
        try:
            DatabaseConnection.execute_update(query, (name, code, head, department_id))
            return True, "Department updated successfully"
        except Exception as exc:
            logger.error("Update department error: %s", exc)
            return False, str(exc)

    @staticmethod
    def delete_department(department_id):
        try:
            DatabaseConnection.execute_update("DELETE FROM departments WHERE department_id = %s", (department_id,))
            return True, "Department deleted successfully"
        except Exception as exc:
            logger.error("Delete department error: %s", exc)
            return False, str(exc)


class DepartmentManagementWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Department Management")
        self.geometry("980x600")
        self.config(bg=COLOR_LIGHT)
        self.parent = parent
        self.create_widgets()
        self.load_departments()

    def create_widgets(self):
        top = tk.Frame(self, bg=COLOR_LIGHT)
        top.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(top, text="Search:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(top, font=FONT_NORMAL, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_departments())

        tk.Button(top, text="Search", font=FONT_NORMAL, bg=COLOR_SECONDARY, fg="white",
                  command=self.search_departments).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Add Department", font=FONT_NORMAL, bg=COLOR_SUCCESS, fg="white",
                  command=self.open_add).pack(side=tk.LEFT, padx=5)

        table = tk.Frame(self, bg=COLOR_LIGHT)
        table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tree = ttk.Treeview(
            table,
            columns=("ID", "Name", "Code", "Head", "Created"),
            show="headings"
        )
        for column, width in [("ID", 60), ("Name", 220), ("Code", 110), ("Head", 200), ("Created", 140)]:
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
                  command=self.load_departments).pack(side=tk.LEFT, padx=5)

    def load_departments(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in DepartmentOperations.get_all_departments():
            self.tree.insert("", tk.END, values=row)

    def search_departments(self):
        term = self.search_entry.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = DepartmentOperations.search_departments(term) if term else DepartmentOperations.get_all_departments()
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def _selected_id(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Selection", "Please select a department first")
            return None
        return self.tree.item(selection[0], "values")[0]

    def open_add(self):
        AddDepartmentWindow(self)

    def edit_selected(self):
        department_id = self._selected_id()
        if department_id:
            EditDepartmentWindow(self, department_id)

    def delete_selected(self):
        department_id = self._selected_id()
        if not department_id:
            return
        if messagebox.askyesno("Confirm", "Delete this department?"):
            success, message = DepartmentOperations.delete_department(department_id)
            if success:
                messagebox.showinfo("Success", message)
                self.load_departments()
            else:
                messagebox.showerror("Error", message)


class _DepartmentFormBase(tk.Toplevel):
    def _common_fields(self):
        form = tk.Frame(self, bg=COLOR_LIGHT)
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(form, text="Department Name:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.name_entry = tk.Entry(form, font=FONT_NORMAL)
        self.name_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Department Code:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.code_entry = tk.Entry(form, font=FONT_NORMAL)
        self.code_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Head of Department:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.head_entry = tk.Entry(form, font=FONT_NORMAL)
        self.head_entry.pack(fill=tk.X, pady=(0, 10))

        return form

    def _buttons(self, label, command):
        buttons = tk.Frame(self, bg=COLOR_LIGHT)
        buttons.pack(fill=tk.X, padx=20, pady=10)
        tk.Button(buttons, text=label, font=FONT_NORMAL, bg=COLOR_SUCCESS, fg="white",
                  command=command).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons, text="Cancel", font=FONT_NORMAL, bg=COLOR_DANGER, fg="white",
                  command=self.destroy).pack(side=tk.LEFT, padx=5)


class AddDepartmentWindow(_DepartmentFormBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Department")
        self.geometry("380x300")
        self.config(bg=COLOR_LIGHT)
        self.parent = parent
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        self._common_fields()
        self._buttons("Save", self.save_department)

    def save_department(self):
        name = self.name_entry.get().strip()
        code = self.code_entry.get().strip()
        head = self.head_entry.get().strip()

        if not name or not code:
            messagebox.showerror("Validation", MSG_FILL_FIELDS)
            return

        success, result = DepartmentOperations.add_department(name, code, head)
        if success:
            messagebox.showinfo("Success", "Department added successfully")
            self.parent.load_departments()
            self.destroy()
        else:
            messagebox.showerror("Error", result)


class EditDepartmentWindow(_DepartmentFormBase):
    def __init__(self, parent, department_id):
        super().__init__(parent)
        self.title("Edit Department")
        self.geometry("380x300")
        self.config(bg=COLOR_LIGHT)
        self.parent = parent
        self.department_id = department_id
        self._common_fields()
        self._buttons("Update", self.update_department)
        self._load_data()

    def _load_data(self):
        department = DepartmentOperations.get_department_by_id(self.department_id)
        if not department:
            return
        self.name_entry.insert(0, department[1] or "")
        self.code_entry.insert(0, department[2] or "")
        self.head_entry.insert(0, department[3] or "")

    def update_department(self):
        name = self.name_entry.get().strip()
        code = self.code_entry.get().strip()
        head = self.head_entry.get().strip()

        if not name or not code:
            messagebox.showerror("Validation", MSG_FILL_FIELDS)
            return

        success, message = DepartmentOperations.update_department(self.department_id, name, code, head)
        if success:
            messagebox.showinfo("Success", message)
            self.parent.load_departments()
            self.destroy()
        else:
            messagebox.showerror("Error", message)