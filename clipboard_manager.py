import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import threading
import time
import os
import json
import sys
from PIL import Image, ImageDraw
import pystray
from ttkthemes import ThemedTk

# --- مكتبات خاصة بالويندوز للتشغيل التلقائي ---
try:
    import win32com.client
except ImportError:
    messagebox.showerror("خطأ في المكتبات", "مكتبة pywin32 غير مثبتة. لا يمكن تفعيل خاصية التشغيل مع الويندوز.")
    sys.exit(1)


# --- إعدادات البرنامج ---
APP_DATA_DIR = os.path.join(os.getenv('APPDATA'), 'ClipboardManager')
HISTORY_FILE = os.path.join(APP_DATA_DIR, 'history.json')
SETTINGS_FILE = os.path.join(APP_DATA_DIR, 'settings.json') # ملف لحفظ الإعدادات
MAX_HISTORY_ITEMS = 200

# --- المتغيرات العامة ---
clipboard_history = []
settings = {'autostart': False} # إعدادات افتراضية


# --- دوال إدارة الملفات (السجل والإعدادات) ---
def setup_storage():
    if not os.path.exists(APP_DATA_DIR):
        os.makedirs(APP_DATA_DIR)

def load_data():
    """تحميل السجل والإعدادات عند بدء التشغيل."""
    global clipboard_history, settings
    # تحميل السجل
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                clipboard_history = json.load(f)
        except (json.JSONDecodeError, IOError):
            clipboard_history = []
    # تحميل الإعدادات
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except (json.JSONDecodeError, IOError):
            settings = {'autostart': False}

def save_history():
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(clipboard_history, f, ensure_ascii=False, indent=4)

def save_settings():
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=4)


# --- دالة التشغيل التلقائي مع الويندوز ---
def toggle_autostart():
    """إنشاء أو حذف اختصار البرنامج في مجلد بدء التشغيل."""
    settings['autostart'] = autostart_var.get()
    save_settings()
    
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    shortcut_path = os.path.join(startup_folder, "ClipboardManager.lnk")
    
    if settings['autostart']:
        try:
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath = sys.executable # مسار الملف التنفيذي الحالي
            shortcut.WorkingDirectory = os.path.dirname(sys.executable)
            shortcut.IconLocation = sys.executable
            shortcut.save()
            status_label.config(text="تم تفعيل التشغيل التلقائي مع الويندوز.")
        except Exception as e:
            status_label.config(text=f"خطأ: لم يتم تفعيل التشغيل التلقائي.")
    else:
        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            status_label.config(text="تم إلغاء تفعيل التشغيل التلقائي.")

# --- دوال البرنامج الأساسية ---
def monitor_clipboard():
    # ... (نفس الكود السابق بدون تغيير)
    global last_copied_item
    while True:
        try:
            current_item = pyperclip.paste()
            if current_item and current_item != last_copied_item:
                last_copied_item = current_item
                if current_item not in clipboard_history:
                    clipboard_history.insert(0, current_item)
                    if len(clipboard_history) > MAX_HISTORY_ITEMS:
                        clipboard_history.pop()
                    save_history()
                    root.after(100, update_history_listbox)
        except pyperclip.PyperclipException:
            pass
        time.sleep(1)


def update_history_listbox():
    # ... (نفس الكود السابق بدون تغيير)
    history_listbox.delete(0, tk.END)
    for item in clipboard_history:
        display_item = (item[:100] + '...') if len(item) > 100 else item
        history_listbox.insert(tk.END, display_item.replace('\n', ' '))


def on_item_select(event):
    # ... (نفس الكود السابق بدون تغيير)
    selected_indices = history_listbox.curselection()
    if selected_indices:
        item_to_copy = clipboard_history[selected_indices[0]]
        pyperclip.copy(item_to_copy)
        status_label.config(text=f"تم نسخ العنصر المحدد!")


