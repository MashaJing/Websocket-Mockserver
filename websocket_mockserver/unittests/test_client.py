import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from websocket_mockserver.client import WebSocketMockServerClient


class WebSocketMockServerClientTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        async_client_patcher = patch(
            "websocket_mockserver.client.httpx.AsyncClient"
        )
        self.async_client_factory = async_client_patcher.start()
        self.addCleanup(async_client_patcher.stop)

        self.http_client = self.async_client_factory.return_value
        self.http_client.get = AsyncMock()
        self.http_client.post = AsyncMock()
        self.http_client.delete = AsyncMock()
        self.client = WebSocketMockServerClient(
            base_url="http://mockserver.test",
            connection_path="events",
        )

    @staticmethod
    def response(payload=None, status_code=200, text=""):
        return SimpleNamespace(
            status_code=status_code,
            text=text,
            json=Mock(return_value=payload),
        )

    async def assert_http_error(self, request_mock, call):
        request_mock.return_value = self.response(
            status_code=503,
            text="service unavailable",
        )

        with self.assertRaises(RuntimeError) as context:
            await call()

        self.assertIn("503 service unavailable", str(context.exception))

    def test_creates_async_http_client(self):
        self.async_client_factory.assert_called_once_with()

    async def test_get_rules_returns_response_json_and_reports_error(self):
        expected = {"oneshot rules": [], "inbound rules": []}
        response = self.response(expected)
        self.http_client.get.return_value = response

        result = await self.client.get_rules()

        self.assertEqual(result, expected)
        self.http_client.get.assert_awaited_once_with(
            "http://mockserver.test/admin/rules"
        )
        response.json.assert_called_once_with()

        await self.assert_http_error(
            self.http_client.get,
            self.client.get_rules,
        )

    async def test_add_inbound_rule_posts_response_rules_and_reports_error(self):
        expected = {"status": "ok", "inbound_rules_added": 2}
        response = self.response(expected)
        self.http_client.post.return_value = response

        result = await self.client.add_inbound_rule(
            [{"event": "created"}, {"event": "updated"}],
            expected_type="order.changed",
            expected_payload={"id": 42},
        )

        self.assertEqual(result, expected)
        self.http_client.post.assert_awaited_once_with(
            "http://mockserver.test/admin/mapping/inbound",
            json=[
                {
                    "url_path": "events",
                    "response": {"event": "created"},
                    "type": "order.changed",
                    "payload": {"id": 42},
                },
                {
                    "url_path": "events",
                    "response": {"event": "updated"},
                    "type": "order.changed",
                    "payload": {"id": 42},
                },
            ],
        )
        response.json.assert_called_once_with()

        await self.assert_http_error(
            self.http_client.post,
            lambda: self.client.add_inbound_rule(
                [],
                expected_type="order.changed",
                expected_payload={},
            ),
        )

    async def test_add_oneshot_rule_posts_messages_and_reports_error(self):
        expected = {"status": "ok", "oneshot_rules_added": 2}
        response = self.response(expected)
        self.http_client.post.return_value = response

        result = await self.client.add_oneshot_rule(
            [{"id": 1}, {"id": 2}],
            timeout=0.25,
        )

        self.assertEqual(result, expected)
        self.http_client.post.assert_awaited_once_with(
            "http://mockserver.test/admin/mapping/oneshot",
            json=[
                {
                    "url_path": "events",
                    "message": {"id": 1},
                    "timeout": 0.25,
                },
                {
                    "url_path": "events",
                    "message": {"id": 2},
                    "timeout": 0.25,
                },
            ],
        )
        response.json.assert_called_once_with()

        await self.assert_http_error(
            self.http_client.post,
            lambda: self.client.add_oneshot_rule([]),
        )

    async def test_delete_oneshot_rule_sends_payload_and_reports_error(self):
        expected = {"status": "ok", "oneshot_rules_removed": 1}
        response = self.response(expected)
        self.http_client.delete.return_value = response
        rule = {"message": {"id": 1}, "url_path": "events"}

        result = await self.client.delete_oneshot_rule(rule)

        self.assertEqual(result, expected)
        self.http_client.delete.assert_awaited_once_with(
            "http://mockserver.test/admin/mapping/oneshot",
            json=rule,
        )
        response.json.assert_called_once_with()

        await self.assert_http_error(
            self.http_client.delete,
            lambda: self.client.delete_oneshot_rule(rule),
        )

    async def test_add_schedule_rule_posts_messages_and_reports_error(self):
        expected = {"status": "ok", "schedule_rules_added": 2}
        response = self.response(expected)
        self.http_client.post.return_value = response

        result = await self.client.add_schedule_rule(
            [{"id": 1}, {"id": 2}],
            timeout=5,
        )

        self.assertEqual(result, expected)
        self.http_client.post.assert_awaited_once_with(
            "http://mockserver.test/admin/mapping/schedule",
            json=[
                {
                    "url_path": "events",
                    "message": {"id": 1},
                    "timeout": 5,
                },
                {
                    "url_path": "events",
                    "message": {"id": 2},
                    "timeout": 5,
                },
            ],
        )
        response.json.assert_called_once_with()

        await self.assert_http_error(
            self.http_client.post,
            lambda: self.client.add_schedule_rule([], timeout=5),
        )

    async def test_delete_schedule_rule_sends_payload_and_reports_error(self):
        expected = {"status": "ok", "schedule_rules_removed": 1}
        response = self.response(expected)
        self.http_client.delete.return_value = response
        rule = {"message": {"id": 1}, "url_path": "events"}

        result = await self.client.delete_schedule_rule(rule)

        self.assertEqual(result, expected)
        self.http_client.delete.assert_awaited_once_with(
            "http://mockserver.test/admin/mapping/schedule",
            json=rule,
        )
        response.json.assert_called_once_with()

        await self.assert_http_error(
            self.http_client.delete,
            lambda: self.client.delete_schedule_rule(rule),
        )

    async def test_reset_server_posts_without_body_and_reports_error(self):
        expected = {"status": "ok"}
        response = self.response(expected)
        self.http_client.post.return_value = response

        result = await self.client.reset_server()

        self.assertEqual(result, expected)
        self.http_client.post.assert_awaited_once_with(
            "http://mockserver.test/admin/mapping/reset"
        )
        response.json.assert_called_once_with()

        await self.assert_http_error(
            self.http_client.post,
            self.client.reset_server,
        )


if __name__ == "__main__":
    unittest.main()
