from os.path import dirname, join

from app import FONTS
from gfxlib.objects import Screen, Line, Label, TEXT_ALIGN_CENTER, FileImage, IMAGE_RMODE_RENDER_NON_ALPHA, GfxApp

MY_DIR = dirname(__file__)
RES_DIR = join(MY_DIR, 'res')


class QuestionDialog(Screen):
    def __init__(self,
                 screen_id: str, screen_title: str,
                 question: str,
                 confirm_text: str = 'OK',
                 cancel_text: str = 'CANCEL'):
        super().__init__(screen_id)
        self.add_objects(Line((0, 8), (128, 8)),
                         Label((64, 0), FONTS['small'], screen_title or screen_id,
                               align=TEXT_ALIGN_CENTER),
                         Line((0, 55), (128, 55)),
                         Line((42, 55), (42, 64)),
                         Line((85, 55), (85, 64)),
                         Label((21, 56), FONTS['small'], confirm_text,
                               align=TEXT_ALIGN_CENTER),
                         Label((106, 56), FONTS['small'], cancel_text,
                               align=TEXT_ALIGN_CENTER),
                         FileImage((0, 16), join(RES_DIR, 'question.png'),
                                   render_mode=IMAGE_RMODE_RENDER_NON_ALPHA),
                         Label((35, 12), FONTS['med'], question)
                         )
        self._source_screen = None

    def on_navigate_to(self, from_screen: str = None):
        self._source_screen = from_screen

    def on_minus_pressed(self, app):
        self._on_confirm_pressed(app)

    def on_plus_pressed(self, app):
        self._on_cancel_pressed(app)

    def _on_confirm_pressed(self, app: GfxApp):
        pass

    def _on_cancel_pressed(self, app: GfxApp):
        app.navigate_to(self._source_screen)
