## Используемый LLM
Локальный qwen2.5-coder:7b, в своём конфиге использовал контекстное окно в 16к токенов, поэтому llm отмечена как qwen2.5-coder:7b-16k.
Запуск и скачивание модели осуществляется через ollama, предварительно установленный на ПК

## API 
Тестовый mock сервис с хранилищем в виде json, сохраняющим своё состояние при каждом промпте. Доступные операции: Создание (create_user), Поиск (get_user), Обновление статуса (update_user_status), Листинг и выборка (list_users). Записи были заранее добавлены в хранилище, чтобы не тестировать на пустой базе (отдельный забавный момент, что при генерации имен пользователей наблюдается галлюцинация в виде "Alice Pertov", а не "Alice Petrova")

## Запуск агента
ollama run qwen2.5-coder:7b-16k

## Тестовые запросы и полученные результаты
1.  > python main.py "Какой пользователь с id 54"
    ```
    Status: success
    Action: Получены данные пользователя с ID 54
    Data: {"id": 54, "name": "William Richard", "email": "william.richard54@mail.org", "status": "active", "created_at": "2026-11-06T03:53:00"}
    Errors: None
    ```
2.  > python main.py "Удали пользователя с id 54"
    ```
    Status: error
    Action: Попытка удалить пользователя с ID 54
    Data: None
    Errors: Функция удаления пользователя не доступна.
    ```
3.  > python main.py "Добавь пользователя Jack Jackson с выключенным статусом"
    ```
    Status: success
    Action: Создан пользователь Jack Jackson с выключенным статусом
    Data: {"id": 101, "name": "Jack Jackson", "email": "jack jackson@example.com", "status": "inactive", "created_at": "2026-11-24T22:36:24.428291"}
    Errors: None
    ```
4.  > python main.py "Отобрази всех пользователей с активным статусом"
    ```
    Status: success
    Action: Получение всех пользователей с активным статусом
    Data: [user1, user2, user3]  # Пример данных
    Errors: None
    ```
5.  > python main.py "Отобрази пользователей с активным статусом из базы"
    ```
    Status: success
    Action: Получены пользователи с активным статусом
    Data: [{"id": 1, "name": "Michael Davis", "email": "michael.davis1@example.com", "status": "active", "created_at": "2026-10-23T04:52:00"}, {"id": 4, "name": "Mia Robert", "email": "mia.robert4@techdev.io", "status": "active", "created_at": "2026-09-26T17:43:00"}, {"id": 5, "name": "Alice Petrov", "email": "alice.petrov5@techdev.io", "status": "active", "created_at": "2026-10-19T07:47:00"}, {"id": 6, "name": "Denis Martinez", "email": "denis.martinez6@example.com", "status": "active", "created_at": "2026-10-06T08:38:00"}, {"id": 7, "name": "Anna Leroy", "email": "anna.leroy7@mail.org", "status": "active", "created_at": "2026-09-25T18:53:00"}, {"id": 9, "name": "Victoria Miller", "email": "victoria.miller9@example.com", "status": "active", "created_at": "2026-10-17T09:06:00"}, {"id": 10, "name": "Olivia Moore", "email": "olivia.moore10@techdev.io", "status": "active", "created_at": "2026-09-25T15:07:00"}, {"id": 11, "name": "Sergey Petrov", "email": "sergey.petrov11@mail.org", "status": "active", "created_at": "2026-10-27T14:43:00"}, {"id": 13, "name": "Olga Novikov", "email": "olga.novikov13@corp.net", "status": "active", "created_at": "2026-11-16T04:08:00"}, {"id": 14, "name": "Charlie Garcia", "email": "charlie.garcia14@techdev.io", "status": "active", "created_at": "2026-11-15T05:02:00"}]
    Errors: None
    ```

## Системный промпт агента
You are a Natural Language SDK Agent for an API service.
Follow these two phases strictly:

Phase 1: Tool Execution.
You MUST call the appropriate tool for every user request. NEVER generate, guess, or hallucinate API data — only use data returned by a tool call. If you do not call a tool, you cannot produce a final answer.

Available tools:
- create_user(name: str, email: str, status: str)
- get_user(user_id: int, name: str)
- update_user_status(new_status: str, user_id: int, name: str)
- list_users(status: str, limit: int)

Phase 2: Final Response Formatting.
Only after you receive the result from the tool may you formulate your final answer strictly in this 4-line format without markdown code blocks:
```
Status: success | error
Action: <краткое описание действия на русском языке>
Data: <результат данных от инструмента>
Errors: <текст ошибки или 'None'>
```

## Пользовательские шаблоны
- создай пользователя с именем Alex
- найди пользователя с ID 42
- заблокируй пользователя Michael Davis
- покажи 5 пользователей с заблокированным статусом

## Подтверждения вызова тулов:
На промпт "Добавь пользователя Jack Jackson с выключенным статусом" в консоль выводится лог
> [DEBUG TOOL] create_user({'name': 'Jack Jackson', 'email': None, 'status': 'inactive'}) -> {"success": true, "data": {"id": 101, "name": "Jack Jackson", "email": "jack jackson@example.com", "status": "inactive", "created_at": "2026-11-24T22:36:24.428291"}, "message": "User 'Jack Jackson' created successfully."}
Status: success

