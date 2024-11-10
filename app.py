from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uuid
from typing import List, Dict

app = FastAPI()

# Временные хранилища
rooms = []
main_bill_items = []
user_bills = {}


# Модели для API
class RoomCreate(BaseModel):
    room_name: str


class RoomResponse(BaseModel):
    room_name: str
    room_id: str


class MainBillItem(BaseModel):
    dish: str
    quantity: int
    price: float


class MainBillRequest(BaseModel):
    items: List[MainBillItem]


class UserBillRequest(BaseModel):
    user_id: str
    items: List[Dict[str, int]]

class UserBillResponse(BaseModel):
    user_id: str
    items: List[Dict[str, float]]


# Эндпоинт для создания комнаты
@app.post("/rooms/", response_model=RoomResponse)
async def create_room(room: RoomCreate):
    room_id = str(uuid.uuid4())
    new_room = {"room_id": room_id, "room_name": room.room_name}
    rooms.append(new_room)
    return RoomResponse(room_name=new_room["room_name"], room_id=new_room["room_id"])



@app.get("/rooms/{room_id}", response_model=RoomResponse)
async def get_room(room_id: str):
    room = next((r for r in rooms if r["room_id"] == room_id), None)
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")
    return RoomResponse(room_name=room["room_name"], room_id=room["room_id"])

@app.post("/main_bill/")
async def add_items_to_main_bill(request: MainBillRequest):
    for item in request.items:
        new_item = {
            "item_id": str(uuid.uuid4()),
            "dish": item.dish,
            "quantity": item.quantity,
            "price": item.price
        }
        main_bill_items.append(new_item)
    return {"message": "Items added to main bill successfully"}

@app.post("/user_bill/", response_model=UserBillResponse)
async def get_user_bill(request: UserBillRequest):
    selected_items = []

    for user_item in request.items:
        main_item = next((item for item in main_bill_items if item["dish"] == user_item["dish"]), None)

        if main_item is None:
            raise HTTPException(status_code=404, detail=f"Dish {user_item['dish']} not found in main bill")

        if user_item["quantity"] > main_item["quantity"]:
            raise HTTPException(
                status_code=400,
                detail=f"Requested quantity for {user_item['dish']} exceeds available quantity"
            )

        total_price = main_item["price"] * user_item["quantity"]
        selected_items.append({
            "dish": main_item["dish"],
            "quantity": user_item["quantity"],
            "price": total_price
        })


    user_bills[request.user_id] = selected_items

    return UserBillResponse(user_id=request.user_id, items=selected_items)