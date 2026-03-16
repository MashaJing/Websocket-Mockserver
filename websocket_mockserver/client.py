import httpx
from typing import Any


class WebSocketMockServerClient:
    """Клиент для управления отправкой данных на сокет-сервере.

    Отправка данных из сокет-сервера регулируется посредством правил, которые могут быть добавлены или удалены.
    Существует 3 типа правил:
    - oneshot: для отправки сообщения один раз.
    - inbound: для отправки в ответ на конкретное сообщение.
    - schedule: для постоянной отправки сообщений с заданным интервалом.

    Attributes:
        base_url: URL сокет-сервера.
        connection_path: URL сокет-сервера.
    """
    def __init__(self, base_url: str = "", connection_path: str = ""):
        self.base_url = base_url
        self.connection_path = connection_path
        self._client = httpx.AsyncClient()

    async def get_rules(self) -> dict[str, Any]:
        """Получить все добавленные правила (oneshot, inbound, schedule) с mock-сервера.

        Returns:
            Словарь с текущими правилами.
        """
        url = f"{self.base_url}/admin/rules"
        response = await self._client.get(url)
        if response.status_code != 200:
            raise RuntimeError(f"Не удалось получить правила:"
                               f"{response.status_code} {response.text}")
        return response.json()

    async def add_inbound_rule(self, messages: list[dict[str, Any]],
                               expected_type: str, expected_payload: dict[str, Any]) -> dict[str, Any]:
        """Добавить inbound правило для ответа на конкретное websocket сообщение.

        Args:
            messages: Список сообщений для отправки
            expected_type: Тип сообщения для фильтрации
            expected_payload: Payload для фильтрации

        Returns:
            Ответ сервера с количеством добавленных inbound правил
        """
        url = f"{self.base_url}/admin/mapping/inbound"
        data = []
        for message in messages:
            data.append({
                "url_path": self.connection_path,
                "message": message,
                "type": expected_type,
                "payload": expected_payload,
            })
        response = await self._client.post(url, json=data)
        if response.status_code != 200:
            raise RuntimeError(f"Не удалось добавить inbound правило:"
                               f"{response.status_code} {response.text}")
        return response.json()

    async def add_oneshot_rule(self, messages: list[dict[str, Any]], timeout: float = 0.0) -> dict[str, Any]:
        """Добавить oneshot правило для единовременной отправки сообщений клиенту при подключении.

        Args:
        messages: Список сообщений для отправки клиенту.
        timeout: Задержка перед отправкой сообщений (секунды).

        Returns:
            Ответ сервера с количеством добавленных oneshot правил.
        """
        url = f"{self.base_url}/admin/mapping/oneshot"
        data = []
        for message in messages:
            data.append({
                "url_path": self.connection_path,
                "message": message,
                "timeout": timeout,
            })
        response = await self._client.post(url, json=data)
        if response.status_code != 200:
            raise RuntimeError(f"Не удалось добавить oneshot правило:"
                               f"{response.status_code} {response.text}")
        return response.json()

    async def delete_oneshot_rule(self, data: dict[str, Any]) -> dict[str, Any]:
        """Удалить oneshot правило с сервера.

        Args:
            data: Данные для удаления правила.

        Returns:
            Ответ сервера с количеством удалённых oneshot правил.
        """
        url = f"{self.base_url}/admin/mapping/oneshot"
        response = await self._client.delete(url, json=data)
        if response.status_code != 200:
            raise RuntimeError(f"Не удалось удалить oneshot правило:"
                               f"{response.status_code} {response.text}")
        return response.json()

    async def add_schedule_rule(self, messages: list[dict[str, Any]], timeout: float) -> dict[str, Any]:
        """Добавить schedule правило для периодической отправки сообщений клиенту.

        Args:
            messages: Список сообщений для отправки.
            timeout: Таймаут между отправкой сообщений (секунды).

        Returns:
            Ответ сервера с количеством добавленных schedule правил.
        """
        url = f"{self.base_url}/admin/mapping/schedule"
        data = []
        for message in messages:
            data.append({
                "url_path": self.connection_path,
                "message": message,
                "timeout": timeout,
            })
        response = await self._client.post(url, json=data)
        if response.status_code != 200:
            raise RuntimeError(f"Не удалось добавить schedule правило:"
                               f"{response.status_code} {response.text}")
        return response.json()

    async def delete_schedule_rule(self, data: dict[str, Any]) -> dict[str, Any]:
        """Удалить schedule правило с сервера.

        Args:
            data: Данные для удаления правила.

        Returns:
            Ответ сервера с количеством удалённых schedule правил
        """
        url = f"{self.base_url}/admin/mapping/schedule"
        response = await self._client.delete(url, json=data)
        if response.status_code != 200:
            raise RuntimeError(f"Не удалось удалить schedule правило:"
                               f"{response.status_code} {response.text}")
        return response.json()

    async def reset_server(self) -> dict[str, Any]:
        """Сбросить все правила на mock-сервере.

        Returns:
            Ответ сервера о результате сброса.
        """
        url = f"{self.base_url}/admin/mapping/reset"
        response = await self._client.post(url)
        if response.status_code != 200:
            raise RuntimeError(f"Не удалось сбросить сервер:"
                               f"{response.status_code} {response.text}")
        return response.json()
