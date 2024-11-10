from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

# Создаем приложение FastAPI
app = FastAPI()

# Модель для обработки входящих данных JSON
class Item(BaseModel):
    name: str
    count: int
    price: float

class MainBill(BaseModel):
    room_id: str
    items: List[Item]

# Эндпоинт для получения данных JSON
@app.post("/main-bills/")
async def create_main_bill(main_bill: MainBill):
    # Логика обработки полученных данных
    # Например, просто выведем их на сервере
    print("Получены данные:", main_bill.dict())

    # Здесь можно добавить сохранение данных в БД или любую другую логику

    return {"message": "Данные получены успешно", "data": main_bill.dict()}

# Запуск приложения
# Запускайте сервер, используя команду: uvicorn server:app --host 0.0.0.0 --port 8000 --reload