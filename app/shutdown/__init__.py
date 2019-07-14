from datetime import datetime

from PIL import ImageDraw
from PIL.Image import Image
from gfxhat.touch import set_led

from app import FONTS
from lib.objects import Screen, GfxApp, Label, TEXT_ALIGN_CENTER, TEXT_VALIGN_CENTER

SCREEN_ID = 'shutdown'


class ShutdownScreen(Screen):
    def __init__(self):
        super().__init__(SCREEN_ID)

        self.add_objects(Label((64, 32), FONTS['default'],
                               'Shutting down',
                               align=TEXT_ALIGN_CENTER,
                               valign=TEXT_VALIGN_CENTER)
                         )
        self._has_rendered = False

    def on_navigate_to(self, from_screen: str = None):
        for i in range(6):
            set_led(i, 0)
        self._has_rendered = False

    def _render(self, draw: ImageDraw.ImageDraw, image: Image):
        super()._render(draw, image)
        self._has_rendered = True

    def update(self, now: datetime, app):
        super().update(now, app)
        if self._has_rendered:
            try:
                from os import execlp
                from subprocess import call
                call(["/sbin/halt", "-p", "-f"])
            except:
                print("Failed to run SHUTDOWN")

    def on_back_pressed(self, app: GfxApp):
        app.navigate_to('BOOT')
