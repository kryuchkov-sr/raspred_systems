from flask import Flask, request
import ssl
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509 import load_pem_x509_certificate
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

app = Flask(__name__)

@app.before_request
def verify_client_cert():
    try:
        cert = request.json.get('certificate')
        if not cert:
            return {'error': 'Сертификат не предоставлен'}, 401
        
        if not verify_certificate(cert):
            return {'error': 'Неверный сертификат'}, 401
        
    except Exception as e:
        return {'error': f'Ошибка проверки сертификата: {str(e)}'}, 401

@app.route('/api/data', methods=['POST'])
def get_data():
    try:
        data = request.json.get('data')
        sort_order = request.json.get('sort', 'asc')  # 'asc' - по возрастанию, 'desc' - по убыванию
        
        if not data:
            return {'error': 'Данные не предоставлены'}, 400
        
        # Расшифровка данных
        decrypted_data = decrypt_data(data)
        
        try:
            # Предполагаем, что данные - числа, разделенные запятыми
            numbers = list(map(int, decrypted_data.decode().split(',')))
        except ValueError:
            return {'error': 'Неверный формат данных, ожидались числа через запятую'}, 400
        
        # Сортировка
        if sort_order == 'asc':
            numbers.sort()  # по возрастанию
        elif sort_order == 'desc':
            numbers.sort(reverse=True)  # по убыванию
        else:
            return {'error': 'Неверный порядок сортировки, используйте "asc" или "desc"'}, 400
        
        sorted_data_str = ','.join(map(str, numbers))
        return {'result': 'ok', 'sorted_data': sorted_data_str}
        
    except Exception as e:
        return {'error': str(e)}, 400

def verify_certificate(cert_pem):
    """
    Проверяет, что клиентский сертификат подписан CA.
    """
    try:
        # Загружаем клиентский сертификат
        client_cert = load_pem_x509_certificate(cert_pem.encode(), default_backend())
        
        # Загружаем сертификат CA
        with open('ca_cert.pem', 'rb') as f:
            ca_cert = load_pem_x509_certificate(f.read(), default_backend())
        
        # Проверяем, что клиентский сертификат подписан CA
        ca_public_key = ca_cert.public_key()
        ca_public_key.verify(
            client_cert.signature,
            client_cert.tbs_certificate_bytes,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False

def decrypt_data(encrypted_data):
    """
    Расшифровывает данные с использованием симметричного шифрования Fernet.
    """
    try:
        # Загружаем ключ шифрования
        with open('encryption_key.txt', 'rb') as f:
            key = f.read()
        
        # Расшифровываем данные
        cipher = Fernet(key)
        decrypted_bytes = cipher.decrypt(encrypted_data.encode())
        return decrypted_bytes
        
    except FileNotFoundError:
        raise Exception("Файл с ключом шифрования не найден")
    except Exception as e:
        raise Exception(f"Ошибка расшифровки: {str(e)}")

if __name__ == '__main__':
    import sys
    
    # Порт можно указать как аргумент командной строки или переменную окружения
    port = 5000
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    elif 'PORT' in os.environ:
        port = int(os.environ['PORT'])
    
    # Настраиваем SSL контекст для mTLS
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain('server_cert.pem', 'server_key.pem')
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations('ca_cert.pem')
    
    print(f"Запуск сервера на порту {port}")
    app.run(host='0.0.0.0', port=port, ssl_context=context)
