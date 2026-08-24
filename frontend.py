# Импортируем Streamlit (st - это общепринятое короткое имя)
import streamlit as st
import httpx # Для отправки запросов на наш Backend
import asyncio # Для асинхронной работы

# Устанавливаем настройки страницы (заголовок и иконку вкладки в браузере)
st.set_page_config(page_title="CodeMind AI", page_icon="🧠", layout="wide")

# Рисуем заголовок на самой странице
st.title("🧠 CodeMind AI: Умный наставник по коду")
st.markdown("Вставьте свой код ниже, и искусственный интеллект найдет ошибки, предложит улучшения и напишет готовые блоки (Low-code).")

# Создаем колонки. Слева будет ввод имени, справа - пусто (для красоты)
col1, col2 = st.columns([1, 2])
with col1:
    # Поле ввода текста. Результат сразу попадает в переменную username
    username = st.text_input("Ваше имя (username):", value="Luckylake215")

# Большое текстовое поле для ввода кода
code_input = st.text_area("Ваш код для проверки:", height=200, placeholder="def hello():\n    print('Привет, мир!')")

# Кнопка для запуска анализа
if st.button("🚀 Проанализировать код", type="primary"):
    
    # Если поля пустые, ругаемся
    if not username or not code_input:
        st.error("Пожалуйста, введите имя и код.")
    else:
        # Показываем красивый индикатор загрузки (спиннер), пока ИИ думает
        with st.spinner("ИИ анализирует ваш код (это может занять несколько секунд)..."):
            try:
                # Отправляем запрос на НАШ ЖЕ бэкенд, который работает на порту 8000
                import requests
                response = requests.post("http://127.0.0.1:8000/analyze", json={
                    "username": username,
                    "code": code_input
                })
                
                # Если сервер ответил ошибкой (например, 500), показываем её
                response.raise_for_status() 
                
                # Достаем данные из ответа
                result = response.json()
                
                # Выводим успешное сообщение и сам разбор от ИИ
                st.success(result["message"])
                
                # st.markdown красиво отрисовывает текст и даже подсвечивает синтаксис кода
                st.markdown("### Разбор от ИИ:")
                st.markdown(result["ai_review"])
                
                # Сохраняем ID подсказки в "состояние сессии" (память интерфейса), чтобы потом отправить лайк/дизлайк
                st.session_state['suggestion_id'] = result.get("suggestion_id")

            except Exception as e:
                st.error(f"Ошибка соединения с сервером: {e}")

# Отрисовываем кнопки обратной связи, ТОЛЬКО ЕСЛИ у нас есть suggestion_id (то есть анализ уже прошел)
if 'suggestion_id' in st.session_state and st.session_state['suggestion_id']:
    st.markdown("---") # Рисуем разделительную линию
    st.markdown("#### Помог ли вам этот совет?")
    
    # Две колонки для кнопок лайка и дизлайка
    btn_col1, btn_col2, _ = st.columns([1, 1, 8])
    
    with btn_col1:
        if st.button("👍 Да, супер"):
            # Если нажали Лайк, отправляем запрос на роут /feedback с is_accepted=True
            import requests
            requests.post("http://127.0.0.1:8000/feedback", json={
                "suggestion_id": st.session_state['suggestion_id'],
                "is_accepted": True
            })
            st.toast("Спасибо за оценку! ИИ становится умнее.")
            st.session_state['suggestion_id'] = None # Сбрасываем ID, чтобы скрыть кнопки
            st.rerun() # Перезагружаем интерфейс
            
    with btn_col2:
        if st.button("👎 Нет, ерунда"):
            # Если нажали Дизлайк, отправляем is_accepted=False
            import requests
            requests.post("http://127.0.0.1:8000/feedback", json={
                "suggestion_id": st.session_state['suggestion_id'],
                "is_accepted": False
            })
            st.toast("Принято. ИИ постарается лучше в следующий раз.")
            st.session_state['suggestion_id'] = None
            st.rerun()