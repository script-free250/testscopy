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
        self.root.geometry("1300x800")
        
        self.style = tb.Style(theme="darkly")
        self.db_connect()
        self.create_widgets()
        self.load_data()

    def db_connect(self):
        self.conn = sqlite3.connect('cards.db')
        self.conn.row_factory = sqlite3.Row
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
        main_paned_window = ttk.PanedWindow(self.root, orient=HORIZONTAL)
        main_paned_window.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # --- Left Pane (Controls) ---
        controls_frame = tb.Frame(main_paned_window)
        main_paned_window.add(controls_frame, weight=1)

        # --- Card Management Frame ---
        mgmt_frame = tb.Labelframe(controls_frame, text="إدارة البطاقات", bootstyle="info")
        mgmt_frame.pack(fill=X, padx=5, pady=5, anchor="n")
        
        tb.Label(mgmt_frame, text="رقم الفيزا:").pack(pady=(10, 5), padx=10, fill=X)
        self.visa_entry = tb.Entry(mgmt_frame, bootstyle="primary")
        self.visa_entry.pack(pady=5, padx=10, fill=X)
        
        btn_frame = tb.Frame(mgmt_frame)
        btn_frame.pack(pady=10)
        tb.Button(btn_frame, text="قبول ➕", bootstyle="success-outline", command=self.handle_accept).pack(side=LEFT, padx=5)
        tb.Button(btn_frame, text="رفض ➖", bootstyle="danger-outline", command=self.handle_decline).pack(side=LEFT, padx=5)

        # --- Search Frame ---
        search_frame = tb.Labelframe(controls_frame, text="قسم البحث", bootstyle="info")
        search_frame.pack(fill=X, padx=5, pady=15, anchor="n")
        
        tb.Label(search_frame, text="كلمة البحث:").pack(pady=(10, 5), padx=10, fill=X)
        self.search_entry = tb.Entry(search_frame, bootstyle="primary")
        self.search_entry.pack(pady=5, padx=10, fill=X)
        
        self.search_scope = tk.StringVar(value="all")
        scope_frame = tb.Frame(search_frame)
        scope_frame.pack(pady=5)
        tb.Radiobutton(scope_frame, text="الكل", variable=self.search_scope, value="all", bootstyle="primary").pack(side=RIGHT, padx=5)
        tb.Radiobutton(scope_frame, text="المقبولة", variable=self.search_scope, value="accepted", bootstyle="success").pack(side=RIGHT, padx=5)
        tb.Radiobutton(scope_frame, text="المرفوضة", variable=self.search_scope, value="declined", bootstyle="danger").pack(side=RIGHT, padx=5)
        
        tb.Button(search_frame, text="بحث 🔎", bootstyle="primary", command=self.execute_search).pack(pady=10, fill=X, padx=10)

        # --- Right Pane (Data) ---
        self.notebook = tb.Notebook(main_paned_window, bootstyle="primary")
        main_paned_window.add(self.notebook, weight=3)

        self.accepted_frame = tb.Frame(self.notebook)
        self.notebook.add(self.accepted_frame, text="البطاقات المقبولة (0)")
        self.accepted_tree = self.create_treeview_tab(self.accepted_frame, "accepted")

        self.declined_frame = tb.Frame(self.notebook)
        self.notebook.add(self.declined_frame, text="البطاقات المرفوضة (0)")
        self.declined_tree = self.create_treeview_tab(self.declined_frame, "declined")

        # --- Status Bar ---
        self.status_bar = tb.Label(self.root, text="جاهز", relief=SUNKEN, anchor=W, bootstyle="inverse-primary")
        self.status_bar.pack(side=BOTTOM, fill=X)
        self.create_menu()

    def create_treeview_tab(self, parent, card_type):
        tree_frame = tb.Frame(parent)
        tree_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        if card_type == "accepted":
            cols = ("id", "visa_number", "name", "email", "buyer_name", "price", "notes", "timestamp")
            headings = ("ID", "رقم الفيزا", "الاسم", "الإيميل", "المشتري", "السعر", "ملاحظات", "تاريخ الإضافة")
            tree = self.create_treeview(tree_frame, cols, headings)
            # Total Info
            self.total_price_label = tb.Label(parent, text="إجمالي السعر: 0.00", font=("Helvetica", 12, "bold"), bootstyle="success")
            self.total_price_label.pack(pady=5, padx=10, anchor=E)
        else: # declined
            cols = ("id", "visa_number", "reason", "notes", "timestamp")
            headings = ("ID", "رقم الفيزا", "سبب الرفض", "ملاحظات", "تاريخ الإضافة")
            tree = self.create_treeview(tree_frame, cols, headings)
        return tree

    def create_treeview(self, parent, columns, headings):
        tree = tb.Treeview(parent, columns=columns, show="headings", bootstyle="primary")
        for col, head in zip(columns, headings):
            tree.heading(col, text=head, command=lambda c=col, t=tree: self.sort_treeview(t, c, False))
            tree.column(col, width=100, anchor=CENTER)
        
        tree.column("id", width=40, anchor="center")
        tree.column("visa_number", width=150, anchor="w")
        tree.column("notes", width=150, anchor="w")
        tree.column("timestamp", width=140, anchor="center")

        v_scroll = tb.Scrollbar(parent, orient=VERTICAL, command=tree.yview, bootstyle="round")
        v_scroll.pack(side=RIGHT, fill=Y)
        tree.configure(yscrollcommand=v_scroll.set)
        
        tree.pack(fill=BOTH, expand=True)
        
        context_menu = tk.Menu(tree, tearoff=0)
        context_menu.add_command(label="تعديل", command=lambda t=tree: self.edit_entry(t))
        context_menu.add_command(label="حذف", command=lambda t=tree: self.delete_entry(t))
        context_menu.add_separator()
        context_menu.add_command(label="نسخ الصف", command=lambda t=tree: self.copy_to_clipboard(t))
        tree.bind("<Button-3>", lambda e, t=tree, m=context_menu: self.show_context_menu(e, t, m))

        return tree

    def create_menu(self):
        # (Same as before)
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

    def load_data(self):
        self.execute_search()
        self.update_totals()

    def execute_search(self):
        search_term = self.search_entry.get().strip()
        scope = self.search_scope.get()
        
        if scope == "all" or scope == "accepted":
            self.load_tree_data(self.accepted_tree, "accepted_cards", search_term)
        if scope == "all" or scope == "declined":
            self.load_tree_data(self.declined_tree, "declined_cards", search_term)

        self.update_totals()
        self.status_bar.config(text=f"تم عرض نتائج البحث عن: '{search_term}'")

    def load_tree_data(self, tree, table_name, search_term=""):
        for i in tree.get_children():
            tree.delete(i)
        
        query = f"SELECT * FROM {table_name}"
        params = []
        if search_term:
            cols_info = self.cursor.execute(f"PRAGMA table_info({table_name})").fetchall()
            cols = [row['name'] for row in cols_info]
            clauses = " OR ".join([f"CAST({col} AS TEXT) LIKE ?" for col in cols])
            query += f" WHERE {clauses}"
            params = [f"%{search_term}%"] * len(cols)
        
        records = self.cursor.execute(query, params).fetchall()
        for row in records:
            tree.insert("", "end", values=tuple(row), tags=('new_item',))

    def handle_accept(self):
        visa = self.visa_entry.get().strip()
        if not visa: return messagebox.showwarning("تنبيه", "يجب إدخال رقم الفيزا.")
        
        dialog = CardDetailsDialog(self.root, title="إضافة تفاصيل البطاقة")
        if dialog.result:
            data = dialog.result
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("""
                INSERT INTO accepted_cards (visa_number, name, email, buyer_name, price, notes, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (visa, data['name'], data['email'], data['buyer_name'], data['price'], data['notes'], timestamp))
            self.conn.commit()
            new_id = self.cursor.lastrowid
            
            self.load_data()
            self.visa_entry.delete(0, END)
            self.status_bar.config(text=f"تم حفظ البطاقة {visa} بنجاح.")
            
            # Find the newly inserted item and animate it
            for item in self.accepted_tree.get_children():
                if int(self.accepted_tree.item(item, 'values')[0]) == new_id:
                    self.animate_new_row(self.accepted_tree, item)
                    break

    def handle_decline(self):
        visa = self.visa_entry.get().strip()
        if not visa: return messagebox.showwarning("تنبيه", "يجب إدخال رقم الفيزا.")

        dialog = DeclineReasonDialog(self.root, title="تحديد سبب الرفض")
        if dialog.result:
            data = dialog.result
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute("""
                INSERT INTO declined_cards (visa_number, reason, notes, timestamp) VALUES (?, ?, ?, ?)
            """, (visa, data['reason'], data['notes'], timestamp))
            self.conn.commit()
            new_id = self.cursor.lastrowid
            
            self.load_data()
            self.visa_entry.delete(0, END)
            self.status_bar.config(text=f"تم رفض البطاقة {visa}.")

            # Find the newly inserted item and animate it
            for item in self.declined_tree.get_children():
                if int(self.declined_tree.item(item, 'values')[0]) == new_id:
                    self.animate_new_row(self.declined_tree, item)
                    break

    def update_totals(self):
        self.cursor.execute("SELECT SUM(price) FROM accepted_cards")
        total = self.cursor.fetchone()[0] or 0.0
        self.total_price_label.config(text=f"إجمالي السعر: {total:.2f}")

        accepted_count = len(self.accepted_tree.get_children())
        declined_count = len(self.declined_tree.get_children())
        self.notebook.tab(0, text=f"البطاقات المقبولة ({accepted_count})")
        self.notebook.tab(1, text=f"البطاقات المرفوضة ({declined_count})")

    def sort_treeview(self, tree, col, reverse):
        # (Same as before)
        l = [(tree.set(k, col), k) for k in tree.get_children('')]
        try: l.sort(key=lambda t: float(t[0]), reverse=reverse)
        except (ValueError, TypeError): l.sort(key=lambda t: str(t[0]), reverse=reverse)
        for index, (val, k) in enumerate(l): tree.move(k, '', index)
        tree.heading(col, command=lambda: self.sort_treeview(tree, col, not reverse))

    def show_context_menu(self, event, tree, menu):
        if tree.identify_row(event.y):
            tree.selection_set(tree.identify_row(event.y))
            menu.post(event.x_root, event.y_root)

    def edit_entry(self, tree):
        if not tree.focus(): return
        
        selected_item = tree.focus()
        item_values = tree.item(selected_item, 'values')
        item_id = item_values[0]

        try:
            if tree == self.accepted_tree:
                dialog = CardDetailsDialog(self.root, title="تعديل بيانات البطاقة", initial_data=item_values)
                if dialog.result:
                    data = dialog.result
                    self.cursor.execute("""
                        UPDATE accepted_cards SET name=?, email=?, buyer_name=?, price=?, notes=? WHERE id=?
                    """, (data['name'], data['email'], data['buyer_name'], data['price'], data['notes'], item_id))
            else: # Declined tree
                dialog = DeclineReasonDialog(self.root, title="تعديل سبب الرفض", initial_data=item_values)
                if dialog.result:
                    data = dialog.result
                    self.cursor.execute("UPDATE declined_cards SET reason=?, notes=? WHERE id=?", (data['reason'], data['notes'], item_id))
            
            self.conn.commit()
            self.load_data()
            self.status_bar.config(text=f"تم تحديث السجل ID: {item_id}.")
        except Exception as e:
            messagebox.showerror("خطأ في التعديل", f"حدث خطأ: {e}")
        
    def delete_entry(self, tree):
        # (Same as before, now with correct context)
        if not tree.focus(): return
        if messagebox.askyesno("تأكيد الحذف", "هل أنت متأكد من أنك تريد حذف هذا السجل؟", icon='warning'):
            selected_item = tree.focus()
            item_id = tree.item(selected_item, 'values')[0]
            table_name = "accepted_cards" if tree == self.accepted_tree else "declined_cards"
            
            self.cursor.execute(f"DELETE FROM {table_name} WHERE id=?", (item_id,))
            self.conn.commit()
            self.load_data()
            self.status_bar.config(text=f"تم حذف السجل ID: {item_id}.")

    def copy_to_clipboard(self, tree):
        # (Same as before)
        if not tree.focus(): return
        selected_item = tree.focus()
        item_values = tree.item(selected_item, 'values')
        clipboard_text = ", ".join(map(str, item_values))
        self.root.clipboard_clear()
        self.root.clipboard_append(clipboard_text)
        self.status_bar.config(text="تم نسخ الصف إلى الحافظة.")

    def export_to_csv(self, table_name):
        # (Same as before)
        filepath = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")], initialfile=f"{table_name}.csv")
        if not filepath: return
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            header = [description[0] for description in self.cursor.description]
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(self.cursor.fetchall())
            self.status_bar.config(text=f"تم تصدير البيانات بنجاح إلى {filepath}")
        except Exception as e: messagebox.showerror("خطأ في التصدير", f"حدث خطأ: {e}")

    def show_about(self):
        messagebox.showinfo("حول البرنامج", "مدير البطاقات الاحترافي\nإصدار 2.0\n\nتصميم وتطوير لتسهيل إدارة البطاقات.")
    
    def on_closing(self):
        if messagebox.askokcancel("خروج", "هل تريد الخروج؟"):
            self.conn.close()
            self.root.destroy()
            
    def animate_new_row(self, tree, item_id, step=15):
        """Animates the background of a new row from green to default."""
        if step < 0:
            tree.tag_configure('new', background='') # Reset to default
            return
        
        # A simple green fade effect
        # On dark themes, green is very visible. We fade the hex value.
        color_val = step * 16 # 15*16=240 -> F0
        hex_color = f'#00{color_val:02x}00'
        tree.tag_configure('new', background=hex_color)
        tree.item(item_id, tags=('new',))
        
        self.root.after(50, lambda: self.animate_new_row(tree, item_id, step - 1))


# --- DIALOGS (Modified to handle initial_data correctly) ---
class CustomDialog(tk.Toplevel):
    # (Largely the same, just constructor change)
    def __init__(self, parent, title=None, initial_data=None):
        super().__init__(parent)
        self.transient(parent)
        if title: self.title(title)
        self.parent = parent
        self.result = None
        self.initial_data = initial_data
        
        body = tb.Frame(self)
        self.initial_focus = self.create_body(body)
        body.pack(padx=20, pady=20)

        self.create_buttons()
        self.grab_set()
        if not self.initial_focus: self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry(f"+{parent.winfo_rootx()+50}+{parent.winfo_rooty()+50}")
        self.initial_focus.focus_set()
        self.wait_window(self)
        
    def create_body(self, master): pass # To be overridden
    def create_buttons(self):
        # (Same as before)
        buttonbox = tb.Frame(self)
        ok_btn = tb.Button(buttonbox, text="حفظ", width=10, command=self.ok, bootstyle=SUCCESS)
        ok_btn.pack(side=LEFT, padx=5, pady=10)
        cancel_btn = tb.Button(buttonbox, text="إلغاء", width=10, command=self.cancel, bootstyle=DANGER)
        cancel_btn.pack(side=LEFT, padx=5, pady=10)
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)
        buttonbox.pack()
    def ok(self, event=None):
        if not self.validate(): self.initial_focus.focus_set(); return
        self.withdraw(); self.update(); self.apply(); self.cancel()
    def cancel(self, event=None): self.parent.focus_set(); self.destroy()
    def validate(self): return 1
    def apply(self): pass

class CardDetailsDialog(CustomDialog):
    # (Same as before, but corrected data population)
    def create_body(self, master):
        is_edit = self.initial_data is not None
        
        tb.Label(master, text="الاسم على البطاقة:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        self.name_entry = tb.Entry(master, width=30); self.name_entry.grid(row=0, column=1, padx=5, pady=5)
        
        tb.Label(master, text="البريد الإلكتروني:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        self.email_entry = tb.Entry(master, width=30); self.email_entry.grid(row=1, column=1, padx=5, pady=5)
        
        tb.Label(master, text="اسم المشتري:").grid(row=2, column=0, sticky=W, padx=5, pady=5)
        self.buyer_name_entry = tb.Entry(master, width=30); self.buyer_name_entry.grid(row=2, column=1, padx=5, pady=5)
        
        tb.Label(master, text="سعر الفيزا:").grid(row=3, column=0, sticky=W, padx=5, pady=5)
        self.price_entry = tb.Entry(master, width=30); self.price_entry.grid(row=3, column=1, padx=5, pady=5)
        
        tb.Label(master, text="ملاحظات:").grid(row=4, column=0, sticky=W, padx=5, pady=5)
        self.notes_entry = tb.Entry(master, width=30); self.notes_entry.grid(row=4, column=1, padx=5, pady=5)
        
        if is_edit:
            self.name_entry.insert(0, self.initial_data[2])
            self.email_entry.insert(0, self.initial_data[3])
            self.buyer_name_entry.insert(0, self.initial_data[4])
            self.price_entry.insert(0, self.initial_data[5])
            self.notes_entry.insert(0, self.initial_data[6] or "")
            
        return self.name_entry
    # (Validate and apply methods are the same)
    def validate(self):
        try: float(self.price_entry.get()); return 1
        except ValueError: messagebox.showwarning("خطأ", "قيمة السعر غير صالحة.", parent=self); return 0
    def apply(self):
        self.result = {"name": self.name_entry.get().strip(), "email": self.email_entry.get().strip(), "buyer_name": self.buyer_name_entry.get().strip(), "price": float(self.price_entry.get()), "notes": self.notes_entry.get().strip()}

class DeclineReasonDialog(CustomDialog):
    # (Same as before, but corrected data population)
    def create_body(self, master):
        is_edit = self.initial_data is not None
        
        tb.Label(master, text="سبب الرفض:").pack(pady=5)
        reasons = ["الفيزا ملغاة", "الفيزا لا تعمل", "رصيد غير كافٍ", "بيانات خاطئة"]
        self.reason_combo = tb.Combobox(master, values=reasons, state="readonly"); self.reason_combo.pack(fill=X, padx=5, pady=5)
        
        tb.Label(master, text="ملاحظات:").pack(pady=5)
        self.notes_entry = tb.Entry(master, width=40); self.notes_entry.pack(fill=X, padx=5, pady=5)

        if is_edit: self.reason_combo.set(self.initial_data[2]); self.notes_entry.insert(0, self.initial_data[3] or "")
        else: self.reason_combo.current(0)
            
        return self.reason_combo
    def apply(self): self.result = {"reason": self.reason_combo.get(), "notes": self.notes_entry.get().strip()}

if __name__ == "__main__":
    root = tb.Window(themename="darkly")
    app = CardManagerApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()

