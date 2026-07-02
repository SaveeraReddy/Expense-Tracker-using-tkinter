for i in range(10)
    print(hello)

import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
import csv

# ========== Initialize Window ==========
root = tk.Tk()
root.title("Expense Tracker by Saveera")
root.geometry("800x600")
root.configure(bg="#f2f2f2")

# ========== Initialize DB ==========
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            category TEXT,
            amount REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ========== Functions ==========

def load_expenses():
    # Clear existing table
    for row in expense_table.get_children():
        expense_table.delete(row)

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT date, category, amount FROM expenses ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        expense_table.insert("", tk.END, values=row)

    update_total()

def add_expense():
    d = date_entry.get()
    c = category_var.get()
    a = amount_entry.get()

    if d == "" or c == "" or a == "":
        messagebox.showwarning("Input Error", "Please fill in all fields.")
        return

    try:
        a = float(a)
    except ValueError:
        messagebox.showerror("Invalid Input", "Amount must be a number.")
        return

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)", (d, c, a))
    conn.commit()
    conn.close()

    messagebox.showinfo("Success", "Expense added successfully!")

    # Clear form
    amount_entry.delete(0, tk.END)
    category_var.set("")
    date_entry.delete(0, tk.END)
    date_entry.insert(0, date.today().strftime("%Y-%m-%d"))

    load_expenses()

def show_pie_chart():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()
    conn.close()

    if not data:
        messagebox.showinfo("No Data", "No expenses to visualize.")
        return

    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    fig, ax = plt.subplots()
    ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=140)
    ax.set_title("Expenses by Category")
    show_chart(fig)

def show_category_bar_chart():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category")
    data = cursor.fetchall()
    conn.close()

    if not data:
        messagebox.showinfo("No Data", "No expenses to visualize.")
        return

    categories = [row[0] for row in data]
    amounts = [row[1] for row in data]

    fig, ax = plt.subplots()
    ax.bar(categories, amounts, color='coral')
    ax.set_title("Expenses by Category")
    ax.set_ylabel("Amount")
    show_chart(fig)

def show_chart(fig):
    chart_window = tk.Toplevel(root)
    chart_window.title("Expense Chart")
    canvas = FigureCanvasTkAgg(fig, master=chart_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

def export_to_csv():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT date, category, amount FROM expenses")
    rows = cursor.fetchall()
    conn.close()

    with open("expenses.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Category", "Amount"])
        writer.writerows(rows)

    messagebox.showinfo("Export Complete", "Expenses exported to expenses.csv successfully!")

def update_total():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total = cursor.fetchone()[0]
    conn.close()
    total_label.config(text=f"Total Spent: ₹{total:.2f}" if total else "Total Spent: ₹0.00")

# ========== Layout - Entry Section ==========
entry_frame = tk.Frame(root, bg="#f2f2f2", pady=10)
entry_frame.pack(fill="x")

# Date
tk.Label(entry_frame, text="Date (YYYY-MM-DD):", bg="#f2f2f2").grid(row=0, column=0, padx=10, pady=5, sticky="w")
date_entry = tk.Entry(entry_frame)
date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
date_entry.grid(row=0, column=1, padx=5)

# Category
tk.Label(entry_frame, text="Category:", bg="#f2f2f2").grid(row=0, column=2, padx=10, pady=5, sticky="w")
category_var = tk.StringVar()
category_dropdown = ttk.Combobox(entry_frame, textvariable=category_var)
category_dropdown['values'] = ("Food", "Travel", "Shopping", "Bills", "Entertainment", "Others")
category_dropdown.grid(row=0, column=3, padx=5)

# Amount
tk.Label(entry_frame, text="Amount:", bg="#f2f2f2").grid(row=0, column=4, padx=10, pady=5, sticky="w")
amount_entry = tk.Entry(entry_frame)
amount_entry.grid(row=0, column=5, padx=5)

# Add Button
add_button = tk.Button(entry_frame, text="Add Expense", bg="#4CAF50", fg="white", padx=10, command=add_expense)
add_button.grid(row=0, column=6, padx=10)

# ========== Layout - Table Section ==========
table_frame = tk.Frame(root, bg="#f2f2f2", pady=10)
table_frame.pack(fill="both", expand=True)

columns = ("Date", "Category", "Amount")
expense_table = ttk.Treeview(table_frame, columns=columns, show="headings")
for col in columns:
    expense_table.heading(col, text=col)
    expense_table.column(col, anchor="center")
expense_table.pack(fill="both", expand=True)

# ========== Layout - Chart Buttons + Total ==========
chart_frame = tk.Frame(root, bg="#f2f2f2", pady=10)
chart_frame.pack(fill="x")

pie_button = tk.Button(chart_frame, text="Show Pie Chart", bg="#2196F3", fg="white", padx=10, command=show_pie_chart)
pie_button.pack(side="left", padx=10)

bar_button = tk.Button(chart_frame, text="Show Bar Chart", bg="#4CAF50", fg="white", padx=10, command=show_category_bar_chart)
bar_button.pack(side="left", padx=10)

export_button = tk.Button(chart_frame, text="Export to CSV", bg="#1C23E2", fg="white", padx=10, command=export_to_csv)
export_button.pack(side="right", padx=10)

total_label = tk.Label(chart_frame, text="", bg="#f2f2f2", font=("Arial", 10, "bold"))
total_label.pack(side="left", padx=20)

style = ttk.Style()
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
style.configure("Treeview", font=("Segoe UI", 10))
load_expenses()
root.mainloop()
