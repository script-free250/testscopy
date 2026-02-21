import tkinter as tk
from tkinter import messagebox
import pyperclip
import threading
import time

# قائمة لتخزين النصوص المنسوخة
clipboard_history = []
# متغير لتتبع آخر نص منسوخ لتجنب التكرار
last_copied_item = ""

def monitor_clipboard():
    """
    تعمل هذه الدالة في الخلفية لمراقبة الحافظة باستمرار.
    """
    global last_copied_item, clipboard_history

    while True:
        try:
            # جلب المحتوى الحالي للحافظة
            current_item = pyperclip.paste()

            # التأكد من أن المحتوى جديد وليس فارغاً
            if current_item and current_item != last_copied_item:
                last_copied_item = current_item
                # التأكد من عدم وجود العنصر مسبقاً في القائمة
                if current_item not in clipboard_history:
                    # إضافة العنصر الجديد إلى بداية القائمة
                    clipboard_history.insert(0, current_item)
                    # تحديث القائمة في الواجهة الرسومية
                    update_history_listbox()
        except pyperclip.PyperclipException:
            # تجاهل المحتويات التي ليست نصاً (مثل الصور)
            pass
        
        # الانتظار لمدة ثانية واحدة قبل التحقق مرة أخرى
        time.sleep(1)

def update_history_listbox():
    """
    تقوم هذه الدالة بتحديث القائمة الظاهرة في واجهة البرنامج.
    """
    # مسح القائمة الحالية
    history_listbox.delete(0, tk.END)
    # إعادة تعبئة القائمة من سجل الحافظة
    for item in clipboard_history:
        # عرض أول 75 حرفاً فقط من كل عنصر لتسهيل القراءة
        display_item = (item[:75] + '...') if len(item) > 75 else item
        history_listbox.insert(tk.END, display_item.replace('\n', ' '))

def on_item_select(event):
    """
    يتم استدعاء هذه الدالة عند اختيار عنصر من القائمة.
    تقوم بنسخ العنصر المختار مرة أخرى إلى الحافظة.
    """
    # الحصول على العناصر المحددة
    selected_indices = history_listbox.curselection()
    if selected_indices:
        # الحصول على فهرس العنصر المحدد
        index = selected_indices[0]
        # جلب النص الكامل للعنصر من السجل (وليس النص المقتطع)
        item_to_copy = clipboard_history[index]
        # نسخه إلى الحافظة
        pyperclip.copy(item_to_copy)
        # إظهار رسالة تأكيد في شريط الحالة
        status_label.config(text=f"تم نسخ: { (item_to_copy[:40] + '...') if len(item_to_copy) > 40 else item_to_copy }")

def on_closing():
    """
    دالة للتأكيد قبل إغلاق البرنامج.
    """
    if messagebox.askokcancel("إغلاق", "هل تريد بالتأكيد إغلاق مدير الحافظة؟"):
        root.destroy()

# --- إعداد الواجهة الرسومية ---
if __name__ == "__main__":
    root = tk.Tk()
    root.title("مدير الحافظة")
    root.geometry("600x400")

    title_label = tk.Label(root, text="سجل الحافظة", font=("Helvetica", 16))
    title_label.pack(pady=10)

    # إطار يحتوي على القائمة وشريط التمرير
    frame = tk.Frame(root)
    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
    history_listbox = tk.Listbox(frame, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE, font=("Helvetica", 12))
    
    scrollbar.config(command=history_listbox.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    # ربط حدث تحديد عنصر بالدالة on_item_select
    history_listbox.bind("<<ListboxSelect>>", on_item_select)

    # شريط الحالة في الأسفل
    status_label = tk.Label(root, text="اختر عنصراً من القائمة لنسخه.", bd=1, relief=tk.SUNKEN, anchor=tk.W)
    status_label.pack(side=tk.BOTTOM, fill=tk.X)

    # بدء تشغيل مراقب الحافظة في الخلفية
    monitor_thread = threading.Thread(target=monitor_clipboard, daemon=True)
    monitor_thread.start()

    # التأكيد عند الإغلاق
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # بدء تشغيل الواجهة الرسومية
    root.mainloop()

