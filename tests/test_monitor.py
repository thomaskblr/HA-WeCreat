"""Exercise the production reader against an HTTP server and the example trigger."""
import importlib.util
from pathlib import Path
from unittest import IsolatedAsyncioTestCase
from aiohttp import ClientSession, web
from aiohttp.test_utils import TestServer
import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("wecreat_api", ROOT / "custom_components/wecreat/api.py")
api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api)


class MonitorTests(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.payload = {"code": 0, "status": 2}
        self.http_status = 200

        async def status(request):
            self.assertEqual(await request.read(), b"")
            return web.json_response(self.payload, status=self.http_status)

        app = web.Application()
        app.router.add_post("/process/status", status)
        self.server = TestServer(app)
        await self.server.start_server()
        self.addAsyncCleanup(self.server.close)
        self.session = ClientSession()
        self.addAsyncCleanup(self.session.close)

    async def read(self):
        return await api.read_status(self.session, self.server.host, self.server.port)

    async def test_observed_sequence_and_reconnect(self):
        trigger = yaml.safe_load((ROOT / "examples/ready_notification.yaml").read_text())["triggers"][0]
        states = []
        for status in [4, 2, 3, 3, 4, 4, None, 4, 99]:
            self.http_status = 503 if status is None else 200
            self.payload["status"] = status
            if status is None:
                with self.assertRaises(api.StatusError):
                    await self.read()
                states.append("unavailable")
            else:
                raw = await self.read()
                self.assertEqual(raw, status)
                states.append(api.LABELS.get(raw, "unrecognized"))
        self.assertEqual(states[-1], "unrecognized")
        matches = [i for i in range(1, len(states))
                   if states[i-1] == trigger["from"] and states[i] == trigger["to"]]
        self.assertEqual(matches, [4])

    async def test_invalid_payloads(self):
        for payload in [[], {}, {"code": 1, "status": 4}, {"code": 0, "status": True}]:
            self.payload = payload
            with self.subTest(payload=payload), self.assertRaises(api.StatusError):
                await self.read()
