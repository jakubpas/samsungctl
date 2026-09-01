import base64
import json
import logging
import websocket
import time
import os
import ssl

from . import exceptions

URL_FORMAT = "ws://{}:{}/api/v2/channels/samsung.remote.control?name={}"
SSL_URL_FORMAT = "wss://{}:{}/api/v2/channels/samsung.remote.control?name={}"


class RemoteWebsocket:
    """Object for remote control connection."""

    def __init__(self, config):
        self.token_file = os.path.dirname(os.path.realpath(__file__)) + "/token.txt"
        self._config = config

        if not config["port"]:
            config["port"] = 8001

        if config["timeout"] == 0:
            config["timeout"] = None

        self._connect()

    def _connect(self):
        config = self._config
        if config["port"] == 8001:
            url = URL_FORMAT.format(config["host"], config["port"],
                                    self._serialize_string(config["name"]))
            self.connection = websocket.create_connection(url, config["timeout"])
        elif config["port"] == 8002:
            url = SSL_URL_FORMAT.format(config["host"], config["port"],
                                        self._serialize_string(config["name"]))
            if os.path.isfile(self.token_file):
                with open(self.token_file, "r") as token_file:
                    url += "&token=" + token_file.readline()
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            self.connection = websocket.create_connection(
                url, config["timeout"],
                sslopt={"context": ssl_context}
            )

        self._read_response()

    def __enter__(self):
        return self

    def __exit__(self, kind, value, traceback):
        self.close()

    def close(self):
        """Close the connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
            logging.debug("Connection closed.")

    def _ensure_connected(self):
        """Reconnect if the connection has been dropped."""
        try:
            self.connection.ping()
        except Exception:
            logging.debug("Connection lost, reconnecting.")
            self._connect()

    def _send(self, method, params, delay=0):
        if not self.connection:
            self._connect()

        self._ensure_connected()
        payload = json.dumps({
            "method": method,
            "params": params
        })
        self.connection.send(payload)
        if delay:
            time.sleep(delay)

    def control(self, key):
        """Send a remote key."""
        logging.info("Sending control command: %s", key)
        self._send("ms.remote.control", {
            "Cmd": "Click",
            "DataOfCmd": key,
            "Option": "false",
            "TypeOfRemote": "SendRemoteKey"
        }, self._key_interval)

    def move_cursor(self, x, y, duration=0):
        """Move the TV cursor by relative x and y offsets."""
        self._send("ms.remote.control", {
            "Cmd": "Move",
            "Position": {
                "x": x,
                "y": y,
                "Time": str(duration)
            },
            "TypeOfRemote": "ProcessMouseDevice"
        })

    def click_cursor(self, button="left"):
        """Click a TV cursor button."""
        buttons = {
            "left": "LeftClick",
            "right": "RightClick"
        }
        try:
            command = buttons[button.lower()]
        except (AttributeError, KeyError):
            raise ValueError("button must be 'left' or 'right'")

        self._send("ms.remote.control", {
            "Cmd": command,
            "TypeOfRemote": "ProcessMouseDevice"
        })

    def send_text(self, text):
        """Send UTF-8 text to the active TV input field."""
        if not text:
            return

        self._send("ms.channel.emit", {
            "event": "custom.remote.textReceived",
            "to": "broadcast"
        }, self._key_interval)
        self._send("ms.remote.control", {
            "Cmd": self._serialize_string(text),
            "DataOfCmd": "base64",
            "TypeOfRemote": "SendInputString"
        }, self._key_interval)

    def end_text(self):
        """Finish the current TV text input session."""
        self._send("ms.remote.control", {
            "TypeOfRemote": "SendInputEnd"
        })

    _key_interval = 0.2

    def _read_response(self):
        response = self.connection.recv()
        response = json.loads(response)

        if 'data' in response and 'token' in response["data"]:
            with open(self.token_file, "w") as token_file:
                token_file.write(response['data']["token"])

        if response["event"] != "ms.channel.connect":
            self.close()
            raise exceptions.UnhandledResponse(response)

        logging.debug("Access granted.")

    @staticmethod
    def _serialize_string(string):
        if isinstance(string, str):
            string = str.encode(string)

        return base64.b64encode(string).decode("utf-8")

    def get_installed_apps(self):
        """Send a control command."""
        if not self.connection:
            raise exceptions.ConnectionClosed()

        payload = json.dumps({
            "method": "ms.channel.emit",
            "params": {
                "data": "",
                "event": "ed.installedApp.get",
                # "event": "ed.edenApp.get",
                "to": "host"
            }
        })

        logging.info("Asking for installed apps.")
        self.connection.send(payload)
        data = json.loads(self.connection.recv())
        installed_apps = []
        for app in data['data']['data']:
            installed_apps.append([app['name'], app['appId']])
        return installed_apps
