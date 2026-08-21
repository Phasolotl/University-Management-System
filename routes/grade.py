"""Grade management module."""

import tkinter as tk
from tkinter import messagebox, ttk

from config import *
from database import DatabaseConnection, logger


class GradeOperations:
    @staticmethod
    def get_enrollments():
        query = """
            SELECT e.enrollment_id, u.username, c.course_code, c.course_name
            FROM enrollments e
            JOIN students s ON e.student_id = s.student_id
            JOIN users u ON s.user_id = u.user_id
            JOIN courses c ON e.course_id = c.course_id
            ORDER BY e.enrollment_id
        """
        return DatabaseConnection.execute_query(query)

    @staticmethod
    def get_all_grades():
        query = """
            SELECT g.grade_id, u.username, c.course_code, g.assignment_1, g.assignment_2,
                   g.midterm, g.final_exam, g.final_grade, g.grade_letter
            FROM grades g
            JOIN enrollments e ON g.enrollment_id = e.enrollment_id
            JOIN students s ON e.student_id = s.student_id
            JOIN users u ON s.user_id = u.user_id
            JOIN courses c ON e.course_id = c.course_id
            ORDER BY g.grade_id
        """
        return DatabaseConnection.execute_query(query)

    @staticmethod
    def search_grades(term):
        query = """
            SELECT g.grade_id, u.username, c.course_code, g.assignment_1, g.assignment_2,
                   g.midterm, g.final_exam, g.final_grade, g.grade_letter
            FROM grades g
            JOIN enrollments e ON g.enrollment_id = e.enrollment_id
            JOIN students s ON e.student_id = s.student_id
            JOIN users u ON s.user_id = u.user_id
            JOIN courses c ON e.course_id = c.course_id
            WHERE u.username ILIKE %s
               OR c.course_code ILIKE %s
               OR COALESCE(g.grade_letter, '') ILIKE %s
            ORDER BY g.grade_id
        """
        like = f"%{term}%"
        return DatabaseConnection.execute_query(query, (like, like, like))

    @staticmethod
    def get_grade_by_id(grade_id):
        query = """
            SELECT grade_id, enrollment_id, assignment_1, assignment_2, midterm, final_exam, final_grade, grade_letter
            FROM grades
            WHERE grade_id = %s
        """
        return DatabaseConnection.execute_fetchone(query, (grade_id,))

    @staticmethod
    def calculate_final_grade(a1, a2, midterm, final_exam):
        total = a1 + a2 + midterm + final_exam
        if total >= 80:
            letter = "A"
        elif total >= 70:
            letter = "B"
        elif total >= 60:
            letter = "C"
        elif total >= 50:
            letter = "D"
        else:
            letter = "F"
        return round(total, 2), letter

    @staticmethod
    def add_grade(enrollment_id, assignment_1, assignment_2, midterm, final_exam):
        final_grade, grade_letter = GradeOperations.calculate_final_grade(
            assignment_1, assignment_2, midterm, final_exam
        )
        query = """
            INSERT INTO grades (enrollment_id, assignment_1, assignment_2, midterm, final_exam, final_grade, grade_letter)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING grade_id
        """
        conn = DatabaseConnection.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(
                query,
                (enrollment_id, assignment_1, assignment_2, midterm, final_exam, final_grade, grade_letter),
            )
            grade_id = cursor.fetchone()[0]
            conn.commit()
            logger.info("Grade added: %s", grade_id)
            return True, grade_id
        except Exception as exc:
            conn.rollback()
            logger.error("Add grade error: %s", exc)
            return False, str(exc)
        finally:
            cursor.close()

    @staticmethod
    def update_grade(grade_id, enrollment_id, assignment_1, assignment_2, midterm, final_exam):
        final_grade, grade_letter = GradeOperations.calculate_final_grade(
            assignment_1, assignment_2, midterm, final_exam
        )
        query = """
            UPDATE grades
            SET enrollment_id = %s,
                assignment_1 = %s,
                assignment_2 = %s,
                midterm = %s,
                final_exam = %s,
                final_grade = %s,
                grade_letter = %s
            WHERE grade_id = %s
        """
        try:
            DatabaseConnection.execute_update(
                query,
                (enrollment_id, assignment_1, assignment_2, midterm, final_exam, final_grade, grade_letter, grade_id),
            )
            return True, "Grade updated successfully"
        except Exception as exc:
            logger.error("Update grade error: %s", exc)
            return False, str(exc)

    @staticmethod
    def delete_grade(grade_id):
        try:
            DatabaseConnection.execute_update("DELETE FROM grades WHERE grade_id = %s", (grade_id,))
            return True, "Grade deleted successfully"
        except Exception as exc:
            logger.error("Delete grade error: %s", exc)
            return False, str(exc)


class GradeManagementWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Grade Management")
        self.geometry("1150x600")
        self.config(bg=COLOR_LIGHT)
        self.parent = parent
        self.create_widgets()
        self.load_grades()

    def create_widgets(self):
        top = tk.Frame(self, bg=COLOR_LIGHT)
        top.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(top, text="Search:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(top, font=FONT_NORMAL, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_grades())
        tk.Button(top, text="Search", font=FONT_NORMAL, bg=COLOR_SECONDARY, fg="white",
                  command=self.search_grades).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Add Grade", font=FONT_NORMAL, bg=COLOR_SUCCESS, fg="white",
                  command=self.open_add).pack(side=tk.LEFT, padx=5)

        table = tk.Frame(self, bg=COLOR_LIGHT)
        table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(
            table,
            columns=("ID", "Student", "Course", "A1", "A2", "Midterm", "Final Exam", "Final Grade", "Letter"),
            show="headings"
        )
        for column, width in [("ID", 60), ("Student", 140), ("Course", 100), ("A1", 70), ("A2", 70),
                              ("Midterm", 80), ("Final Exam", 90), ("Final Grade", 90), ("Letter", 60)]:
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
                  command=self.load_grades).pack(side=tk.LEFT, padx=5)

    def load_grades(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in GradeOperations.get_all_grades():
            self.tree.insert("", tk.END, values=row)

    def search_grades(self):
        term = self.search_entry.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = GradeOperations.search_grades(term) if term else GradeOperations.get_all_grades()
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def _selected_id(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Selection", "Please select a grade first")
            return None
        return self.tree.item(selection[0], "values")[0]

    def open_add(self):
        AddGradeWindow(self)

    def edit_selected(self):
        grade_id = self._selected_id()
        if grade_id:
            EditGradeWindow(self, grade_id)

    def delete_selected(self):
        grade_id = self._selected_id()
        if not grade_id:
            return
        if messagebox.askyesno("Confirm", "Delete this grade?"):
            success, message = GradeOperations.delete_grade(grade_id)
            if success:
                messagebox.showinfo("Success", message)
                self.load_grades()
            else:
                messagebox.showerror("Error", message)


class _GradeFormBase(tk.Toplevel):
    def _load_enrollments(self):
        enrollments = GradeOperations.get_enrollments()
        self.enrollment_map = {
            f"{username} - {code}": enrollment_id for enrollment_id, username, code, _ in enrollments
        }
        self.enrollment_combo["values"] = list(self.enrollment_map.keys())

    def _common_fields(self):
        form = tk.Frame(self, bg=COLOR_LIGHT)
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(form, text="Enrollment:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.enrollment_combo = ttk.Combobox(form, font=FONT_NORMAL, state="readonly")
        self.enrollment_combo.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Assignment 1:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.assignment_1_entry = tk.Entry(form, font=FONT_NORMAL)
        self.assignment_1_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Assignment 2:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.assignment_2_entry = tk.Entry(form, font=FONT_NORMAL)
        self.assignment_2_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Midterm:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.midterm_entry = tk.Entry(form, font=FONT_NORMAL)
        self.midterm_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Final Exam:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.final_exam_entry = tk.Entry(form, font=FONT_NORMAL)
        self.final_exam_entry.pack(fill=tk.X, pady=(0, 10))

        self._load_enrollments()

    def _buttons(self, label, command):
        buttons = tk.Frame(self, bg=COLOR_LIGHT)
        buttons.pack(fill=tk.X, padx=20, pady=10)
        tk.Button(buttons, text=label, font=FONT_NORMAL, bg=COLOR_SUCCESS, fg="white",
                  command=command).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons, text="Cancel", font=FONT_NORMAL, bg=COLOR_DANGER, fg="white",
                  command=self.destroy).pack(side=tk.LEFT, padx=5)

    def _parse_scores(self):
        try:
            return (
                float(self.assignment_1_entry.get().strip()),
                float(self.assignment_2_entry.get().strip()),
                float(self.midterm_entry.get().strip()),
                float(self.final_exam_entry.get().strip()),
            )
        except ValueError:
            messagebox.showerror("Validation", "Scores must be numeric")
            return None


class AddGradeWindow(_GradeFormBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Grade")
        self.geometry("420x470")
        self.config(bg=COLOR_LIGHT)
        self.parent = parent
        self.transient(parent)
        self.grab_set()
        self.focus_force()
        self._common_fields()
        self._buttons("Save", self.save_grade)

    def save_grade(self):
        enrollment_key = self.enrollment_combo.get().strip()
        if not enrollment_key:
            messagebox.showerror("Validation", MSG_FILL_FIELDS)
            return
        scores = self._parse_scores()
        if scores is None:
            return
        success, result = GradeOperations.add_grade(self.enrollment_map[enrollment_key], *scores)
        if success:
            messagebox.showinfo("Success", "Grade added successfully")
            self.parent.load_grades()
            self.destroy()
        else:
            messagebox.showerror("Error", result)


class EditGradeWindow(_GradeFormBase):
    def __init__(self, parent, grade_id):
        super().__init__(parent)
        self.title("Edit Grade")
        self.geometry("420x470")
        self.config(bg=COLOR_LIGHT)
        self.parent = parent
        self.grade_id = grade_id
        self._common_fields()
        self._buttons("Update", self.update_grade)
        self._load_data()

    def _load_data(self):
        grade = GradeOperations.get_grade_by_id(self.grade_id)
        if not grade:
            return
        self.enrollment_combo.set(next((name for name, pk in self.enrollment_map.items() if pk == grade[1]), ""))
        self.assignment_1_entry.insert(0, grade[2] if grade[2] is not None else "")
        self.assignment_2_entry.insert(0, grade[3] if grade[3] is not None else "")
        self.midterm_entry.insert(0, grade[4] if grade[4] is not None else "")
        self.final_exam_entry.insert(0, grade[5] if grade[5] is not None else "")

    def update_grade(self):
        enrollment_key = self.enrollment_combo.get().strip()
        if not enrollment_key:
            messagebox.showerror("Validation", MSG_FILL_FIELDS)
            return
        scores = self._parse_scores()
        if scores is None:
            return
        success, message = GradeOperations.update_grade(self.grade_id, self.enrollment_map[enrollment_key], *scores)
        if success:
            messagebox.showinfo("Success", message)
            self.parent.load_grades()
            self.destroy()
        else:
            messagebox.showerror("Error", message)
