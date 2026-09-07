import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from fastapi import WebSocketDisconnect

from websocket_mockserver.rules import InboundRule, OneshotRule, ScheduleRule
from websocket_mockserver.server import RemoteMockServer


class RemoteMockServerTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.server = RemoteMockServer()

    def endpoint(self, path, method=None):
        for route in self.server.app.routes:
            if route.path != path:
                continue
            if method is None or method in getattr(route, "methods", set()):
                return route.endpoint
        self.fail(f"Route {method or 'WEBSOCKET'} {path} was not registered")


class AdminRoutesTests(RemoteMockServerTestCase):
    async def test_get_rules_returns_all_rule_types(self):
        oneshot = OneshotRule(message={"event": "ready"}, timeout=0.1)
        inbound = InboundRule(type="ping", response={"type": "pong"})
        schedule = ScheduleRule(message={"event": "tick"}, timeout=1)
        self.server.oneshot_rules.append(oneshot)
        self.server.inbound_rules.append(inbound)
        self.server.schedule_rules.append(schedule)

        result = await self.endpoint("/admin/rules", "GET")()

        self.assertEqual(
            result,
            {
                "oneshot rules": [oneshot.dict()],
                "inbound rules": [inbound.dict()],
                "schedule rules": [schedule.dict()],
            },
        )

    async def test_add_inbound_rules_replaces_matching_rule(self):
        existing = InboundRule(
            channels="orders",
            url_path="events",
            type="created",
            response={"version": 1},
        )
        replacement = InboundRule(
            channels="orders",
            url_path="events",
            type="created",
            response={"version": 2},
        )
        additional = InboundRule(
            channels="orders",
            url_path="events",
            type="updated",
            response={"version": 3},
        )
        self.server.inbound_rules.append(existing)

        result = await self.endpoint("/admin/mapping/inbound", "POST")(
            [replacement, additional]
        )

        self.assertEqual(result, {"status": "ok", "inbound_rules_added": 1})
        self.assertEqual(self.server.inbound_rules, [replacement, additional])

    async def test_add_and_delete_oneshot_rules(self):
        retained = OneshotRule(message={"id": 1}, channels="private", timeout=0)
        removed = OneshotRule(message={"id": 2}, channels="public", timeout=1)
        add = self.endpoint("/admin/mapping/oneshot", "POST")
        delete = self.endpoint("/admin/mapping/oneshot", "DELETE")

        add_result = await add([retained, removed])
        delete_result = await delete([removed])

        self.assertEqual(
            add_result, {"status": "ok", "oneshot_rules_added": 2}
        )
        self.assertEqual(
            delete_result, {"status": "ok", "oneshot_rules_removed": 1}
        )
        self.assertEqual(self.server.oneshot_rules, [retained])

    async def test_add_and_delete_schedule_rules(self):
        retained = ScheduleRule(message={"id": 1}, channels="private", timeout=1)
        removed = ScheduleRule(message={"id": 2}, channels="public", timeout=2)
        add = self.endpoint("/admin/mapping/schedule", "POST")
        delete = self.endpoint("/admin/mapping/schedule", "DELETE")

        add_result = await add([retained, removed])
        delete_result = await delete([removed])

        self.assertEqual(
            add_result, {"status": "ok", "schedule_rules_added": 2}
        )
        self.assertEqual(
            delete_result, {"status": "ok", "schedule_rules_removed": 1}
        )
        self.assertEqual(self.server.schedule_rules, [retained])

    async def test_delete_routes_report_zero_for_unknown_rules(self):
        unknown_oneshot = OneshotRule(message={"id": 1})
        unknown_schedule = ScheduleRule(message={"id": 2})

        oneshot_result = await self.endpoint(
            "/admin/mapping/oneshot", "DELETE"
        )([unknown_oneshot])
        schedule_result = await self.endpoint(
            "/admin/mapping/schedule", "DELETE"
        )([unknown_schedule])

        self.assertEqual(
            oneshot_result, {"status": "ok", "oneshot_rules_removed": 0}
        )
        self.assertEqual(
            schedule_result, {"status": "ok", "schedule_rules_removed": 0}
        )

    async def test_reset_clears_all_rules(self):
        self.server.oneshot_rules.append(OneshotRule(message={"id": 1}))
        self.server.inbound_rules.append(
            InboundRule(type="ping", response={"type": "pong"})
        )
        self.server.schedule_rules.append(ScheduleRule(message={"id": 2}))

        result = await self.endpoint("/admin/mapping/reset", "POST")()

        self.assertEqual(result, {"status": "ok"})
        self.assertEqual(self.server.oneshot_rules, [])
        self.assertEqual(self.server.inbound_rules, [])
        self.assertEqual(self.server.schedule_rules, [])


