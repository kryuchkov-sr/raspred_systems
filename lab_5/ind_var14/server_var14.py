import json
import requests
from cryptography.fernet import Fernet

@app.route('/api/data', methods=['POST'])
def get_data():
    try:
        data = request.get_json()
        if not data or 'data' not in data:
            return {'error': 'Data not provided'}, 400

        # Получаем зашифрованные данные и параметр сортировки
        encrypted_data = data['data']
        sort_order = data.get('sort_order', 'asc')  # По умолчанию — по возрастанию

        # Расшифровываем данные
        decrypted_bytes = decrypt_data(encrypted_data)
        decrypted_str = decrypted_bytes.decode('utf-8')

        # Пытаемся распарсить как JSON (ожидаем массив)
        import json
        try:
            parsed_data = json.loads(decrypted_str)
            if not isinstance(parsed_data, list):
                raise ValueError("Data must be a JSON array")
        except (json.JSONDecodeError, ValueError) as e:
            return {'error': f'Invalid data format: {str(e)}'}, 400

        # Сортируем данные
        if sort_order == 'desc':
            sorted_data = sorted(parsed_data, reverse=True)
        else:  # asc
            sorted_data = sorted(parsed_data)

        # Логируем
        print(f"Decrypted data: {parsed_data}")
        print(f"Sorted data ({sort_order}): {sorted_data}")

        # Возвращаем результат
        return {
            'result': 'ok',
            'original_data': parsed_data,
            'sorted_data': sorted_data,
            'sort_order': sort_order
        }

    except Exception as e:
        return {'error': str(e)}, 400
