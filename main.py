from fastapi import FastAPI
from pydantic import BaseModel
import asyncpg
# Импортируем httpx для общения с нашей локальной нейросетью Ollama
import httpx 

app = FastAPI()

class CodeRequest(BaseModel):
    username: str
    code: str

DB_URL = "postgresql://localhost/codemind_db"

@app.post("/analyze")
async def analyze_code(request: CodeRequest):
    conn = await asyncpg.connect(DB_URL)
    
    try:
        # 1. Работа с пользователем и историей (как и было)
        await conn.execute('''
            INSERT INTO users (username) VALUES ($1) ON CONFLICT (username) DO NOTHING
        ''', request.username)
        
        user_id = await conn.fetchval('''
            SELECT id FROM users WHERE username = $1
        ''', request.username)
        
        check_id = await conn.fetchval('''
            INSERT INTO code_checks (user_id, submitted_code)
            VALUES ($1, $2)
            RETURNING id
        ''', user_id, request.code)
        
        # 2. ФОРМИРУЕМ ЗАПРОС К ИИ
        # Пишем "Промпт" (задание) для нейросети
        prompt = f"Ты опытный наставник по программированию (Senior Developer). Найди ошибки или плохой стиль в этом коде и напиши исправленный вариант. Код пользователя:\n{request.code}"
        
        # 3. ОТПРАВЛЯЕМ КОД В OLLAMA (Локальный ИИ)
        # Открываем асинхронный клиент для HTTP-запросов
        async with httpx.AsyncClient() as client:
            # Стучимся на локальный адрес Ollama (порт 11434 по умолчанию)
            response = await client.post("http://localhost:11434/api/generate", json={
                "model": "qwen2.5-coder:1.5b", # Название модели, которую мы скачали
                "prompt": prompt,              # Наше задание
                "stream": False                # Ждем ответ целиком, а не по одной букве
            }, timeout=30.0) # Даем нейросети 30 секунд на раздумья
            
            # Достаем текст ответа из JSON, который вернула Ollama
            ai_text = response.json()["response"]

        # 4. СОХРАНЯЕМ ОТВЕТ ИИ В БАЗУ ДАННЫХ
        await conn.execute('''
            INSERT INTO ai_suggestions (check_id, suggested_code)
            VALUES ($1, $2)
        ''', check_id, ai_text)
        
        # 5. ВОЗВРАЩАЕМ РЕЗУЛЬТАТ ПОЛЬЗОВАТЕЛЮ
        return {
            "status": "success",
            "message": "ИИ завершил анализ кода.",
            "ai_review": ai_text, # Здесь будет полный разбор от нейросети!
            "suggestion_id": check_id
        }
        
    finally:
        await conn.close()
# Создаем новую схему запроса. 
# Мы просим фронтенд прислать ID подсказки и булево значение: True (👍) или False (👎).
class FeedbackRequest(BaseModel):
    suggestion_id: int
    is_accepted: bool

# Создаем новый endpoint по адресу /feedback. 
# Метод POST, так как мы отправляем данные для сохранения.
@app.post("/feedback")
async def save_feedback(feedback: FeedbackRequest):
    conn = await asyncpg.connect(DB_URL)
    try:
        # Обновляем (UPDATE) строку в таблице ai_suggestions.
        # Мы ищем ту подсказку, чей id совпадает с suggestion_id, который прислал пользователь,
        # и записываем в колонку is_accepted значение True или False.
        await conn.execute('''
            UPDATE ai_suggestions 
            SET is_accepted = $1 
            WHERE check_id = $2
        ''', feedback.is_accepted, feedback.suggestion_id)
        
        # Если лайк, радуемся. Если дизлайк, обещаем исправиться.
        status_msg = "Спасибо! ИИ запомнил, что это хороший совет 👍" if feedback.is_accepted else "Принято. ИИ учтет, что совет был плохим 👎"
        
        return {
            "status": "success",
            "message": status_msg
        }
    finally:
        await conn.close()