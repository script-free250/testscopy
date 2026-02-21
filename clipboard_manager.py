import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import threading
import time
import os
import json
from PIL import Image, ImageDraw
import pystray

# --- إعدادات البرنامج ---
# مسار حفظ ملف السجل في مجلد بيانات التطبيق الخاص بالمستخدم
APP_DATA_DIR = os.path.join(os.getenv('APPDATA'), 'ClipboardManager')
HISTORY_FILE = os.path.join(APP_DATA_DIR, 'history.json')
MAX_HISTORY_ITEMS = 100  # تحديد أقصى عدد للعناصر في السجل

# --- المتغيرات العامة ---
clipboard_history = []
last_copied_item = ""

# --- دوال إدارة السجل (الحفظ والتحميل) ---
def setup_storage():
    """إنشاء مجلد التخزين إذا لم يكن موجودًا."""
    if not os.path.exists(APP_DATA_DIR):
        os.makedirs(APP_DATA_DIR)

def load_history():
    """تحميل السجل من الملف عند بدء التشغيل."""
    global clipboard_history
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                clipboard_history = json.load(f)
        except (json.JSONDecodeError, IOError):
            clipboard_history = []
    else:
        clipboard_history = []

def save_history():
    """حفظ السجل الحالي إلى الملف."""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(clipboard_history, f, ensure_ascii=False, indent=4)

# --- دوال البرنامج الأساسية ---
def monitor_clipboard():
    """تراقب الحافظة وتضيف العناصر الجديدة."""
    global last_copied_item
    while True:
        try:
            current_item = pyperclip.paste()
            if current_item and current_item != last_copied_item:
                last_copied_item = current_item
                if current_item not in clipboard_history:
                    clipboard_history.insert(0, current_item)
                    # الحفاظ على حجم السجل ضمن الحد الأقصى
                    if len(clipboard_history) > MAX_HISTORY_ITEMS:
                        clipboard_history.pop()
                    save_history()
                    # استخدام after لتحديث الواجهة من الخيط الرئيسي
                    root.after(100, update_history_listbox)
        except pyperclip.PyperclipException:
            pass
        time.sleep(1)

def update_history_listbox():
    """تحديث قائمة العرض في الواجهة."""
    history_listbox.delete(0, tk.END)
    for item in clipboard_history:
        display_item = (item[:100] + '...') if len(item) > 100 else item
        history_listbox.insert(tk.END, display_item.replace('\n', ' '))

def on_item_select(event):
    """نسخ العنصر المحدد إلى الحافظة."""
    selected_indices = history_listbox.curselection()
    if selected_indices:
        item_to_copy = clipboard_history[selected_indices[0]]
        pyperclip.copy(item_to_copy)
        status_label.config(text=f"تم نسخ العنصر المحدد!")

def clear_history():
    """مسح سجل الحافظة."""
    if messagebox.askyesno("مسح السجل", "هل أنت متأكد أنك تريد مسح كل سجل الحافظة؟ لا يمكن التراجع عن هذا الإجراء."):
        global clipboard_history
        clipboard_history = []
        save_history()
        update_history_listbox()
        status_label.config(text="تم مسح السجل.")

# --- دوال إدارة واجهة الخلفية (System Tray) ---
def create_image():
    """إنشاء أيقونة بسيطة للبرنامج."""
    # يمكنك استبدال هذا بأيقونة من ملف 'icon.png'
    try:
        return Image.open("icon.ico")
    except FileNotFoundError:
        image = Image.new('RGB', (64, 64), 'gray')
        dc = ImageDraw.Draw(image)
        dc.rectangle((16, 16, 48, 48), fill='white')
        return image


def show_window(icon, item):
    """إظهار نافذة البرنامج الرئيسية."""
    icon.stop()
    root.after(0, root.deiconify)

def quit_app(icon, item):
    """إغلاق البرنامج بالكامل."""
    icon.stop()
    root.destroy()

def hide_window():
    """إخفاء النافذة وتشغيل أيقونة الخلفية."""
    root.withdraw()
    image = create_image()
    menu = (pystray.MenuItem('إظهار', show_window, default=True), pystray.MenuItem('خروج', quit_app))
    icon = pystray.Icon("clipboard_manager", image, "مدير الحافظة", menu)
    icon.run()

# --- إعداد الواجهة الرسومية ---
if __name__ == "__main__":
    setup_storage()
    load_history()

    root = tk.Tk()
    root.title("مدير الحافظة الاحترافي")
    root.geometry("700x500")
    root.protocol("WM_DELETE_WINDOW", hide_window)

    # استخدام থিমات لتحسين المظهر
    style = ttk.Style(root)
    style.theme_use("clam") # يمكنك تجربة "alt", "default", "classic", "clam"

    # الإطار الرئيسي
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # عنوان
    title_label = ttk.Label(main_frame, text="سجل الحافظة", font=("Segoe UI", 16, "bold"))
    title_label.pack(pady=(0, 10))

    # إطار القائمة مع شريط التمرير
    list_frame = ttk.Frame(main_frame)
    list_frame.pack(fill=tk.BOTH, expand=True)
    
    scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
    history_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE, 
                                 font=("Segoe UI", 11), borderwidth=0, highlightthickness=0)
    scrollbar.config(command=history_listbox.yview)
    
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    history_listbox.bind("<<ListboxSelect>>", on_item_select)
    update_history_listbox()
    
    # زر مسح السجل
    clear_button = ttk.Button(main_frame, text="مسح السجل", command=clear_history)
    clear_button.pack(pady=10)

    # شريط الحالة
    status_label = ttk.Label(root, text="جاهز - اختر عنصراً لنسخه أو أغلق النافذة للعمل في الخلفية.", 
                             relief=tk.SUNKEN, anchor=tk.W, padding=5)
    status_label.pack(side=tk.BOTTOM, fill=tk.X)

    # بدء مراقب الحافظة
    monitor_thread = threading.Thread(target=monitor_clipboard, daemon=True)
    monitor_thread.start()

    root.mainloop()