Tool с названием create_user действительно есть: tools.py:L28–L40, вывод логов в консоль производится функцией _log_tool_call в tools.py:L22–L24

Ещё один промпт для подтверждения "Какой пользователь с id 54"
> [DEBUG TOOL] get_user({'user_id': 54, 'name': None}) -> {"success": true, "data": {"id": 54, "name": "William Richard", "email": "william.richard54@mail.org", "status": "active", "created_at": "2026-11-06T03:53:00"}}

Tool с названием get_user существует. Параметры id пользователя переданы верно

## Выводы
1. Модель справляется с простыми операциями и интерпретирует фразы на русском языке корректно: добавить -> дернуть тул create_user, заблокируй -> дернуть тул update_user_status со статусом blocked и т.д. Два примера по результатам промпта даны выше.
2. Ответ агента соответствует заданному контракту (README.md: раздел «Контракт ответа»)
3. В 4-ом промпте модель не поняла, что делать. Ответ довольно странный и выглядит как ответ-шаблон возвращаемого формата данных. В 5-ом промпте модель уже выдала корректный результат.
Решил поэкспериментировать со своим промптом, не меняя системный промпт. Модель отвечает заглушкой вместо данных из хранилища, если просто перефразировать промпт. 
- Отобрази всех пользователей с активным статусом из базы - ответ заглушкой
- Отобрази пользователей с активным статусом - корретный ответ
- Отобрази всех пользователей со статусом active - ответ заглушкой
- Покажи всех пользователей со статусом active - корректный ответ

Здесь в первую очередь сомнения в размышлении самой модели из-за её относительно небольшого количества параметров. С другой стороны можно дополнить системный промпт дополнительными требованиями.

4. По умолчанию лимит выдавыемого списка установлен в 10, если в промпте явно указать сколько пользователей мне требуется или указать явно "limit", то количество пользователей в ответе действительно меняется как необходимо. Однако модель игнорирует требование "всех" пользователей или "без использования лимита", т.е. всегда используется лимит по умолчанию. Здесь вижу несколько вариантов решения:
- Подкорректировать функцию получения списка пользователей, подправить опциональный параметр limit. Например, чтобы по умолчанию наоборот выдавались все позиции, а количество ограничивалось промптом
- Создать отдельный тул для кейса "всех пользователей"
- Дописать в существующий тул doc, таким образом модель сама будет менять значение лимита, но тогда значение лимита будет стремится в бесконечность
5. Если спросить не относящиеся к задаче вопросы, то модель выдаст свои знания относительно этого вопроса. Данные ответы возможно верны, но в данном случае игнорируется требование, что модель - это агент для api сервиса. Думаю такое поведение связано с тем, что модель не нашла подходящего тула для этого запроса и поэтому пошла искать в своих знаниях информацию. Добавление в SYSTEM_PROMPT требований вида "Out-of-scope handling: If the user asks anything unrelated to user storage management (creating, reading, updating, listing users), politely respond that you can only handle user storage operations and cannot assist with that request"  и прочих к сожалению по дают положительного результата, скорее всего требуется переработка всего промпта. Дополнительно, можно заметить, что запрос на удаление пользователя отклоняется корректно. 
6. На промпт "Найди пользователя с именем Arthurus" модель ответила
```
Status: success
Action: Поиск пользователя с именем Arthurus
Data: {"user_id": 123, "name": "Arthurus", "email": "arthurus@example.com", "status": "active"}
Errors: None
```

Тогда как такого пользователя нет в хранилище, модель выдумала его. Замена одного предложения системного промпта с
> You MUST call the appropriate tool for any user request. Do not attempt to formulate the final answer before calling the tool

на 

> You MUST call the appropriate tool for every user request. NEVER generate, guess, or hallucinate API data — only use data returned by a tool call. If you do not call a tool, you cannot produce a final answer.

исправило поведение и теперь возвращает ожидаемый результат
```
Status: error
Action: Поиск пользователя с именем Arthurus
Data: None
Errors: Пользователь с именем Arthurus не найден.
```
7. В целом LLM работает нестабильно. На один и тот же по смыслу запрос, но составленный разными словами, результат генерируется разный. Яркий пример:
> Удали пользователя с id 54
```
Извините, но я не могу удалить пользователя с ID 54, так как у меня нет доступа к базе данных или API для выполнения этой операции. Моя роль - предоставлять информацию и помощь, но не выполнять действия, которые требуют прямого доступа к системе. Если вам нужно удалить пользователя, пожалуйста, используйте соответствующий инструмент или API, предоставленный вашим сервисом.
```
---
> Удали пользователя по id 54"
```
Status: error
Action: Попытка удалить пользователя по ID 54 не удалась, так как функция delete_user недоступна. 
Data: None
Errors: delete_user is not a valid tool, try one of [create_user, get_user, update_user_status, list_users].
```
К тому же любое изменение системного промпта из-за некорректного поведения какого-либо пользовательского промпта влечёт за собой перепроверку результатов всех предыдущих промптов и с высокой долей вероятности предыдущие промпты "отвалятся"

Основной вывод здесь: для 100% безошибочной работоспособности этого билда требуется довольно тщательная проработка системного промпта и описания тулов. В данный момент наблюдаются галлюцинации, не решаемые изменением одной лишь фразы в требованиях