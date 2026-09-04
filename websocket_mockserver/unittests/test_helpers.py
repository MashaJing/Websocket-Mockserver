import asyncio
import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from websocket_mockserver.helpers import DEFAULT_TIMEOUT, Helpers
from websocket_mockserver.rules import InboundRule, OneshotRule, ScheduleRule


class MatchingHelpersTests(unittest.TestCase):
    def test_parse_channels_normalizes_and_deduplicates_values(self):
        cases = [
            (None, set()),
            ("", set()),
            (" public, private, public, , ", {"public", "private"}),
        ]

        for raw_channels, expected in cases:
            with self.subTest(raw_channels=raw_channels):
                self.assertEqual(Helpers.parse_channels(raw_channels), expected)

    def test_dicts_compare_accepts_expected_subset(self):
        actual = {"id": 1, "nested": {"enabled": True}, "extra": "value"}

        self.assertTrue(
            Helpers.dicts_compare(
                actual, {"id": 1, "nested": {"enabled": True}}
            )
        )
        self.assertFalse(Helpers.dicts_compare(actual, {"missing": "value"}))
        self.assertFalse(Helpers.dicts_compare(actual, {"id": 2}))

    def test_channels_compare_applies_exact_and_pattern_constraints(self):
        websocket = SimpleNamespace(
            headers={"X-Websocket-Channels": "private, public-news"}
        )

        self.assertTrue(
            Helpers.channels_compare(
                websocket,
                OneshotRule(
                    channels="public-news, other",
                    channels_pattern=r"public-.*",
                ),
            )
        )
        self.assertFalse(
            Helpers.channels_compare(
                websocket, OneshotRule(channels="unknown")
            )
        )
        self.assertFalse(
            Helpers.channels_compare(
                websocket, OneshotRule(channels_pattern=r"admin-.*")
            )
        )

    def test_channels_compare_allows_rule_without_constraints(self):
        websocket = SimpleNamespace(headers={})

        self.assertTrue(
            Helpers.channels_compare(websocket, OneshotRule())
        )

    def test_path_compare_applies_exact_and_pattern_constraints(self):
        matching_rule = OneshotRule(
            url_path="events/42", url_pattern=r"events/\d+"
        )

        self.assertTrue(Helpers.path_compare("events/42", matching_rule))
        self.assertFalse(Helpers.path_compare("events/43", matching_rule))
        self.assertFalse(
            Helpers.path_compare(
                "events/42", OneshotRule(url_pattern=r"orders/\d+")
            )
        )
        self.assertTrue(Helpers.path_compare("any/path", OneshotRule()))

    def test_type_compare_applies_exact_and_pattern_constraints(self):
        matching_rule = InboundRule(
            type="order.created",
            type_pattern=r"order\..+",
            response={},
        )

        self.assertTrue(Helpers.type_compare("order.created", matching_rule))
        self.assertFalse(Helpers.type_compare("order.updated", matching_rule))
        self.assertFalse(
            Helpers.type_compare(
                "order.created",
                InboundRule(type_pattern=r"user\..+", response={}),
            )
        )
        self.assertTrue(
            Helpers.type_compare("any.type", InboundRule(response={}))
        )

    def test_inbound_rules_compare_matches_identity_fields(self):
        existing = InboundRule(
            channels="public",
            url_path="events",
            type="created",
            response={"version": 1},
        )
        replacement = InboundRule(
            channels="public",
            url_path="events",
            type="created",
            response={"version": 2},
        )
        different_type = replacement.copy(update={"type": "updated"})

        self.assertTrue(
            Helpers.inbound_rules_compare(existing, replacement)
        )
        self.assertFalse(
            Helpers.inbound_rules_compare(existing, different_type)
        )

    def test_inbound_rules_compare_supports_pattern_identity(self):
        existing = InboundRule(
            channels_pattern=r"public-.*",
            url_pattern=r"events/\d+",
            type_pattern=r"order\..+",
            response={"version": 1},
        )
        replacement = existing.copy(update={"response": {"version": 2}})

        self.assertTrue(
            Helpers.inbound_rules_compare(existing, replacement)
        )


