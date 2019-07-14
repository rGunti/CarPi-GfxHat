from lib.utils import init_fonts, get_new_font
from obd.config import init_config_env

init_fonts()
FONTS = {
    'default': get_new_font('10x20', 20),
    'med': get_new_font('6x10', 10),
    'small': get_new_font('5x8', 8)
}

CONFIG = init_config_env('CARPI_UI_CONFIG', ['ui.conf', '/etc/carpi/ui.conf'])
