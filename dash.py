import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px

# Путь к базе данных
DB_PATH = 'supermarket.db'

# Подключение к базе данных
def load_data(query, params=None):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn, params=params)

# Заголовок дашборда
st.title("Анализ данных продаж супермаркета")

# Боковая панель
st.sidebar.header("Фильтры")

# Фильтры для ежедневных продаж
start_date = st.sidebar.date_input("Начальная дата для ежедневные продажи", value=pd.to_datetime("2024-01-01"))
end_date = st.sidebar.date_input("Конечная дата для ежедневные продажи", value=pd.to_datetime("2024-01-31"))

# Фильтр для количества топ-товаров
top_n = st.sidebar.slider("Количество топ-товаров", min_value=1, max_value=50, value=10)

# Раздел 1: Ежедневные продажи
st.header("Ежедневные продажи")
daily_sales_query = """
    SELECT 
        strftime('%Y-%m-%d', Дата_Продажи) AS Дата,
        Общая_Выручка
    FROM Ежедневные_Продажи
    WHERE Дата_Продажи BETWEEN ? AND ?
    ORDER BY Дата;
"""
daily_sales = load_data(daily_sales_query, params=(start_date, end_date))

if not daily_sales.empty:
    fig = px.line(daily_sales, x='Дата', y='Общая_Выручка', title="Ежедневная выручка")
    st.plotly_chart(fig)
else:
    st.warning("Нет данных для выбранного периода.")

# Раздел 2:Топ-товары
st.header("Топ товаров")
top_products_query = f"""
    SELECT 
        Название_Товара,
        Общая_Выручка
    FROM Топовые_Товары
    ORDER BY Общая_Выручка DESC
    LIMIT {top_n};
"""
top_products = load_data(top_products_query)

if not top_products.empty:
    fig = px.bar(
        top_products, 
        x='Название_Товара', 
        y='Общая_Выручка', 
        title=f"Топ-{top_n} товаров"
    )
    st.plotly_chart(fig)
else:
    st.warning("Нет данных для топ-товаров.")

# Раздел 3:  Анализ скидок
st.header("Анализ скидок")

# Фильтры для анализа скидок в боковой панели
discount_start_date = st.sidebar.date_input("Начальная дата для анализа скидок", value=pd.to_datetime("2024-01-01"))
discount_end_date = st.sidebar.date_input("Конечная дата для анализа скидок", value=pd.to_datetime("2024-01-31"))

discount_sales_query = """
    SELECT 
        strftime('%Y-%m-%d', П.Дата) AS Дата,
        Д.Скидка,
        SUM(Д.Количество) AS Количество_Продано,
        SUM(Д.Сумма) AS Общая_Выручка
    FROM Продажи П
    JOIN Детали_Продаж Д ON П.ID_Продажи = Д.ID_Продажи
    WHERE П.Дата BETWEEN ? AND ?
    GROUP BY Д.Скидка
    ORDER BY Д.Скидка;
"""
discount_sales = load_data(discount_sales_query, params=(discount_start_date, discount_end_date))

if not discount_sales.empty:
    # Расчет процента от общего количества проданного
    discount_sales['Процент_От_Общего'] = (discount_sales['Количество_Продано'] /
                                           discount_sales['Количество_Продано'].sum()) * 100

    # Построение бар-графика
    fig = px.bar(
        discount_sales,
        x='Скидка',
        y='Количество_Продано',
        color='Процент_От_Общего',
        title=f"Анализ скидок ({discount_start_date} - {discount_end_date})",
        labels={'Процент_От_Общего': 'Процент от общего'},
        color_continuous_scale='Teal'
    )
    st.plotly_chart(fig)
else:
    st.warning("Нет данных для анализа скидок за выбранный период.")
    
# Раздел 4: # Раздел 3: Продажи по дням недели
st.header("Продажи по дням недели")

# Фильтры для анализа по дням недели в боковой панели
weekly_start_date = st.sidebar.date_input("Начальная дата для анализа по дням недели", value=pd.to_datetime("2024-01-01"))
weekly_end_date = st.sidebar.date_input("Конечная дата для анализа по дням недели", value=pd.to_datetime("2024-01-31"))

weekly_sales_query = """
    SELECT 
        CASE strftime('%w', П.Дата)
            WHEN '0' THEN 'Воскресенье'
            WHEN '1' THEN 'Понедельник'
            WHEN '2' THEN 'Вторник'
            WHEN '3' THEN 'Среда'
            WHEN '4' THEN 'Четверг'
            WHEN '5' THEN 'Пятница'
            WHEN '6' THEN 'Суббота'
        END AS День_Недели,
        SUM(Д.Сумма) AS Общая_Выручка
    FROM Продажи П
    JOIN Детали_Продаж Д ON П.ID_Продажи = Д.ID_Продажи
    WHERE П.Дата BETWEEN ? AND ?
    GROUP BY День_Недели
    ORDER BY 
        CASE День_Недели
            WHEN 'Понедельник' THEN 1
            WHEN 'Вторник' THEN 2
            WHEN 'Среда' THEN 3
            WHEN 'Четверг' THEN 4
            WHEN 'Пятница' THEN 5
            WHEN 'Суббота' THEN 6
            WHEN 'Воскресенье' THEN 7
        END;
"""
weekly_sales = load_data(weekly_sales_query, params=(weekly_start_date, weekly_end_date))

if not weekly_sales.empty:
    fig = px.bar(
        weekly_sales,
        x='День_Недели',
        y='Общая_Выручка',
        title=f"Продажи по дням недели ({weekly_start_date} - {weekly_end_date})",
        color='Общая_Выручка',
        color_continuous_scale='Viridis'
    )
    st.plotly_chart(fig)
else:
    st.warning("Нет данных для анализа по дням недели за выбранный период.")

# Раздел 5: Тренды выручки по месяцам
st.header("Тренды выручки по месяцам")
monthly_trends_query = """
    SELECT 
        Месяц,
        Общая_Выручка,
        Сумма_Скидок
    FROM Тренды_Выручки_По_Месяцам
    ORDER BY Месяц;
"""
monthly_trends = load_data(monthly_trends_query)

if not monthly_trends.empty:
    monthly_trends['Мин_Выручка'] = monthly_trends['Общая_Выручка'].min()

    fig = px.line(
        monthly_trends,
        x='Месяц',
        y=['Общая_Выручка', 'Сумма_Скидок'],
        title="Тренды выручки по месяцам"
    )
    fig.add_scatter(x=monthly_trends['Месяц'], y=monthly_trends['Мин_Выручка'],
                    mode='lines', name='Линия тренда (мин. выручка)')
    st.plotly_chart(fig)
else:
    st.warning("Нет данных для трендов выручки по месяцам.")

# Раздел 6: Производительность кассиров
st.header("Производительность кассиров")
cashier_performance_query = """
    SELECT 
        Имя_Кассира,
        Сумма_Продаж AS Общая_Выручка,
        Количество_Чеков
    FROM Производительность_Кассиров
    ORDER BY Общая_Выручка DESC;
"""
cashier_performance = load_data(cashier_performance_query)

if not cashier_performance.empty:
    fig = px.bar(
        cashier_performance,
        x='Имя_Кассира',
        y='Общая_Выручка',
        title="Производительность кассиров"
    )
    st.plotly_chart(fig)
else:
    st.warning("Нет данных для производительности кассиров.")
