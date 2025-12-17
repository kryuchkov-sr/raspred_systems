import requests
from cryptography.fernet import Fernet
import sys

def make_request(sort_order='asc'):
    # Загружаем ключ шифрования (тот же, что и на сервере)
    try:
        key = open('encryption_key.txt', 'rb').read()
        cipher = Fernet(key)
        
        # Данные для сортировки (числа через запятую)
        plaintext_data = "5,3,9,1,7,2"
        encrypted_data = cipher.encrypt(plaintext_data.encode()).decode()
        
    except FileNotFoundError:
        print("Ошибка: файл encryption_key.txt не найден")
        return
    
    data = {
        "certificate": open('client_cert.pem', 'r').read(),
        "data": encrypted_data,
        "sort": sort_order  # Параметр сортировки
    }

    try:
        # Отправляем HTTP запрос к координатору
        response = requests.post('http://localhost:8000/api/data', json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Успех: {result}")
        else:
            print(f"Ошибка: {response.status_code} - {response.text}")
            
    except requests.exceptions.RequestException as req_error:
        print(f"Ошибка запроса: {req_error}")

if __name__ == '__main__':
    # Можно передать аргумент сортировки через командную строку
    sort_order = sys.argv[1] if len(sys.argv) > 1 else 'asc'
    make_request(sort_order)
