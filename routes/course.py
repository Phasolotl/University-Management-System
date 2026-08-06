"""Course management module."""

import tkinter as tk
from tkinter import messagebox, ttk

from config import *
from database import DatabaseConnection, logger


class CourseOperations:
    @staticmethod
    def get_departments():
        return DatabaseConnection.execute_query(
            "SELECT department_id, department_name FROM departments ORDER BY department_name"
        )

    @staticmethod
    def get_lecturers():
        query = """
            SELECT l.lecturer_id, u.username, d.department_name
            FROM lecturers l
            JOIN users u ON l.user_id = u.user_id
            JOIN departments d ON l.department_id = d.department_id
            ORDER BY u.username
        """
        return DatabaseConnection.execute_query(query)

    @staticmethod
    def get_all_courses():
        query = """
            SELECT c.course_id, c.course_code, c.course_name, d.department_name,
                   u.username, c.credits, COALESCE(c.description, '')
            FROM courses c
            JOIN departments d ON c.department_id = d.department_id
            JOIN lecturers l ON c.lecturer_id = l.lecturer_id
            JOIN users u ON l.user_id = u.user_id
            ORDER BY c.course_id
        """
        return DatabaseConnection.execute_query(query)

    @staticmethod
    def search_courses(term):
        query = """
            SELECT c.course_id, c.course_code, c.course_name, d.department_name,
                   u.username, c.credits, COALESCE(c.description, '')
            FROM courses c
            JOIN departments d ON c.department_id = d.department_id
            JOIN lecturers l ON c.lecturer_id = l.lecturer_id
            JOIN users u ON l.user_id = u.user_id
            WHERE c.course_code ILIKE %s
               OR c.course_name ILIKE %s
               OR d.department_name ILIKE %s
               OR u.username ILIKE %s
            ORDER BY c.course_id
        """
        like = f"%{term}%"
        return DatabaseConnection.execute_query(query, (like, like, like, like))

    @staticmethod
    def get_course_by_id(course_id):
        query = """
            SELECT c.course_id, c.course_code, c.course_name, c.department_id, c.lecturer_id,
                   c.credits, COALESCE(c.description, '')
            FROM courses c
            WHERE c.course_id = %s
        """
        return DatabaseConnection.execute_fetchone(query, (course_id,))

    @staticmethod
    def add_course(course_code, course_name, department_id, lecturer_id, credits, description):
        query = """
            INSERT INTO courses (course_code, course_name, department_id, lecturer_id, credits, description)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING course_id
        """
        conn = DatabaseConnection.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (course_code, course_name, department_id, lecturer_id, credits, description))
            course_id = cursor.fetchone()[0]
            conn.commit()
            logger.info("Course added: %s", course_id)
            return True, course_id
        except Exception as exc:
            conn.rollback()
            logger.error("Add course error: %s", exc)
            return False, str(exc)
        finally:
            cursor.close()

    @staticmethod
    def update_course(course_id, course_code, course_name, department_id, lecturer_id, credits, description):
        query = """
            UPDATE courses
            SET course_code = %s,
                course_name = %s,
                department_id = %s,
                lecturer_id = %s,
                credits = %s,
                description = %s
            WHERE course_id = %s
        """
        try:
            DatabaseConnection.execute_update(
                query, (course_code, course_name, department_id, lecturer_id, credits, description, course_id)
            )
            return True, "Course updated successfully"
        except Exception as exc:
            logger.error("Update course error: %s", exc)
            return False, str(exc)

    @staticmethod
    def delete_course(course_id):
        try:
            DatabaseConnection.execute_update("DELETE FROM courses WHERE course_id = %s", (course_id,))
            return True, "Course deleted successfully"
        except Exception as exc:
            logger.error("Delete course error: %s", exc)
            return False, str(exc)


class CourseManagementWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Course Management")
        self.geometry("1150x600")
        self.config(bg=COLOR_LIGHT)
        self.parent = parent
        self.create_widgets()
        self.load_courses()

    def create_widgets(self):
        top = tk.Frame(self, bg=COLOR_LIGHT)
        top.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(top, text="Search:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(top, font=FONT_NORMAL, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_courses())
        tk.Button(top, text="Search", font=FONT_NORMAL, bg=COLOR_SECONDARY, fg="white",
                  command=self.search_courses).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Add Course", font=FONT_NORMAL, bg=COLOR_SUCCESS, fg="white",
                  command=self.open_add).pack(side=tk.LEFT, padx=5)

        table = tk.Frame(self, bg=COLOR_LIGHT)
        table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(
            table,
            columns=("ID", "Code", "Name", "Department", "Lecturer", "Credits", "Description"),
            show="headings"
        )
        for column, width in [("ID", 60), ("Code", 90), ("Name", 190), ("Department", 140),
                              ("Lecturer", 130), ("Credits", 70), ("Description", 280)]:
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
                  command=self.load_courses).pack(side=tk.LEFT, padx=5)

    def load_courses(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in CourseOperations.get_all_courses():
            self.tree.insert("", tk.END, values=row)

    def search_courses(self):
        term = self.search_entry.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = CourseOperations.search_courses(term) if term else CourseOperations.get_all_courses()
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def _selected_id(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Selection", "Please select a course first")
            return None
        return self.tree.item(selection[0], "values")[0]

    def open_add(self):
        AddCourseWindow(self)

    def edit_selected(self):
        course_id = self._selected_id()
        if course_id:
            EditCourseWindow(self, course_id)

    def delete_selected(self):
        course_id = self._selected_id()
        if not course_id:
            return
        if messagebox.askyesno("Confirm", "Delete this course?"):
            success, message = CourseOperations.delete_course(course_id)
            if success:
                messagebox.showinfo("Success", message)
                self.load_courses()
            else:
                messagebox.showerror("Error", message)


class _CourseFormBase(tk.Toplevel):
    def _load_departments(self):
        departments = CourseOperations.get_departments()
        self.department_map = {name: dept_id for dept_id, name in departments}
        self.department_combo["values"] = list(self.department_map.keys())

    def _load_lecturers(self):
        lecturers = CourseOperations.get_lecturers()
        self.lecturer_map = {f"{username} ({department})": lecturer_id for lecturer_id, username, department in lecturers}
        self.lecturer_combo["values"] = list(self.lecturer_map.keys())

    def _common_fields(self):
        form = tk.Frame(self, bg=COLOR_LIGHT)
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(form, text="Course Code:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.code_entry = tk.Entry(form, font=FONT_NORMAL)
        self.code_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Course Name:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.name_entry = tk.Entry(form, font=FONT_NORMAL)
        self.name_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Department:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.department_combo = ttk.Combobox(form, font=FONT_NORMAL, state="readonly")
        self.department_combo.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Lecturer:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.lecturer_combo = ttk.Combobox(form, font=FONT_NORMAL, state="readonly")
        self.lecturer_combo.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Credits:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.credits_entry = tk.Entry(form, font=FONT_NORMAL)
        self.credits_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Description:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.description_text = tk.Text(form, font=FONT_NORMAL, height=4)
        self.description_text.pack(fill=tk.BOTH, pady=(0, 10))

        self._load_departments()
        self._load_lecturers()

    def _buttons(self, label, command):
        buttons = tk.Frame(self, bg=COLOR_LIGHT)
        buttons.pack(fill=tk.X, padx=20, pady=10)
        tk.Button(buttons, text=label, font=FONT_NORMAL, bg=COLOR_SUCCESS, fg="white",
                  command=command).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons, text="Cancel", font=FONT_NORMAL, bg=COLOR_DANGER, fg="white",
                  command=self.destroy).pack(side=tk.LEFT, padx=5)


class AddCourseWindow(_CourseFormBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Course")
        self.geometry("450x560")
        self.config(bg=COLOR_LIGHT)
        self.parent = parent
        self._common_fields()
        self._buttons("Save", self.save_course)

    def save_course(self):
        code = self.code_entry.get().strip()
        name = self.name_entry.get().strip()
        department_key = self.department_combo.get().strip()
        lecturer_key = self.lecturer_combo.get().strip()
        credits = self.credits_entry.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()

        if not all([code, name, department_key, lecturer_key, credits]):
            messagebox.showerror("Validation", MSG_FILL_FIELDS)
            return
        if not credits.isdigit():
            messagebox.showerror("Validation", "Credits must be a number")
            return

        success, result = CourseOperations.add_course(
            code,
            name,
            self.department_map[department_key],
            self.lecturer_map[lecturer_key],
            int(credits),
            description,
        )
        if success:
            messagebox.showinfo("Success", "Course added successfully")
            self.parent.load_courses()
            self.destroy()
        else:
            messagebox.showerror("Error", result)


class EditCourseWindow(_CourseFormBase):
    def __init__(self, parent, course_id):
        super().__init__(parent)
        self.title("Edit Course")
        self.geometry("450x560")
        self.config(bg=COLOR_LIGHT)
        self.parent = parent
        self.course_id = course_id
        self._common_fields()
        self._buttons("Update", self.update_course)
        self._load_data()

    def _load_data(self):
        course = CourseOperations.get_course_by_id(self.course_id)
        if not course:
            return
        self.code_entry.insert(0, course[1] or "")
        self.name_entry.insert(0, course[2] or "")
        self.department_combo.set(next((name for name, pk in self.department_map.items() if pk == course[3]), ""))
        self.lecturer_combo.set(next((name for name, pk in self.lecturer_map.items() if pk == course[4]), ""))
        self.credits_entry.insert(0, str(course[5]) if course[5] is not None else "")
        self.description_text.insert("1.0", course[6] or "")

    def update_course(self):
        code = self.code_entry.get().strip()
        name = self.name_entry.get().strip()
        department_key = self.department_combo.get().strip()
        lecturer_key = self.lecturer_combo.get().strip()
        credits = self.credits_entry.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()

        if not all([code, name, department_key, lecturer_key, credits]):
            messagebox.showerror("Validation", MSG_FILL_FIELDS)
            return
        if not credits.isdigit():
            messagebox.showerror("Validation", "Credits must be a number")
            return

        success, message = CourseOperations.update_course(
            self.course_id,
            code,
            name,
            self.department_map[department_key],
            self.lecturer_map[lecturer_key],
            int(credits),
            description,
        )
        if success:
            messagebox.showinfo("Success", message)
            self.parent.load_courses()
            self.destroy()
        else:
            messagebox.showerror("Error", message)