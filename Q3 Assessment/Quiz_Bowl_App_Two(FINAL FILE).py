import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# --------------------------- DATABASE SETUP --------------------------- #

# This will set up the necessarry databases if they don't already exist (which they should).
CATEGORIES = ["BMGT_3720", "DS_3520", "DS_3850", "DS_3860", "FIN_3210"]

class QuizDatabase:
    def __init__(self):
        self.conn = sqlite3.connect("quiz.db")
        self.create_tables()

    def create_tables(self):
        for category in CATEGORIES:
            self.conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {category} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT,
                    option1 TEXT,
                    option2 TEXT,
                    option3 TEXT,
                    option4 TEXT,
                    answer TEXT
                )
            """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS Scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                score INTEGER,
                total INTEGER,
                missed_questions TEXT
            )
        """)
        self.conn.commit()

# This allows user to add questions for each subject.
    def add_question(self, category, question, options, answer):
        try:
            self.conn.execute(f"INSERT INTO {category} (question, option1, option2, option3, option4, answer) VALUES (?, ?, ?, ?, ?, ?)",
                              (question, *options, answer))
            self.conn.commit()
        except Exception as e:
            messagebox.showerror("Database Error", str(e))

    def get_questions(self, category):
        cursor = self.conn.execute(f"SELECT * FROM {category}")
        return cursor.fetchall()

    def delete_question(self, category, qid):
        self.conn.execute(f"DELETE FROM {category} WHERE id = ?", (qid,))
        self.conn.commit()

    def update_question(self, category, qid, question, options, answer):
        self.conn.execute(f"""
            UPDATE {category}
            SET question=?, option1=?, option2=?, option3=?, option4=?, answer=?
            WHERE id=?
        """, (question, *options, answer, qid))
        self.conn.commit()

    def save_score(self, category, score, total, missed_questions):
        missed_str = "|".join(missed_questions)
        self.conn.execute("INSERT INTO Scores (category, score, total, missed_questions) VALUES (?, ?, ?, ?)",
                          (category, score, total, missed_str))
        self.conn.commit()

    def get_scores(self):
        cursor = self.conn.execute("SELECT * FROM Scores")
        return cursor.fetchall()

# --------------------------- QUESTION CLASS --------------------------- #

# This will ask the questions.
class Question:
    def __init__(self, qtext, options, answer):
        self.qtext = qtext
        self.options = options
        self.answer = answer

    def is_correct(self, selected):
        return selected == self.answer

# --------------------------- ADMIN INTERFACE --------------------------- #

