from ignis.app import IgnisApp
from ignis.utils import Utils

from widgets.bar import bar

# Add CSS and Icons
app = IgnisApp.get_default()
app.apply_css("./assets/style.scss")
app.add_icons("./assets")

# Init bar for each monitor
for i in range(Utils.get_n_monitors()):  # type: ignore
    bar(i)
