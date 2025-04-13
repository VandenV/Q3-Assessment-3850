import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
def connect_db():
    # Connect to SQLite database (or create it if it doesn't exist)
    return sqlite3.connect('quiz_bowl.db')

def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # Create the courses table
    cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
                        course_id INTEGER PRIMARY KEY,
                        course_name TEXT)''')

    # Create the questions table
    cursor.execute('''CREATE TABLE IF NOT EXISTS questions (
                        question_id INTEGER PRIMARY KEY,
                        question_text TEXT,
                        option_a TEXT,
                        option_b TEXT,
                        option_c TEXT,
                        option_d TEXT,
                        correct_answer TEXT,
                        course_id INTEGER,
                        FOREIGN KEY (course_id) REFERENCES courses(course_id))''')

    # Create the admin password table (if it doesn't already exist)
    # Admin Password 123456
    cursor.execute('''CREATE TABLE IF NOT EXISTS admin_password (
                        id INTEGER PRIMARY KEY,
                        password_hash TEXT)''')

    conn.commit()
    conn.close()

def save_question_to_db(question, options, correct_answer, course_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO questions (question_text, option_a, option_b, option_c, option_d, correct_answer, course_id)
                      VALUES (?, ?, ?, ?, ?, ?, ?)''', (question, options['A'], options['B'], options['C'], options['D'], correct_answer, course_id))
    conn.commit()
    conn.close()

def create_admin_password():
    def save_password():
        password = password_entry.get()
        if password:
            hashed_password = hash_password(password)
            conn = connect_db()
            cursor = conn.cursor()

            # Insert or update the password in the admin_password table
            cursor.execute('''INSERT OR REPLACE INTO admin_password (id, password_hash)
                              VALUES (1, ?)''', (hashed_password,))

            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Admin password has been set successfully!")
            password_window.destroy()

    def hash_password(password):
        # Hash the password using SHA-256
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

    # Create the window for password entry
    password_window = tk.Tk()
    password_window.title("Set Admin Password")

    tk.Label(password_window, text="Enter New Admin Password:").pack()
    password_entry = tk.Entry(password_window, show="*", width=20)
    password_entry.pack()

    tk.Button(password_window, text="Save Password", command=save_password).pack()

    password_window.mainloop()

def admin_login():
    def authenticate():
        entered_password = password_entry.get()
        # Assuming you have a hashed password stored in the database
        stored_password_hash = get_admin_password_hash()

        if hash_password(entered_password) == stored_password_hash:
            open_admin_panel()
        else:
            messagebox.showerror("Login Failed", "Invalid password. Please try again.")

    def get_admin_password_hash():
        # You can store a hashed password in the database or use a hardcoded hash for testing
        return '5f4dcc3b5aa765d61d8327deb882cf99'  # MD5 hash for "password" (just an example)

    def hash_password(password):
        return hashlib.md5(password.encode()).hexdigest()

    # Create login window
    login_window = tk.Tk()
    login_window.title("Admin Login")

    tk.Label(login_window, text="Enter Password:").pack()
    password_entry = tk.Entry(login_window, show="*", width=20)
    password_entry.pack()

    tk.Button(login_window, text="Login", command=authenticate).pack()
    login_window.mainloop()

def admin_login():
    def authenticate():
        entered_password = password_entry.get()
        stored_password_hash = get_admin_password_hash()

        if hash_password(entered_password) == stored_password_hash:
            open_admin_panel()
        else:
            messagebox.showerror("Login Failed", "Invalid password. Please try again.")

    def get_admin_password_hash():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash FROM admin_password WHERE id = 1')
        result = cursor.fetchone()
        conn.close()

        if result:
            return result[0]
        else:
            # If the password is not set yet, prompt the user to create one
            messagebox.showerror("No Admin Password", "No admin password is set. Please create one.")
            create_admin_password()
            return None

    def hash_password(password):
        # Hash the password using SHA-256
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()

    # Create login window
    login_window = tk.Tk()
    login_window.title("Admin Login")

    tk.Label(login_window, text="Enter Password:").pack()
    password_entry = tk.Entry(login_window, show="*", width=20)
    password_entry.pack()

    tk.Button(login_window, text="Login", command=authenticate).pack()
    login_window.mainloop()

