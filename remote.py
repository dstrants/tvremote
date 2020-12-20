from pathlib import Path
from ipaddress import IPv4Address
from typing import Optional
import time

import yaml
from pydantic import BaseModel
from pywebostv.connection import WebOSClient
from pywebostv.controls import ApplicationControl, MediaControl, SystemControl
from pywebostv.controls import TvControl as Tv
from tinydb import TinyDB, Query


class TvControl(Tv):
    """This class monkeypatches `TvControl` to add missing endpoints."""
    COMMANDS = {
        "channel_down": {"uri": "ssap://tv/channelDown"},
        "channel_up": {"uri": "ssap://tv/channelUp"},
        'channel_list': {'uri': 'ssap://tv/getChannelList'},
        'get_current_channel': {'uri': 'ssap://tv/getCurrentChannel'}
    }


class RemoteConfig(BaseModel):
    ip: IPv4Address
    token: str


class Remote():
    Channel = Query()

    def __init__(self, ip: Optional[str] = None):
        self.config_file: Path = Path().home() / ".tvremote" / "remote.yaml"
        self.config = RemoteConfig(**self._configure(ip))
        self.client = WebOSClient(ip or str(self.config.ip))
        self.channels: TinyDB = TinyDB(Path().home() / ".tvremote" / "channels.json")
        self.apps: TinyDB = TinyDB(Path().home() / ".tvremote" / "apps.json")

    def _connect(self, force_registration: bool = False):
        self.client.connect()
        if force_registration:
            store = {}
        else:
            store = {'client_key': self.config.token}
        for status in self.client.register(store):
            if status == WebOSClient.PROMPTED:
                print("Please accept the connect on the TV!")
            elif status == WebOSClient.REGISTERED:
                print("Registration successful!")
        return store

    def _build_config(self, ip: str) -> None:
        (Path().home() / ".tvremote").mkdir(exist_ok=True)
        store = self._connect(force_registration=True)
        config = {
            "ip": ip,
            "token": store['client_key']
        }
        with open(str(self.config_file), "w") as conf_file:
            yaml.dump(config, conf_file, default_flow_style=False)
        print("Conf file created")

    def _configure(self, ip: Optional[str]) -> dict:
        if ip:
            self._build_config(ip)
        if not self.config_file.exists():
            raise ValueError("Ip is needed to build configuration")
        with open(str(self.config_file)) as config:
            conf_dict = yaml.load(config)
        return conf_dict

    def mute(self, mute: bool = True):
        self._connect()
        media = MediaControl(self.client)
        return media.mute(mute)

    def get_volume(self):
        self._connect()
        media = MediaControl(self.client)
        return media.get_volume()

    def volume_up(self):
        self._connect()
        media = MediaControl(self.client)
        return media.volume_up()

    def volume_down(self):
        self._connect()
        media = MediaControl(self.client)
        return media.volume_down()

    def set_volume(self, vol: int):
        self._connect()
        media = MediaControl(self.client)
        return media.set_volume(vol)

    def turn_off(self):
        self._connect()
        system = SystemControl(self.client)
        system.notify("System will turn off now!")
        time.sleep(5)
        return system.power_off()

    def get_channels(self, force_sync: bool = False):
        if force_sync:
            self.channels.truncate()
            self._connect()
            control = TvControl(self.client)
            channels = control.channel_list()
            for ch in channels['channelList']:
                self.channels.insert(ch)
        return self.channels.all()

    def channel_down(self):
        self._connect()
        control = TvControl(self.client)
        return control.channel_down()

    def channel_up(self):
        self._connect()
        control = TvControl(self.client)
        return control.channel_up()

    def get_current_channel(self):
        self._connect()
        control = TvControl(self.client)
        return control.get_current_channel()

    def get_apps(self, force_sync: bool = False):
        if force_sync:
            self.apps.truncate()
            self._connect()
            app_menu = ApplicationControl(self.client)
            apps = app_menu.list_apps()
            for app in apps:
                self.apps.insert(app.data)
        return self.apps.all()
