import tkinter as tk
from tkinter import messagebox, filedialog
from datetime import datetime
import json
from tkcalendar import DateEntry  # pip install tkcalendar


class ToDoApp:
    def __init__(self, master):
        self.master = master
        master.title("THINGS TO COMPLETE")
        master.geometry("450x600")
        master.resizable(True, True)

        self.todo_items = []

        # --- Button Frame (Save/Load) ---
        button_frame = tk.Frame(master)
        button_frame.pack(fill='x', padx=20, pady=5)

        self.save_button = tk.Button(button_frame, text="Save List", command=self.save_tasks,
                                     bg='#1E88E5', fg='white', font=('Arial', 10, 'bold'), relief='raised')
        self.save_button.pack(side='left', padx=(0, 10))

        self.load_button = tk.Button(button_frame, text="Load Last Save", command=self.load_tasks,
                                     bg='#FFC107', fg='black', font=('Arial', 10, 'bold'), relief='raised')
        self.load_button.pack(side='left')

        # --- Input Section ---
        input_frame = tk.Frame(master, padx=10, pady=5)
        input_frame.pack(fill='x')

        # 1. Date Entry Field with Calendar
        date_frame = tk.Frame(input_frame)
        date_frame.pack(fill='x', pady=5)

        tk.Label(date_frame, text="Task Date:", font=('Arial', 10, 'bold')).pack(side='left', padx=(0, 5))

        self.date_entry = DateEntry(date_frame, width=12, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.pack(side='left', padx=(0, 20))

        # 2. Task Name Entry Field
        tk.Label(input_frame, text="Thing to Complete:", anchor='w').pack(fill='x', pady=(5, 0))
        self.name_entry = tk.Entry(input_frame, width=40, font=('Arial', 10))
        self.name_entry.pack(fill='x', pady=5)
        self.name_entry.bind("<Return>", self.add_task_event)

        # 3. Add Button
        self.add_button = tk.Button(input_frame, text="Add Thing", command=self.add_task,
                                    bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'), relief='raised')
        self.add_button.pack(pady=10)

        # --- List Display Section ---
        tk.Label(master, text="--- List of THINGS TO COMPLETE ---", font=('Arial', 12, 'underline'), pady=5).pack()

        self.list_outer_frame = tk.Frame(master, bg='red', bd=2, relief='solid')
        self.list_outer_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.list_inner_frame = tk.Frame(self.list_outer_frame, bg='white')
        self.list_inner_frame.pack(fill='both', expand=True, padx=2, pady=2)

        self.canvas = tk.Canvas(self.list_inner_frame, bg='white', highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self.list_inner_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='white')

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # ✅ Load tasks AFTER UI is built
        self.load_tasks(silent=True)

    # ---------------- Functions ---------------- #

    def add_task_event(self, event=None):
        self.add_task()

    def add_task(self):
        task_date = self.date_entry.get()
        task_name = self.name_entry.get().strip()

        if not task_name:
            messagebox.showwarning("Warning", "Please enter a 'Thing to Complete'.")
            return

        new_task = [task_date, task_name]
        self.todo_items.append(new_task)
        self.name_entry.delete(0, tk.END)
        self.update_task_list_display()
        self.save_tasks(silent=True)

    def update_task_list_display(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        self.todo_items.sort(key=lambda item: item[0])

        for index, (date, name) in enumerate(self.todo_items):
            task_container = tk.Frame(self.scrollable_frame, bg='white')
            task_container.pack(fill='x', padx=5, pady=2)

            task_text = f"• {date} | {name}"
            tk.Label(task_container, text=task_text, anchor='w', bg='white',
                     font=('Arial', 10)).pack(side='left', fill='x', expand=True)

            remove_btn = tk.Button(task_container, text="X", fg='red', bg='lightgray',
                                   font=('Arial', 8, 'bold'), relief='flat',
                                   command=lambda i=index: self.remove_task(i))
            remove_btn.pack(side='right', padx=(5, 0))

            if index < len(self.todo_items) - 1:
                tk.Frame(self.scrollable_frame, height=1, bg='lightgray').pack(fill='x', padx=5, pady=2)

        self.scrollable_frame.update_idletasks()
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def remove_task(self, index):
        sorted_items = sorted(self.todo_items, key=lambda item: item[0])
        item_to_delete = sorted_items[index]
        original_index = self.todo_items.index(item_to_delete)

        if messagebox.askyesno("Delete Thing", f"Are you sure you want to delete '{self.todo_items[original_index][1]}' ?"):
            del self.todo_items[original_index]
            self.update_task_list_display()
            self.save_tasks(silent=True)

    def save_tasks(self, silent=False):
        try:
            with open("things_to_complete.json", "w") as f:
                json.dump(self.todo_items, f)
            if not silent:
                messagebox.showinfo("Save Success", "Tasks saved successfully.")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save tasks: {e}")

    def load_tasks(self, silent=False):
        try:
            with open("things_to_complete.json", "r") as f:
                loaded_items = json.load(f)
                if isinstance(loaded_items, list):
                    self.todo_items = loaded_items
                    self.update_task_list_display()
                    if not silent:
                        messagebox.showinfo("Load Success", f"Loaded {len(self.todo_items)} tasks.")
                else:
                    messagebox.showerror("Load Error", "File content format is incorrect.")
        except FileNotFoundError:
            self.todo_items = []
            self.update_task_list_display()
            if not silent:
                messagebox.showwarning("Load Warning", "No saved file found.")
        except json.JSONDecodeError:
            messagebox.showerror("Load Error", "Error reading saved JSON file.")
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load tasks: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ToDoApp(root)
    root.mainloop()
