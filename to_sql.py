import pandas as pd
from sqlalchemy import create_engine


menu_df = pd.read_excel("restaurant_menu.xlsx")

username = "your_username"       # Замените на ваш логин PostgreSQL
password = "your_password"       # Замените на ваш пароль PostgreSQL
host = "localhost"               # Замените на адрес вашего сервера PostgreSQL
port = "5432"                    # Стандартный порт PostgreSQL
database = "your_database_name"  # Замените на имя вашей базы данных

# Создаем подключение к базе данных
engine = create_engine(f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}")

# Проверка наличия таблицы и создание, если её нет
with engine.connect() as connection:
    if not engine.dialect.has_table(connection, "menu_items"):
        menu_df.to_sql("menu_items", engine, index=False, if_exists="replace")
        print("Таблица 'menu_items' создана и данные загружены.")
    else:
        # Если таблица существует, просто добавляем данные
        menu_df.to_sql("menu_items", engine, index=False, if_exists="append")
        print("Данные добавлены в существующую таблицу 'menu_items'.")