import browser_cookie3
import os
import sys

def get_cookies():
    """
    يستخرج الكوكيز من جميع المتصفحات المدعومة ويحفظها في ملفات نصية
    داخل مجلد 'cookies'
    """
    # إنشاء مجلد لتخزين الكوكيز إذا لم يكن موجودًا
    if not os.path.exists('cookies'):
        os.makedirs('cookies')

    print("[-] جاري البحث عن الكوكيز في المتصفحات...")
    
    # قائمة لتتبع المواقع التي تم حفظ الكوكيز لها
    saved_domains = set()

    try:
        # تحميل الكوكيز من جميع المتصفحات المدعومة
        # firefox, chrome, chromium, brave, opera, edge
        cj = browser_cookie3.load()

        for cookie in cj:
            # تنظيف اسم النطاق ليكون اسم ملف صالح
            domain_name = cookie.domain.lstrip('.')
            # استبدال النقاط في اسم النطاق بشرطة سفلية لتجنب المشاكل
            safe_filename = domain_name.replace('.', '_') + '.txt'
            filepath = os.path.join('cookies', safe_filename)

            # كتابة الكوكيز في ملف خاص بالموقع
            with open(filepath, 'a', encoding='utf-8') as f:
                # كتابة معلومات الكوكي بتنسيق Netscape cookie file format
                f.write(
                    f"{cookie.domain}\t"
                    f"{'TRUE' if cookie.domain.startswith('.') else 'FALSE'}\t"
                    f"{cookie.path}\t"
                    f"{'TRUE' if cookie.secure else 'FALSE'}\t"
                    f"{cookie.expires if cookie.expires is not None else 0}\t"
                    f"{cookie.name}\t"
                    f"{cookie.value}\n"
                )
            
            if cookie.domain not in saved_domains:
                saved_domains.add(cookie.domain)

        if saved_domains:
            print(f"[+] تم العثور على وحفظ الكوكيز للمواقع التالية:")
            for domain in sorted(list(saved_domains)):
                print(f"  - {domain}")
            print(f"\n[+] تم حفظ جميع الملفات في مجلد 'cookies'")
        else:
            print("[!] لم يتم العثور على أي كوكيز.")

    except Exception as e:
        print(f"[!] حدث خطأ: {e}")
        print("[!] قد تحتاج إلى تشغيل البرنامج بصلاحيات المسؤول أو إغلاق المتصفحات.")

if __name__ == "__main__":
    get_cookies()
    # إبقاء نافذة الأوامر مفتوحة بعد التنفيذ لرؤية الناتج
    if sys.platform == "win32":
        os.system("pause")
