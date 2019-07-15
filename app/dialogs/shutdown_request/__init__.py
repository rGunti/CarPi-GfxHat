from app.templates.question import QuestionDialog
from gfxlib.objects import GfxApp


class ShutdownRequestDialog(QuestionDialog):
    def __init__(self):
        super().__init__('dialog-shutdown', 'SHUTDOWN',
                         'Shutdown\ndevice?',
                         'YES', 'NO')

    def _on_confirm_pressed(self, app: GfxApp):
        app.navigate_to('shutdown')
