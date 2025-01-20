-- Таблица кассиров
CREATE TABLE IF NOT EXISTS Кассиры (
    ID_Кассира INTEGER PRIMARY KEY,
    Имя TEXT NOT NULL
);

-- Таблица товаров
CREATE TABLE IF NOT EXISTS Товары (
    ID_Товара INTEGER PRIMARY KEY,
    Артикул INTEGER UNIQUE NOT NULL,
    Название TEXT NOT NULL
);

-- Таблица продаж
CREATE TABLE IF NOT EXISTS Продажи (
    ID_Продажи INTEGER PRIMARY KEY,
    Номер_Чека INTEGER NOT NULL,
    ID_Транзакции TEXT NOT NULL,
    ID_Кассира INTEGER,
    Дата DATE NOT NULL,
    Время TIME NOT NULL,
    Номер_Кассы INTEGER NOT NULL
);

-- Таблица деталей продаж
CREATE TABLE IF NOT EXISTS Детали_Продаж (
    ID_Детали INTEGER PRIMARY KEY,
    ID_Продажи INTEGER REFERENCES Продажи(ID_Продажи),
    ID_Товара INTEGER REFERENCES Товары(ID_Товара),
    Количество REAL NOT NULL,
    Сумма REAL NOT NULL,
    Скидка REAL DEFAULT 0
);
