import browser_cookie3
import os
import sys
import sqlite3

def get_and_save_cookies():
    """
    يستخرج الكوكيز بعد مطالبة المستخدم بإغلاق المتصفحات،
    ويحفظ الملفات في نفس مجلد البرنامج.
    """
    try:
        # ------------------ الخطوة الأهم ------------------
        print("--------------------------------------------------")
        print("[-] هام جدا: يرجى اغلاق جميع المتصفحات بالكامل الان")
        print("[-] (Chrome, Firefox, Edge, Opera, etc.)")
        input("[-] اضغط على مفتاح Enter بعد اغلاق المتصفحات للمتابعة...")
        print("--------------------------------------------------\n")
        # ----------------------------------------------------

        print("[-] جاري البحث عن الكوكيز، يرجى الانتظار...")
        
        saved_domains = set()
        
        # تحميل الكوكيز من جميع المتصفحات المدعومة
        cj = browser_cookie3.load()

        if not cj:
            print("\n[!] فشل: لم يتم العثور على أي كوكيز.")
            print("[!] تاكد من أن المتصفحات كانت مغلقة تماما.")
            print("[!] حاول تشغيل البرنامج 'كـ مسؤول' (Run as administrator).")
            return

        for cookie in cj:
            domain_name = cookie.domain.lstrip('.')
            # إنشاء اسم ملف واضح ومباشر في نفس المجلد
            safe_filename = f"cookies_{domain_name.replace('.', '_')}.txt"
            
            # 'a' للكتابة والإضافة في نهاية الملف
            with open(safe_filename, 'a', encoding='utf-8') as f:
                # كتابة ترويسة الملف مرة واحدة فقط
                if os.path.getsize(safe_filename) == 0:
                    f.write(f"# Netscape Cookie File for {cookie.domain}\n\n")

                f.write(
                    f"{cookie.domain}\t"
                    f"{'TRUE' if cookie.domain.startswith('.') else 'FALSE'}\t"
                    f"{cookie.path}\t"
                    f"{'TRUE' if cookie.secure else 'FALSE'}\t"
                    f"{cookie.expires if cookie.expires is not None else 0}\t"
                    f"{cookie.name}\t"
                    f"{cookie.value}\n"
                )
            
            saved_domains.add(cookie.domain)

        if saved_domains:
            print(f"\n[+] نجاح! تم العثور على وحفظ الكوكيز للمواقع التالية:")
            for domain in sorted(list(saved_domains)):
                print(f"  - {domain}")
            print(f"\n[+] تم حفظ الملفات بنجاح في نفس مجلد البرنامج.")
        else:
            # هذه الرسالة قد لا تظهر بسبب التحقق المسبق, لكنها للاحتياط
            print("\n[!] لم يتم العثور على أي كوكيز بعد الفحص.")

    except sqlite3.OperationalError as e:
        if "database is locked" in str(e).lower():
            print("\n[!] خطأ فادح: قاعدة بيانات احد المتصفحات مقفلة!")
            print("[!] السبب: المتصفح لا يزال يعمل في الخلفية.")
            print("[!] الحل: اغلق المتصفح بالكامل (يمكنك استخدام مدير المهام Task Manager للتاكد) ثم شغل البرنامج مجددا.")
        else:
            print(f"\n[!] حدث خطأ في قاعدة البيانات: {e}")
            
    except Exception as e:
        print(f"\n[!] حدث خطأ غير متوقع: {e}")
        print("[!] نصائح: تاكد من اغلاق المتصفحات او حاول تشغيل البرنامج 'كـ مسؤول'.")

if __name__ == "__main__":
    get_and_save_cookies()
    print("\n--------------------------------------------------")
    print("[-] انتهت العملية. يمكنك اغلاق هذه النافذة.")
    # هذا السطر يبقي النافذة مفتوحة حتى ترى الرسائل قبل أن تغلق
    os.system("pause")
