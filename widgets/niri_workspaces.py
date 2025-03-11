import asyncio
from typing import Any

from ignis.services.niri import NiriService
from ignis.utils import Utils
from ignis.widgets import Widget

# Niri service
niri = NiriService.get_default()


def get_icon_widget(image: str):
    """Get Icon Widget"""
    if image == "kitty":
        image = "kitty-custom"

    return Widget.Icon(image=image.lower())


def focus_workspace(ws_id: int):
    """Focus Workspace"""
    niri.switch_to_workspace(ws_id)


def cycle_windows(ws_id: int, is_up: bool):
    """Cycle Windows"""
    focus_workspace(ws_id)
    asyncio.create_task(
        Utils.exec_sh_async(  # type: ignore
            f"niri msg action focus-column-{'right' if is_up else 'left'}"
        )
    )


def workspace_windows(ws_id: int, is_active: bool, ws_windows: list[dict[str, Any]]):
    """Workspace Windows"""
    windows = [
        get_icon_widget(window["app_id"])
        for window in ws_windows
        if window["workspace_id"] == ws_id
    ]

    if len(windows) == 0 and is_active:
        windows.append(get_icon_widget("archlinux-logo"))

    return windows


def workspace(ws_info: dict[str, Any]):
    """Workspace Widget"""
    # Set classes
    classes = ["hl-workspace"]
    if ws_info["is_active"] and ws_info["is_focused"]:
        classes.append("hl-workspace-active")

    # Button widget
    return Widget.EventBox(
        css_classes=classes,
        on_click=lambda _: focus_workspace(ws_info["idx"]),
        on_scroll_up=lambda _: cycle_windows(ws_info["idx"], True),
        on_scroll_down=lambda _: cycle_windows(ws_info["idx"], False),
        child=[
            Widget.Box(
                spacing=8,
                child=niri.bind(
                    "windows",
                    transform=lambda windows: workspace_windows(
                        ws_info["id"], ws_info["is_active"], windows
                    ),
                ),
            )
        ],
    )


def niri_workspaces(monitor_id: int = 0):
    # Get connector name
    monitor: str = Utils.get_monitor(monitor_id).get_connector()  # type: ignore
    return Widget.Box(
        css_classes=["bar-section"],
        spacing=4,
        child=niri.bind(
            "workspaces",
            transform=lambda ws_li: [
                workspace(ws_info) for ws_info in ws_li if ws_info["output"] == monitor
            ],
        ),
    )
