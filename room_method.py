from fastapi import FastAPI, HTTPException, Depends, Request, APIapp
from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import uuid

from pydantic import BaseModel
from typing import List

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app = APIapp(prefix="/api")  # Добавляем префикс '/api'
# Настройка CORS
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    # Добавляем CORS-заголовки
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
    return response

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


# Настройка базы данных PostgreSQL
DATABASE_URL = "postgresql://postgres:postgres@localhost/postgres"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Определение моделей

class Room(Base):
    __tablename__ = "room"
    room_id = Column(String, primary_key=True, index=True)
    room_name = Column(String, unique=True, index=True)
    bills = relationship("Bill", back_populates="room")


class User(Base):
    __tablename__ = "user"
    user_id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    bills = relationship("Bill", back_populates="user")


class MainBill(Base):
    __tablename__ = "main_bill"
    main_bill_id = Column(String, primary_key=True, index=True)
    room_id = Column(String, ForeignKey("room.room_id"))
    total_amount = Column(Float)
    bills = relationship("Bill", back_populates="main_bill")


class Bill(Base):
    __tablename__ = "bills"
    bill_id = Column(String, primary_key=True, index=True)
    item_name = Column(String, index=True)
    quantity = Column(Integer)
    price = Column(Float)
    user_id = Column(String, ForeignKey("user.user_id"))
    main_bill_id = Column(String, ForeignKey("main_bill.main_bill_id"))
    room_id = Column(String, ForeignKey("room.room_id"))
    main_bill = relationship("MainBill", back_populates="bills")
    room = relationship("Room", back_populates="bills")
    user = relationship("User", back_populates="bills")


# Создание таблиц в БД
Base.metadata.create_all(bind=engine)


# Pydantic модели

class RoomCreate(BaseModel):
    room_name: str


class RoomResponse(BaseModel):
    room_name: str
    room_id: str


class ItemData(BaseModel):
    name: str
    count: int
    price: float


class MainBillCreate(BaseModel):
    room_id: str
    items: list[ItemData]


# Получение сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Эндпоинт для создания комнаты
@app.post("/rooms/", response_model=RoomResponse)
async def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    room_id = str(uuid.uuid4())
    db_room = db.query(Room).filter(Room.room_name == room.room_name).first()
    if db_room:
        raise HTTPException(status_code=400, detail="Room name already exists")
    new_room = Room(room_id=room_id, room_name=room.room_name)
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return RoomResponse(room_name=new_room.room_name, room_id=new_room.room_id)


# Эндпоинт для получения комнаты по room_id
@app.get("/rooms/{room_id}", response_model=RoomResponse)
async def get_room(room_id: str, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.room_id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return RoomResponse(room_name=room.room_name, room_id=room.room_id)


# Эндпоинт для регистрации пользователя
@app.post("/users/", response_model=dict)
async def create_user(username: str, db: Session = Depends(get_db)):
    user_id = str(uuid.uuid4())
    db_user = db.query(User).filter(User.username == username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = User(user_id=user_id, username=username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"user_id": new_user.user_id, "username": new_user.username}


# Эндпоинт для создания основного счета
@app.post("/main-bills/", response_model=dict)
async def create_main_bill(main_bill: MainBillCreate, db: Session = Depends(get_db)):
    main_bill_id = str(uuid.uuid4())
    total_amount = sum(item.count * item.price for item in main_bill.items)
    db_main_bill = MainBill(main_bill_id=main_bill_id, room_id=main_bill.room_id, total_amount=total_amount)
    db.add(db_main_bill)

    for item in main_bill.items:
        bill_id = str(uuid.uuid4())
        db_bill = Bill(
            bill_id=bill_id,
            item_name=item.name,
            quantity=item.count,
            price=item.price,
            main_bill_id=main_bill_id,
            room_id=main_bill.room_id,
        )
        db.add(db_bill)

    db.commit()
    db.refresh(db_main_bill)
    return {
        "main_bill_id": db_main_bill.main_bill_id,
        "room_id": db_main_bill.room_id,
        "total_amount": db_main_bill.total_amount
    }


# Эндпоинт для получения счета по ID
@app.get("/main-bills/{main_bill_id}", response_model=dict)
async def get_main_bill(main_bill_id: str, db: Session = Depends(get_db)):
    main_bill = db.query(MainBill).filter(MainBill.main_bill_id == main_bill_id).first()
    if main_bill is None:
        raise HTTPException(status_code=404, detail="Main bill not found")

    bills = db.query(Bill).filter(Bill.main_bill_id == main_bill_id).all()
    items = [
        {
            "item_name": bill.item_name,
            "quantity": bill.quantity,
            "price": bill.price
        }
        for bill in bills
    ]

    return {
        "main_bill_id": main_bill.main_bill_id,
        "room_id": main_bill.room_id,
        "total_amount": main_bill.total_amount,
        "items": items
    }