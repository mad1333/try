# app.py
import openpyxl

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Настройки базы данных SQLite
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Создание сессии для работы с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Модель базы данных для таблицы пользователей
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)


# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)


# Pydantic модель для добавления нового пользователя
class UserCreate(BaseModel):
    name: str


# Эндпоинт для добавления пользователя в базу данных
@app.post("/join-room/")
async def join_room(user: UserCreate):
    session = SessionLocal()
    existing_user = session.query(User).filter(User.name == user.name).first()

    if existing_user:
        session.close()
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует.")

    new_user = User(name=user.name)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    session.close()

    return {"message": f"Пользователь '{user.name}' успешно добавлен в комнату.", "id": new_user.id}


# Эндпоинт для получения списка всех пользователей
@app.get("/room-users/")
async def get_room_users():
    session = SessionLocal()
    users = session.query(User).all()
    session.close()
    return [{"id": user.id, "name": user.name} for user in users]
#@app.post("/restaurant-menu")
#def choose_items(params):

def load_menu():
    try:
        menu_df = pd.read_excel("restaurant_menu.xlsx")
        menu = menu_df.to_dict(orient="records")  # Конвертируем в список словарей
        return menu
    except FileNotFoundError:
        return [{"error": "Файл restaurant_menu.xlsx не найден"}]

# Эндпоинт для отображения меню
@app.get("/menu")
async def get_menu():
    menu = load_menu()
    return menu
