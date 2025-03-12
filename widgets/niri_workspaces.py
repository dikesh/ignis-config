import asyncio
from typing import Any

from ignis.services.niri import NiriService
from ignis.utils import Utils
from ignis.widgets import Widget

# Type Alias
DictStrAny = dict[str, Any]
WS_EMPTY_ICON = "archlinux-logo"

# Niri service
niri = NiriService.get_default()


def _focus_workspace(ws_num: int):
    """Focus Workspace"""
    niri.switch_to_workspace(ws_num)


def _cycle_windows(ws_num: int, is_up: bool):
    """Cycle Windows"""
    _focus_workspace(ws_num)
    asyncio.create_task(
        Utils.exec_sh_async(  # type: ignore
            f"niri msg action focus-column-{'right' if is_up else 'left'}"
        )
    )


def _get_monitor_workspaces(monitor: str, ws_li: list[DictStrAny]):
    """Get Monitor Workspaces"""
    return [ws for ws in ws_li if ws["output"] == monitor]


def _is_ws_visible(monitor: str, ws_li: list[DictStrAny], ws_num: int):
    """Is Workspace Visible or not"""
    monitor_ws_li = _get_monitor_workspaces(monitor, ws_li)

    return len(monitor_ws_li) > ws_num or (
        len(monitor_ws_li) >= ws_num
        and monitor_ws_li[ws_num - 1]["is_active"]
        and monitor_ws_li[ws_num - 1]["is_focused"]
    )


def _niri_window(monitor: str, ws_num: int, window_num: int):
    """Niri Window"""

    def _is_visible(ws_li: list[DictStrAny], windows: list[DictStrAny]):
        """Is Window Visible"""
        is_visible = _is_ws_visible(monitor, ws_li, ws_num)

        if is_visible:
            ws_info = next(
                ws for ws in ws_li if ws["output"] == monitor and ws["idx"] == ws_num
            )
            ws_windows = [
                window for window in windows if window["workspace_id"] == ws_info["id"]
            ]
            is_visible = len(ws_windows) >= window_num or (
                len(ws_windows) == 0 and ws_info["is_active"] and window_num == 1
            )

        return is_visible

    def _get_icon(ws_li: list[DictStrAny], windows: list[DictStrAny]):
        """Is Window Visible"""
        # Get Workspace Info
        ws_info = next(
            (ws for ws in ws_li if ws["output"] == monitor and ws["idx"] == ws_num),
            None,
        )
        if ws_info is None:
            return WS_EMPTY_ICON

        ws_windows = [
            window for window in windows if window["workspace_id"] == ws_info["id"]
        ]

        if len(ws_windows) < window_num:
            return WS_EMPTY_ICON

        icon_name = ws_windows[window_num - 1]["app_id"].lower()
        if icon_name == "kitty":
            icon_name = "kitty-custom"

        return icon_name

    return Widget.Box(
        visible=niri.bind_many(["workspaces", "windows"], transform=_is_visible),
        child=[
            Widget.Icon(
                image=niri.bind_many(["workspaces", "windows"], transform=_get_icon),
            )
        ],
    )


def _niri_workspace(monitor: str, ws_num: int):
    """Workspace Widget"""

    def _get_classes(ws_li: list[DictStrAny]):
        """Get classes"""
        monitor_ws_li = _get_monitor_workspaces(monitor, ws_li)
        classes = ["hl-workspace"]

        if len(monitor_ws_li) >= ws_num and (
            monitor_ws_li[ws_num - 1]["is_active"]
            and monitor_ws_li[ws_num - 1]["is_focused"]
        ):
            classes.append("hl-workspace-active")

        return classes

    # Button widget
    return Widget.EventBox(
        visible=niri.bind(
            "workspaces", transform=lambda ws_li: _is_ws_visible(monitor, ws_li, ws_num)
        ),
        css_classes=niri.bind("workspaces", transform=_get_classes),
        on_click=lambda _: _focus_workspace(ws_num),
        on_scroll_up=lambda _: _cycle_windows(ws_num, True),
        on_scroll_down=lambda _: _cycle_windows(ws_num, False),
        child=[
            Widget.Box(
                spacing=8,
                child=[_niri_window(monitor, ws_num, idx + 1) for idx in range(3)],
            )
        ],
    )


def niri_workspaces(monitor_id: int = 0):
    # Get connector name
    monitor: str = Utils.get_monitor(monitor_id).get_connector()  # type: ignore
    return Widget.Box(
        css_classes=["bar-section"],
        spacing=4,
        child=[_niri_workspace(monitor, idx + 1) for idx in range(4)],
    )
