import asyncio

from ignis.utils import Utils
from ignis.widgets import Widget

from widgets.niri_workspaces import niri_workspaces
from widgets.resources import system_resources
from widgets.screenrec import screen_rec


def applications():
    """Applications Widget"""
    cmd = "~/.config/rofi/launchers/type-3/launcher.sh"
    return Widget.Button(
        css_classes=["bar-section", "apps"],
        child=Widget.Label(label="󰀻"),
        on_click=lambda _: asyncio.create_task(Utils.exec_sh_async(cmd)),  # type: ignore
    )


def bar_left(monitor_id: int = 0):
    """Bar Left"""
    return Widget.Box(
        spacing=8,
        child=[
            system_resources(),
            applications(),
            screen_rec(),
            niri_workspaces(monitor_id),
        ],
    )
