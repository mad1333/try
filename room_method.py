from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = "postgresql://prod_backend:prod_backend@158.160.79.20/prod_backend"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Room(Base):
    __tablename__ = "room"
    room_id = Column(String, primary_key=True, index=True)
    room_name = Column(String, unique=True, index=True)
    bills = relationship("Bill", back_populates="room")

class Bill(Base):
    __tablename__ = "bills"
    bill_id = Column(String, primary_key=True, index=True)
    bill_name = Column(String, index=True)
    room_id = Column(String, ForeignKey("room.room_id"))
    room = relationship("Room", back_populates="bills")

class User(Base):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True, index=True)
    user_name = Column(String, unique=True, index=True)

Base.metadata.create_all(bind=engine)

class RoomCreate(BaseModel):
    room_name: str

class RoomResponse(BaseModel):
    room_name: str
    room_id: str

class UserCreate(BaseModel):
    user_name: str

class UserResponse(BaseModel):
    user_name: str
    user_id: str

class BillCreate(BaseModel):
    room_id: str
    bill_name: str

class BillResponse(BaseModel):
    bill_id: str
    bill_name: str
    room_id: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/rooms/", response_model=RoomResponse)
async def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    room_id = str(uuid.uuid4())
    if db.query(Room).filter(Room.room_name == room.room_name).first():
        raise HTTPException(status_code=400, detail="Room name already exists")
    new_room = Room(room_id=room_id, room_name=room.room_name)
    db.add(new_room)
    db.commit()
    db.refresh(new_room)
    return RoomResponse(room_name=new_room.room_name, room_id=new_room.room_id)

@app.get("/rooms/{room_id}", response_model=RoomResponse)
async def get_room(room_id: str, db: Session = Depends(get_db)):
    room = db.query(Room).filter(Room.room_id == room_id).first()
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return RoomResponse(room_name=room.room_name, room_id=room.room_id)

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    user_id = str(uuid.uuid4())
    db_user = db.query(User).filter(User.user_name == user.user_name).first()
    if db_user:
        return UserResponse(user_name=db_user.user_name, user_id=db_user.user_id)
    new_user = User(user_id=user_id, user_name=user.user_name)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserResponse(user_name=new_user.user_name, user_id=new_user.user_id)

@app.post("/bills/", response_model=BillResponse)
async def create_bill(bill: BillCreate, db: Session = Depends(get_db)):
    if not db.query(Room).filter(Room.room_id == bill.room_id).first():
        raise HTTPException(status_code=404, detail="Room not found")
    bill_id = str(uuid.uuid4())
    new_bill = Bill(bill_id=bill_id, bill_name=bill.bill_name, room_id=bill.room_id)
    db.add(new_bill)
    db.commit()
    db.refresh(new_bill)
    return BillResponse(bill_id=new_bill.bill_id, bill_name=new_bill.bill_name, room_id=new_bill.room_id)

@app.get("/bills/{bill_id}", response_model=BillResponse)
async def get_bill(bill_id: str, db: Session = Depends(get_db)):
    bill = db.query(Bill).filter(Bill.bill_id == bill_id).first()
    if bill is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    return BillResponse(bill_id=bill.bill_id, bill_name=bill.bill_name, room_id=bill.room_id)