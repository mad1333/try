# app.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

# Временное хранилище пользователей
room_users = []

# Модель данных для запроса регистрации пользователя
class User(BaseModel):
    name: str

# Эндпоинт для регистрации пользователя в комнате
@app.post("/join-room/")
async def join_room(user: User):
    # Проверка, что пользователь с таким именем не зарегистрирован
    if user.name in room_users:
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже зарегистрирован.")

    # Добавляем пользователя в список
    room_users.append(user.name)
    return {"message": f"Пользователь '{user.name}' успешно добавлен в комнату."}

# Эндпоинт для просмотра всех пользователей в комнате
@app.get("/room-users/")
async def get_room_users():
    return {"users": room_users}