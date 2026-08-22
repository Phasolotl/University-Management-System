# routes/student.py
"""
Student Management Module
Handles all student-related operations (CRUD, search, validation)
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
from database import DatabaseConnection, logger
from config import *


class StudentOperations:
    """Database operations for students"""

    @staticmethod
    def add_student(user_id, department_id, enrollment_date, phone, address, date_of_birth):
        """Add new student"""
        try:
            query = """
                INSERT INTO students (user_id, department_id, enrollment_date, phone, address, date_of_birth)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING student_id
            """
            conn = DatabaseConnection.connect()
            cursor = conn.cursor()
            cursor.execute(query, (user_id, department_id, enrollment_date, phone, address, date_of_birth))
            student_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            logger.info(f"Student added: {student_id}")
            return True, student_id
        except Exception as e:
            logger.error(f"Add student error: {e}")
            return False, str(e)

    @staticmethod
    def get_all_students():
        """Get all students with details"""
        try:
            query = """
                SELECT s.student_id, u.username, u.email, d.department_name, 
                       s.enrollment_date, s.phone, s.address, s.date_of_birth
                FROM students s
                JOIN users u ON s.user_id = u.user_id
                JOIN departments d ON s.department_id = d.department_id
                ORDER BY s.student_id
            """
            return DatabaseConnection.execute_query(query)
        except Exception as e:
            logger.error(f"Get students error: {e}")
            return []

    @staticmethod
    def get_student_by_id(student_id):
        """Get specific student details"""
        try:
            query = """
                SELECT s.student_id, s.user_id, u.username, u.email, s.department_id,
                       d.department_name, s.enrollment_date, s.phone, s.address, s.date_of_birth
                FROM students s
                JOIN users u ON s.user_id = u.user_id
                JOIN departments d ON s.department_id = d.department_id
                WHERE s.student_id = %s
            """
            return DatabaseConnection.execute_fetchone(query, (student_id,))
        except Exception as e:
            logger.error(f"Get student error: {e}")
            return None

    @staticmethod
    def update_student(student_id, phone, address, department_id):
        """Update student information"""
        try:
            query = """
                UPDATE students 
                SET phone = %s, address = %s, department_id = %s
                WHERE student_id = %s
            """
            DatabaseConnection.execute_update(query, (phone, address, department_id, student_id))
            logger.info(f"Student updated: {student_id}")
            return True, "Student updated successfully"
        except Exception as e:
            logger.error(f"Update student error: {e}")
            return False, str(e)

    @staticmethod
    def delete_student(student_id):
        """Delete student"""
        try:
            query = "DELETE FROM students WHERE student_id = %s"
            DatabaseConnection.execute_update(query, (student_id,))
            logger.info(f"Student deleted: {student_id}")
            return True, "Student deleted successfully"
        except Exception as e:
            logger.error(f"Delete student error: {e}")
            return False, str(e)

    @staticmethod
    def search_students(search_term):
        """Search students by username or email"""
        try:
            query = """
                SELECT s.student_id, u.username, u.email, d.department_name,
                       s.enrollment_date, s.phone, s.address, s.date_of_birth
                FROM students s
                JOIN users u ON s.user_id = u.user_id
                JOIN departments d ON s.department_id = d.department_id
                WHERE u.username ILIKE %s OR u.email ILIKE %s
                ORDER BY s.student_id
            """
            search = f"%{search_term}%"
            return DatabaseConnection.execute_query(query, (search, search))
        except Exception as e:
            logger.error(f"Search students error: {e}")
            return []

    @staticmethod
    def get_departments():
        """Get all departments"""
        try:
            query = "SELECT department_id, department_name FROM departments ORDER BY department_name"
            return DatabaseConnection.execute_query(query)
        except Exception as e:
            logger.error(f"Get departments error: {e}")
            return []

    @staticmethod
    def get_available_users():
        """Get student-role users not yet linked to a student record"""
        try:
            query = """
                SELECT u.user_id, u.username, u.email
                FROM users u
                JOIN roles r ON u.role_id = r.role_id
                WHERE r.role_name = 'Student'
                  AND NOT EXISTS (
                      SELECT 1 FROM students s WHERE s.user_id = u.user_id
                  )
                ORDER BY u.username
            """
            return DatabaseConnection.execute_query(query)
        except Exception as e:
            logger.error(f"Get available users error: {e}")
            return []


class StudentManagementWindow(tk.Toplevel):
    """Student Management GUI"""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Student Management")
        self.geometry("1000x600")
        self.config(bg=COLOR_LIGHT)

        self.create_widgets()
        self.load_students()

    def create_widgets(self):
        """Create UI components"""
        # Top Frame - Search and Add
        top_frame = tk.Frame(self, bg=COLOR_LIGHT)
        top_frame.pack(fill=tk.X, padx=10, pady=10)

        search_label = tk.Label(
            top_frame, text="Search:", font=FONT_NORMAL, bg=COLOR_LIGHT
        )
        search_label.pack(side=tk.LEFT, padx=5)

        self.search_entry = tk.Entry(top_frame, font=FONT_NORMAL, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_students())

        search_btn = tk.Button(
            top_frame, text="Search", font=FONT_NORMAL,
            bg=COLOR_SECONDARY, fg="white", command=self.search_students
        )
        search_btn.pack(side=tk.LEFT, padx=5)

        add_btn = tk.Button(
            top_frame, text="Add Student", font=FONT_NORMAL,
            bg=COLOR_SUCCESS, fg="white", command=self.open_add_student
        )
        add_btn.pack(side=tk.LEFT, padx=5)

        # Table Frame
        table_frame = tk.Frame(self, bg=COLOR_LIGHT)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create Treeview
        self.tree = ttk.Treeview(
            table_frame,
            columns=("ID", "Username", "Email", "Department", "Enrollment", "Phone"),
            height=20
        )
        self.tree.column("#0", width=0, stretch=tk.NO)
        self.tree.column("ID", anchor=tk.CENTER, width=50)
        self.tree.column("Username", anchor=tk.W, width=100)
        self.tree.column("Email", anchor=tk.W, width=150)
        self.tree.column("Department", anchor=tk.W, width=120)
        self.tree.column("Enrollment", anchor=tk.CENTER, width=100)
        self.tree.column("Phone", anchor=tk.W, width=100)

        self.tree.heading("#0", text="", anchor=tk.W)
        self.tree.heading("ID", text="ID", anchor=tk.CENTER)
        self.tree.heading("Username", text="Username", anchor=tk.W)
        self.tree.heading("Email", text="Email", anchor=tk.W)
        self.tree.heading("Department", text="Department", anchor=tk.W)
        self.tree.heading("Enrollment", text="Enrollment", anchor=tk.CENTER)
        self.tree.heading("Phone", text="Phone", anchor=tk.W)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind double-click for editing
        self.tree.bind('<Double-1>', self.on_tree_double_click)

        # Bottom Frame - Buttons
        bottom_frame = tk.Frame(self, bg=COLOR_LIGHT)
        bottom_frame.pack(fill=tk.X, padx=10, pady=10)

        edit_btn = tk.Button(
            bottom_frame, text="Edit", font=FONT_NORMAL,
            bg=COLOR_SECONDARY, fg="white", command=self.edit_student
        )
        edit_btn.pack(side=tk.LEFT, padx=5)

        delete_btn = tk.Button(
            bottom_frame, text="Delete", font=FONT_NORMAL,
            bg=COLOR_DANGER, fg="white", command=self.delete_student
        )
        delete_btn.pack(side=tk.LEFT, padx=5)

        refresh_btn = tk.Button(
            bottom_frame, text="Refresh", font=FONT_NORMAL,
            bg=COLOR_WARNING, fg="white", command=self.load_students
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)

    def load_students(self):
        """Load all students into table"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        students = StudentOperations.get_all_students()
        for student in students:
            self.tree.insert("", tk.END, values=student)

    def search_students(self):
        """Search students"""
        search_term = self.search_entry.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)

        if search_term:
            students = StudentOperations.search_students(search_term)
        else:
            students = StudentOperations.get_all_students()

        for student in students:
            self.tree.insert("", tk.END, values=student)

    def on_tree_double_click(self, event):
        """Handle double-click on tree item"""
        item = self.tree.selection()[0]
        values = self.tree.item(item, 'values')
        if values:
            self.open_edit_student(values[0])

    def open_add_student(self):
        """Open add student dialog"""
        AddStudentWindow(self)

    def open_edit_student(self, student_id):
        """Open edit student dialog"""
        EditStudentWindow(self, student_id)

    def edit_student(self):
        """Edit selected student"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Selection", "Please select a student to edit")
            return

        item = selection[0]
        values = self.tree.item(item, 'values')
        self.open_edit_student(values[0])

    def delete_student(self):
        """Delete selected student"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Selection", "Please select a student to delete")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete this student?"):
            item = selection[0]
            values = self.tree.item(item, 'values')
            success, message = StudentOperations.delete_student(values[0])
            if success:
                messagebox.showinfo("Success", message)
                self.load_students()
            else:
                messagebox.showerror("Error", message)


