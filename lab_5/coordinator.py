from flask import Flask, request
import requests

app = Flask(__name__)
# URL серверов для балансировки нагрузки
server_urls = ['https://127.0.0.1:5001', 'https://127.0.0.1:5002']

@app.route('/api/data', methods=['POST'])
def handle_request():
    data = request.get_json()
    
    # Пробуем отправить запрос каждому серверу по очереди
    for url in server_urls:
        try:
            # Координатор предоставляет клиентский сертификат для mTLS
            # Проверяем сертификаты серверов с использованием CA сертификата
            response = requests.post(
                f"{url}/api/data", 
                json=data, 
                verify='ca_cert.pem',
                cert=('client_cert.pem', 'client_key.pem'),  # Клиентский сертификат для mTLS
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
                
        except requests.exceptions.RequestException:
            # Если сервер не отвечает, пробуем следующий
            continue
    
    return {'error': 'Все серверы недоступны'}, 503

if __name__ == '__main__':
    print("Запуск координатора на порту 8000")
    app.run(host='0.0.0.0', port=8000)
