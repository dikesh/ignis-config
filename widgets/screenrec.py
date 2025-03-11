import asyncio
from datetime import datetime as dt
from datetime import timezone

from ignis.utils import Utils
from ignis.variable import Variable
from ignis.widgets import Widget

# Variables
filename = Variable("")
is_recording = Variable(False)


async def start_recording():
    """Start Recording"""
    # Start recording
    now = dt.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    filename.value = f"~/Videos/screenrec-{now}.mp4"  # type: ignore
    is_recording.value = True  # type: ignore

    cmd = f'wl-screenrec -g "$(slurp)" -f {filename.value}'
    try:
        await Utils.exec_sh_async(cmd)  # type: ignore
    except:  # noqa: E722
        is_recording.value = False  # type: ignore


async def stop_recording():
    """Stop Recording"""
    # Kill process and Update flag
    await Utils.exec_sh_async("pkill wl-screenrec")  # type: ignore
    is_recording.value = False  # type: ignore

    # Send notification
    await Utils.exec_sh_async(  # type: ignore
        f"notify-send 'Screen Recorder ..' 'Filename: {filename.value}'"
    )


async def toggle_recording():
    """Toggle Recording"""
    if is_recording.value:
        await stop_recording()
    else:
        await start_recording()


def screen_rec():
    """Screen Recording Widget"""
    # Constants
    icon_recording_on = "record-desktop-indicator-recording"
    icon_recording_off = "record-desktop-indicator"

    # Record button
    return Widget.Button(
        css_classes=["bar-section"],
        child=Widget.Icon(
            image=is_recording.bind(
                "value",
                transform=lambda flag: icon_recording_on
                if flag
                else icon_recording_off,
            )
        ),
        on_click=lambda _: asyncio.create_task(toggle_recording()),
    )
