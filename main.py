import tkinter as tk
from tkinter import ttk, messagebox, Toplevel

class CardManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("مدير بيانات البطاقات")
        self.root.geometry("900x700")

        # Set a professional theme
        style = ttk.Style(self.root)
        style.theme_use("clam")

        # Data storage
        self.accepted_cards = []
        self.declined_cards = []

        # --- Input Frame ---
        input_frame = ttk.LabelFrame(self.root, text="إدخال بيانات البطاقة", padding=(10, 10))
        input_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(input_frame, text="رقم الفيزا:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.visa_entry = ttk.Entry(input_frame, width=40)
        self.visa_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        accept_button = ttk.Button(input_frame, text="قبول", command=self.handle_accept)
        accept_button.grid(row=0, column=2, padx=10, pady=5)

        decline_button = ttk.Button(input_frame, text="رفض", command=self.handle_decline)
        decline_button.grid(row=0, column=3, padx=10, pady=5)

        # --- Data Display Tabs ---
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=10, pady=10)

        # --- Accepted Cards Tab ---
        self.accepted_frame = ttk.Frame(self.notebook, padding=(10, 10))
        self.notebook.add(self.accepted_frame, text="البطاقات المقبولة")
        self.create_accepted_cards_view()

        # --- Declined Cards Tab ---
        self.declined_frame = ttk.Frame(self.notebook, padding=(10, 10))
        self.notebook.add(self.declined_frame, text="البطاقات المرفوضة")
        self.create_declined_cards_view()

    def create_accepted_cards_view(self):
        # Treeview for accepted cards
        columns = ("visa_number", "name", "email", "buyer_name", "price")
        self.accepted_tree = ttk.Treeview(self.accepted_frame, columns=columns, show="headings")
        
        self.accepted_tree.heading("visa_number", text="رقم الفيزا")
        self.accepted_tree.heading("name", text="الاسم على البطاقة")
        self.accepted_tree.heading("email", text="البريد الإلكتروني")
        self.accepted_tree.heading("buyer_name", text="اسم المشتري")
        self.accepted_tree.heading("price", text="السعر")
        
        self.accepted_tree.pack(expand=True, fill="both")

        # Total price label
        self.total_price_label = ttk.Label(self.accepted_frame, text="إجمالي السعر: 0.00", font=("Helvetica", 12, "bold"))
        self.total_price_label.pack(pady=10, anchor="e")

    def create_declined_cards_view(self):
        # Treeview for declined cards
        columns = ("visa_number", "reason")
        self.declined_tree = ttk.Treeview(self.declined_frame, columns=columns, show="headings")
        
        self.declined_tree.heading("visa_number", text="رقم الفيزا")
        self.declined_tree.heading("reason", text="سبب الرفض")
        
        self.declined_tree.pack(expand=True, fill="both")

    def get_visa_number(self):
        visa_number = self.visa_entry.get().strip()
        if not visa_number:
            messagebox.showerror("خطأ", "الرجاء إدخال رقم الفيزا أولاً.")
            return None
        return visa_number

    def handle_accept(self):
        visa_number = self.get_visa_number()
        if not visa_number:
            return

        # Create a new window for additional details
        self.accept_window = Toplevel(self.root)
        self.accept_window.title("إضافة تفاصيل البطاقة المقبولة")
        self.accept_window.geometry("400x300")
        
        details_frame = ttk.Frame(self.accept_window, padding=(20, 10))
        details_frame.pack(expand=True, fill="both")

        ttk.Label(details_frame, text="الاسم على البطاقة:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.name_entry = ttk.Entry(details_frame, width=30)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(details_frame, text="البريد الإلكتروني:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.email_entry = ttk.Entry(details_frame, width=30)
        self.email_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(details_frame, text="اسم المشتري:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.buyer_name_entry = ttk.Entry(details_frame, width=30)
        self.buyer_name_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(details_frame, text="سعر الفيزا:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.price_entry = ttk.Entry(details_frame, width=30)
        self.price_entry.grid(row=3, column=1, padx=5, pady=5)

        save_button = ttk.Button(details_frame, text="حفظ", command=lambda: self.save_accepted_card(visa_number))
        save_button.grid(row=4, column=0, columnspan=2, pady=20)
        
        self.accept_window.transient(self.root)
        self.accept_window.grab_set()
        self.root.wait_window(self.accept_window)

    def save_accepted_card(self, visa_number):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        buyer_name = self.buyer_name_entry.get().strip()
        price_str = self.price_entry.get().strip()

        if not all([name, email, buyer_name, price_str]):
            messagebox.showerror("خطأ", "يجب ملء جميع الحقول.", parent=self.accept_window)
            return

        try:
            price = float(price_str)
        except ValueError:
            messagebox.showerror("خطأ", "الرجاء إدخال سعر صحيح.", parent=self.accept_window)
            return
            
        card_data = {
            "visa_number": visa_number,
            "name": name,
            "email": email,
            "buyer_name": buyer_name,
            "price": price
        }
        
        self.accepted_cards.append(card_data)
        self.accepted_tree.insert("", "end", values=(visa_number, name, email, buyer_name, f"{price:.2f}"))
        self.update_total_price()
        
        self.visa_entry.delete(0, 'end')
        self.accept_window.destroy()

    def handle_decline(self):
        visa_number = self.get_visa_number()
        if not visa_number:
            return

        # Create a new window to select decline reason
        self.decline_window = Toplevel(self.root)
        self.decline_window.title("تحديد سبب الرفض")
        self.decline_window.geometry("350x200")

        decline_frame = ttk.Frame(self.decline_window, padding=(20, 10))
        decline_frame.pack(expand=True, fill="both")

        ttk.Label(decline_frame, text="اختر سبب الرفض:").pack(pady=10)
        
        self.reason_var = tk.StringVar()
        reasons = ["الفيزا ملغاة (Cancelled)", "الفيزا لا تعمل (Not Working)"]
        reason_menu = ttk.Combobox(decline_frame, textvariable=self.reason_var, values=reasons, state="readonly")
        reason_menu.pack(pady=5, padx=10, fill="x")
        reason_menu.set(reasons[0])

        save_button = ttk.Button(decline_frame, text="حفظ", command=lambda: self.save_declined_card(visa_number))
        save_button.pack(pady=20)

        self.decline_window.transient(self.root)
        self.decline_window.grab_set()
        self.root.wait_window(self.decline_window)


    def save_declined_card(self, visa_number):
        reason = self.reason_var.get()
        if not reason:
            messagebox.showerror("خطأ", "الرجاء اختيار سبب الرفض.", parent=self.decline_window)
            return
            
        card_data = {"visa_number": visa_number, "reason": reason}
        self.declined_cards.append(card_data)
        self.declined_tree.insert("", "end", values=(visa_number, reason))

        self.visa_entry.delete(0, 'end')
        self.decline_window.destroy()


    def update_total_price(self):
        total = sum(card['price'] for card in self.accepted_cards)
        self.total_price_label.config(text=f"إجمالي السعر: {total:.2f}")


if __name__ == "__main__":
    root = tk.Tk()
    app = CardManagerApp(root)
    root.mainloop()

