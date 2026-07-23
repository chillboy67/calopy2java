from pathlib import Path

from shiny import App

from calopy.calopy_server import calopy_server
from calopy.calopy_ui import calopy_ui

www_dir = Path(__file__).parent / "calopy" / "assets"
app = App(ui=calopy_ui, server=calopy_server, static_assets=www_dir)
