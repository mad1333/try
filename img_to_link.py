'''import requests

API_KEY = '27a38476e5f5e0036c4d4fb912805bc6'

with open("photo.jpg", "rb") as img:
    response = requests.post(
        "https://api.imgbb.com/1/upload",
        data={"key": API_KEY},
        files={"image": img}
    )

if response.status_code == 200:
    link = response.json()['data']['url']
    print(f"Image uploaded: {link}")
else:
    print(f"Error: {response.status_code}")'''
'''

# Import the base64 encoding library.
import base64
import gzip
# Pass the image data to an encoding function.
def encode_image(image):
    with open(image, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    print(encoded_string)
    compressed_base64 = gzip.compress(encoded_string)
    print(compressed_base64)
    return compressed_base64

encode_image("photo.jpg")'''
from PIL import Image
import base64
import io

# Открываем изображение и конвертируем в WebP
with Image.open("path/to/your/image.jpg") as img:
    buffered = io.BytesIO()
    img.save(buffered, format="WEBP", quality=50)  # Понизьте качество при необходимости

    # Кодируем в Base64
    img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

print(img_base64)