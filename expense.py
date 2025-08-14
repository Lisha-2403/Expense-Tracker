import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

# --- Database Setup ---
import os
import sqlite3

# Make a folder on Desktop for your database (optional)
os.makedirs(os.path.expanduser("~/Desktop/ExpenseTracker"), exist_ok=True)

# Set the database path
db_path = os.path.expanduser("~/Desktop/ExpenseTracker/expenses.db")
conn = sqlite3.connect(db_path)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    amount REAL NOT NULL,
    category TEXT NOT NULL,
    date TEXT NOT NULL,
    notes TEXT
)
""")
conn.commit()

# --- Functions ---
def add_expense():
    amount = amount_entry.get()
    category = category_entry.get()
    date = date_entry.get()
    notes = notes_entry.get()

    if not amount or not category or not date:
        messagebox.showwarning("Warning", "Please fill all required fields!")
        return

    try:
        cursor.execute("INSERT INTO expenses (amount, category, date, notes) VALUES (?, ?, ?, ?)",
                       (float(amount), category, date, notes))
        conn.commit()
        messagebox.showinfo("Success", "Expense added successfully!")
        amount_entry.delete(0, tk.END)
        category_entry.delete(0, tk.END)
        date_entry.delete(0, tk.END)
        notes_entry.delete(0, tk.END)
        view_expenses()
    except ValueError:
        messagebox.showerror("Error", "Amount must be a number.")

def view_expenses():
    for row in tree.get_children():
        tree.delete(row)
    cursor.execute("SELECT * FROM expenses ORDER BY date DESC")
    for row in cursor.fetchall():
        tree.insert("", tk.END, values=row)

def delete_expense():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Warning", "Select an expense to delete!")
        return
    for sel in selected:
        cursor.execute("DELETE FROM expenses WHERE id=?", (tree.item(sel)['values'][0],))
    conn.commit()
    view_expenses()

def calculate_total():
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0]
    total_label.config(text=f"Total Expenses: ₹{total if total else 0:.2f}")

# --- GUI ---
root = tk.Tk()
root.title("Expense Tracker")
root.geometry("600x500")

# Input Frame
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="Amount*").grid(row=0, column=0)
amount_entry = tk.Entry(input_frame)
amount_entry.grid(row=0, column=1)

tk.Label(input_frame, text="Category*").grid(row=1, column=0)
category_entry = tk.Entry(input_frame)
category_entry.grid(row=1, column=1)

tk.Label(input_frame, text="Date* (YYYY-MM-DD)").grid(row=2, column=0)
date_entry = tk.Entry(input_frame)
date_entry.grid(row=2, column=1)
date_entry.insert(0, datetime.today().strftime('%Y-%m-%d'))

tk.Label(input_frame, text="Notes").grid(row=3, column=0)
notes_entry = tk.Entry(input_frame)
notes_entry.grid(row=3, column=1)

tk.Button(input_frame, text="Add Expense", command=add_expense).grid(row=4, column=0, columnspan=2, pady=5)

# Expense Table
tree = ttk.Treeview(root, columns=("ID", "Amount", "Category", "Date", "Notes"), show='headings')
tree.heading("ID", text="ID")
tree.heading("Amount", text="Amount")
tree.heading("Category", text="Category")
tree.heading("Date", text="Date")
tree.heading("Notes", text="Notes")
tree.pack(pady=20)

tk.Button(root, text="Delete Selected Expense", command=delete_expense).pack()
total_label = tk.Label(root, text="Total Expenses: ₹0.00", font=("Arial", 14))
total_label.pack(pady=10)

# Initialize Table
view_expenses()
calculate_total()

root.mainloop()
conn.close()
