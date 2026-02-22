# main.py - ИСПРАВЛЕННАЯ ВЕРСИЯ С ВАШИМИ ДАННЫМИ
import hashlib
import requests
import json
import os
import sys
from datetime import datetime


class ProtimeShaChecker:
    def __init__(self):
        self.version = "1.0"
        self.author = "Protime1"
        # ВАШИ ДАННЫЕ (измените если нужно)
        self.github_username = "Protime1"  # Ваш логин GitHub
        self.github_repo = "certificates"  # Ваш репозиторий
        self.cert_db = {}
        self.load_db()

    def load_db(self):
        db_file = "certificates_db.json"
        if os.path.exists(db_file):
            try:
                with open(db_file, 'r') as f:
                    self.cert_db = json.load(f)
                print(f"✅ Загружено {len(self.cert_db)} сертификатов")
            except:
                self.cert_db = {}

    def save_db(self):
        with open("certificates_db.json", 'w') as f:
            json.dump(self.cert_db, f, indent=2)

    def get_file_hash(self, file_path):
        try:
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(65536), b''):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None

    def check_on_github(self, file_hash):
        print("🌐 Проверка на GitHub...")
        url = f"https://raw.githubusercontent.com/{self.github_username}/{self.github_repo}/main/certificates.json"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Проверяем в разных форматах
                if file_hash in data:
                    return data[file_hash]
                # Если файл в формате списка
                if isinstance(data, list):
                    for cert in data:
                        if cert.get('file_hash') == file_hash:
                            return cert
        except:
            pass
        return None

    def verify_file(self, file_path):
        print("\n" + "=" * 60)
        print(f"🔍 Protime1 SHA Checker v{self.version}")
        print("=" * 60)

        if not os.path.exists(file_path):
            print(f"❌ Файл не найден: {file_path}")
            return

        print(f"📁 Файл: {os.path.basename(file_path)}")
        file_hash = self.get_file_hash(file_path)

        if not file_hash:
            return

        print(f"🔑 Хеш: {file_hash[:32]}...")  # Показываем только первые 32 символа

        # Поиск в локальной базе
        if file_hash in self.cert_db:
            cert = self.cert_db[file_hash]
            print("\n" + "=" * 60)
            print("✅ НАЙДЕНО В ЛОКАЛЬНОЙ БАЗЕ!")
            print("=" * 60)
            print(f"📌 Программа: {cert.get('software_name', 'Неизвестно')}")
            print(f"📌 Издатель: {cert.get('publisher', 'Неизвестно')}")
            print(f"📌 Версия: {cert.get('version', 'Неизвестно')}")
            if 'description' in cert:
                print(f"📌 Описание: {cert['description']}")
            print("=" * 60)
            return True

        # Поиск на GitHub
        cert = self.check_on_github(file_hash)
        if cert:
            print("\n" + "=" * 60)
            print("✅ НАЙДЕНО НА GITHUB!")
            print("=" * 60)
            print(f"📌 Программа: {cert.get('software_name', 'Неизвестно')}")
            print(f"📌 Издатель: {cert.get('publisher', 'Неизвестно')}")
            print(f"📌 Версия: {cert.get('version', 'Неизвестно')}")
            if 'description' in cert:
                print(f"📌 Описание: {cert['description']}")
            print("=" * 60)

            # Сохраняем в локальную базу
            self.cert_db[file_hash] = cert
            self.save_db()
            return True

        print("\n" + "=" * 60)
        print("❌ СЕРТИФИКАТ НЕ НАЙДЕН")
        print("=" * 60)
        print("Это НЕ значит, что программа опасна.")
        print("Но запуск только на ваш страх и риск.")
        print("\nХотите добавить этот файл в базу?")

        choice = input("\nДобавить? (y/n): ")
        if choice.lower() == 'y':
            self.add_certificate(file_path, file_hash)

        return False

    def add_certificate(self, file_path, file_hash):
        print("\n📝 ДОБАВЛЕНИЕ НОВОГО СЕРТИФИКАТА")
        print("-" * 40)

        name = input("Название программы: ")
        publisher = input("Издатель (ваше имя): ")
        version = input("Версия (можно пропустить): ")
        description = input("Описание (можно пропустить): ")

        certificate = {
            "file_name": os.path.basename(file_path),
            "file_hash": file_hash,
            "software_name": name,
            "publisher": publisher,
            "version": version if version else "1.0",
            "description": description if description else "",
            "date_added": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Сохраняем локально
        self.cert_db[file_hash] = certificate
        self.save_db()

        # Сохраняем в отдельный файл
        filename = f"{name.lower().replace(' ', '_')}.json"
        with open(filename, 'w') as f:
            json.dump(certificate, f, indent=2)

        print(f"\n✅ Сертификат создан и сохранен!")
        print(f"📄 Локальный файл: {filename}")
        print("\n📤 ДЛЯ ЗАГРУЗКИ НА GITHUB:")
        print(f"1. Зайдите на GitHub: https://github.com/{self.github_username}/{self.github_repo}")
        print(f"2. Загрузите файл: {filename}")
        print("\n📋 ИЛИ скопируйте это в certificates.json:")
        print("-" * 40)
        print(json.dumps({file_hash: certificate}, indent=2))
        print("-" * 40)

    def menu(self):
        while True:
            try:
                print("\n" + "=" * 60)
                print(f"🚀 Protime1 SHA Checker v{self.version}")
                print("=" * 60)
                print(f"📊 В базе: {len(self.cert_db)} сертификатов")
                print(f"👤 Автор: {self.author}")
                print(f"🌐 GitHub: {self.github_username}/{self.github_repo}")
                print("\n1. 🔍 Проверить файл")
                print("2. 📥 Обновить базу с GitHub")
                print("3. 📊 Показать все сертификаты")
                print("4. ❌ Выход")

                choice = input("\nВыберите действие (1-4): ")

                if choice == '1':
                    file_path = input("📂 Путь к файлу: ").strip('"')
                    if os.path.exists(file_path):
                        self.verify_file(file_path)
                    else:
                        print("❌ Файл не найден")

                elif choice == '2':
                    print("🔄 Обновление базы с GitHub...")
                    url = f"https://raw.githubusercontent.com/{self.github_username}/{self.github_repo}/main/certificates.json"
                    try:
                        response = requests.get(url, timeout=10)
                        if response.status_code == 200:
                            data = response.json()
                            count = 0
                            if isinstance(data, dict):
                                for h, cert in data.items():
                                    if h not in self.cert_db:
                                        self.cert_db[h] = cert
                                        count += 1
                            self.save_db()
                            print(f"✅ Добавлено {count} новых сертификатов")
                        else:
                            print("❌ Не удалось загрузить с GitHub")
                    except Exception as e:
                        print(f"❌ Ошибка: {e}")

                elif choice == '3':
                    print("\n📋 ВСЕ СЕРТИФИКАТЫ:")
                    print("=" * 40)
                    if not self.cert_db:
                        print("База пуста")
                    for h, cert in list(self.cert_db.items())[:10]:  # Показываем первые 10
                        print(f"📌 {cert.get('software_name', 'Неизвестно')} - {cert.get('publisher', '?')}")
                    if len(self.cert_db) > 10:
                        print(f"... и еще {len(self.cert_db) - 10}")

                elif choice == '4':
                    print("\n👋 До свидания!")
                    break

                # Защищенный ввод Enter
                try:
                    input("\nНажмите Enter для продолжения...")
                except KeyboardInterrupt:
                    print("\n\n👋 Выход по запросу")
                    break

            except KeyboardInterrupt:
                print("\n\n👋 Программа остановлена")
                break
            except Exception as e:
                print(f"\n❌ Ошибка: {e}")
                try:
                    input("\nНажмите Enter для продолжения...")
                except:
                    break


# Запуск программы
if __name__ == "__main__":
    try:
        print("🚀 Запуск Protime1 SHA Checker...")
        print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        checker = ProtimeShaChecker()
        checker.menu()
    except KeyboardInterrupt:
        print("\n\n👋 Программа завершена")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        input("\nНажмите Enter для выхода...")