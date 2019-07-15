from os import environ
from time import sleep

from gfxhat.backlight import set_all as set_all_bg, show as show_bg
from gfxhat.lcd import clear as clear_screen, show as show_screen

from app.boot import BootScreen
from app.dialogs.shutdown_request import ShutdownRequestDialog
from app.fuel_stats import FuelStatsScreen
from app.menus.main import MainMenu
from app.shutdown import ShutdownScreen
from app.templates.question import QuestionDialog
from app.value_display import ValueDisplayScreen
from gfxlib import pipeline
from gfxlib.objects import GfxApp

SKIP_BOOT_SCREEN = environ.get('CARPI_UI_SKIP_BOOT', None) == '1'
START_WITH_SCREEN = environ.get('CARPI_UI_START_WITH', None)
ENABLE_TIMING = environ.get('CARPI_UI_PROFILING', None) == '1'

set_all_bg(255, 0, 0)
show_bg()


APP = GfxApp()
if not SKIP_BOOT_SCREEN:
    APP.add_screen(BootScreen())

APP.add_screen(FuelStatsScreen())
APP.add_screen(ValueDisplayScreen())
APP.add_screen(ShutdownScreen())
APP.add_screen(MainMenu())
APP.add_screen(QuestionDialog('test-dialog', 'Test Question',
                              'Would you like\nto do that\nimportant thing?',
                              'YES', 'NO'))
APP.add_screen(ShutdownRequestDialog())

PIPELINE = pipeline.RenderPipeline(APP,
                                   enable_reinit=True,
                                   enable_timing=ENABLE_TIMING,
                                   fps_limit=10,
                                   orientation=pipeline.ORIENT_LANDSCAPE,
                                   #modifiers=pipeline.MODIFIER_DRAW_IN_DIFF_MODE
                                   )
try:
    if START_WITH_SCREEN:
        APP.navigate_to(START_WITH_SCREEN)

    while APP.alive:
        PIPELINE.loop_step()
except KeyboardInterrupt or SystemError or SystemExit:
    pass

clear_screen()
show_screen()

set_all_bg(100, 0, 0)
show_bg()

sleep(1)
exit(1)
