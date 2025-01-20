import sqlite3
import pandas as pd
from datetime import datetime
import os

# Путь к базе данных
DB_PATH = 'supermarket.db'

# Список запросов для выполнения
queries = {
    "Ежедневные_Продажи_Выше_1000": """
        SELECT * 
        FROM Ежедневные_Продажи
        WHERE Общая_Выручка > 1000;
    """,
    "Продажи_По_Дням_Недели": """
        SELECT * 
        FROM Продажи_По_Дням_Недели;
    """,
    "Топ_10_Товаров": """
        SELECT * 
        FROM Топовые_Товары
        LIMIT 10;
    """,
    "Товары_С_Низкими_Продажами": """
        SELECT * 
        FROM Товары_С_Низкими_Продажами;
    """,
    "Анализ_Скидок_По_Месяцам": """
        SELECT * 
        FROM Анализ_Скидок_По_Месяцам;
    """,
    "Производительность_Кассиров": """
        SELECT * 
        FROM Производительность_Кассиров
        WHERE Количество_Чеков > 10;
    """,
    "Рейтинг_Товаров_По_Количеству": """
        SELECT 
            Название_Товара, 
            Общее_Количество,
            RANK() OVER (ORDER BY Общее_Количество DESC) AS Ранг_По_Количеству
        FROM Топовые_Товары;
    """,
    "Тренды_Выручки_По_Месяцам": """
        SELECT * 
        FROM Тренды_Выручки_По_Месяцам;
    """
}

# Получение текущей даты для имени файла
current_date = datetime.now().strftime('%Y-%m-%d')

# Путь к файлу Excel на рабочем столе
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
output_file = os.path.join(desktop, f"Отчет_Продаж_{current_date}.xlsx")

# Подключение к базе данных
conn = sqlite3.connect(DB_PATH)

# Создание Excel Writer
with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
    errors = []  # Список ошибок
    for sheet_name, query in queries.items():
        print(f"Выполнение запроса: {sheet_name}")
        try:
            # Выполнение запроса
            data = pd.read_sql_query(query, conn)
            
            # Вывод данных для проверки
            print(f"Данные для {sheet_name}:\n{data.head()}\n")
            
            # Проверка, если данные пустые
            if data.empty:
                print(f"Предупреждение: данных для {sheet_name} нет!")
            
            # Запись данных в Excel
            data.to_excel(writer, sheet_name=sheet_name, index=False)
            print(f"Результаты добавлены в лист: {sheet_name}")
        except Exception as e:
            error_message = f"Ошибка при выполнении запроса {sheet_name}: {e}"
            print(error_message)
            errors.append(error_message)

# Закрытие подключения
conn.close()

# Вывод ошибок, если они были
if errors:
    error_log = os.path.join(desktop, f"Ошибка_Запросов_{current_date}.txt")
    with open(error_log, 'w', encoding='utf-8') as f:
        f.write("\n".join(errors))
    print(f"Ошибки сохранены в файл: {error_log}")

print(f"Отчет успешно сохранен: {output_file}")
