import tkinter as tk

class ClipboardHistory:
    """
    تطبيق بسيط لمدير الحافظة (Clipboard) باستخدام Tkinter.
    يسجل تاريخ النصوص المنسوخة ويسمح للمستخدم بإعادة نسخها.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("سجل الحافظة (Clipboard History)")
        self.root.geometry("400x500") # تحديد حجم النافذة

        # قائمة لتخزين النصوص المنسوخة
        self.history = []
        # لتجنب تكرار إضافة نفس النص
        self.last_clipboard_content = ""

        # لجعل النافذة تظهر دائمًا فوق النوافذ الأخرى
        self.root.attributes("-topmost", True)

        # عنوان داخل النافذة
        label = tk.Label(root, text="انقر نقرًا مزدوجًا لنسخ عنصر", font=("Arial", 12))
        label.pack(pady=5)

        # إنشاء قائمة لعرض النصوص
        self.history_listbox = tk.Listbox(root, width=58, height=25, font=("Arial", 10))
        self.history_listbox.pack(pady=10, padx=10)

        # ربط حدث النقر المزدوج بوظيفة النسخ
        self.history_listbox.bind("<Double-1>", self.copy_selection)

        # بدء عملية التحقق من الحافظة
        self.check_clipboard()

    def check_clipboard(self):
        """
         تتحقق هذه الوظيفة بشكل دوري من محتوى الحافظة.
        """
        try:
            # الحصول على النص الحالي من الحافظة
            current_clipboard = self.root.clipboard_get()

            # إذا كان المحتوى جديدًا وليس فارغًا, قم بإضافته إلى السجل
            if current_clipboard != self.last_clipboard_content:
                self.last_clipboard_content = current_clipboard
                if self.last_clipboard_content:
                    # إضافة العنصر الجديد في بداية القائمة
                    self.history.insert(0, self.last_clipboard_content)
                    self.update_listbox()
        except tk.TclError:
            # يتم تجاهل الخطأ إذا كان المحتوى المنسوخ ليس نصًا (مثل صورة)
            pass

        # جدولة التحقق التالي بعد 1000 مللي ثانية (1 ثانية)
        self.root.after(1000, self.check_clipboard)

    def update_listbox(self):
        """
        تحديث القائمة المعروضة في النافذة.
        """
        # مسح القائمة الحالية
        self.history_listbox.delete(0, tk.END)

        # إضافة جميع العناصر من السجل إلى القائمة
        for item in self.history:
            # اقتصاص النصوص الطويلة لتجنب تشويه الواجهة
            display_item = (item[:70] + '...') if len(item) > 70 else item
            self.history_listbox.insert(tk.END, display_item.strip().replace('\n', ' '))


    def copy_selection(self, event):
        """
        نسخ العنصر المحدد من القائمة إلى الحافظة.
        """
        # الحصول على العنصر المحدد
        selected_indices = self.history_listbox.curselection()
        if not selected_indices:
            return
            
        selected_index = selected_indices[0]
        # الحصول على النص الأصلي من قائمة السجل (history)
        original_text = self.history[selected_index]

        # مسح الحافظة وإضافة النص المحدد
        self.root.clipboard_clear()
        self.root.clipboard_append(original_text)
        
        # تحديث آخر محتوى تم نسخه لتجنب إضافته مرة أخرى
        self.last_clipboard_content = original_text
        
        print(f"تم النسخ إلى الحافظة: {original_text[:50]}...")


if __name__ == "__main__":
    # إنشاء النافذة الرئيسية وتشغيل التطبيق
    root = tk.Tk()
    app = ClipboardHistory(root)
    root.mainloop()
