import json
import requests  # Если понадобится отправка данных приложению

# JSON-данные
data = {
    "restaurant": {
        "name": "Наименование ресторана",
        "address": "Адрес ресторана"
    },
    "check": {
        "number": "#",
        "table": "#6",
        "guests": 2,
        "date": "29-11-2013",
        "opened": "21:23",
        "closed": "29-11-2018",
        "cashier": "Кассир",
        "waiter": "Лилия",
        "items": [
            {
                "dish": "Фитнесс. салат",
                "quantity": 1,
                "price": 210.00
            },
            {
                "dish": "Цезарь с курицей",
                "quantity": 1,
                "price": 240.00
            },
            {
                "dish": "РИЗОТТО С МОРЕПРОДУКТАМ",
                "quantity": 1,
                "price": 300.00
            },
            {
                "dish": "БАРАШЕК С РОЗМАРИНОМ",
                "quantity": 1,
                "price": 500.00
            },
            {
                "dish": "Хлеб",
                "quantity": 1,
                "price": 50.00
            },
            {
                "dish": "Рисовая лапша с креветками",
                "quantity": 1,
                "price": 290.00
            }
        ],
        "tip_commendation": "Вознаграждение официанту приветствуется и всегда остается на Ваше усмотрение."
    }
}

# Извлечение нужных данных
items_summary = [
    {"dish": item["dish"], "quantity": item["quantity"], "price": item["price"]}
    for item in data["check"]["items"]
]

# Сохранение в JSON-файл
with open("filtered_items.json", "w", encoding="utf-8") as f:
    json.dump(items_summary, f, ensure_ascii=False, indent=4)

# Печать, чтобы проверить содержимое файла (опционально)
print("Data saved to filtered_items.json")

# Подготовка данных для отправки приложению (пример отправки)
json_data = json.dumps(items_summary, ensure_ascii=False)

# Если нужно отправить данные, пример с requests (поменяйте URL на нужный)
try:
    response = requests.post("http://example.com/api/items", data=json_data, headers={"Content-Type": "application/json"})
    print("Response status:", response.status_code)
    print("Response body:", response.json())
except requests.exceptions.RequestException as e:
    print("Error sending data:", e)