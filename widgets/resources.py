import asyncio
import re
from datetime import datetime as dt

from ignis.services.fetch import FetchService
from ignis.utils import Utils
from ignis.variable import Variable
from ignis.widgets import Widget

# Fetch service
fetch = FetchService.get_default()


def cpu_usage():
    """CPU Usage Widget"""
    # Average CPU
    avg_cpu = Variable(value="0.00")

    async def _set_avg_cpu():
        """Set Avg CPU"""
        proc = await Utils.exec_sh_async("top -b -n1")  # type: ignore
        line: str = proc.stdout.split("\n")[0]
        matches = re.findall(r"average: (\d+.\d+)", line)
        if len(matches):
            avg_cpu.value = matches[0]

    Utils.Poll(10000, callback=lambda _: asyncio.create_task(_set_avg_cpu()))

    return Widget.Box(
        css_classes=["system-cpu"],
        spacing=8,
        child=[
            Widget.Label(label="󰌢"),
            Widget.Label(label=avg_cpu.bind("value")),
        ],
    )


def ram_usage():
    """RAM Usage Widget"""
    # Poll datetime
    now = Variable("")

    def _update_now():
        now.value = dt.now()  # type: ignore

    Utils.Poll(1000, callback=lambda _: _update_now())

    def _to_gib(val: int):
        """To GiB"""
        return f"{round(val / 1024 / 1024, 1)}Gi"

    return Widget.Box(
        css_classes=["system-memory"],
        spacing=8,
        child=[
            Widget.Label(label="󰍛"),
            Widget.Label(
                label=now.bind("value", transform=lambda _: _to_gib(fetch.mem_used)),
                tooltip_text=now.bind(
                    "value",
                    transform=lambda _: f"Available: {_to_gib(fetch.mem_available)} "
                    f"/ {_to_gib(fetch.mem_total)}",
                ),
            ),
        ],
    )


def temperature():
    """Temperature Usage Widget"""
    # Poll datetime
    now = Variable("")

    def _update_now():
        now.value = dt.now()  # type: ignore

    Utils.Poll(10000, callback=lambda _: _update_now())

    return Widget.Box(
        css_classes=["system-temperature"],
        spacing=8,
        child=[
            Widget.Label(label=""),
            Widget.Label(
                label=now.bind(
                    "value", transform=lambda _: f"{round(fetch.cpu_temp)}°C"
                )
            ),
        ],
    )


def disk_usage():
    """Disk Usage Widget"""
    # Root disk usage
    root_disk_usage = Variable({"total": "0", "used": "0", "available": "0"})

    async def _set_disk_usage():
        """Set Disk Usage"""
        cmd = await Utils.exec_sh_async("df -h")  # type: ignore
        parts = next(
            line.split() for line in cmd.stdout.split("\n") if line.endswith("/")
        )
        root_disk_usage.value = {  # type: ignore
            "total": f"{parts[1]}i",
            "used": f"{parts[2]}i",
            "available": f"{parts[3]}i",
        }

    Utils.Poll(15000, callback=lambda _: asyncio.create_task(_set_disk_usage()))

    return Widget.Box(
        css_classes=["system-disk"],
        spacing=8,
        child=[
            Widget.Label(label=""),
            Widget.Label(
                label=root_disk_usage.bind(
                    "value", transform=lambda val: val["available"]
                ),
                tooltip_text=root_disk_usage.bind(
                    "value",
                    transform=lambda val: f"{val['used']} used out of {val['total']} on /",
                ),
            ),
        ],
    )


def system_resources():
    """System Resources"""
    return Widget.EventBox(
        css_classes=["bar-section"],
        spacing=8,
        child=[
            cpu_usage(),
            ram_usage(),
            temperature(),
            disk_usage(),
        ],
        on_click=lambda _: asyncio.create_task(Utils.exec_sh_async("kitty -e btop")),  # type: ignore
    )
