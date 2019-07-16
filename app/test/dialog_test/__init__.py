from os.path import join, dirname

from app import FONTS
from gfxlib.objects import Screen, Line, Rectangle, FileImage, IMAGE_RMODE_RENDER_NON_ALPHA, Label, TEXT_ALIGN_CENTER, \
    OverlayDialog

MY_DIR = dirname(__file__)
RES_DIR = join(MY_DIR, 'res')


class DialogTestScreen(Screen):
    def __init__(self):
        super().__init__('test-dialog')

        # Background
        self.add_objects(Line((0, 0), (127, 63)),
                         Line((0, 63), (127, 0)))

        # Dialog
        self._dialog = OverlayDialog((108, 53),
                                     join(RES_DIR, 'warn32.png'),
                                     'Check\nEngine!',
                                     FONTS['med'],
                                     FONTS['small'])
        self.add_objects(self._dialog)

    def on_plus_pressed(self, app):
        if self._dialog.is_visible:
            self._dialog.on_plus_pressed(app)
        else:
            super().on_plus_pressed(app)

    def on_enter_pressed(self, app):
        if not self._dialog.is_visible:
            self._dialog.show()
