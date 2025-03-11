from datetime import datetime as dt
from datetime import timezone

from ignis.utils import Utils
from ignis.variable import Variable
from ignis.widgets import Widget

# Date time format
FORMAT = "%H:%M:%S %a %d %b %Y"


def bar_center():
    """Bar Center"""
    # Variable to indicate to show UTC time or now
    show_utc = Variable(value=False)

    def toggle_show_utc():
        show_utc.value = not show_utc.value  # type: ignore

    return Widget.Box(
        css_classes=["bar-section", "clock"],
        spacing=8,
        child=[
            # Icon
            Widget.Icon(image="preferences-system-time-symbolic"),
            # Clock button
            Widget.Button(
                child=Widget.Label(
                    label=Utils.Poll(
                        50,
                        lambda _: dt.now(
                            timezone.utc if show_utc.value else None
                        ).strftime(FORMAT),
                    ).bind("output")
                ),
                on_click=lambda _: toggle_show_utc(),
            ),
        ],
    )
