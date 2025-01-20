import sqlite3
import os

# Путь к базе данных
DB_PATH = 'supermarket.db'

# Путь к файлу SQL
CREATE_VIEWS_SQL_FILE = './queries/create_views.sql'

# Проверка существования базы данных и SQL-скрипта
if not os.path.exists(DB_PATH):
    print(f"Ошибка: база данных {DB_PATH} не найдена!")
    exit()

if not os.path.exists(CREATE_VIEWS_SQL_FILE):
    print(f"Ошибка: файл {CREATE_VIEWS_SQL_FILE} не найден!")
    exit()

# Подключение к базе данных
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Выполнение скрипта
try:
    with open(CREATE_VIEWS_SQL_FILE, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Выполнение SQL-скрипта
    cursor.executescript(sql_script)
    conn.commit()
    print("Все представления успешно созданы!")
except sqlite3.Error as e:
    print(f"Ошибка SQLite при создании представлений: {e}")
except Exception as e:
    print(f"Неизвестная ошибка: {e}")
finally:
    # Закрытие подключения
    conn.close()
