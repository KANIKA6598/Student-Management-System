import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
import re
import os

try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


# ==================== FIXED DATABASE PATH ====================
# Always use the database located beside this Python file.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "student_management.db")


def get_connection():
    """Open the one fixed database used by this application."""
    return sqlite3.connect(DB_PATH)


# ==================== DATABASE INITIALIZATION ====================
def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            gender TEXT,
            email TEXT,
            phone TEXT,
            course TEXT,
            marks REAL,
            address TEXT
        )
    """)

    conn.commit()
    conn.close()


init_db()


# ==================== MAIN APPLICATION ====================
class StudentManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Management System - Mini Project")
        self.root.geometry("1240x720")
        self.root.configure(bg="#f8fafc")

        self.PRIMARY_COLOR = "#0f172a"
        self.CARD_BG = "#ffffff"
        self.TEXT_COLOR = "#334155"

        self.var_id = tk.StringVar()
        self.var_name = tk.StringVar()
        self.var_gender = tk.StringVar()
        self.var_email = tk.StringVar()
        self.var_phone = tk.StringVar()
        self.var_course = tk.StringVar()
        self.var_marks = tk.StringVar()
        self.var_address = tk.StringVar()

        self.var_search_by = tk.StringVar(value="All Fields")
        self.var_search_txt = tk.StringVar()

        self.kpi_total_students = tk.StringVar(value="0")
        self.kpi_total_courses = tk.StringVar(value="0")
        self.kpi_avg_marks = tk.StringVar(value="0.0%")

        self.setup_styles()

        # Header
        header = tk.Frame(self.root, bg=self.PRIMARY_COLOR, height=65)
        header.pack(fill="x", side="top")

        tk.Label(
            header,
            text="Student Management System",
            font=("Segoe UI", 18, "bold"),
            fg="white",
            bg=self.PRIMARY_COLOR
        ).pack(side="left", padx=20, pady=15)

        tk.Button(
            header,
            text=" Graphical Analytics",
            font=("Segoe UI", 10, "bold"),
            bg="#0284c7",
            fg="white",
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2",
            command=self.show_analytics
        ).pack(side="right", padx=(0, 15), pady=15)

        tk.Button(
            header,
            text="Logout",
            font=("Segoe UI", 10, "bold"),
            bg="#dc2626",
            fg="white",
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2",
            command=self.logout
        ).pack(side="right", padx=15, pady=15)

        # Main container
        main_frame = tk.Frame(self.root, bg="#f8fafc")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)

        # ==================== LEFT PANEL ====================
        left_frame = tk.LabelFrame(
            main_frame,
            text=" Student Personal & Academic Details ",
            font=("Segoe UI", 11, "bold"),
            bg=self.CARD_BG,
            fg=self.PRIMARY_COLOR,
            bd=1,
            relief="solid"
        )
        left_frame.place(x=0, y=0, width=420, height=615)

        fields = [
            ("Student ID*", self.var_id),
            ("Full Name*", self.var_name),
            ("Gender", self.var_gender),
            ("Email ID", self.var_email),
            ("Phone Number", self.var_phone),
            ("Course / Branch", self.var_course),
            ("Marks / Percentage", self.var_marks),
            ("Address", self.var_address)
        ]

        for row_idx, (label_text, var) in enumerate(fields):
            tk.Label(
                left_frame,
                text=label_text,
                font=("Segoe UI", 10, "bold"),
                bg=self.CARD_BG,
                fg=self.TEXT_COLOR
            ).grid(row=row_idx, column=0, sticky="w", padx=15, pady=6)

            if label_text == "Gender":
                ttk.Combobox(
                    left_frame,
                    textvariable=var,
                    font=("Segoe UI", 10),
                    state="readonly",
                    values=["Male", "Female", "Other"]
                ).grid(row=row_idx, column=1, sticky="ew", padx=15, pady=6)

            elif label_text == "Course / Branch":
                ttk.Combobox(
                    left_frame,
                    textvariable=var,
                    font=("Segoe UI", 10),
                    values=["BCA", "B.Tech CSE", "B.Tech IT",
                            "B.Sc CS", "MCA", "MBA"]
                ).grid(row=row_idx, column=1, sticky="ew", padx=15, pady=6)

            else:
                tk.Entry(
                    left_frame,
                    textvariable=var,
                    font=("Segoe UI", 10),
                    bd=1,
                    relief="solid"
                ).grid(row=row_idx, column=1, sticky="ew", padx=15, pady=6)

        left_frame.grid_columnconfigure(1, weight=1)

        # Buttons
        btn_frame = tk.Frame(left_frame, bg=self.CARD_BG)
        btn_frame.place(x=15, y=370, width=385, height=220)

        tk.Button(
            btn_frame, text="Add Record",
            font=("Segoe UI", 10, "bold"),
            bg="#10b981", fg="white", bd=0,
            cursor="hand2", command=self.add_student
        ).place(x=0, y=10, width=180, height=36)

        tk.Button(
            btn_frame, text="Update Record",
            font=("Segoe UI", 10, "bold"),
            bg="#2563eb", fg="white", bd=0,
            cursor="hand2", command=self.update_student
        ).place(x=195, y=10, width=180, height=36)

        tk.Button(
            btn_frame, text="Delete Record",
            font=("Segoe UI", 10, "bold"),
            bg="#ef4444", fg="white", bd=0,
            cursor="hand2", command=self.delete_student
        ).place(x=0, y=55, width=180, height=36)

        tk.Button(
            btn_frame, text="Clear Fields",
            font=("Segoe UI", 10, "bold"),
            bg="#64748b", fg="white", bd=0,
            cursor="hand2", command=self.clear_fields
        ).place(x=195, y=55, width=180, height=36)

        tk.Button(
            btn_frame, text="Export Data to CSV",
            font=("Segoe UI", 10, "bold"),
            bg="#8b5cf6", fg="white", bd=0,
            cursor="hand2", command=self.export_csv
        ).place(x=0, y=105, width=375, height=40)

        # ==================== RIGHT PANEL ====================
        right_frame = tk.Frame(main_frame, bg="#f8fafc")
        right_frame.place(x=435, y=0, width=775, height=615)

        kpi_frame = tk.Frame(right_frame, bg="#f8fafc")
        kpi_frame.pack(fill="x", side="top", pady=(0, 15))

        cards = [
            ("Total Students", self.kpi_total_students, "#3b82f6"),
            ("Active Courses", self.kpi_total_courses, "#10b981"),
            ("Average Marks", self.kpi_avg_marks, "#8b5cf6")
        ]

        for title, variable, bg in cards:
            card = tk.Frame(kpi_frame, bg=bg, height=70)
            card.pack(side="left", fill="both", expand=True, padx=(0, 10))
            card.pack_propagate(False)

            tk.Label(
                card, text=title,
                font=("Segoe UI", 10, "bold"),
                fg="white", bg=bg
            ).pack(anchor="w", padx=12, pady=(8, 0))

            tk.Label(
                card, textvariable=variable,
                font=("Segoe UI", 18, "bold"),
                fg="white", bg=bg
            ).pack(anchor="w", padx=12)

        # Search
        search_frame = tk.LabelFrame(
            right_frame,
            text=" Search & Filter Records ",
            font=("Segoe UI", 10, "bold"),
            bg=self.CARD_BG,
            fg=self.PRIMARY_COLOR,
            bd=1,
            relief="solid"
        )
        search_frame.pack(fill="x", side="top", pady=(0, 10))

        tk.Label(
            search_frame, text="Search:",
            font=("Segoe UI", 9, "bold"),
            bg=self.CARD_BG
        ).grid(row=0, column=0, padx=8, pady=8)

        tk.Entry(
            search_frame,
            textvariable=self.var_search_txt,
            font=("Segoe UI", 9),
            bd=1,
            relief="solid",
            width=20
        ).grid(row=0, column=1, padx=5, pady=8)

        tk.Label(
            search_frame, text="By:",
            font=("Segoe UI", 9, "bold"),
            bg=self.CARD_BG
        ).grid(row=0, column=2, padx=5, pady=8)

        ttk.Combobox(
            search_frame,
            textvariable=self.var_search_by,
            font=("Segoe UI", 9),
            state="readonly",
            width=12,
            values=["All Fields", "ID", "Name", "Course", "Email"]
        ).grid(row=0, column=3, padx=5, pady=8)

        tk.Button(
            search_frame, text="Search",
            font=("Segoe UI", 9, "bold"),
            bg="#0284c7", fg="white", bd=0,
            padx=10, pady=3,
            cursor="hand2",
            command=self.search_student
        ).grid(row=0, column=4, padx=5, pady=8)

        tk.Button(
            search_frame, text="Reset",
            font=("Segoe UI", 9, "bold"),
            bg="#64748b", fg="white", bd=0,
            padx=10, pady=3,
            cursor="hand2",
            command=self.fetch_data
        ).grid(row=0, column=5, padx=5, pady=8)

        # Table
        table_frame = tk.Frame(
            right_frame,
            bg=self.CARD_BG,
            bd=1,
            relief="solid"
        )
        table_frame.pack(fill="both", expand=True)

        scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")
        scroll_y = ttk.Scrollbar(table_frame, orient="vertical")

        self.student_table = ttk.Treeview(
            table_frame,
            columns=(
                "id", "name", "gender", "email",
                "phone", "course", "marks", "address"
            ),
            xscrollcommand=scroll_x.set,
            yscrollcommand=scroll_y.set,
            selectmode="browse"
        )

        scroll_x.pack(side="bottom", fill="x")
        scroll_y.pack(side="right", fill="y")

        scroll_x.config(command=self.student_table.xview)
        scroll_y.config(command=self.student_table.yview)

        headings = {
            "id": "Student ID",
            "name": "Name",
            "gender": "Gender",
            "email": "Email ID",
            "phone": "Phone",
            "course": "Course",
            "marks": "Marks (%)",
            "address": "Address"
        }

        widths = {
            "id": 80, "name": 120, "gender": 70, "email": 140,
            "phone": 100, "course": 90, "marks": 80, "address": 130
        }

        for col in headings:
            self.student_table.heading(col, text=headings[col])
            self.student_table.column(col, width=widths[col])

        self.student_table["show"] = "headings"
        self.student_table.pack(fill="both", expand=True)

        self.student_table.bind("<ButtonRelease-1>", self.get_cursor_data)

        self.fetch_data()

        # Show the exact database being used.
        print("=" * 55)
        print("DATABASE USED:")
        print(DB_PATH)
        print("=" * 55)

    # ==================== STYLES ====================
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"),
            background="#334155",
            foreground="white"
        )

        style.configure(
            "Treeview",
            font=("Segoe UI", 9),
            rowheight=26
        )

        style.map(
            "Treeview",
            background=[("selected", "#2563eb")],
            foreground=[("selected", "white")]
        )

    # ==================== VALIDATION ====================
    def validate_inputs(self):
        if not self.var_id.get().strip() or not self.var_name.get().strip():
            messagebox.showerror(
                "Validation Error",
                "Student ID and Full Name are mandatory fields!"
            )
            return False

        email = self.var_email.get().strip()

        if email and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            messagebox.showerror(
                "Validation Error",
                "Please enter a valid Email ID."
            )
            return False

        phone = self.var_phone.get().strip()

        if phone and (not phone.isdigit() or len(phone) != 10):
            messagebox.showerror(
                "Validation Error",
                "Phone number must be exactly 10 digits."
            )
            return False

        marks = self.var_marks.get().strip()

        if marks:
            try:
                value = float(marks)

                if value < 0 or value > 100:
                    raise ValueError

            except ValueError:
                messagebox.showerror(
                    "Validation Error",
                    "Marks must be a number between 0 and 100."
                )
                return False

        return True

    # ==================== ADD ====================
    def add_student(self):
        if not self.validate_inputs():
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO students
                (id, name, gender, email, phone, course, marks, address)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.var_id.get().strip(),
                self.var_name.get().strip(),
                self.var_gender.get().strip(),
                self.var_email.get().strip(),
                self.var_phone.get().strip(),
                self.var_course.get().strip(),
                float(self.var_marks.get()) if self.var_marks.get().strip() else 0.0,
                self.var_address.get().strip()
            ))

            conn.commit()
            conn.close()

            self.fetch_data()
            self.clear_fields()

            messagebox.showinfo(
                "Success",
                "Student record added successfully!"
            )

        except sqlite3.IntegrityError:
            messagebox.showerror(
                "Database Error",
                "Student ID already exists!"
            )

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # ==================== FETCH ====================
    def fetch_data(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM students ORDER BY id")
            rows = cursor.fetchall()

            self.student_table.delete(*self.student_table.get_children())

            for row in rows:
                self.student_table.insert("", "end", values=row)

            cursor.execute("""
                SELECT COUNT(*),
                       COUNT(DISTINCT course),
                       AVG(marks)
                FROM students
            """)

            stats = cursor.fetchone()

            self.kpi_total_students.set(str(stats[0] or 0))
            self.kpi_total_courses.set(str(stats[1] or 0))
            self.kpi_avg_marks.set(
                f"{stats[2]:.1f}%" if stats[2] is not None else "0.0%"
            )

            conn.close()

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # ==================== SELECT RECORD ====================
    def get_cursor_data(self, event=None):
        selected = self.student_table.selection()

        if not selected:
            return

        item = self.student_table.item(selected[0])
        row = item.get("values")

        if not row:
            return

        self.var_id.set(str(row[0]))
        self.var_name.set(str(row[1]))
        self.var_gender.set(str(row[2]))
        self.var_email.set(str(row[3]))
        self.var_phone.set(str(row[4]))
        self.var_course.set(str(row[5]))
        self.var_marks.set(str(row[6]))
        self.var_address.set(str(row[7]))

    # ==================== UPDATE ====================
    def update_student(self):
        student_id = self.var_id.get().strip()

        if not student_id:
            messagebox.showerror(
                "Error",
                "Please select a student record from the table first!"
            )
            return

        if not self.validate_inputs():
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE students
                SET name=?,
                    gender=?,
                    email=?,
                    phone=?,
                    course=?,
                    marks=?,
                    address=?
                WHERE id=?
            """, (
                self.var_name.get().strip(),
                self.var_gender.get().strip(),
                self.var_email.get().strip(),
                self.var_phone.get().strip(),
                self.var_course.get().strip(),
                float(self.var_marks.get())
                if self.var_marks.get().strip() else 0.0,
                self.var_address.get().strip(),
                student_id
            ))

            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()

            print("Rows updated:", affected_rows)

            if affected_rows == 0:
                messagebox.showerror(
                    "Update Error",
                    f"Student ID '{student_id}' was not found."
                )
                return

            self.fetch_data()
            self.clear_fields()

            messagebox.showinfo(
                "Success",
                "Student details updated successfully!"
            )

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # ==================== DELETE ====================
    def delete_student(self):
        student_id = self.var_id.get().strip()

        if not student_id:
            messagebox.showerror(
                "Error",
                "Please select a student record from the table first!"
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete Student ID '{student_id}'?"
        )

        if not confirm:
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "DELETE FROM students WHERE id=?",
                (student_id,)
            )

            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()

            print("Rows deleted:", affected_rows)

            if affected_rows == 0:
                messagebox.showerror(
                    "Delete Error",
                    f"Student ID '{student_id}' was not found."
                )
                return

            self.fetch_data()
            self.clear_fields()

            messagebox.showinfo(
                "Success",
                "Record deleted successfully!"
            )

        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    # ==================== CLEAR ====================
    def clear_fields(self):
        self.var_id.set("")
        self.var_name.set("")
        self.var_gender.set("")
        self.var_email.set("")
        self.var_phone.set("")
        self.var_course.set("")
        self.var_marks.set("")
        self.var_address.set("")

        # Remove table selection too.
        for item in self.student_table.selection():
            self.student_table.selection_remove(item)

    # ==================== SEARCH ====================
    def search_student(self):
        search_txt = self.var_search_txt.get().strip()
        search_by = self.var_search_by.get()

        if not search_txt:
            self.fetch_data()
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            if search_by == "ID":
                query = "SELECT * FROM students WHERE id LIKE ?"
                params = (f"%{search_txt}%",)

            elif search_by == "Name":
                query = "SELECT * FROM students WHERE name LIKE ?"
                params = (f"%{search_txt}%",)

            elif search_by == "Course":
                query = "SELECT * FROM students WHERE course LIKE ?"
                params = (f"%{search_txt}%",)

            elif search_by == "Email":
                query = "SELECT * FROM students WHERE email LIKE ?"
                params = (f"%{search_txt}%",)

            else:
                query = """
                    SELECT * FROM students
                    WHERE id LIKE ?
                       OR name LIKE ?
                       OR email LIKE ?
                       OR course LIKE ?
                """
                value = f"%{search_txt}%"
                params = (value, value, value, value)

            cursor.execute(query, params)
            rows = cursor.fetchall()

            self.student_table.delete(*self.student_table.get_children())

            for row in rows:
                self.student_table.insert("", "end", values=row)

            conn.close()

        except Exception as e:
            messagebox.showerror("Search Error", str(e))

    # ==================== ANALYTICS ====================
    def show_analytics(self):
        if not MATPLOTLIB_AVAILABLE:
            messagebox.showwarning(
                "Missing Library",
                "Install matplotlib using: pip install matplotlib"
            )
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT course, COUNT(*) FROM students GROUP BY course"
            )

            data = cursor.fetchall()
            conn.close()

            if not data:
                messagebox.showinfo(
                    "No Data",
                    "Add student records first to generate analytics."
                )
                return

            courses = [
                row[0] if row[0] else "Unassigned"
                for row in data
            ]

            counts = [row[1] for row in data]

            plt.figure(figsize=(7, 5))
            plt.pie(
                counts,
                labels=courses,
                autopct="%1.1f%%",
                startangle=140
            )
            plt.title("Course-Wise Student Enrolment Distribution")
            plt.tight_layout()
            plt.show()

        except Exception as e:
            messagebox.showerror("Analytics Error", str(e))

    # ==================== EXPORT ====================
    def export_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")]
        )

        if not file_path:
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM students ORDER BY id")
            rows = cursor.fetchall()

            conn.close()

            with open(
                file_path,
                "w",
                newline="",
                encoding="utf-8"
            ) as f:
                writer = csv.writer(f)

                writer.writerow([
                    "Student ID",
                    "Name",
                    "Gender",
                    "Email",
                    "Phone",
                    "Course",
                    "Marks/GPA",
                    "Address"
                ])

                writer.writerows(rows)

            messagebox.showinfo(
                "Success",
                "Data exported successfully!"
            )

        except Exception as e:
            messagebox.showerror("Export Error", str(e))

    # ==================== LOGOUT ====================
    def logout(self):
        confirm = messagebox.askyesno(
            "Logout",
            "Are you sure you want to exit?"
        )

        if confirm:
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagementSystem(root)
    root.mainloop()
