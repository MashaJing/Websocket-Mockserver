import json
import asyncio
import logging.config
import uvicorn.config
import re

from typing import Any, Optional, Dict, Set, List
from fastapi import WebSocket

from websocket_mockserver.rules import ScheduleRule, OneshotRule, InboundRule

logging.config.dictConfig(uvicorn.config.LOGGING_CONFIG)
log = logging.getLogger("uvicorn.error")
log.setLevel(logging.INFO)

CHANNELS_HEADER = "X-Websocket-Channels"
DEFAULT_TIMEOUT = 0.5

class Helpers:

    @staticmethod
    def parse_channels(channels_str: Optional[str]) -> Set[str]:
        if not channels_str:
            return set()
        return {ch.strip() for ch in channels_str.split(",") if ch.strip()}

    @staticmethod
    def dicts_compare(actual: Dict, expected: Dict) -> bool:
        for key, value in expected.items():
            if key not in actual or actual[key] != value:
                return False
        return True

    @staticmethod
    def channels_compare(websocket: WebSocket, rule) -> bool:
        connection_channels = Helpers.parse_channels(websocket.headers.get(CHANNELS_HEADER))
        if rule.channels is not None:
            rule_channels = Helpers.parse_channels(rule.channels)
            if not (connection_channels & rule_channels):
                return False

        if rule.channels_pattern is not None:
            if not any(re.match(rule.channels_pattern, ch) for ch in connection_channels):
                return False

        return True

    @staticmethod
    def path_compare(ws_path: str, rule) -> bool:
        if rule.url_path is not None:
            if ws_path != rule.url_path:
                return False

        if rule.url_pattern is not None:
            if re.match(rule.url_pattern, ws_path) is None:
                return False

        return True

    @staticmethod
    def type_compare(type: str, rule) -> bool:
        if rule.type is not None:
            if type != rule.type:
                return False

        if rule.type_pattern is not None:
            if re.match(rule.type_pattern, type) is None:
                return False

        return True

    @staticmethod
    def inbound_rules_compare(existing, rule):
        url_matches = (
            (existing.url_path is not None and rule.url_path is not None and existing.url_path == rule.url_path) or
            (existing.url_pattern is not None and rule.url_pattern is not None and existing.url_pattern == rule.url_pattern)
        )

        type_matches = (
            (existing.type is not None and rule.type is not None and existing.type == rule.type) or
            (existing.type_pattern is not None and rule.type_pattern is not None and existing.type_pattern == rule.type_pattern)
        )

        channels_matches = (
            (existing.channels is not None and rule.channels is not None and existing.channels == rule.channels) or
            (existing.channels_pattern is not None and rule.channels_pattern is not None and existing.channels_pattern == rule.channels_pattern)
        )
        return url_matches and type_matches and channels_matches

    @staticmethod
    async def send_message(websocket: WebSocket, data: Any):
        if isinstance(data, dict):
            await asyncio.wait_for(websocket.send_text(json.dumps(data, ensure_ascii=False)), timeout=DEFAULT_TIMEOUT)
        else:
            await asyncio.wait_for(websocket.send_text(str(data)), timeout=DEFAULT_TIMEOUT)

    @staticmethod
    async def send_oneshot(websocket: WebSocket, rule: OneshotRule):
        try:
            if rule.timeout:
                try:
                    await asyncio.sleep(float(rule.timeout))
                except Exception as e:
                    log.warning(f"Error on oneshot timeout: {e}")
            await Helpers.send_message(websocket, rule.message)
        except Exception as e:
            log.warning(f"Cannot send message on oneshot: {e}")

    @staticmethod
    async def send_schedule(websocket: WebSocket, rule: ScheduleRule):
        timeout = rule.timeout if rule.timeout is not None else DEFAULT_TIMEOUT
        while True:
            try:
                await Helpers.send_message(websocket, rule.message)
            except Exception as e:
                log.warning(f"Cannot send message on schedule: {e}")
            await asyncio.sleep(timeout)

    @staticmethod
    async def send_inbound_matches(websocket: WebSocket, message: str, ws_path: str, rules: List[InboundRule]):
        response = "{}"
        for rule in rules:
            if not Helpers.path_compare(ws_path, rule):
                continue

            try:
                parsed_msg = json.loads(message)
            except json.JSONDecodeError:
                log.warning("Error while parse raw message")
                continue

            msg_type = str(parsed_msg.get("type", ""))
            if not Helpers.type_compare(msg_type, rule):
                continue

            if rule.payload is not None:
                incoming_payload = parsed_msg.get("payload", {})
                if not Helpers.dicts_compare(incoming_payload, rule.payload):
                    log.warning(f"payload not matched")
                    continue

            response = rule.response
        try:
            await Helpers.send_message(websocket, response)
        except Exception as e:
            log.warning(f"Cannot send message on inbound: {e}")
