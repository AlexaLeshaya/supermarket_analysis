import sqlite3
import pandas as pd
import os

# Путь к базе данных
DB_PATH = 'supermarket.db'

# Путь к исходным данным
DATA_DIR = './source'

# Путь к SQL-скрипту для создания таблиц
CREATE_TABLES_SQL_FILE = './queries/create_tables.sql'

# Подключение к SQLite
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Функция для создания таблиц
def create_tables():
    try:
        with open(CREATE_TABLES_SQL_FILE, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        cursor.executescript(sql_script)
        conn.commit()
        print("Таблицы успешно созданы!")
    except Exception as e:
        print(f"Ошибка при создании таблиц: {e}")

# Загрузка данных в таблицу Кассиры
def load_cashiers(data):
    try:
        кассиры = data[['Кассир']].drop_duplicates().reset_index(drop=True)
        кассиры['ID_Кассира'] = range(1, len(кассиры) + 1)
        кассиры = кассиры.rename(columns={'Кассир': 'Имя'})

        # Преобразование в текст
        кассиры['Имя'] = кассиры['Имя'].astype(str)

        # Загрузка данных
        кассиры.to_sql('Кассиры', conn, if_exists='append', index=False)
        print("Данные успешно загружены в таблицу Кассиры.")
        return кассиры
    except Exception as e:
        print(f"Ошибка при загрузке данных в таблицу Кассиры: {e}")
        return None

# Загрузка данных в таблицу Товары
def load_products(data):
    try:
        товары = data[['НомерАртикула', 'Товар']].drop_duplicates().reset_index(drop=True)
        товары['ID_Товара'] = range(1, len(товары) + 1)
        товары = товары.rename(columns={
            'НомерАртикула': 'Артикул',
            'Товар': 'Название'
        })

        # Преобразование в текст
        товары['Название'] = товары['Название'].astype(str)

        # Загрузка данных
        товары.to_sql('Товары', conn, if_exists='append', index=False)
        print("Данные успешно загружены в таблицу Товары.")
        return товары
    except Exception as e:
        print(f"Ошибка при загрузке данных в таблицу Товары: {e}")
        return None

# Загрузка данных в таблицу Продажи
def load_sales(data, кассиры):
    try:
        продажи = data[['НомерЧека', 'НомерТранзакции', 'НомерКассы', 'ВремяЧека', 'Кассир']].drop_duplicates()
        продажи['Дата'] = pd.to_datetime(продажи['ВремяЧека']).dt.date
        продажи['Время'] = pd.to_datetime(продажи['ВремяЧека']).dt.time
        продажи = продажи.rename(columns={
            'НомерЧека': 'Номер_Чека',
            'НомерТранзакции': 'ID_Транзакции',
            'НомерКассы': 'Номер_Кассы'
        })

        if кассиры is not None:
            продажи = продажи.merge(кассиры, left_on='Кассир', right_on='Имя', how='left')
        else:
            raise ValueError("Данные о кассирах отсутствуют!")

        продажи['ID_Продажи'] = range(1, len(продажи) + 1)
        продажи = продажи[['ID_Продажи', 'Номер_Чека', 'ID_Транзакции', 'ID_Кассира', 'Дата', 'Время', 'Номер_Кассы']]

        # Загрузка данных
        продажи.to_sql('Продажи', conn, if_exists='append', index=False)
        print("Данные успешно загружены в таблицу Продажи.")
        return продажи
    except Exception as e:
        print(f"Ошибка при загрузке данных в таблицу Продажи: {e}")
        return None

# Загрузка данных в таблицу Детали_Продаж
def load_sale_details(data, продажи, товары):
    try:
        детали = data[['НомерЧека', 'НомерАртикула', 'Количество', 'Сумма (руб)', 'Скидка (%)']].rename(columns={
            'НомерЧека': 'Номер_Чека',
            'НомерАртикула': 'Артикул',
            'Количество': 'Количество',
            'Сумма (руб)': 'Сумма',
            'Скидка (%)': 'Скидка'
        })

        if продажи is not None and товары is not None:
            детали = детали.merge(продажи[['Номер_Чека', 'ID_Продажи']], on='Номер_Чека', how='left')
            детали = детали.merge(товары[['Артикул', 'ID_Товара']], on='Артикул', how='left')
        else:
            raise ValueError("Данные о продажах или товарах отсутствуют!")

        детали['ID_Детали'] = range(1, len(детали) + 1)
        детали = детали[['ID_Детали', 'ID_Продажи', 'ID_Товара', 'Количество', 'Сумма', 'Скидка']]

        # Загрузка данных
        детали.to_sql('Детали_Продаж', conn, if_exists='append', index=False)
        print("Данные успешно загружены в таблицу Детали_Продаж.")
    except Exception as e:
        print(f"Ошибка при загрузке данных в таблицу Детали_Продаж: {e}")

# Основная функция
def main():
    create_tables()

    file_path = os.path.join(DATA_DIR, 'supermarket_data.csv')
    if not os.path.exists(file_path):
        print(f"Файл {file_path} не найден!")
        return

    data = pd.read_csv(file_path, encoding='utf-8')
    кассиры = load_cashiers(data)
    товары = load_products(data)
    продажи = load_sales(data, кассиры)
    if продажи is not None and товары is not None:
        load_sale_details(data, продажи, товары)

if __name__ == "__main__":
    main()
    conn.close()
