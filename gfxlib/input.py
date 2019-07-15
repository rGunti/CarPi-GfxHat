from gfxhat import touch

BTN_UP = 0
BTN_DOWN = 1
BTN_BACK = 2
BTN_MINUS = 3
BTN_ENTER = 4
BTN_PLUS = 5

BUTTONS = [
    BTN_UP,
    BTN_DOWN,
    BTN_BACK,
    BTN_MINUS,
    BTN_ENTER,
    BTN_PLUS
]

EVT_PRESS = 'press'
EVT_RELEASE = 'release'


def on_touch(button: int, handler):
    touch.on(button, handler)
