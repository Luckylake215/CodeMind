# Импортируем классы для создания виртуальных пользователей из Locust
from locust import HttpUser, task, between

# Создаем класс нашего пользователя (виртуального тестировщика)
class CodeMindUser(HttpUser):
    # Указываем, что юзер будет ждать от 1 до 3 секунд между отправкой запросов
    wait_time = between(1, 3)

    # Декоратор @task означает "Делай это действие снова и снова"
    @task
    def test_analyze_code(self):
        # Отправляем кусок кода на анализ
        # self.client работает точно так же, как requests из предыдущего примера
        self.client.post("/analyze", json={
            "username": "LoadTester",
            "code": "def hello():\n  return 'Привет!'"
        })