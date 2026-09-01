import base64
import json
import unittest
from unittest import mock

from samsungctl.remote_websocket import RemoteWebsocket


class RemoteWebsocketInputTest(unittest.TestCase):
    def setUp(self):
        self.remote = RemoteWebsocket.__new__(RemoteWebsocket)
        self.remote.connection = mock.Mock()
        self.remote._ensure_connected = mock.Mock()

    def payloads(self):
        return [
            json.loads(call.args[0])
            for call in self.remote.connection.send.call_args_list
        ]

    def test_moves_cursor(self):
        self.remote.move_cursor(25, -10, 50)

        self.assertEqual(self.payloads(), [{
            "method": "ms.remote.control",
            "params": {
                "Cmd": "Move",
                "Position": {"x": 25, "y": -10, "Time": "50"},
                "TypeOfRemote": "ProcessMouseDevice"
            }
        }])

    def test_clicks_cursor(self):
        self.remote.click_cursor("right")

        self.assertEqual(
            self.payloads()[0]["params"],
            {"Cmd": "RightClick", "TypeOfRemote": "ProcessMouseDevice"}
        )

    def test_rejects_unknown_cursor_button(self):
        with self.assertRaises(ValueError):
            self.remote.click_cursor("middle")

    @mock.patch("samsungctl.remote_websocket.time.sleep")
    def test_sends_base64_text(self, sleep):
        self.remote.send_text("zażółć")
        self.remote.end_text()

        payloads = self.payloads()
        self.assertEqual(payloads[0], {
            "method": "ms.channel.emit",
            "params": {
                "event": "custom.remote.textReceived",
                "to": "broadcast"
            }
        })
        self.assertEqual(payloads[1], {
            "method": "ms.remote.control",
            "params": {
                "Cmd": base64.b64encode(
                    "zażółć".encode("utf-8")
                ).decode("utf-8"),
                "DataOfCmd": "base64",
                "TypeOfRemote": "SendInputString"
            }
        })
        self.assertEqual(payloads[2]["params"], {
            "TypeOfRemote": "SendInputEnd"
        })
        self.assertEqual(sleep.call_count, 2)
