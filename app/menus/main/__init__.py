from app.templates.menu import BaseMenu
from gfxlib.objects import GfxApp


class MainMenu(BaseMenu):
    ID = 'main-menu'

    def __init__(self):
        super().__init__(MainMenu.ID, 'Main Menu', [
            '< Back',
            'Settings',
            'Info',
            'Shutdown'
        ], [
            self._on_back_selected,
            None,
            None,
            self._on_shutdown_selected
        ]
        )

    def _on_shutdown_selected(self, i, app: GfxApp):
        app.navigate_to('dialog-shutdown')

    def _on_back_selected(self, i, app: GfxApp):
        app.navigate_to('fuel-stats')
