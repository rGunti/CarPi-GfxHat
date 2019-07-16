from datetime import datetime

from PIL import ImageDraw, Image
from gfxhat.backlight import set_all as set_all_bg, show as show_bg
from gfxlib import pipeline
from gfxlib.objects import GfxApp, Screen, Label, TEXT_ALIGN_CENTER, TEXT_VALIGN_CENTER, TEXT_VALIGN_BOTTOM, Line
from gfxlib.utils import init_fonts, get_new_font


init_fonts()
FONTS = {
    'default': get_new_font('10x20', 20),
    'med': get_new_font('6x10', 10),
    'small': get_new_font('5x8', 8)
}


class DevelopScreen(Screen):
    ID = 'develop'

    def __init__(self):
        super().__init__(DevelopScreen.ID)
        self.add_objects(Line((0, 0), (127, 0)),
                         Line((0, 0), (0, 63)),
                         Line((0, 63), (127, 63)),
                         Line((127, 0), (127, 63)),
                         Label((64, 21), FONTS['default'], 'Develop Mode',
                               align=TEXT_ALIGN_CENTER, valign=TEXT_VALIGN_BOTTOM),
                         Line((0, 22), (128, 22)),
                         Label((64, 27), FONTS['med'], 'Device is in Develop',
                               align=TEXT_ALIGN_CENTER),
                         Label((64, 37), FONTS['med'], 'Mode. To disable',
                               align=TEXT_ALIGN_CENTER),
                         Label((64, 47), FONTS['med'], 'run develop.sh',
                               align=TEXT_ALIGN_CENTER)
                         )

    def on_enter_pressed(self, app: GfxApp):
        app.navigate_to(DisableDevelopModeScreen.ID)


class DisableDevelopModeScreen(Screen):
    ID = 'disable-dev-mode'

    def __init__(self):
        super().__init__(DisableDevelopModeScreen.ID)
        self.add_objects(Line((0, 0), (127, 0)),
                         Line((0, 0), (0, 63)),
                         Line((0, 63), (127, 63)),
                         Line((127, 0), (127, 63)),
                         Label((64, 32), FONTS['default'], 'Disabling\nDevelop Mode',
                               align=TEXT_ALIGN_CENTER, valign=TEXT_VALIGN_CENTER)
                         )
        self._has_been_rendered = False
        self._has_been_executed = False

    def _render(self, draw: ImageDraw.ImageDraw, image: Image.Image):
        super()._render(draw, image)
        self._has_been_rendered = True

    def update(self, now: datetime, app):
        if self._has_been_rendered and not self._has_been_executed:
            self.disable_dev_mode()
            self._has_been_executed = True
        super().update(now, app)

    def disable_dev_mode(self):
        try:
            from os import execlp
            from subprocess import call
            call(["/bin/bash", "develop.sh", "-d"])
            call(["/sbin/reboot", "-f"])
        except Exception as e:
            print("Failed to run DISABLE and REBOOT", e)


APP = GfxApp()
APP.add_screens([DevelopScreen(),
                 DisableDevelopModeScreen()])
PIPELINE = pipeline.RenderPipeline(APP, fps_limit=1)

set_all_bg(255, 0, 0)
show_bg()

i = 0
while i < 30:
    PIPELINE.loop_step()
    # PIPELINE.set_modifiers(pipeline.MODIFIER_COLOR_INVERTED
    #                        if i % 2 else pipeline.MODIFIER_NONE)
    i += 1


set_all_bg(100, 0, 0)
show_bg()
