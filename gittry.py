from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Модели данных для запросов и ответов
class UserCreate(BaseModel):
    name: str
    email: str

class ExpenseCreate(BaseModel):
    category: str
    amount: float
    participants: List[int]

class ExpenseItemCreate(BaseModel):
    name: str
    price: float
    user_id: int

# Список пользователей (для примера)
users_db = []

@app.post("/register", response_model=UserCreate)
async def register_user(user: UserCreate):
    user_id = len(users_db) + 1
    users_db.append({"id": user_id, **user.dict()})
    return {"id": user_id, **user.dict()}

@app.post("/trips", response_model=dict)
async def create_trip(name: str, creator_id: int):
    # Логика для создания поездки
    trip_id = len(trips_db) + 1
    trips_db.append({"id": trip_id, "name": name, "creator_id": creator_id, "expenses": []})
    return {"id": trip_id, "name": name}

@app.post("/trips/{trip_id}/expenses", response_model=dict)
async def add_expense(trip_id: int, expense: ExpenseCreate):
    # Логика для добавления расходов
    expense_id = len(expenses_db) + 1
    expenses_db.append({"id": expense_id, **expense.dict()})
    return {"id": expense_id, **expense.dict()}

@app.post("/expenses/{expense_id}/items", response_model=dict)
async def add_expense_item(expense_id: int, item: ExpenseItemCreate):
    # Логика для добавления позиции в счёт
    items_db.append({"expense_id": expense_id, **item.dict()})
    return {"expense_id": expense_id, **item.dict()}

@app.get("/trips/{trip_id}/summary", response_model=dict)
async def get_trip_summary(trip_id: int):
    # Логика для расчёта долгов и отображения сводной информации
    summary = calculate_summary(trip_id)
    return summary