class AddStudentWindow(tk.Toplevel):
    """Add new student dialog"""

    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Student")
        self.geometry("400x500")
        self.config(bg=COLOR_LIGHT)
        self.parent = parent

        self.transient(parent)
        self.grab_set()
        self.focus_force()

        self.create_widgets()

    def create_widgets(self):
        """Create form widgets"""
        form_frame = tk.Frame(self, bg=COLOR_LIGHT)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(form_frame, text="User:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.user_combo = ttk.Combobox(form_frame, font=FONT_NORMAL, state="readonly")
        self.user_combo.pack(fill=tk.X, pady=(4, 10))

        fields = [
            ("Phone:", "phone"),
            ("Address:", "address"),
            ("Date of Birth (YYYY-MM-DD):", "dob"),
            ("Department:", "department"),
        ]

        self.entries = {}
        self.user_map = {}

        self.load_users()

        for label_text, field_name in fields:
            label = tk.Label(form_frame, text=label_text, font=FONT_NORMAL, bg=COLOR_LIGHT)
            label.pack(anchor=tk.W, pady=(10, 0))

            if field_name == "department":
                self.entries[field_name] = ttk.Combobox(
                    form_frame, font=FONT_NORMAL, state="readonly"
                )
                self.load_departments()
                self.entries[field_name].pack(fill=tk.X, pady=(0, 10))
            elif field_name == "address":
                self.entries[field_name] = tk.Text(form_frame, font=FONT_NORMAL, height=3, width=30)
                self.entries[field_name].pack(fill=tk.X, pady=(0, 10))
            else:
                self.entries[field_name] = tk.Entry(form_frame, font=FONT_NORMAL)
                self.entries[field_name].pack(fill=tk.X, pady=(0, 10))

        # Buttons
        button_frame = tk.Frame(form_frame, bg=COLOR_LIGHT)
        button_frame.pack(fill=tk.X, pady=20)

        save_btn = tk.Button(
            button_frame, text="Save", font=FONT_NORMAL,
            bg=COLOR_SUCCESS, fg="white", command=self.save_student
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(
            button_frame, text="Cancel", font=FONT_NORMAL,
            bg=COLOR_DANGER, fg="white", command=self.destroy
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def load_departments(self):
        """Load departments into combobox"""
        departments = StudentOperations.get_departments()
        dept_dict = {name: dept_id for dept_id, name in departments}
        self.dept_dict = dept_dict
        self.entries["department"]["values"] = list(dept_dict.keys())

    def load_users(self):
        """Load student users into combobox"""
        users = StudentOperations.get_available_users()
        self.user_map = {f"{username} ({email})": user_id for user_id, username, email in users}
        self.user_combo["values"] = list(self.user_map.keys())

    def save_student(self):
        """Save new student"""
        user_key = self.user_combo.get().strip()
        phone = self.entries["phone"].get().strip()
        address = self.entries["address"].get("1.0", tk.END).strip()
        dob = self.entries["dob"].get().strip()
        department = self.entries["department"].get()

        # Validation
        if not all([user_key, phone, address, dob, department]):
            messagebox.showerror("Validation", MSG_FILL_FIELDS)
            return

        if not phone.isdigit() or len(phone) < 10:
            messagebox.showerror("Validation", MSG_INVALID_PHONE)
            return

        try:
            datetime.strptime(dob, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation", "Invalid date format. Use YYYY-MM-DD")
            return

        dept_id = self.dept_dict[department]
        today = datetime.now().strftime("%Y-%m-%d")

        success, result = StudentOperations.add_student(
            user_id=self.user_map[user_key],
            department_id=dept_id,
            enrollment_date=today,
            phone=phone,
            address=address,
            date_of_birth=dob
        )

        if success:
            messagebox.showinfo("Success", "Student added successfully!")
            self.parent.load_students()
            self.destroy()
        else:
            messagebox.showerror("Error", result)


class EditStudentWindow(tk.Toplevel):
    """Edit student dialog"""

    def __init__(self, parent, student_id):
        super().__init__(parent)
        self.title("Edit Student")
        self.geometry("400x500")
        self.config(bg=COLOR_LIGHT)
        self.parent = parent
        self.student_id = student_id

        self.create_widgets()
        self.load_student_data()

    def create_widgets(self):
        """Create form widgets"""
        form_frame = tk.Frame(self, bg=COLOR_LIGHT)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        fields = [
            ("Username:", "username", True),
            ("Email:", "email", True),
            ("Phone:", "phone", False),
            ("Address:", "address", False),
            ("Department:", "department", False),
        ]

        self.entries = {}

        for label_text, field_name, readonly in fields:
            label = tk.Label(form_frame, text=label_text, font=FONT_NORMAL, bg=COLOR_LIGHT)
            label.pack(anchor=tk.W, pady=(10, 0))

            if field_name == "department":
                self.entries[field_name] = ttk.Combobox(
                    form_frame, font=FONT_NORMAL, state="readonly"
                )
                self.load_departments()
                self.entries[field_name].pack(fill=tk.X, pady=(0, 10))
            elif field_name == "address":
                self.entries[field_name] = tk.Text(form_frame, font=FONT_NORMAL, height=3, width=30)
                self.entries[field_name].pack(fill=tk.X, pady=(0, 10))
            else:
                self.entries[field_name] = tk.Entry(form_frame, font=FONT_NORMAL)
                if readonly:
                    self.entries[field_name].config(state="readonly")
                self.entries[field_name].pack(fill=tk.X, pady=(0, 10))

        # Buttons
        button_frame = tk.Frame(form_frame, bg=COLOR_LIGHT)
        button_frame.pack(fill=tk.X, pady=20)

        save_btn = tk.Button(
            button_frame, text="Update", font=FONT_NORMAL,
            bg=COLOR_SUCCESS, fg="white", command=self.update_student
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(
            button_frame, text="Cancel", font=FONT_NORMAL,
            bg=COLOR_DANGER, fg="white", command=self.destroy
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def load_departments(self):
        """Load departments"""
        departments = StudentOperations.get_departments()
        dept_dict = {name: dept_id for dept_id, name in departments}
        self.dept_dict = dept_dict
        self.entries["department"]["values"] = list(dept_dict.keys())

    def load_student_data(self):
        """Load student data into form"""
        student = StudentOperations.get_student_by_id(self.student_id)
        if student:
            self.entries["username"].insert(0, student[2])
            self.entries["email"].insert(0, student[3])
            self.entries["phone"].insert(0, student[7] if student[7] else "")
            self.entries["address"].insert("1.0", student[8] if student[8] else "")
            self.entries["department"].set(student[5])

    def update_student(self):
        """Update student"""
        phone = self.entries["phone"].get().strip()
        address = self.entries["address"].get("1.0", tk.END).strip()
        department = self.entries["department"].get()

        if not all([phone, address, department]):
            messagebox.showerror("Validation", MSG_FILL_FIELDS)
            return

        if not phone.isdigit() or len(phone) < 10:
            messagebox.showerror("Validation", MSG_INVALID_PHONE)
            return

        dept_id = self.dept_dict[department]
        success, message = StudentOperations.update_student(self.student_id, phone, address, dept_id)

        if success:
            messagebox.showinfo("Success", message)
            self.parent.load_students()
            self.destroy()
        else:
            messagebox.showerror("Error", message)