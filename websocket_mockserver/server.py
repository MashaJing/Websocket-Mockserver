import uvicorn.config
import logging.config
import asyncio

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

from websocket_mockserver.helpers import Helpers, CHANNELS_HEADER, DEFAULT_TIMEOUT
from websocket_mockserver.rules import OneshotRule, InboundRule, ScheduleRule

logging.config.dictConfig(uvicorn.config.LOGGING_CONFIG)
log = logging.getLogger("uvicorn.error")
log.setLevel(logging.INFO)

class RemoteMockServer:
    def __init__(self):
        self.app = FastAPI()
        self.oneshot_rules: List[OneshotRule] = []
        self.inbound_rules: List[InboundRule] = []
        self.schedule_rules: List[ScheduleRule] = []

        self._setup_routes()

    def _setup_routes(self):
        @self.app.get("/admin/rules")
        async def get_rules():
            return {
                "oneshot rules": [oneshot.dict() for oneshot in self.oneshot_rules],
                "inbound rules": [inbound.dict() for inbound in self.inbound_rules],
                "schedule rules": [schedule.dict() for schedule in self.schedule_rules]
            }

        @self.app.post("/admin/mapping/inbound")
        async def add_inbound_rules(rules: List[InboundRule]):
            before = len(self.inbound_rules)
            for rule in rules:
                self.inbound_rules = [
                    existing for existing in self.inbound_rules
                    if not Helpers.inbound_rules_compare(existing, rule)
                ]
                self.inbound_rules.append(rule)
            added = len(self.inbound_rules) - before
            return {"status": "ok", "inbound_rules_added": added}

        @self.app.post("/admin/mapping/oneshot")
        async def add_push_rules(rules: List[OneshotRule]):
            for rule in rules:
                self.oneshot_rules.append(rule)
            return {"status": "ok", "oneshot_rules_added": len(rules)}

        @self.app.delete("/admin/mapping/oneshot")
        async def delete_oneshot_rules(rules: List[OneshotRule]):
            before = len(self.oneshot_rules)
            for rule in rules:
                self.oneshot_rules = [
                    existing for existing in self.oneshot_rules
                    if not (
                        existing.message == rule.message
                        and existing.channels == rule.channels
                        and existing.timeout == rule.timeout
                    )
                ]
            removed = before - len(self.oneshot_rules)
            return {"status": "ok", "oneshot_rules_removed": removed}

        @self.app.post("/admin/mapping/schedule")
        async def add_push_rules(rules: List[ScheduleRule]):
            before = len(self.schedule_rules)
            for rule in rules:
                self.schedule_rules.append(rule)
            added = len(self.schedule_rules) - before
            return {"status": "ok", "schedule_rules_added": added}

        @self.app.delete("/admin/mapping/schedule")
        async def delete_schedule_rules(rules: List[ScheduleRule]):
            before = len(self.schedule_rules)
            for rule in rules:
                self.schedule_rules = [
                    existing for existing in self.schedule_rules
                    if not (existing.message == rule.message and existing.channels == rule.channels and existing.timeout == rule.timeout)
                ]
            removed = before - len(self.schedule_rules)
            return {"status": "ok", "schedule_rules_removed": removed}


        @self.app.post("/admin/mapping/reset")
        async def reset_rules():
            self.schedule_rules.clear()
            self.oneshot_rules.clear()
            self.inbound_rules.clear()
            return {"status": "ok"}

        @self.app.websocket("/ws/{ws_path:path}")
        async def ws_endpoint(websocket: WebSocket, ws_path: str):
            await websocket.accept()
            client = websocket.client
            log.info(f"WebSocket client connected from {client.host}:{client.port} with ws_path='{ws_path}'")

            oneshot_completed_rules = set()
            active_schedule_tasks = {}

            async def oneshot_monitor():
                while True:
                    for rule in self.oneshot_rules:
                        if not Helpers.channels_compare(websocket, rule):
                            continue

                        if not Helpers.path_compare(ws_path, rule):
                            continue

                        rule_id = id(rule)
                        if rule_id in oneshot_completed_rules:
                            continue

                        await Helpers.send_oneshot(websocket, rule)
                        oneshot_completed_rules.add(rule_id)

                        await asyncio.sleep(DEFAULT_TIMEOUT)
                    await asyncio.sleep(DEFAULT_TIMEOUT)

            async def schedule_monitor():
                while True:
                    # Запуск новых schedule-задач для вновь добавленных правил
                    for rule in self.schedule_rules:
                        if not Helpers.channels_compare(websocket, rule):
                            continue

                        if not Helpers.path_compare(ws_path, rule):
                            continue

                        rule_id = id(rule)
                        if rule_id not in active_schedule_tasks:
                            schedule_task = asyncio.create_task(Helpers.send_schedule(websocket, rule))
                            active_schedule_tasks[rule_id] = schedule_task

                    # Отмена задач для удалённых правил
                    for rule_id in list(active_schedule_tasks.keys()):
                        if not any(id(rule) == rule_id for rule in self.schedule_rules):
                            active_schedule_tasks[rule_id].cancel()
                            del active_schedule_tasks[rule_id]

                    await asyncio.sleep(DEFAULT_TIMEOUT)

            oneshot_monitor_task = asyncio.create_task(oneshot_monitor())
            schedule_monitor_task = asyncio.create_task(schedule_monitor())

            try:
                while True:
                    raw_msg = await websocket.receive_text()
                    await Helpers.send_inbound_matches(websocket, raw_msg, ws_path, self.inbound_rules)
            except WebSocketDisconnect:
                log.info("WebSocket client disconnected")
            except Exception as e:
                log.error(f"WebSocket error: {e}")
            finally:
                tasks = [oneshot_monitor_task, schedule_monitor_task, *(active_schedule_tasks.values())]
                for task in tasks:
                    task.cancel()
                await asyncio.gather(*tasks, return_exceptions=True)
                log.info("Finished handling WebSocket connection")
