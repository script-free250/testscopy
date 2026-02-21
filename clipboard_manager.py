import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
import pyperclip
import threading
import time
import os
import json
import sys
import queue
from PIL import Image, ImageDraw

try:
    import win32com.client
except ImportError:
    # هذا سيسمح للبرنامج بالعمل على أنظمة غير ويندوز ولكن بدون ميزة التشغيل التلقائي
    win32com = None

# --- إعدادات البرنامج وثوابته ---
APP_DATA_DIR = os.path.join(os.getenv('APPDATA'), 'ClipboardManagerPro')
HISTORY_FILE = os.path.join(APP_DATA_DIR, 'history.json')
SETTINGS_FILE = os.path.join(APP_DATA_DIR, 'settings.json')
MAX_HISTORY_ITEMS = 200
MAX_TEXT_SIZE = 1024 * 1024  # 1 MB حد أقصى لحجم النص
UPDATE_INTERVAL_MS = 150 # سرعة تحديث الواجهة

# --- متغيرات عامة وطابور التواصل ---
clipboard_history = []
settings = {'autostart': False}
clipboard_queue = queue.Queue() # طابور آمن للتواصل بين الخيوط

# --- دوال إدارة الملفات (حفظ وتحميل) ---
def setup_storage():
    if not os.path.exists(APP_DATA_DIR): os.makedirs(APP_DATA_DIR)

def load_data():
    global clipboard_history, settings
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f: clipboard_history = json.load(f)
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f: settings = json.load(f)
    except (json.JSONDecodeError, IOError):
        clipboard_history, settings = [], {'autostart': False}

def save_data_on_exit():
    """حفظ كل البيانات مرة واحدة عند الخروج."""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f: json.dump(clipboard_history, f, ensure_ascii=False, indent=4)
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f: json.dump(settings, f, indent=4)

# --- دوال البرنامج والمنطق ---
def monitor_clipboard():
    """تراقب الحافظة وتضع العناصر الجديدة في الطابور (Queue)."""
    last_item = ""
    while True:
        try:
            current_item = pyperclip.paste()
            if current_item and current_item != last_item:
                last_item = current_item
                # التحقق من حجم النص قبل إضافته
                if sys.getsizeof(current_item) <= MAX_TEXT_SIZE:
                    clipboard_queue.put(current_item)
        except (pyperclip.PyperclipException, TypeError):
            pass # تجاهل المحتوى غير النصي
        time.sleep(0.8) # تقليل التكرار قليلاً

def process_queue():
    """تفحص الطابور وتحدث الواجهة الرئيسية."""
    try:
        while not clipboard_queue.empty():
            item = clipboard_queue.get_nowait()
            if item not in clipboard_history:
                clipboard_history.insert(0, item)
                if len(clipboard_history) > MAX_HISTORY_ITEMS: clipboard_history.pop()
                
                display_item = (item[:120] + '...') if len(item) > 120 else item
                history_listbox.insert(0, display_item.replace('\n', ' '))
    finally:
        root.after(UPDATE_INTERVAL_MS, process_queue) # إعادة جدولة الفحص

def on_item_select(event):
    if not history_listbox.curselection(): return
    index = history_listbox.curselection()[0]
    pyperclip.copy(clipboard_history[index])
    status_label.config(text="✓ تم نسخ العنصر المحدد")

def clear_history():
    if messagebox.askyesno("مسح السجل", "هل أنت متأكد أنك تريد مسح كل السجل؟", icon='warning'):
        clipboard_history.clear()
        history_listbox.delete(0, tk.END)
        status_label.config(text="تم مسح السجل.")

