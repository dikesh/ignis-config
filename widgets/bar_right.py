import asyncio
import math

from ignis.services.audio import AudioService
from ignis.services.bluetooth import BluetoothService
from ignis.services.network import NetworkService
from ignis.services.system_tray import SystemTrayItem, SystemTrayService
from ignis.services.upower import UPowerService
from ignis.utils import Utils
from ignis.variable import Variable
from ignis.widgets import Widget

# Services
audio = AudioService.get_default()
bt_service = BluetoothService.get_default()
system_tray = SystemTrayService.get_default()
upower = UPowerService.get_default()
network = NetworkService.get_default()


def bluetooth_widget():
    """Bluetooth Widget"""
    # Variable to watch
    total_devices = Variable(0)

    def _update_total_devices():
        """Update variable"""
        total_devices.value = len(bt_service.connected_devices)  # type: ignore

    # Signals to notify
    bt_service.connect("device_added", lambda _, _devices: _update_total_devices())  # type: ignore
    bt_service.connect(
        "notify::connected-devices", lambda _, _devices: _update_total_devices()
    )

    # Command to run
    cmd = "./scripts/bluetooth.sh"

    return Widget.Button(
        css_classes=["bar-section", "bluetooth"],
        child=Widget.Box(
            spacing=8,
            child=total_devices.bind(
                "value",
                transform=lambda total: [
                    Widget.Box(
                        visible=total > 0,
                        child=[
                            Widget.Box(
                                spacing=8,
                                child=[
                                    Widget.Icon(image=f"{device.icon_name}-symbolic"),
                                    Widget.Label(label=device.alias),
                                ],
                            )
                            for device in bt_service.connected_devices
                        ],
                    ),
                    Widget.Icon(
                        image=bt_service.bind(
                            "powered",
                            transform=lambda is_on: "bluetooth-active-symbolic"
                            if is_on
                            else "bluetooth-disabled-symbolic",
                        )
                    ),
                ],
            ),
        ),
        on_click=lambda _: asyncio.create_task(Utils.exec_sh_async(cmd)),  # type: ignore
    )


def volume_widget():
    """Volume Widget"""
    return Widget.EventBox(
        css_classes=["bar-section", "volume"],
        child=[
            Widget.Box(
                spacing=8,
                child=[
                    Widget.Icon(image=audio.speaker.bind("icon_name")),  # type: ignore
                    Widget.Label(
                        label=audio.speaker.bind("volume", lambda value: f"{value}%")  # type: ignore
                    ),
                ],
            )
        ],
        on_click=lambda _: asyncio.create_task(
            Utils.exec_sh_async("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle")  # type: ignore
        ),
        on_scroll_up=lambda _: asyncio.create_task(
            Utils.exec_sh_async("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-")  # type: ignore
        ),
        on_scroll_down=lambda _: asyncio.create_task(
            Utils.exec_sh_async("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%+")  # type: ignore
        ),
    )


def wifi_widget():
    """Wifi Widget"""
    return Widget.Box(
        child=network.bind(
            "wifi",
            transform=lambda wifi: [
                Widget.Box(
                    css_classes=["bar-section", "battery"],
                    spacing=8,
                    child=[
                        Widget.Icon(image=wifi.icon_name),
                        Widget.Label(label=device.ap.ssid),
                    ],
                )
                for device in wifi.devices
            ],
        )
    )


def battery_level():
    """Battery Level Widget"""
    return Widget.Box(
        spacing=8,
        child=upower.bind(
            "batteries",
            transform=lambda batteries: [
                Widget.Box(
                    css_classes=["bar-section", "battery"],
                    spacing=4,
                    child=[
                        Widget.Icon(image=battery.bind("icon_name")),
                        Widget.Label(
                            label=battery.bind(
                                "percent",
                                transform=lambda percent: f"{math.floor(percent)}%",
                            )
                        ),
                    ],
                )
                for battery in batteries
            ],
        ),
    )


def tray_item(item: SystemTrayItem) -> Widget.Button:
    """Tray Item Widget"""
    # Menu
    menu = item.menu.copy() if item.menu else None

    return Widget.Button(
        child=Widget.Box(
            child=[Widget.Icon(image=item.bind("icon"), pixel_size=16), menu]
        ),
        setup=lambda self: item.connect("removed", lambda _: self.unparent()),
        tooltip_text=item.bind("tooltip"),
        on_click=lambda _: asyncio.create_task(item.activate_async()),
        on_right_click=lambda _: menu.popup() if menu else None,
        css_classes=["traymenu"],
    )


def tray():
    """System Tray Widget"""
    return Widget.Box(
        css_classes=["bar-section", "systray"],
        spacing=8,
        setup=lambda self: system_tray.connect(
            "added", lambda _, item: self.append(tray_item(item))
        ),
    )


def power_menu():
    """Power Menu Widget"""
    cmd = "~/.config/rofi/powermenu/type-5/powermenu.sh"
    return Widget.Button(
        css_classes=["bar-section", "power"],
        child=Widget.Icon(image="system-shutdown-symbolic"),
        on_click=lambda _: asyncio.create_task(Utils.exec_sh_async(cmd)),  # type: ignore
    )


def bar_right():
    """Bar Right"""
    return Widget.Box(
        halign="end",
        spacing=8,
        child=[
            bluetooth_widget(),
            volume_widget(),
            wifi_widget(),
            battery_level(),
            tray(),
            power_menu(),
        ],
    )
