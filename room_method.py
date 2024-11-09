from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import uuid
import os
app = FastAPI()

DATABASE_URL = "postgresql://prod_backend:prod_backend@158.160.79.20/prod_backend"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Room(Base):
    __tablename__ = "rooms"
    room_id = Column(String, primary_key=True, index=True)
    room_name = Column(String, unique=True, index=True)

Base.metadata.create_all(bind=engine)


class RoomCreate(BaseModel):
    room_name: str

# Определяем модель ответа
class RoomResponse(BaseModel):
    room_name: str
    room_id: str

# Вспомогательная функция для создания сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Метод для создания комнаты
@app.post("/rooms/", response_model=RoomResponse)
async def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    room_id = str(uuid.uuid4())

    db_room = db.query(Room).filter(Room.room_name == room.room_name).first()
    if db_room:
        raise HTTPException(status_code=400, detail="Room name already exists")

    # Создаем запись для новой комнаты
    new_room = Room(room_id=room_id, room_name=room.room_name)
    db.add(new_room)
    db.commit()
    db.refresh(new_room)

    # Возвращаем ответ с room_name и room_id
    return RoomResponse(room_name=new_room.room_name, room_id=new_room.room_id)

