from flask import Flask, jsonify, request

app = Flask(__name__)

# Используем простой список словарей в качестве "базы данных" в памяти
# (сущность: id, dish_name, price, category)
dishes = [
    {"id": 1, "dish_name": "Паста Карбонара", "price": 450.0, "category": "Основные блюда"},
    {"id": 2, "dish_name": "Цезарь с курицей", "price": 350.0, "category": "Салаты"},
    {"id": 3, "dish_name": "Тирамису", "price": 250.0, "category": "Десерты"}
]

next_id = 4

@app.route('/api/dishes', methods=['GET'])
def get_dishes():
    """Получить список всех блюд"""
    return jsonify({'dishes': dishes})

@app.route('/api/dishes/<int:dish_id>', methods=['GET'])
def get_dish(dish_id):
    """Получить блюдо по ID"""
    dish = next((dish for dish in dishes if dish['id'] == dish_id), None)
    if dish:
        return jsonify(dish)
    return jsonify({'error': 'Dish not found'}), 404

@app.route('/api/dishes', methods=['POST'])
def create_dish():
    """Создать новое блюдо"""
    global next_id
    
    # Проверяем наличие обязательных полей
    if not request.json:
        return jsonify({'error': 'Request must be JSON'}), 400
    
    required_fields = ['dish_name', 'price', 'category']
    for field in required_fields:
        if field not in request.json:
            return jsonify({'error': f'Field "{field}" is required'}), 400
    
    # Проверяем тип цены
    try:
        price = float(request.json['price'])
    except ValueError:
        return jsonify({'error': 'Price must be a number'}), 400
    
    # Создаем новое блюдо
    new_dish = {
        'id': next_id,
        'dish_name': request.json['dish_name'],
        'price': price,
        'category': request.json['category']
    }
    
    dishes.append(new_dish)
    next_id += 1
    return jsonify(new_dish), 201


# --------------- 
# Новый блок
# ---------------


# Эндпоинт сводки меню

@app.route('/api/dishes/menu_summary', methods=['GET'])
def get_financial_summary():
    """Получить финансовую сводку меню"""
    
    if not dishes:
        return jsonify({
            'total_menu_value': 0,
            'average_dish_price': 0,
            'price_distribution': {
                'budget': 0,      # до 300 руб
                'medium': 0,      # 300-600 руб
                'premium': 0      # выше 600 руб
            },
            'price_percentages': {
                'budget_percentage': 0,
                'medium_percentage': 0,
                'premium_percentage': 0
            },
            'cheapest_dish': None,
            'most_expensive_dish': None,
            'message': 'Меню пустое'
        })
    
    # Общая стоимость всех блюд в меню
    total_menu_value = sum(d['price'] for d in dishes)
    total_dishes = len(dishes)
    average_dish_price = total_menu_value / total_dishes
    
    # Распределение по ценовым диапазонам
    price_ranges = {
        'budget': 0,      # до 300 руб
        'medium': 0,      # 300-600 руб
        'premium': 0      # выше 600 руб
    }
    
    for dish in dishes:
        price = dish['price']
        if price < 300:
            price_ranges['budget'] += 1
        elif price <= 600:
            price_ranges['medium'] += 1
        else:
            price_ranges['premium'] += 1
    
    # Процентное соотношение
    price_percentages = {
        'budget_percentage': round((price_ranges['budget'] / total_dishes) * 100, 2),
        'medium_percentage': round((price_ranges['medium'] / total_dishes) * 100, 2),
        'premium_percentage': round((price_ranges['premium'] / total_dishes) * 100, 2)
    }
    
    # Самое дешевое и дорогое блюдо
    cheapest_dish = min(dishes, key=lambda x: x['price'])
    most_expensive_dish = max(dishes, key=lambda x: x['price'])
    
    summary = {
        'total_menu_value': round(total_menu_value, 2),
        'average_dish_price': round(average_dish_price, 2),
        'price_distribution': price_ranges,
        'price_percentages': price_percentages,
        'cheapest_dish': {
            'id': cheapest_dish['id'],
            'name': cheapest_dish['dish_name'],
            'price': cheapest_dish['price'],
            'category': cheapest_dish['category']
        },
        'most_expensive_dish': {
            'id': most_expensive_dish['id'],
            'name': most_expensive_dish['dish_name'],
            'price': most_expensive_dish['price'],
            'category': most_expensive_dish['category']
        },
        'total_dishes': total_dishes,
        'message': 'Финансовая сводка меню ресторана'
    }
    
    return jsonify(summary)

if __name__ == '__main__':
    # Слушаем на порту 5000, доступном для всех интерфейсов
    app.run(host='0.0.0.0', port=5000, debug=True)
