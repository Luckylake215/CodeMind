import requests # Библиотека для отправки запросов (как браузер, только в коде)

# Адрес нашего локального сервера
BASE_URL = "http://127.0.0.1:8000"

# В pytest любая функция, начинающаяся со слова "test_", будет запущена автоматически
def test_analyze_endpoint_success():
    """Тест 1: Проверяем, как система реагирует на код, в котором есть print (должно быть предупреждение)"""
    
    # 1. Формируем данные (Паттерн Arrange)
    payload = {
        "username": "QA_Engineer",
        "code": "print('Тест')"
    }
    
    # 2. Отправляем POST-запрос на сервер (Паттерн Act)
    response = requests.post(f"{BASE_URL}/analyze", json=payload)
    
    # 3. Проверяем результаты (Паттерн Assert - утверждение)
    # Если статус ответа не 200 (ОК), тест с треском провалится
    assert response.status_code == 200
    
    # Достаем JSON из ответа
    data = response.json()
    
    # Мы ожидаем, что раз в коде есть print, статус должен быть "warning" или "success" 
    # (в зависимости от того, что ответит нейросеть)
    assert "status" in data
    assert "ai_review" in data

def test_feedback_endpoint():
    """Тест 2: Проверяем, работает ли сохранение лайков/дизлайков"""
    payload = {
        "suggestion_id": 1, # Допустим, мы лайкаем первую подсказку в БД
        "is_accepted": True
    }
    
    response = requests.post(f"{BASE_URL}/feedback", json=payload)
    
    assert response.status_code == 200
    assert response.json()["status"] == "success"