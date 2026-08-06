"""Payment management module."""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

from config import *
from database import DatabaseConnection, logger


class PaymentOperations:
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
    def get_all_payments():
        query = """
            SELECT p.payment_id, u.username, p.amount, p.payment_date, p.payment_method, p.status
            FROM payments p
            JOIN students s ON p.student_id = s.student_id
            JOIN users u ON s.user_id = u.user_id
            ORDER BY p.payment_id
        """
        return DatabaseConnection.execute_query(query)

    @staticmethod
    def search_payments(term):
        query = """
            SELECT p.payment_id, u.username, p.amount, p.payment_date, p.payment_method, p.status
            FROM payments p
            JOIN students s ON p.student_id = s.student_id
            JOIN users u ON s.user_id = u.user_id
            WHERE u.username ILIKE %s
               OR COALESCE(p.payment_method, '') ILIKE %s
               OR COALESCE(p.status, '') ILIKE %s
            ORDER BY p.payment_id
        """
        like = f"%{term}%"
        return DatabaseConnection.execute_query(query, (like, like, like))

    @staticmethod
    def get_payment_by_id(payment_id):
        query = """
            SELECT payment_id, student_id, amount, payment_date, payment_method, status, COALESCE(description, '')
            FROM payments
            WHERE payment_id = %s
        """
        return DatabaseConnection.execute_fetchone(query, (payment_id,))

    @staticmethod
    def add_payment(student_id, amount, payment_date, payment_method, status, description):
        query = """
            INSERT INTO payments (student_id, amount, payment_date, payment_method, status, description)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING payment_id
        """
        conn = DatabaseConnection.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (student_id, amount, payment_date, payment_method, status, description))
            payment_id = cursor.fetchone()[0]
            conn.commit()
            logger.info("Payment added: %s", payment_id)
            return True, payment_id
        except Exception as exc:
            conn.rollback()
            logger.error("Add payment error: %s", exc)
            return False, str(exc)
        finally:
            cursor.close()

    @staticmethod
    def update_payment(payment_id, student_id, amount, payment_date, payment_method, status, description):
        query = """
            UPDATE payments
            SET student_id = %s,
                amount = %s,
                payment_date = %s,
                payment_method = %s,
                status = %s,
                description = %s
            WHERE payment_id = %s
        """
        try:
            DatabaseConnection.execute_update(
                query, (student_id, amount, payment_date, payment_method, status, description, payment_id)
            )
            return True, "Payment updated successfully"
        except Exception as exc:
            logger.error("Update payment error: %s", exc)
            return False, str(exc)

    @staticmethod
    def delete_payment(payment_id):
        try:
            DatabaseConnection.execute_update("DELETE FROM payments WHERE payment_id = %s", (payment_id,))
            return True, "Payment deleted successfully"
        except Exception as exc:
            logger.error("Delete payment error: %s", exc)
            return False, str(exc)


class PaymentManagementWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Payment Management")
        self.geometry("1000x600")
        self.config(bg=COLOR_LIGHT)
        self.parent = parent
        self.create_widgets()
        self.load_payments()

    def create_widgets(self):
        top = tk.Frame(self, bg=COLOR_LIGHT)
        top.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(top, text="Search:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(top, font=FONT_NORMAL, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_payments())
        tk.Button(top, text="Search", font=FONT_NORMAL, bg=COLOR_SECONDARY, fg="white",
                  command=self.search_payments).pack(side=tk.LEFT, padx=5)
        tk.Button(top, text="Add Payment", font=FONT_NORMAL, bg=COLOR_SUCCESS, fg="white",
                  command=self.open_add).pack(side=tk.LEFT, padx=5)

        table = tk.Frame(self, bg=COLOR_LIGHT)
        table.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(
            table,
            columns=("ID", "Student", "Amount", "Payment Date", "Method", "Status"),
            show="headings"
        )
        for column, width in [("ID", 60), ("Student", 160), ("Amount", 100),
                              ("Payment Date", 110), ("Method", 120), ("Status", 100)]:
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
                  command=self.load_payments).pack(side=tk.LEFT, padx=5)

    def load_payments(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in PaymentOperations.get_all_payments():
            self.tree.insert("", tk.END, values=row)

    def search_payments(self):
        term = self.search_entry.get().strip()
        for item in self.tree.get_children():
            self.tree.delete(item)
        rows = PaymentOperations.search_payments(term) if term else PaymentOperations.get_all_payments()
        for row in rows:
            self.tree.insert("", tk.END, values=row)

    def _selected_id(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Selection", "Please select a payment first")
            return None
        return self.tree.item(selection[0], "values")[0]

    def open_add(self):
        AddPaymentWindow(self)

    def edit_selected(self):
        payment_id = self._selected_id()
        if payment_id:
            EditPaymentWindow(self, payment_id)

    def delete_selected(self):
        payment_id = self._selected_id()
        if not payment_id:
            return
        if messagebox.askyesno("Confirm", "Delete this payment?"):
            success, message = PaymentOperations.delete_payment(payment_id)
            if success:
                messagebox.showinfo("Success", message)
                self.load_payments()
            else:
                messagebox.showerror("Error", message)


class _PaymentFormBase(tk.Toplevel):
    def _load_students(self):
        students = PaymentOperations.get_students()
        self.student_map = {f"{username} ({email})": student_id for student_id, username, email in students}
        self.student_combo["values"] = list(self.student_map.keys())

    def _common_fields(self):
        form = tk.Frame(self, bg=COLOR_LIGHT)
        form.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(form, text="Student:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.student_combo = ttk.Combobox(form, font=FONT_NORMAL, state="readonly")
        self.student_combo.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Amount:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.amount_entry = tk.Entry(form, font=FONT_NORMAL)
        self.amount_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Payment Date (YYYY-MM-DD):", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.date_entry = tk.Entry(form, font=FONT_NORMAL)
        self.date_entry.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Payment Method:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.method_combo = ttk.Combobox(form, font=FONT_NORMAL, state="readonly")
        self.method_combo["values"] = ("Cash", "Bank Transfer", "Mobile Money", "Card")
        self.method_combo.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Status:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.status_combo = ttk.Combobox(form, font=FONT_NORMAL, state="readonly")
        self.status_combo["values"] = ("Pending", "Paid", "Failed")
        self.status_combo.pack(fill=tk.X, pady=(0, 10))

        tk.Label(form, text="Description:", font=FONT_NORMAL, bg=COLOR_LIGHT).pack(anchor=tk.W)
        self.description_text = tk.Text(form, font=FONT_NORMAL, height=4)
        self.description_text.pack(fill=tk.BOTH, pady=(0, 10))

        self._load_students()

    def _buttons(self, label, command):
        buttons = tk.Frame(self, bg=COLOR_LIGHT)
        buttons.pack(fill=tk.X, padx=20, pady=10)
        tk.Button(buttons, text=label, font=FONT_NORMAL, bg=COLOR_SUCCESS, fg="white",
                  command=command).pack(side=tk.LEFT, padx=5)
        tk.Button(buttons, text="Cancel", font=FONT_NORMAL, bg=COLOR_DANGER, fg="white",
                  command=self.destroy).pack(side=tk.LEFT, padx=5)


class AddPaymentWindow(_PaymentFormBase):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Add Payment")
        self.geometry("420x520")
        self.config(bg=COLOR_LIGHT)
        self.parent = parent
        self._common_fields()
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.status_combo.set("Pending")
        self._buttons("Save", self.save_payment)

    def save_payment(self):
        student_key = self.student_combo.get().strip()
        amount = self.amount_entry.get().strip()
        payment_date = self.date_entry.get().strip()
        method = self.method_combo.get().strip()
        status = self.status_combo.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()

        if not all([student_key, amount, payment_date, method, status]):
            messagebox.showerror("Validation", MSG_FILL_FIELDS)
            return
        try:
            float(amount)
        except ValueError:
            messagebox.showerror("Validation", "Amount must be numeric")
            return
        try:
            datetime.strptime(payment_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation", "Invalid payment date format. Use YYYY-MM-DD")
            return

        success, result = PaymentOperations.add_payment(
            self.student_map[student_key], float(amount), payment_date, method, status, description
        )
        if success:
            messagebox.showinfo("Success", "Payment added successfully")
            self.parent.load_payments()
            self.destroy()
        else:
            messagebox.showerror("Error", result)


class EditPaymentWindow(_PaymentFormBase):
    def __init__(self, parent, payment_id):
        super().__init__(parent)
        self.title("Edit Payment")
        self.geometry("420x520")
        self.config(bg=COLOR_LIGHT)
        self.parent = parent
        self.payment_id = payment_id
        self._common_fields()
        self._buttons("Update", self.update_payment)
        self._load_data()

    def _load_data(self):
        payment = PaymentOperations.get_payment_by_id(self.payment_id)
        if not payment:
            return
        self.student_combo.set(next((name for name, pk in self.student_map.items() if pk == payment[1]), ""))
        self.amount_entry.insert(0, str(payment[2]) if payment[2] is not None else "")
        self.date_entry.insert(0, payment[3].strftime("%Y-%m-%d") if payment[3] else "")
        self.method_combo.set(payment[4] or "")
        self.status_combo.set(payment[5] or "")
        self.description_text.insert("1.0", payment[6] or "")

    def update_payment(self):
        student_key = self.student_combo.get().strip()
        amount = self.amount_entry.get().strip()
        payment_date = self.date_entry.get().strip()
        method = self.method_combo.get().strip()
        status = self.status_combo.get().strip()
        description = self.description_text.get("1.0", tk.END).strip()

        if not all([student_key, amount, payment_date, method, status]):
            messagebox.showerror("Validation", MSG_FILL_FIELDS)
            return
        try:
            float(amount)
        except ValueError:
            messagebox.showerror("Validation", "Amount must be numeric")
            return
        try:
            datetime.strptime(payment_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Validation", "Invalid payment date format. Use YYYY-MM-DD")
            return

        success, message = PaymentOperations.update_payment(
            self.payment_id,
            self.student_map[student_key],
            float(amount),
            payment_date,
            method,
            status,
            description,
        )
        if success:
            messagebox.showinfo("Success", message)
            self.parent.load_payments()
            self.destroy()
        else:
            messagebox.showerror("Error", message)