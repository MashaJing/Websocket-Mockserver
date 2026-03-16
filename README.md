# Websocket mockserver (server + client)

# Принцип работы

`websocket-mockserver` — это сервер для мокирования WebSocket-сообщений.
Сервер позволяет создавать различные правила, которые определяют, какие сообщения и когда будут отправляться подключённому тестируемому приложению.

### Виды правил

- **oneshot** — сообщения отправляются клиенту один раз при подключении. Используется для имитации начального состояния или событий, которые должны произойти только при установлении соединения.
- **inbound** — сообщения отправляются в ответ на конкретное сообщение от клиента. Позволяет эмулировать реакцию сервера на действия пользователя.
- **schedule** — сообщения отправляются клиенту с заданным интервалом времени. Используется для имитации событий, происходящих периодически (например, обновление состояния).

С сервером поставляется класс клиента `WebSocketMockServerClient` на python, который может быть использован для управления правилами в автотестах.

# Обновление

1. Апнуть версию в setup.py
2. Апнуть переменную VERSION в .gitlab-ci.yml
3. Тэгнуть коммит с новым номером версии
4. Тыкнуть джобу build в CI

# Установка

1. Добавляем контейнер с сокет-сервером в желаемую compose-сеть:

```yml
# docker-compose.yml

websocket_server:
  image: <имя_образа>:<тэг>
  environment:
    - PORT=3003
    - LOG_LEVEL=DEBUG
  ports:
    - "3003"
```

2. Устанавливаем библиотеку:

```bash
pip install websocket-mockserver
```

## API

Ниже представлена документация к REST API сервера. Каждому методу сервера соответствует метод в python-клиенте.

### GET _/admin/rules_

Возвращает все добавленные правила.

**response:**

```json
{
  "oneshot rules": [],
  "inbound rules": [],
  "schedule rules": []
}
```

**python:**

```python
async def get_rules(self)
```

### POST _/admin/mapping/inbound_

Добавляет мок для ответа на конкретное websocket-сообщение. Поиск соответствия происходит по полям _type_, _type_pattern_, _payload_.

**params:**

```json
{
  /* каналы сообщений, строка с одним или несколькими каналами через запятую */
  "channels": str,
  /* regexp каналов, по которому будет сравниваться каналы */
  "channels_pattern": str,
  /* точный путь по которому клиент пытается подключиться */
  "url_path": str,
  /* regexp пути подключения */
  "url_pattern": str,
  /* точный тип сообщения */
  "type": str,
  /* regex по которому будет произведен поиск типа сообщения */
  "type_pattern": str,
  /* ответ, ожидаемый клиентом */
  "response": object
  /* полезная нагрузка, ожидаемая сервером */
  "payload": object,
}
```

**response:**

```json
{ "status": "ok", "inbound_rules_added": 0 }
```

**python:**

```python
async def add_inbound_rule(self, messages: list[dict], expected_type: str, expected_payload: dict)
```

### POST, DELETE _/admin/mapping/oneshot_

Добавляет/удаляет правило для разовой отправки сообщения клиенту при подключении.

**params:**

```json
{
  /* каналы сообщений, строка с одним или несколькими каналами через запятую */
  "channels": str,
  /* regexp каналов, по которому будет сравниваться каналы */
  "channels_pattern": str,
  /* точный путь по которому клиент пытается подключиться */
  "url_path": str,
  /* regexp пути подключения */
  "url_pattern": str,
  /* сообщение, ожидаемое клиентом */
  "message": object,
  /* задержка перед отправкой сообщения в сек (как в schedule.timeout) */
  "timeout": float
}
```

**response:**

```json
{ "status": "ok", "oneshot_rules_added": 0 }
{ "status": "ok", "oneshot_rules_removed": 0 }
```

**python:**

```python
async def add_oneshot_rule(self, messages: list[dict])
...
async def delete_oneshot_rule(self, data: dict)
```

### POST, DELETE _/admin/mapping/schedule_

Добавляет/удаляет правило для периодической отправки сообщения клиенту с заданным интервалом.

**params:**

```json
{
  /* каналы сообщений, строка с одним или несколькими каналами через запятую */
  "channels": str,
  /* regexp каналов, по которому будет сравниваться каналы */
  "channels_pattern": str,
  /* точный путь по которому клиент пытается подключиться */
  "url_path": str,
  /* сообщение, ожидаемое клиентом */
  "message": object,
  /* таймаут между отправкой сообщений в сек */
  "timeout": float
}
```

**response:**

```json
{ "status": "ok", "schedule_rules_added": 0 }
{ "status": "ok", "schedule_rules_removed": 0 }
```

**python:**

```python
async def add_schedule_rule(self, messages: list[dict], timeout: float)
...
async def delete_schedule_rule(self, data: dict)
```

### POST _/admin/mapping/reset_

Сбросить все правила на сервере.

**python:**

```python
async def reset_server(self)
```

# Подключение приложения к вебсокет-серверу

Тестируемое приложение подключается к серверу по пути:

```
WS /ws/{ws_path:path}
```

где ws_path - путь до мокируемого сервера. Например, если необходимо замокать

```
ws://example.com/user/ws
```

то подключение к соответствующему каналу нашего сервера будет происходить так (да, там два слэша):

```
ws://websocket_server/ws//user/ws
```

При подключении клиента сервер сравнивает путь и каналы с существующими правилами и отправляет соответствующие сообщения.
