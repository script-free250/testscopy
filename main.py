import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import sqlite3
import datetime
import csv

class CardManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("مدير البطاقات الاحترافي")
        self.root.geometry("1200x800")
        
        # Use ttkbootstrap for a modern, dark theme
        self.style = tb.Style(theme="darkly")

        self.db_connect()
        self.create_widgets()
        self.load_data()

    def db_connect(self):
        self.conn = sqlite3.connect('cards.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS accepted_cards (
                id INTEGER PRIMARY KEY,
                visa_number TEXT NOT NULL,
                name TEXT,
                email TEXT,
                buyer_name TEXT,
                price REAL,
                notes TEXT,
                timestamp TEXT
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS declined_cards (
                id INTEGER PRIMARY KEY,
                visa_number TEXT NOT NULL,
                reason TEXT,
                notes TEXT,
                timestamp TEXT
            )
        ''')
        self.conn.commit()

    def create_widgets(self):
        # --- Main Paned Window ---
        paned_window = ttk.PanedWindow(self.root, orient=HORIZONTAL)
        paned_window.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # --- Input Frame ---
        input_frame = tb.Labelframe(paned_window, text="إدارة البطاقات", bootstyle="info")
        paned_window.add(input_frame, weight=1)

        # Visa Entry
        tb.Label(input_frame, text="رقم الفيزا:").pack(pady=(10, 5))
        self.visa_entry = tb.Entry(input_frame, bootstyle="primary")
        self.visa_entry.pack(pady=5, padx=10, fill=X)

        # Action Buttons
        btn_frame = tb.Frame(input_frame)
        btn_frame.pack(pady=10)
        tb.Button(btn_frame, text="قبول", bootstyle="success", command=self.handle_accept).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="رفض", bootstyle="danger", command=self.handle_decline).pack(side=LEFT, padx=5)

        # --- Data Display Notebook ---
        self.notebook = tb.Notebook(paned_window, bootstyle="primary")
        paned_window.add(self.notebook, weight=3)

        # --- Accepted Cards Tab ---
        self.accepted_frame = tb.Frame(self.notebook)
        self.notebook.add(self.accepted_frame, text="البطاقات المقبولة (0)")
        self.create_treeview_tab(self.accepted_frame, "accepted")

        # --- Declined Cards Tab ---
        self.declined_frame = tb.Frame(self.notebook)
        self.notebook.add(self.declined_frame, text="البطاقات المرفوضة (0)")
        self.create_treeview_tab(self.declined_frame, "declined")
        
        # --- Status Bar ---
        self.status_bar = tb.Label(self.root, text="جاهز", relief=SUNKEN, anchor=W, bootstyle="inverse-primary")
        self.status_bar.pack(side=BOTTOM, fill=X)
        
        # --- Menu ---
        self.create_menu()

    def create_treeview_tab(self, parent, card_type):
        search_frame = tb.Frame(parent)
        search_frame.pack(fill=X, padx=5, pady=5)
        tb.Label(search_frame, text="بحث:").pack(side=LEFT, padx=(0, 5))
        search_entry = tb.Entry(search_frame)
        search_entry.pack(side=LEFT, fill=X, expand=True)
        
        tree_frame = tb.Frame(parent)
        tree_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        if card_type == "accepted":
            cols = ("id", "visa_number", "name", "email", "buyer_name", "price", "notes", "timestamp")
            headings = ("ID", "رقم الفيزا", "الاسم", "الإيميل", "المشتري", "السعر", "ملاحظات", "تاريخ الإضافة")
            self.accepted_tree = self.create_treeview(tree_frame, cols, headings)
            self.accepted_search = search_entry
            search_entry.bind("<KeyRelease>", lambda e: self.search_tree(self.accepted_tree, self.accepted_search.get(), "accepted_cards"))
        else:
            cols = ("id", "visa_number", "reason", "notes", "timestamp")
            headings = ("ID", "رقم الفيزا", "سبب الرفض", "ملاحظات", "تاريخ الإضافة")
            self.declined_tree = self.create_treeview(tree_frame, cols, headings)
            self.declined_search = search_entry
            search_entry.bind("<KeyRelease>", lambda e: self.search_tree(self.declined_tree, self.declined_search.get(), "declined_cards"))

        # Total Info
        if card_type == "accepted":
            self.total_price_label = tb.Label(parent, text="إجمالي السعر: 0.00", font=("Helvetica", 12, "bold"), bootstyle="success")
            self.total_price_label.pack(pady=5, padx=10, anchor=E)
    
    def create_treeview(self, parent, columns, headings):
        tree = tb.Treeview(parent, columns=columns, show="headings", bootstyle="primary")
        for col, head in zip(columns, headings):
            tree.heading(col, text=head, command=lambda c=col: self.sort_treeview(tree, c, False))
            tree.column(col, width=100, anchor=CENTER)
        
        tree.column("id", width=40)
        tree.column("visa_number", width=150)
        tree.column("timestamp", width=140)

        # Scrollbars
        v_scroll = tb.Scrollbar(parent, orient=VERTICAL, command=tree.yview)
        v_scroll.pack(side=RIGHT, fill=Y)
        tree.configure(yscrollcommand=v_scroll.set)
        
        tree.pack(fill=BOTH, expand=True)
        
        # Context menu
        context_menu = tk.Menu(tree, tearoff=0)
        context_menu.add_command(label="تعديل", command=lambda: self.edit_entry(tree))
        context_menu.add_command(label="حذف", command=lambda: self.delete_entry(tree))
        context_menu.add_separator()
        context_menu.add_command(label="نسخ الصف", command=lambda: self.copy_to_clipboard(tree))

        tree.bind("<Button-3>", lambda e: self.show_context_menu(e, tree, context_menu))

        return tree
    
    def create_menu(self):
        menu_bar = tb.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        file_menu = tb.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Export Accepted to CSV", command=lambda: self.export_to_csv("accepted_cards"))
        file_menu.add_command(label="Export Declined to CSV", command=lambda: self.export_to_csv("declined_cards"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        help_menu = tb.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)

    def load_data(self, query=""):
        self.load_tree_data(self.accepted_tree, "accepted_cards", query)
        self.load_tree_data(self.declined_tree, "declined_cards", query)
        self.update_totals()

    def load_tree_data(self, tree, table_name, search_term=""):
        for i in tree.get_children():
            tree.delete(i)
        
        query = f"SELECT * FROM {table_name}"
        if search_term:
            # A simple search across all text-like columns
            cols = [desc[0] for desc in self.cursor.execute(f"PRAGMA table_info({table_name})").fetchall() if 'TEXT' in desc[2]]
            clauses = " OR ".join([f"{col} LIKE ?" for col in cols])
            query += f" WHERE {clauses}"
            params = [f"%{search_term}%"] * len(cols)
            records = self.cursor.execute(query, params).fetchall()
        else:
            records = self.cursor.execute(query).fetchall()

        for row in records:
            tree.insert("", "end", values=row)

    def handle_accept(self):
        visa = self.visa_entry.get().strip()
        if not visa: return messagebox.showwarning("تنبيه", "يجب إدخال رقم الفيزا.")
        
        dialog = CardDetailsDialog(self.root, "إضافة تفاصيل البطاقة", visa)
        if dialog.result:
            data = dialog.result
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("""
                INSERT INTO accepted_cards (visa_number, name, email, buyer_name, price, notes, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (visa, data['name'], data['email'], data['buyer_name'], data['price'], data['notes'], timestamp))
            self.conn.commit()
            self.load_data()
            self.visa_entry.delete(0, END)
            self.status_bar.config(text=f"تم حفظ البطاقة {visa} بنجاح.")

    def handle_decline(self):
        visa = self.visa_entry.get().strip()
        if not visa: return messagebox.showwarning("تنبيه", "يجب إدخال رقم الفيزا.")

        dialog = DeclineReasonDialog(self.root, "تحديد سبب الرفض")
        if dialog.result:
            data = dialog.result
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("""
                INSERT INTO declined_cards (visa_number, reason, notes, timestamp) VALUES (?, ?, ?, ?)
            """, (visa, data['reason'], data['notes'], timestamp))
            self.conn.commit()
            self.load_data()
            self.visa_entry.delete(0, END)
            self.status_bar.config(text=f"تم رفض البطاقة {visa}.")
    
    def update_totals(self):
        # Update accepted total price
        self.cursor.execute("SELECT SUM(price) FROM accepted_cards")
        total = self.cursor.fetchone()[0] or 0.0
        self.total_price_label.config(text=f"إجمالي السعر: {total:.2f}")

        # Update tab counts
        accepted_count = len(self.accepted_tree.get_children())
        declined_count = len(self.declined_tree.get_children())
        self.notebook.tab(0, text=f"البطاقات المقبولة ({accepted_count})")
        self.notebook.tab(1, text=f"البطاقات المرفوضة ({declined_count})")

    def search_tree(self, tree, search_term, table_name):
        self.load_tree_data(tree, table_name, search_term)

    def sort_treeview(self, tree, col, reverse):
        l = [(tree.set(k, col), k) for k in tree.get_children('')]
        
        # Try to sort numerically if possible, otherwise sort as string
        try:
            l.sort(key=lambda t: float(t[0]), reverse=reverse)
        except ValueError:
            l.sort(key=lambda t: t[0], reverse=reverse)

        for index, (val, k) in enumerate(l):
            tree.move(k, '', index)

        tree.heading(col, command=lambda: self.sort_treeview(tree, col, not reverse))

    def show_context_menu(self, event, tree, menu):
        if tree.focus():
            menu.post(event.x_root, event.y_root)

    def edit_entry(self, tree):
        if not tree.focus(): return
        
        selected_item = tree.focus()
        item_values = tree.item(selected_item, 'values')
        item_id = item_values[0]

        if tree == self.accepted_tree:
            dialog = CardDetailsDialog(self.root, "تعديل بيانات البطاقة", item_values[1], item_values)
            if dialog.result:
                data = dialog.result
                self.cursor.execute("""
                    UPDATE accepted_cards SET name=?, email=?, buyer_name=?, price=?, notes=? WHERE id=?
                """, (data['name'], data['email'], data['buyer_name'], data['price'], data['notes'], item_id))
        else: # Declined tree
            dialog = DeclineReasonDialog(self.root, "تعديل سبب الرفض", item_values)
            if dialog.result:
                data = dialog.result
                self.cursor.execute("""
                    UPDATE declined_cards SET reason=?, notes=? WHERE id=?
                """, (data['reason'], data['notes'], item_id))
        
        self.conn.commit()
        self.load_data()
        self.status_bar.config(text=f"تم تحديث السجل ID: {item_id}.")
        
    def delete_entry(self, tree):
        if not tree.focus(): return
        
        if messagebox.askyesno("تأكيد الحذف", "هل أنت متأكد من أنك تريد حذف هذا السجل؟ لا يمكن التراجع عن هذا الإجراء.", icon='warning'):
            selected_item = tree.focus()
            item_id = tree.item(selected_item, 'values')[0]
            table_name = "accepted_cards" if tree == self.accepted_tree else "declined_cards"
            
            self.cursor.execute(f"DELETE FROM {table_name} WHERE id=?", (item_id,))
            self.conn.commit()
            self.load_data()
            self.status_bar.config(text=f"تم حذف السجل ID: {item_id}.")

    def copy_to_clipboard(self, tree):
        if not tree.focus(): return
        selected_item = tree.focus()
        item_values = tree.item(selected_item, 'values')
        clipboard_text = ", ".join(map(str, item_values))
        self.root.clipboard_clear()
        self.root.clipboard_append(clipboard_text)
        self.status_bar.config(text="تم نسخ الصف إلى الحافظة.")

    def export_to_csv(self, table_name):
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")], initialfile=f"{table_name}.csv")
        if not filepath: return
        
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            header = [description[0] for description in self.cursor.description]
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(self.cursor.fetchall())
            self.status_bar.config(text=f"تم تصدير البيانات بنجاح إلى {filepath}")
        except Exception as e:
            messagebox.showerror("خطأ في التصدير", f"حدث خطأ: {e}")

    def show_about(self):
        messagebox.showinfo("حول البرنامج", "مدير البطاقات الاحترافي\nإصدار 1.0\n\nتم تطويره لتنظيم بيانات البطاقات بكفاءة.")

    def on_closing(self):
        if messagebox.askokcancel("خروج", "هل تريد الخروج؟"):
            self.conn.close()
            self.root.destroy()

class CustomDialog(tk.Toplevel):
    def __init__(self, parent, title=None, initial_data=None):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.parent = parent
        self.result = None
        
        self.initial_data = initial_data

        body = tb.Frame(self)
        self.initial_focus = self.create_body(body)
        body.pack(padx=20, pady=20)

        self.create_buttons()

        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self.geometry(f"+{parent.winfo_rootx()+50}+{parent.winfo_rooty()+50}")

        self.initial_focus.focus_set()
        self.wait_window(self)
        
    def create_body(self, master): pass
    
    def create_buttons(self):
        buttonbox = tb.Frame(self)
        ok_btn = tb.Button(buttonbox, text="حفظ", width=10, command=self.ok, bootstyle=SUCCESS)
        ok_btn.pack(side=LEFT, padx=5, pady=10)
        cancel_btn = tb.Button(buttonbox, text="إلغاء", width=10, command=self.cancel, bootstyle=DANGER)
        cancel_btn.pack(side=LEFT, padx=5, pady=10)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        buttonbox.pack()

    def ok(self, event=None):
        if not self.validate():
            self.initial_focus.focus_set()
            return
        self.withdraw()
        self.update()
        self.apply()
        self.cancel()

    def cancel(self, event=None):
        self.parent.focus_set()
        self.destroy()

    def validate(self): return 1
    def apply(self): pass

class CardDetailsDialog(CustomDialog):
    def create_body(self, master):
        is_edit = self.initial_data is not None
        
        tb.Label(master, text="الاسم على البطاقة:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.name_entry = tb.Entry(master, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tb.Label(master, text="البريد الإلكتروني:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.email_entry = tb.Entry(master, width=30)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tb.Label(master, text="اسم المشتري:").grid(row=2, column=0, sticky=W, padx=5, pady=5)
        self.buyer_name_entry = tb.Entry(master, width=30)
        self.buyer_name_entry.grid(row=2, column=1, padx=5, pady=5)
        
        tb.Label(master, text="سعر الفيزا:").grid(row=3, column=0, sticky=W, padx=5, pady=5)
        self.price_entry = tb.Entry(master, width=30)
        self.price_entry.grid(row=3, column=1, padx=5, pady=5)
        
        tb.Label(master, text="ملاحظات:").grid(row=4, column=0, sticky=W, padx=5, pady=5)
        self.notes_entry = tb.Entry(master, width=30)
        self.notes_entry.grid(row=4, column=1, padx=5, pady=5)
        
        if is_edit:
            self.name_entry.insert(0, self.initial_data[2])
            self.email_entry.insert(0, self.initial_data[3])
            self.buyer_name_entry.insert(0, self.initial_data[4])
            self.price_entry.insert(0, self.initial_data[5])
            self.notes_entry.insert(0, self.initial_data[6] if self.initial_data[6] else "")
            
        return self.name_entry

    def validate(self):
        price = self.price_entry.get()
        try:
            float(price)
            return 1
        except ValueError:
            messagebox.showwarning("خطأ", "قيمة السعر غير صالحة. الرجاء إدخال رقم.", parent=self)
            return 0

    def apply(self):
        self.result = {
            "name": self.name_entry.get().strip(),
            "email": self.email_entry.get().strip(),
            "buyer_name": self.buyer_name_entry.get().strip(),
            "price": float(self.price_entry.get()),
            "notes": self.notes_entry.get().strip()
        }

class DeclineReasonDialog(CustomDialog):
    def create_body(self, master):
        is_edit = self.initial_data is not None
        
        tb.Label(master, text="سبب الرفض:").pack(pady=5)
        reasons = ["الفيزا ملغاة (Cancelled)", "الفيزا لا تعمل (Not Working)", "رصيد غير كافٍ", "بيانات خاطئة"]
        self.reason_combo = tb.Combobox(master, values=reasons, state="readonly")
        self.reason_combo.pack(fill=X, padx=5, pady=5)
        
        tb.Label(master, text="ملاحظات:").pack(pady=5)
        self.notes_entry = tb.Entry(master, width=40)
        self.notes_entry.pack(fill=X, padx=5, pady=5)

        if is_edit:
            self.reason_combo.set(self.initial_data[2])
            self.notes_entry.insert(0, self.initial_data[3] if self.initial_data[3] else "")
        else:
            self.reason_combo.current(0)
            
        return self.reason_combo

    def apply(self):
        self.result = {
            "reason": self.reason_combo.get(),
            "notes": self.notes_entry.get().strip()
        }

if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = CardManagerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