class FakeWebSocket:
    def __init__(self, messages):
        self.headers = {"X-Websocket-Channels": "public"}
        self.client = SimpleNamespace(host="127.0.0.1", port=9000)
        self.accept = AsyncMock()
        self._messages = iter(messages)

    async def receive_text(self):
        for _ in range(3):
            await asyncio.sleep(0)
        message = next(self._messages)
        if isinstance(message, Exception):
            raise message
        return message


class WebSocketRouteTests(RemoteMockServerTestCase):
    async def test_websocket_processes_matching_rules_and_inbound_messages(self):
        matching_oneshot = OneshotRule(
            message={"event": "ready"}, channels="public", url_path="events"
        )
        skipped_oneshot = OneshotRule(
            message={"event": "hidden"}, channels="private", url_path="events"
        )
        matching_schedule = ScheduleRule(
            message={"event": "tick"}, channels="public", url_path="events"
        )
        skipped_schedule = ScheduleRule(
            message={"event": "other"}, channels="public", url_path="other"
        )
        inbound = InboundRule(type="ping", response={"type": "pong"})
        self.server.oneshot_rules.extend([matching_oneshot, skipped_oneshot])
        self.server.schedule_rules.extend([matching_schedule, skipped_schedule])
        self.server.inbound_rules.append(inbound)
        websocket = FakeWebSocket(
            ['{"type": "ping"}', WebSocketDisconnect()]
        )

        with (
            patch(
                "websocket_mockserver.server.DEFAULT_TIMEOUT", 0
            ),
            patch(
                "websocket_mockserver.server.Helpers.send_oneshot",
                new_callable=AsyncMock,
            ) as send_oneshot,
            patch(
                "websocket_mockserver.server.Helpers.send_schedule",
                new_callable=AsyncMock,
            ) as send_schedule,
            patch(
                "websocket_mockserver.server.Helpers.send_inbound_matches",
                new_callable=AsyncMock,
            ) as send_inbound_matches,
        ):
            await self.endpoint("/ws/{ws_path:path}")(websocket, "events")

        websocket.accept.assert_awaited_once_with()
        send_oneshot.assert_awaited_once_with(websocket, matching_oneshot)
        send_schedule.assert_awaited_once_with(websocket, matching_schedule)
        send_inbound_matches.assert_awaited_once_with(
            websocket,
            '{"type": "ping"}',
            "events",
            self.server.inbound_rules,
        )

    async def test_websocket_cancels_schedule_task_when_rule_is_removed(self):
        rule = ScheduleRule(
            message={"event": "tick"}, channels="public", url_path="events"
        )
        self.server.schedule_rules.append(rule)
        schedule_started = asyncio.Event()
        schedule_cancelled = asyncio.Event()
        cancelled_before_disconnect = False

        async def send_schedule(websocket, scheduled_rule):
            schedule_started.set()
            try:
                await asyncio.Event().wait()
            except asyncio.CancelledError:
                schedule_cancelled.set()
                raise

        async def receive_text():
            nonlocal cancelled_before_disconnect
            await schedule_started.wait()
            self.server.schedule_rules.remove(rule)
            await asyncio.wait_for(schedule_cancelled.wait(), timeout=1)
            cancelled_before_disconnect = True
            raise WebSocketDisconnect()

        websocket = SimpleNamespace(
            headers={"X-Websocket-Channels": "public"},
            client=SimpleNamespace(host="127.0.0.1", port=9000),
            accept=AsyncMock(),
            receive_text=AsyncMock(side_effect=receive_text),
        )

        with (
            patch("websocket_mockserver.server.DEFAULT_TIMEOUT", 0),
            patch(
                "websocket_mockserver.server.Helpers.send_schedule",
                new_callable=AsyncMock,
                side_effect=send_schedule,
            ) as mocked_send_schedule,
        ):
            await self.endpoint("/ws/{ws_path:path}")(websocket, "events")

        self.assertTrue(cancelled_before_disconnect)
        mocked_send_schedule.assert_awaited_once_with(websocket, rule)

    async def test_websocket_logs_unexpected_receive_error_and_finishes(self):
        websocket = FakeWebSocket([RuntimeError("connection failed")])

        with (
            patch("websocket_mockserver.server.log.error") as log_error,
            patch("websocket_mockserver.server.log.info") as log_info,
        ):
            await self.endpoint("/ws/{ws_path:path}")(websocket, "events")

        log_error.assert_called_once_with(
            "WebSocket error: connection failed"
        )
        log_info.assert_any_call("Finished handling WebSocket connection")


if __name__ == "__main__":
    unittest.main()