class AsyncHelpersTests(unittest.IsolatedAsyncioTestCase):
    async def test_send_message_serializes_dict_without_escaping_unicode(self):
        websocket = SimpleNamespace(send_text=AsyncMock())

        await Helpers.send_message(websocket, {"message": "Привет"})

        websocket.send_text.assert_awaited_once_with(
            '{"message": "Привет"}'
        )

    async def test_send_message_converts_non_dict_value_to_string(self):
        websocket = SimpleNamespace(send_text=AsyncMock())

        await Helpers.send_message(websocket, 42)

        websocket.send_text.assert_awaited_once_with("42")

    async def test_send_oneshot_waits_before_sending(self):
        websocket = SimpleNamespace()
        rule = OneshotRule(message={"event": "ready"}, timeout=0.25)

        with (
            patch(
                "websocket_mockserver.helpers.asyncio.sleep",
                new_callable=AsyncMock,
            ) as sleep,
            patch.object(
                Helpers, "send_message", new_callable=AsyncMock
            ) as send_message,
        ):
            await Helpers.send_oneshot(websocket, rule)

        sleep.assert_awaited_once_with(0.25)
        send_message.assert_awaited_once_with(websocket, rule.message)

    async def test_send_oneshot_logs_send_error(self):
        websocket = SimpleNamespace()
        rule = OneshotRule(message={"event": "ready"})

        with (
            patch.object(
                Helpers,
                "send_message",
                new_callable=AsyncMock,
                side_effect=RuntimeError("send failed"),
            ),
            patch("websocket_mockserver.helpers.log.warning") as warning,
        ):
            await Helpers.send_oneshot(websocket, rule)

        warning.assert_called_once_with(
            "Cannot send message on oneshot: send failed"
        )

    async def test_send_schedule_uses_default_timeout(self):
        websocket = SimpleNamespace()
        rule = ScheduleRule(message={"event": "tick"})

        with (
            patch.object(
                Helpers, "send_message", new_callable=AsyncMock
            ) as send_message,
            patch(
                "websocket_mockserver.helpers.asyncio.sleep",
                new_callable=AsyncMock,
                side_effect=asyncio.CancelledError,
            ) as sleep,
        ):
            with self.assertRaises(asyncio.CancelledError):
                await Helpers.send_schedule(websocket, rule)

        send_message.assert_awaited_once_with(websocket, rule.message)
        sleep.assert_awaited_once_with(DEFAULT_TIMEOUT)

    async def test_send_schedule_logs_error_and_continues(self):
        websocket = SimpleNamespace()
        rule = ScheduleRule(message={"event": "tick"}, timeout=2)

        with (
            patch.object(
                Helpers,
                "send_message",
                new_callable=AsyncMock,
                side_effect=RuntimeError("send failed"),
            ),
            patch(
                "websocket_mockserver.helpers.asyncio.sleep",
                new_callable=AsyncMock,
                side_effect=asyncio.CancelledError,
            ) as sleep,
            patch("websocket_mockserver.helpers.log.warning") as warning,
        ):
            with self.assertRaises(asyncio.CancelledError):
                await Helpers.send_schedule(websocket, rule)

        warning.assert_called_once_with(
            "Cannot send message on schedule: send failed"
        )
        sleep.assert_awaited_once_with(2)

    async def test_send_inbound_matches_uses_last_matching_rule(self):
        websocket = SimpleNamespace()
        rules = [
            InboundRule(
                url_path="other",
                type="order.created",
                response={"version": 0},
            ),
            InboundRule(
                url_path="events",
                type="order.deleted",
                response={"version": 0},
            ),
            InboundRule(
                url_path="events",
                type="order.created",
                payload={"id": 2},
                response={"version": 0},
            ),
            InboundRule(
                url_path="events",
                type="order.created",
                payload={"id": 1},
                response={"version": 1},
            ),
            InboundRule(
                url_pattern=r"event.*",
                type_pattern=r"order\..+",
                payload={"id": 1},
                response={"version": 2},
            ),
        ]

        with patch.object(
            Helpers, "send_message", new_callable=AsyncMock
        ) as send_message:
            await Helpers.send_inbound_matches(
                websocket,
                '{"type":"order.created","payload":{"id":1,"extra":true}}',
                "events",
                rules,
            )

        send_message.assert_awaited_once_with(
            websocket, {"version": 2}
        )

    async def test_send_inbound_matches_sends_default_for_invalid_json(self):
        websocket = SimpleNamespace()
        rules = [InboundRule(url_path="events", response={"matched": True})]

        with (
            patch.object(
                Helpers, "send_message", new_callable=AsyncMock
            ) as send_message,
            patch("websocket_mockserver.helpers.log.warning") as warning,
        ):
            await Helpers.send_inbound_matches(
                websocket, "not-json", "events", rules
            )

        warning.assert_called_once_with("Error while parse raw message")
        send_message.assert_awaited_once_with(websocket, "{}")

    async def test_send_inbound_matches_logs_send_error(self):
        websocket = SimpleNamespace()

        with (
            patch.object(
                Helpers,
                "send_message",
                new_callable=AsyncMock,
                side_effect=RuntimeError("send failed"),
            ),
            patch("websocket_mockserver.helpers.log.warning") as warning,
        ):
            await Helpers.send_inbound_matches(
                websocket, '{"type":"unknown"}', "events", []
            )

        warning.assert_called_once_with(
            "Cannot send message on inbound: send failed"
        )


if __name__ == "__main__":
    unittest.main()
