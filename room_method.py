from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import uuid
from typing import List

app = FastAPI()

# Настройка соединения с базой данных
DATABASE_URL = "postgresql://prod_backend:prod_backend@158.160.79.20/prod_backend"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Определение моделей SQLAlchemy для базы данных
class Room(Base):
    __tablename__ = "rooms"
    room_id = Column(String, primary_key=True, index=True)
    room_name = Column(String, unique=True, index=True)
    bills = relationship("Bill", back_populates="room")

class Bill(Base):
    __tablename__ = "bills"
    bill_id = Column(String, primary_key=True, index=True)
    bill_name = Column(String, index=True)
    total_amount = Column(Float)
    room_id = Column(String, ForeignKey("rooms.room_id"))
    room = relationship("Room", back_populates="bills")

# Pydantic модели для валидации и сериализации данных
class RoomCreate(BaseModel):
    room_name: str

class RoomResponse(BaseModel):
    room_id: str
    room_name: str

class BillCreate(BaseModel):
    bill_name: str
    total_amount: float

class BillResponse(BaseModel):
    bill_id: str
    bill_name: str
    total_amount: float
    room_id: str

# Инициализация базы данных
Base.metadata.create_all(bind=engine)

# Подключение к базе данных
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Эндпоинт для создания комнаты
@app.post("/rooms/", response_model=RoomResponse)
async def create_room(request: RoomCreate, db: Session = Depends(get_db)):
    room_id = str(uuid.uuid4())
    db_room = db.query(Room).filter(Room.room_name == request.room_name).first()
    if db_room:
        raise HTTPException(status_code=400, detail="Room name already exists")
    new_room = Room(room_id=room_id, room_name=request.room_name)
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return RoomResponse(room_id=new_room.room_id, room_name=new_room.room_name)

# Эндпоинт для получения комнаты по room_id
@app.get("/rooms/{room_id}", response_model=RoomResponse)
async def get_room(room_id: str, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.room_id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return RoomResponse(room_id=room.room_id, room_name=room.room_name)

# Эндпоинт для создания счета в комнате
@app.post("/rooms/{room_id}/bills/", response_model=BillResponse)
async def create_bill(room_id: str, request: BillCreate, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.room_id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    bill_id = str(uuid.uuid4())
    new_bill = Bill(bill_id=bill_id, bill_name=request.bill_name, total_amount=request.total_amount, room_id=room_id)
    db.add(new_bill)
    db.commit()
    db.refresh(new_bill)
    return BillResponse(bill_id=new_bill.bill_id, bill_name=new_bill.bill_name, total_amount=new_bill.total_amount, room_id=new_bill.room_id)

# Эндпоинт для получения всех счетов в комнате
@app.get("/rooms/{room_id}/bills/", response_model=List[BillResponse])
async def get_bills(room_id: str, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.room_id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    bills = db.query(Bill).filter(Bill.room_id == room_id).all()
    return [BillResponse(bill_id=bill.bill_id, bill_name=bill.bill_name, total_amount=bill.total_amount, room_id=bill.room_id) for bill in bills]