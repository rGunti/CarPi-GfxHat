from datetime import datetime
from os.path import dirname, join

from math import ceil

from app import FONTS
from app.fuel_stats import FuelStatsScreen
from gfxlib.objects import Screen, Label, TEXT_ALIGN_CENTER, TEXT_VALIGN_CENTER, TEXT_VALIGN_BOTTOM, GfxApp, FileImage, \
    IMAGE_RMODE_RENDER_NON_ALPHA, TEXT_ALIGN_RIGHT
from gfxhat.touch import set_led

BOOT_FRAMES = [
    [0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0],
    [1, 1, 0, 0, 0, 0],
    [1, 1, 1, 0, 0, 0],
    [1, 1, 1, 1, 0, 0],
    [1, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 1],
    [0, 0, 1, 1, 1, 1],
    [0, 0, 0, 1, 1, 1],
    [0, 0, 0, 1, 1, 1],
    [0, 0, 0, 0, 1, 1],
    [0, 0, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0]
]

MY_DIR = dirname(__file__)
RES_DIR = join(MY_DIR, 'res')


class BootScreen(Screen):
    ID = 'BOOT'

    def __init__(self):
        super().__init__(BootScreen.ID)

        self.add_object(
            FileImage((26, 0), join(RES_DIR, 'seat32.png'),
                      render_mode=IMAGE_RMODE_RENDER_NON_ALPHA))
        self.add_object(
            FileImage((70, 0), join(RES_DIR, 'raspberry32.png'),
                      render_mode=IMAGE_RMODE_RENDER_NON_ALPHA))

        self.add_object(
            Label((64, 8), FONTS['default'], '+',
                  TEXT_ALIGN_CENTER))

        self.add_object(
            Label((64, 32), FONTS['default'], 'CarPi Display',
                  TEXT_ALIGN_CENTER))

        self.add_object(
            Label((0, 64), FONTS['small'], '(C)2019, rGunti',
                  valign=TEXT_VALIGN_BOTTOM))

        self.add_object(
            Label((128, 64), FONTS['small'], 'v0.1',
                  TEXT_ALIGN_RIGHT,
                  TEXT_VALIGN_BOTTOM))

        self._frame = 0
        self._first_render: datetime = None

    def update(self, now: datetime, app: GfxApp):
        if not self._first_render:
            self._first_render = datetime.now()

        delta = (datetime.now() - self._first_render).total_seconds()
        if delta > len(BOOT_FRAMES) * 0.2:
            self._first_render = None
            app.navigate_to(FuelStatsScreen.ID)
            return

        frame_i = ceil(delta / 0.2) % len(BOOT_FRAMES)
        frame = BOOT_FRAMES[frame_i]
        for i in range(len(frame)):
            set_led(i, frame[i])