# This is the admin panel for the app.
class AdminPanel:
    def __init__(self, master, db):
        self.master = master
        self.db = db
        self.login_screen()

    def login_screen(self):
        self.clear()
        tk.Label(self.master, text="Admin Login").pack()
        self.pass_entry = tk.Entry(self.master, show="*")
        self.pass_entry.pack()
        tk.Button(self.master, text="Login", command=self.check_login).pack()

    def check_login(self):
        if self.pass_entry.get() == "admin123":
            self.show_menu()
        else:
            messagebox.showerror("Login Failed", "Incorrect password")

    def show_menu(self):
        self.clear()
        tk.Button(self.master, text="Add Question", command=self.add_question_ui).pack()
        tk.Button(self.master, text="View Questions", command=self.view_questions_ui).pack()
        tk.Button(self.master, text="View Scores", command=self.view_scores_ui).pack()

    def add_question_ui(self):
        self.clear()
        self.category = tk.StringVar()
        tk.Label(self.master, text="Select Category:").pack()
        ttk.Combobox(self.master, textvariable=self.category, values=CATEGORIES).pack()

        tk.Label(self.master, text="Question Text:").pack()
        self.q_entry = tk.Entry(self.master, width=50)
        self.q_entry.pack()

        self.options = []
        for i in range(4):
            tk.Label(self.master, text=f"Option {i+1}:").pack()
            entry = tk.Entry(self.master, width=50)
            entry.pack()
            self.options.append(entry)

        tk.Label(self.master, text="Correct Answer:").pack()
        self.answer = tk.Entry(self.master, width=50)
        self.answer.pack()

        tk.Button(self.master, text="Submit", command=self.submit_question).pack()
        tk.Button(self.master, text="Back", command=self.show_menu).pack()

    def submit_question(self):
        options = [opt.get() for opt in self.options]
        self.db.add_question(self.category.get(), self.q_entry.get(), options, self.answer.get())
        messagebox.showinfo("Success", "Question added successfully")

    def view_questions_ui(self):
        self.clear()
        self.cat = tk.StringVar()
        tk.Label(self.master, text="Select Category:").pack()
        cb = ttk.Combobox(self.master, textvariable=self.cat, values=CATEGORIES)
        cb.pack()
        tk.Button(self.master, text="Load", command=self.load_questions).pack()

        self.tree = ttk.Treeview(self.master, columns=("ID", "Question", "Answer"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=200)
        self.tree.pack()

        tk.Button(self.master, text="Edit Selected", command=self.edit_question).pack()
        tk.Button(self.master, text="Delete Selected", command=self.delete_question).pack()
        tk.Button(self.master, text="Back", command=self.show_menu).pack()

    def load_questions(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        rows = self.db.get_questions(self.cat.get())
        for row in rows:
            self.tree.insert("", "end", values=(row[0], row[1], row[-1]))

    def delete_question(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected)
            qid = item['values'][0]
            self.db.delete_question(self.cat.get(), qid)
            self.load_questions()
            messagebox.showinfo("Deleted", "Question deleted successfully.")

    def edit_question(self):
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected)
            qid = item['values'][0]
            question_data = next(q for q in self.db.get_questions(self.cat.get()) if q[0] == qid)
            self.edit_question_ui(qid, question_data)

    def edit_question_ui(self, qid, data):
        self.clear()
        tk.Label(self.master, text=f"Editing Question ID {qid}").pack()

        tk.Label(self.master, text="Question Text:").pack()
        q_entry = tk.Entry(self.master, width=50)
        q_entry.insert(0, data[1])
        q_entry.pack()

        entries = []
        for i, opt in enumerate(data[2:6]):
            tk.Label(self.master, text=f"Option {i+1}:").pack()
            entry = tk.Entry(self.master, width=50)
            entry.insert(0, opt)
            entry.pack()
            entries.append(entry)

        tk.Label(self.master, text="Correct Answer:").pack()
        a_entry = tk.Entry(self.master, width=50)
        a_entry.insert(0, data[6])
        a_entry.pack()

        def save():
            options = [e.get() for e in entries]
            self.db.update_question(self.cat.get(), qid, q_entry.get(), options, a_entry.get())
            messagebox.showinfo("Updated", "Question updated successfully.")
            self.view_questions_ui()

        tk.Button(self.master, text="Save Changes", command=save).pack()
        tk.Button(self.master, text="Cancel", command=self.view_questions_ui).pack()

    def view_scores_ui(self):
        self.clear()
        tk.Label(self.master, text="Previous Quiz Scores").pack()
        self.score_tree = ttk.Treeview(self.master, columns=("ID", "Category", "Score", "Total"), show="headings")
        for col in self.score_tree["columns"]:
            self.score_tree.heading(col, text=col)
            self.score_tree.column(col, width=100, anchor="w")
        self.score_tree.pack(fill=tk.BOTH, expand=True)

        for row in self.db.get_scores():
            self.score_tree.insert("", "end", values=(row[0], row[1], row[2], row[3]), tags=(row[4],))

        self.score_tree.bind("<Double-1>", self.view_missed_questions)
        tk.Button(self.master, text="Back", command=self.show_menu).pack()

    def view_missed_questions(self, event):
        selected = self.score_tree.selection()
        if not selected:
            return
        item = self.score_tree.item(selected)
        missed_data = item['tags'][0]
        if missed_data:
            questions = missed_data.split("|")
            top = tk.Toplevel(self.master)
            top.title("Missed Questions")
            tk.Label(top, text="Missed Questions", font=("Arial", 14)).pack(pady=5)
            for q in questions:
                tk.Label(top, text=q, wraplength=400, justify="left").pack(anchor="w", padx=10, pady=2)

    def clear(self):
        for widget in self.master.winfo_children():
            widget.destroy()

# --------------------------- USER INTERFACE --------------------------- #

# This is all the stuff for the student quiz.
class QuizApp:
    def __init__(self, root, db):
        self.root = root
        self.db = db
        self.welcome_screen()

    def welcome_screen(self):
        self.clear()
        tk.Label(self.root, text="Welcome to the Quiz App").pack()
        tk.Button(self.root, text="Start Quiz", command=self.category_selection).pack()

    def category_selection(self):
        self.clear()
        self.cat = tk.StringVar()
        tk.Label(self.root, text="Select Quiz Category:").pack()
        ttk.Combobox(self.root, textvariable=self.cat, values=CATEGORIES).pack()
        tk.Button(self.root, text="Begin", command=self.start_quiz).pack()

    def start_quiz(self):
        selected_category = self.cat.get()
        if not selected_category:
            messagebox.showwarning("No Category", "Please select a quiz category.")
            return

        questions_data = self.db.get_questions(selected_category)
        if not questions_data:
            messagebox.showinfo("No Questions", "There are no questions in this category yet.")
            return

        self.category = selected_category
        self.questions = [Question(row[1], row[2:6], row[6]) for row in questions_data]
        self.q_index = 0
        self.score = 0
        self.missed = []
        self.show_question()

    def show_question(self):
        self.clear()
        if self.q_index < len(self.questions):
            q = self.questions[self.q_index]
            tk.Label(self.root, text=f"Q{self.q_index + 1}: {q.qtext}", wraplength=500, justify="left").pack(pady=10)
            self.selected = tk.StringVar()
            for opt in q.options:
                tk.Radiobutton(self.root, text=opt, variable=self.selected, value=opt).pack(anchor="w")
            tk.Button(self.root, text="Submit", command=self.submit_answer).pack(pady=10)
        else:
            self.show_result()

    def submit_answer(self):
        selected_answer = self.selected.get()
        if not selected_answer:
            messagebox.showwarning("No Selection", "Please select an answer before submitting.")
            return

        correct_answer = self.questions[self.q_index].answer
        if self.questions[self.q_index].is_correct(selected_answer):
            self.score += 1
            messagebox.showinfo("Correct", "That's correct!")
        else:
            self.missed.append(self.questions[self.q_index].qtext)
            messagebox.showinfo("Incorrect", f"Wrong! Correct answer: {correct_answer}")
        self.q_index += 1
        self.show_question()

    def show_result(self):
        self.db.save_score(self.category, self.score, len(self.questions), self.missed)
        self.clear()
        tk.Label(self.root, text=f"Quiz Complete! Your score: {self.score}/{len(self.questions)}").pack()
        tk.Button(self.root, text="Back to Home", command=self.welcome_screen).pack()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

# --------------------------- MAIN APP --------------------------- #

def main():
    db = QuizDatabase()
    root = tk.Tk()
    root.title("Quiz Application")

    def open_admin():
        win = tk.Toplevel()
        win.title("Admin Panel")
        AdminPanel(win, db)

    QuizApp(root, db)
    tk.Button(root, text="Admin Login", command=open_admin).pack(side=tk.BOTTOM)

    root.mainloop()

if __name__ == "__main__":
    main()

