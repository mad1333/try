from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import qrcode
import uuid
import base64
from io import BytesIO

app = FastAPI()

# Настроим путь для хранения статических файлов, таких как QR-коды
app.mount("/static", StaticFiles(directory="static"), name="static")

# Хранилище для комнат, где ключ - ID комнаты, значение - список участников
rooms = {}


# Главная страница
@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    return """
    <html>
    <body>
        <h1>Добро пожаловать в систему!</h1>
        <p><a href="/create_room">Создать комнату</a></p>
        <p><a href="/join_room">Войти в комнату</a></p>
    </body>
    </html>
    """


# Страница для создания комнаты
@app.get("/create_room", response_class=HTMLResponse)
async def create_room_page():
    return """
    <html>
    <body>
        <h1>Создание комнаты</h1>
        <form action="/create_room" method="post">
            <button type="submit">Создать комнату</button>
        </form>
    </body>
    </html>
    """


# Обработчик для создания комнаты
@app.post("/create_room", response_class=HTMLResponse)
async def create_room():
    room_id = str(uuid.uuid4())  # Генерация уникального ID для комнаты
    rooms[room_id] = []  # Инициализируем список участников

    # Генерация QR-кода
    url = f"http://127.0.0.1:8000/join_room/{room_id}"
    img = qrcode.make(url)
    img_io = BytesIO()
    img.save(img_io)
    img_io.seek(0)

    img_base64 = base64.b64encode(img_io.getvalue()).decode("utf-8")

    return f"""
    <html>
    <body>
        <h1>Комната создана!</h1>
        <h2>Сканируйте QR-код или используйте следующий ID для присоединения:</h2>
        <img src="data:image/png;base64,{img_base64}" alt="QR-код">
        <p>ID комнаты: {room_id}</p>
        <p><a href="/">Вернуться на главную страницу</a></p>
    </body>
    </html>
    """


# Страница для входа в комнату
@app.get("/join_room/{room_id}", response_class=HTMLResponse)
async def join_room_page(room_id: str):
    if room_id not in rooms:
        return HTMLResponse("<h1>Комната не найдена</h1>")

    return f"""
    <html>
    <body>
        <h1>Вход в комнату</h1>
        <h2>Введите ваше имя:</h2>
        <form action="/join_room/{room_id}" method="post">
            <input type="text" name="name" placeholder="Ваше имя" required>
            <button type="submit">Присоединиться</button>
        </form>
    </body>
    </html>
    """


# Обработчик для добавления пользователя в комнату
@app.post("/join_room/{room_id}", response_class=HTMLResponse)
async def join_room(room_id: str, name: str):
    if room_id not in rooms:
        return HTMLResponse("<h1>Комната не найдена</h1>")

    rooms[room_id].append(name)
    participants = ", ".join(rooms[room_id])

    return f"""
    <html>
    <body>
        <h1>{name} присоединился(лась) к комнате!</h1>
        <h2>Список участников:</h2>
        <p>{participants}</p>
        <p><a href="/">Вернуться на главную страницу</a></p>
    </body>
    </html>
    """