def open_admin_panel():
    admin_window = tk.Tk()
    admin_window.title("Admin Panel")

    def add_question():
        add_question_window = tk.Toplevel(admin_window)
        add_question_window.title("Add New Question")

        tk.Label(add_question_window, text="Question:").pack()
        question_entry = tk.Entry(add_question_window, width=40)
        question_entry.pack()

        tk.Label(add_question_window, text="Option A:").pack()
        option_a_entry = tk.Entry(add_question_window, width=40)
        option_a_entry.pack()

        tk.Label(add_question_window, text="Option B:").pack()
        option_b_entry = tk.Entry(add_question_window, width=40)
        option_b_entry.pack()

        tk.Label(add_question_window, text="Option C:").pack()
        option_c_entry = tk.Entry(add_question_window, width=40)
        option_c_entry.pack()

        tk.Label(add_question_window, text="Option D:").pack()
        option_d_entry = tk.Entry(add_question_window, width=40)
        option_d_entry.pack()

        tk.Label(add_question_window, text="Correct Answer (A/B/C/D):").pack()
        correct_answer_entry = tk.Entry(add_question_window, width=20)
        correct_answer_entry.pack()

        def save_question():
            course_id = 1  # Assume a course ID (e.g., 1 for Math)
            question_text = question_entry.get()
            options = {
                'A': option_a_entry.get(),
                'B': option_b_entry.get(),
                'C': option_c_entry.get(),
                'D': option_d_entry.get()
            }
            correct_answer = correct_answer_entry.get()
            save_question_to_db(question_text, options, correct_answer, course_id)
            messagebox.showinfo("Success", "Question added successfully!")
            add_question_window.destroy()

        tk.Button(add_question_window, text="Save Question", command=save_question).pack()

    def view_questions():
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM questions')
        rows = cursor.fetchall()

        view_window = tk.Toplevel(admin_window)
        view_window.title("View Questions")
        for row in rows:
            question_label = tk.Label(view_window, text=f"Q: {row[1]}")
            question_label.pack()

    tk.Button(admin_window, text="Add Question", command=add_question).pack()
    tk.Button(admin_window, text="View Questions", command=view_questions).pack()

    admin_window.mainloop()

def user_interface():
    user_window = tk.Tk()
    user_window.title("Quiz Bowl")

    def start_quiz(course_name):
        quiz_window = tk.Toplevel(user_window)
        quiz_window.title(f"Quiz: {course_name}")

        # Fetch questions from the database
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM questions WHERE course_id = (SELECT course_id FROM courses WHERE course_name = ?)', (course_name,))
        questions = cursor.fetchall()

        # Display first question (simplified)
        def display_question(index=0):
            if index < len(questions):
                question = questions[index]
                question_text = question[1]
                options = [question[2], question[3], question[4], question[5]]
                correct_answer = question[6]

                tk.Label(quiz_window, text=question_text).pack()
                for option in options:
                    tk.Button(quiz_window, text=option, command=lambda ans=option: check_answer(ans, correct_answer, index + 1)).pack()

        def check_answer(user_answer, correct_answer, next_index):
            if user_answer == correct_answer:
                messagebox.showinfo("Correct!", "That's the correct answer!")
            else:
                messagebox.showinfo("Incorrect", "Sorry, that's the wrong answer.")
            display_question(next_index)

        display_question()

    tk.Button(user_window, text="Start Math Quiz", command=lambda: start_quiz("Math")).pack()
    tk.Button(user_window, text="Start Science Quiz", command=lambda: start_quiz("Science")).pack()

    user_window.mainloop()

if __name__ == "__main__":
    create_tables()  # Run this once to set up the database
    admin_login()  # Use this if you want to test admin login
    # Or, for a user interface, use:
    # user_interface()


