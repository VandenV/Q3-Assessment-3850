def open_main_window():
    main_window = tk.Tk()
    main_window.title("Welcome to the Quiz Bowl")

    def admin_login():
        # Trigger the Admin Login function (already defined)
        admin_login()

    def student_login():
        # Trigger the Student Login function (class selection)
        student_class_selection()

    # Buttons for Admin and Student login
    tk.Button(main_window, text="Admin Login", command=admin_login).pack(pady=10)
    tk.Button(main_window, text="Student Login", command=student_login).pack(pady=10)

    main_window.mainloop()

def student_class_selection():
    # Create a new window for class selection
    class_selection_window = tk.Tk()
    class_selection_window.title("Select Class for Quiz")

    tk.Label(class_selection_window, text="Select a class to take a quiz").pack(pady=10)

    def start_quiz(course_name):
        # This function will start the quiz for the selected course
        start_quiz_window(course_name)

    # Buttons for different classes
    tk.Button(class_selection_window, text="Math", command=lambda: start_quiz("Math")).pack(pady=10)
    tk.Button(class_selection_window, text="Science", command=lambda: start_quiz("Science")).pack(pady=10)
    tk.Button(class_selection_window, text="History", command=lambda: start_quiz("History")).pack(pady=10)
    tk.Button(class_selection_window, text="Literature", command=lambda: start_quiz("Literature")).pack(pady=10)

    class_selection_window.mainloop()


def start_quiz_window(course_name):
    quiz_window = tk.Tk()
    quiz_window.title(f"{course_name} Quiz")

    # Fetch 5 questions from the database based on the selected course
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM questions WHERE course_id = (SELECT course_id FROM courses WHERE course_name = ?) LIMIT 5', (course_name,))
    questions = cursor.fetchall()
    conn.close()

    user_answers = []
    question_index = 0

    def display_question():
        nonlocal question_index

        if question_index < len(questions):
            question = questions[question_index]
            question_text = question[1]
            options = [question[2], question[3], question[4], question[5]]
            correct_answer = question[6]

            # Clear previous question (if any)
            for widget in quiz_window.winfo_children():
                widget.destroy()

            tk.Label(quiz_window, text=question_text).pack(pady=10)

            def record_answer(answer):
                user_answers.append((question_index, answer))
                question_index += 1
                display_question()

            for option in options:
                tk.Button(quiz_window, text=option, command=lambda ans=option: record_answer(ans)).pack(pady=5)

            if question_index == len(questions):
                tk.Button(quiz_window, text="Submit Quiz", command=show_results).pack(pady=10)

        else:
            show_results()

    def show_results():
        # Calculate the score based on the answers
        score = 0
        for i, answer in user_answers:
            correct_answer = questions[i][6]  # Correct answer from database
            if answer == correct_answer:
                score += 1

        messagebox.showinfo("Quiz Completed", f"Your score is {score} out of 5.")
        quiz_window.destroy()

    # Start with the first question
    display_question()

    quiz_window.mainloop()


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
            messagebox.showerror("No Admin Password", "No admin password is set. Please create one.")
            create_admin_password()
            return None

    def hash_password(password):
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


if __name__ == "__main__":
    create_tables()  # Run this once to set up the database
    open_main_window()  # Open the main window for choosing Admin or Student login
