# LangChain Natural Language SDK Agent (Mock API Wrapper)

Минимальный прототип AI-агента на базе **LangChain** и локальной LLM (**Qwen2.5-Coder:7b-16k** через Ollama), работающий как natural-language SDK над API-сервисом:
1. Принимает запрос на естественном языке из CLI.
2. Интерпретирует намерение пользователя.
3. Вызывает соответствующие методы API через LangChain Tools.
4. Возвращает структурированный результат в фиксированном формате контракта.

---

## 📂 Структура проекта

```text
langchain-nl-sdk/
├── requirements.txt   # Зафиксированные минимальные зависимости
├── mock_service.py    # Mock API сервис сущности User с сохранением в db.json
├── tools.py           # LangChain Tools (@tool) для операций API
├── agent.py           # Инициализация LLM, системный промпт, middleware и граф агента
├── main.py            # CLI интерфейс (точка входа)
├── db.json            # Локальное хранилище данных (создается автоматически)
└── README.md          # Документация и примеры использования
```

---

## 📋 Контракт ответа

Каждый ответ агента строго соответствует 4-строчному контракту:
```text
Status: success | error
Action: <краткое описание действия>
Data: <структурированные данные API в JSON / None>
Errors: <текст ошибки или None>
```

---

## 🛠️ Операции Mock API

Mock-сервис (`mock_service.py`) реализует 4 ключевые операции над сущностью `User`:
- **Создание сущности**: `create_user(name, email, status)`
- **Получение сущности**: `get_user(user_id, name)`
- **Обновление состояния**: `update_user_status(new_status, user_id, name)`
- **Список сущностей**: `list_users(status, limit)`

Данные сохраняются в локальный файл `db.json`, поэтому созданные и измененные сущности сохраняются между вызовами CLI.

---

## 🚀 Быстрый старт

### 1. Подготовка модели в Ollama
Убедитесь, что Ollama запущена и модель скачана:
```bash
ollama pull qwen2.5-coder:7b-16k
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Запуск команд из CLI

#### Создание пользователя:
```bash
python main.py "создай пользователя с именем Alex"
```
**Вывод:**
```text
Status: success
Action: Создан пользователь с именем Alex
Data: {"id": 3, "name": "Alex", "email": "alex@example.com", "status": "active", "created_at": "..."}
Errors: None
```

#### Поиск пользователя:
```bash
python main.py "найди пользователя Alice"
```
**Вывод:**
```text
[DEBUG TOOL] get_user({'user_id': None, 'name': 'Alice'}) -> {"success": true, "data": {"id": 1, "name": "Alice", "email": "alice@example.com", "status": "active", "created_at": "2026-11-20T10:00:00"}}
Status: success  
Action: Получены данные пользователя Alice  
Data: {"id": 1, "name": "Alice", "email": "alice@example.com", "status": "active", "created_at": "2026-11-20T10:00:00"}  
Errors: None
```

#### Создание пользователя:
```bash
python main.py "создай пользователя с именем Alex"
```
**Вывод:**
```text
[DEBUG TOOL] create_user({'name': 'Alex', 'email': None, 'status': 'active'}) -> {"success": true, "data": {"id": 3, "name": "Alex", "email": "alex@example.com", "status": "active", "created_at": "2026-11-24T21:47:14.262587"}, "message": "User 'Alex' created successfully."}
Status: success
Action: Создан пользователь с именем Alex
Data: {"id": 3, "name": "Alex", "email": "alex@example.com", "status": "active", "created_at": "..."}
Errors: None
```

#### Обновление статуса:
```bash
python main.py "обнови статус пользователя Alex на suspended"
```
**Вывод:**
```text
[DEBUG TOOL] update_user_status({'new_status': 'suspended', 'user_id': None, 'name': 'Alex'}) -> {"success": true, "data": {"id": 3, "name": "Alex", "email": "alex@example.com", "status": "suspended", ...}, "message": "Status of user 'Alex' updated from 'active' to 'suspended'."}
Status: success
Action: Обновлен статус пользователя Alex на suspended
Data: {"id": 3, "name": "Alex", "email": "alex@example.com", "status": "suspended", "created_at": "..."}
Errors: None
```

#### Получение списка по фильтру:
```bash
python main.py "покажи список пользователей со статусом inactive"
```
**Вывод:**
```text
[DEBUG TOOL] list_users({'status': 'inactive', 'limit': 10}) -> {"success": true, "data": [{"id": 2, "name": "Bob", ...}], "total_matched": 1, "total_system_users": 3}
Status: success
Action: Получен список пользователей со статусом inactive
Data: [{"id": 2, "name": "Bob", "email": "bob@example.com", "status": "inactive", "created_at": "..."}]
Errors: None
```

#### Обработка ошибок (сущность не найдена):
```bash
python main.py "найди пользователя с именем UnknownPerson"
```
**Вывод:**
```text
[DEBUG TOOL] get_user({'user_id': None, 'name': 'UnknownPerson'}) -> {"success": false, "error": "User with name='UnknownPerson' not found."}
Status: error
Action: Поиск пользователя с именем 'UnknownPerson'
Data: None
Errors: Пользователь с именем 'UnknownPerson' не найден.
```

---

## ⚙️ Переменные окружения (опционально)

- `OLLAMA_MODEL`: переопределение имени модели (по умолчанию `qwen2.5-coder:7b-16k`).
- `OLLAMA_BASE_URL`: адрес Ollama сервера (по умолчанию `http://localhost:11434`).