def clear_history():
    # ... (نفس الكود السابق بدون تغيير)
    if messagebox.askyesno("مسح السجل", "هل أنت متأكد أنك تريد مسح كل سجل الحافظة؟"):
        global clipboard_history
        clipboard_history = []
        save_history()
        update_history_listbox()
        status_label.config(text="تم مسح السجل.")


# --- دوال واجهة الخلفية (System Tray) ---
# ... (نفس الكود السابق بدون تغيير)
def create_image():
    try: return Image.open("icon.ico")
    except FileNotFoundError:
        image = Image.new('RGB', (64, 64), '#333333'); dc = ImageDraw.Draw(image)
        dc.rectangle((16, 16, 48, 48), fill='white'); return image
def show_window(icon, item): icon.stop(); root.after(0, root.deiconify)
def quit_app(icon, item): icon.stop(); root.destroy()
def hide_window():
    root.withdraw(); image = create_image()
    menu = (pystray.MenuItem('إظهار', show_window, default=True), pystray.MenuItem('خروج', quit_app))
    icon = pystray.Icon("clipboard_manager", image, "مدير الحافظة", menu); icon.run()


# --- إعداد الواجهة الرسومية ---
if __name__ == "__main__":
    setup_storage()
    load_data()

    # --- استخدام ThemedTk لتطبيق الثيم الداكن ---
    root = ThemedTk(theme="equilux")
    root.title("مدير الحافظة")
    root.geometry("750x550")
    root.protocol("WM_DELETE_WINDOW", hide_window)
    
    # --- تحديد ألوان مخصصة للثيم الداكن ---
    dark_bg = "#2b2b2b"
    light_fg = "#d3d3d3"
    select_bg = "#4a4a4a"

    root.configure(bg=dark_bg)
    style = ttk.Style(root)
    style.configure("TLabel", background=dark_bg, foreground=light_fg, font=("Segoe UI", 10))
    style.configure("TButton", background="#3c3f41", foreground=light_fg, font=("Segoe UI", 10))
    style.configure("TCheckbutton", background=dark_bg, foreground=light_fg, font=("Segoe UI", 10))
    
    # الإطار الرئيسي
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)

    title_label = ttk.Label(main_frame, text="سجل الحافظة", font=("Segoe UI", 18, "bold"))
    title_label.pack(pady=(0, 15))

    # إطار القائمة
    list_frame = ttk.Frame(main_frame)
    list_frame.pack(fill=tk.BOTH, expand=True)
    
    scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
    history_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE, 
                                 font=("Segoe UI", 12), bg="#3c3f41", fg=light_fg, 
                                 selectbackground=select_bg, selectforeground="white",
                                 borderwidth=0, highlightthickness=0)
    scrollbar.config(command=history_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    history_listbox.bind("<<ListboxSelect>>", on_item_select)
    update_history_listbox()
    
    # إطار سفلي للأزرار والإعدادات
    bottom_frame = ttk.Frame(main_frame)
    bottom_frame.pack(fill=tk.X, pady=(15, 0))
    
    clear_button = ttk.Button(bottom_frame, text="مسح السجل", command=clear_history, width=15)
    clear_button.pack(side=tk.LEFT, padx=(0, 10))

    # --- خيار التشغيل التلقائي ---
    autostart_var = tk.BooleanVar(value=settings.get('autostart', False))
    autostart_check = ttk.Checkbutton(bottom_frame, text="تشغيل مع بدء الويندوز", 
                                      variable=autostart_var, command=toggle_autostart)
    autostart_check.pack(side=tk.LEFT)

    # شريط الحالة
    status_label = ttk.Label(root, text="جاهز.", relief=tk.SUNKEN, anchor=tk.W, padding=5)
    status_label.pack(side=tk.BOTTOM, fill=tk.X)

    monitor_thread = threading.Thread(target=monitor_clipboard, daemon=True)
    monitor_thread.start()

    root.mainloop()

