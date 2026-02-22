import browser_cookie3
import os
import platform

def get_cookies_and_save():
    """
    يسحب الكوكيز من جميع المتصفحات المدعومة ويحفظها في ملفات
    باسم الموقع المستخرج منه.
    """
    # إنشاء مجلد لحفظ الكوكيز إذا لم يكن موجودًا
    if not os.path.exists("cookies"):
        os.makedirs("cookies")

    try:
        # تحميل الكوكيز من جميع المتصفحات
        # قد يطلب منك إدخال كلمة مرور النظام على macOS
        cj = browser_cookie3.load()

        if not cj:
            print("لم يتم العثور على أي كوكيز.")
            return

        # المرور على الكوكيز وحفظها
        for cookie in cj:
            domain = cookie.domain
            # تنظيف اسم النطاق ليكون اسم ملف صالح
            if domain.startswith("."):
                domain = domain[1:]
            
            # إزالة الأحرف غير الصالحة من اسم الملف
            filename = "".join(c for c in domain if c.isalnum() or c in ('-', '_')).strip()
            
            if not filename:
                continue

            filepath = os.path.join("cookies", f"{filename}.txt")
            
            # كتابة بيانات الكوكي في الملف
            with open(filepath, "a", encoding="utf-8") as f:
                f.write(f"Domain: {cookie.domain}\n")
                f.write(f"Name: {cookie.name}\n")
                f.write(f"Value: {cookie.value}\n")
                f.write(f"Expires: {cookie.expires}\n")
                f.write(f"Path: {cookie.path}\n")
                f.write(f"Secure: {cookie.secure}\n")
                f.write("-" * 20 + "\n\n")
        
        print("تم حفظ الكوكيز بنجاح في مجلد 'cookies'.")

    except Exception as e:
        print(f"حدث خطأ: {e}")
        if platform.system() == "Linux":
            print("على أنظمة لينكس، قد تحتاج بعض المتصفحات إلى keyring. يرجى التأكد من تثبيته.")
        elif platform.system() == "Darwin": # macOS
             print("على نظام macOS، قد تحتاج إلى السماح بالوصول إلى Keychain.")


if __name__ == "__main__":
    get_cookies_and_save()