# --- دوال التشغيل التلقائي وواجهة الخلفية ---
def toggle_autostart():
    if not win32com:
        messagebox.showerror("خطأ", "هذه الميزة مدعومة على نظام ويندوز فقط.")
        autostart_var.set(False)
        return

    settings['autostart'] = autostart_var.get()
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    shortcut_path = os.path.join(startup_folder, "ClipboardManagerPro.lnk")
    
    try:
        if settings['autostart']:
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.Targetpath, shortcut.WorkingDirectory = sys.executable, os.path.dirname(sys.executable)
            shortcut.IconLocation = sys.executable
            shortcut.save()
            status_label.config(text="تم تفعيل التشغيل التلقائي.")
        elif os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            status_label.config(text="تم إلغاء تفعيل التشغيل التلقائي.")
    except Exception:
        status_label.config(text="خطأ في إعداد التشغيل التلقائي.")

def create_tray_icon():
    try: return Image.open("icon.ico")
    except FileNotFoundError:
        img = Image.new('RGB', (64, 64), '#1c1c1c'); dc = ImageDraw.Draw(img)
        dc.rectangle((18, 18, 46, 46), fill='#00bc8c'); return img

def show_window(icon, item): icon.stop(); root.deiconify()
def quit_app(icon, item):
    status_label.config(text="جاري الحفظ... لا تغلق.")
    root.update()
    save_data_on_exit() # حفظ كل شيء قبل الخروج
    icon.stop(); root.destroy()

def hide_window():
    root.withdraw()
    menu = (pystray.MenuItem('إظهار', show_window, default=True), pystray.MenuItem('خروج', quit_app))
    icon = pystray.Icon("ClipboardManagerPro", create_tray_icon(), "مدير الحافظة الاحترافي", menu); icon.run()

# --- بناء الواجهة الرسومية ---
if __name__ == "__main__":
    setup_storage()
    load_data()

    root = ttk.Window(themename="darkly")
    root.title("مدير الحافظة الاحترافي")
    root.geometry("800x600")
    root.protocol("WM_DELETE_WINDOW", hide_window)

    main_frame = ttk.Frame(root, padding="15")
    main_frame.pack(fill=tk.BOTH, expand=True)

    title_label = ttk.Label(main_frame, text="سجل الحافظة", font=("Segoe UI", 20, "bold"))
    title_label.pack(pady=(0, 15), anchor="w")

    list_frame = ttk.Frame(main_frame, style='Card.TFrame', padding=5)
    list_frame.pack(fill=tk.BOTH, expand=True)
    list_frame.columnconfigure(0, weight=1); list_frame.rowconfigure(0, weight=1)

    scrollbar = ttk.Scrollbar(list_frame)
    history_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE, 
                                 font=("Segoe UI", 12), bg="#303030", fg="#d3d3d3",
                                 selectbackground="#00bc8c", selectforeground="white",
                                 borderwidth=0, highlightthickness=0, activestyle='none')
    scrollbar.config(command=history_listbox.yview)
    
    history_listbox.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    for item in clipboard_history:
        display_item = (item[:120] + '...') if len(item) > 120 else item
        history_listbox.insert(tk.END, display_item.replace('\n', ' '))
    history_listbox.bind("<<ListboxSelect>>", on_item_select)
    
    settings_frame = ttk.Labelframe(main_frame, text=" الإعدادات ", padding="10")
    settings_frame.pack(fill=tk.X, pady=(15, 0))

    clear_button = ttk.Button(settings_frame, text="مسح السجل", command=clear_history, style="danger.TButton")
    clear_button.pack(side=tk.RIGHT, padx=(10, 0))

    autostart_var = tk.BooleanVar(value=settings.get('autostart', False))
    autostart_check = ttk.Checkbutton(settings_frame, text="تشغيل مع بدء الويندوز", variable=autostart_var, 
                                      command=toggle_autostart, style="success.TCheckbutton")
    autostart_check.pack(side=tk.LEFT)

    status_label = ttk.Label(root, text="جاهز.", style="secondary.TLabel", padding=5)
    status_label.pack(side=tk.BOTTOM, fill=tk.X)

    monitor_thread = threading.Thread(target=monitor_clipboard, daemon=True)
    monitor_thread.start()
    
    process_queue() # بدء فحص الطابور

    root.mainloop()
