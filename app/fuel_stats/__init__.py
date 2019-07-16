from datetime import datetime
from os.path import join, dirname

from PIL import ImageDraw, Image
from gfxhat import touch, backlight
from math import ceil

from app import CONFIG, FONTS
from app.value_display import _new_label, _new_value_label, ValueDisplayScreen, SPEED_OFFSET_FACTOR
from gfxlib.objects import Screen, Line, SpinnerLabel, TEXT_ALIGN_RIGHT, BarGraph, Label, TEXT_VALIGN_BOTTOM, GfxApp, \
    OverlayDialog
from obd import ObdRedisKeys
from obd.redis import get_redis, get_piped
from obd.work import calculate_fuel_usage, calculate_fuel_efficiency
from utils import try_int

MY_DIR = dirname(__file__)
RES_DIR = join(MY_DIR, 'res')

R_KEYS = [
    ObdRedisKeys.KEY_ALIVE,
    ObdRedisKeys.KEY_MIL_STATUS,
    ObdRedisKeys.KEY_ENGINE_RPM,
    ObdRedisKeys.KEY_INTAKE_TEMP,
    ObdRedisKeys.KEY_INTAKE_MAP,
    ObdRedisKeys.KEY_VEHICLE_SPEED
]

LP100K_BREAK_POINT = 30


class FuelStatsScreen(Screen):
    ID = 'fuel-stats'

    def __init__(self):
        super().__init__(FuelStatsScreen.ID)

        self._redis = get_redis(CONFIG)

        self.add_object(Line((0, 8), (128, 8)))

        self._status_label = _new_label((0, 0), 'AWAIT INIT')
        self._spinner_label = SpinnerLabel((128, 0), FONTS['small'],
                                           align=TEXT_ALIGN_RIGHT)

        self._fuel_usage_bar = BarGraph((16, 12), (96, 8),
                                        value=15,
                                        min_value=0, max_value=20, interval=5)
        self._fuel_economy_bar = BarGraph((16, 20), (96, 8),
                                          value=15,
                                          min_value=0, max_value=20, interval=5)
        self._rpm_bar = BarGraph((0, 58), (62, 5),
                                 value=0,
                                 min_value=0, max_value=8000, interval=1000)
        self._rpm_label = Label((0, 58), FONTS['small'], '---- RPM',
                                valign=TEXT_VALIGN_BOTTOM)
        self._spd_bar = BarGraph((65, 58), (62, 5),
                                 value=0,
                                 min_value=-150, max_value=0, interval=20)
        self._spd_label = Label((129, 58), FONTS['small'], '--- KM/H',
                                align=TEXT_ALIGN_RIGHT, valign=TEXT_VALIGN_BOTTOM)

        self._fuel_usage_label = _new_value_label((75, 48), '--.-')
        self._fuel_usage_unit_label = _new_label((75, 37), 'l/h')

        self.add_objects(self._status_label,
                         self._spinner_label,
                         self._fuel_usage_bar,
                         self._fuel_economy_bar,
                         self._rpm_bar,
                         self._rpm_label,
                         self._spd_bar,
                         self._spd_label,
                         self._fuel_usage_label,
                         self._fuel_usage_unit_label)

        self._had_dtcs = False
        self._dtc_dialog = OverlayDialog((108, 56),
                                         join(RES_DIR, 'warn32.png'),
                                         'Check\nEngine!',
                                         FONTS['med'], FONTS['small'],
                                         initial_visible=False)
        self._dtc_indicator = Label((115, 0), FONTS['small'], '!ENGINE!',
                                    align=TEXT_ALIGN_RIGHT)
        self.add_objects(self._dtc_indicator,
                         self._dtc_dialog)

    def update(self, now: datetime, app: GfxApp):
        has_dtcs = False
        spd = 0
        rpm = 0
        lph = None
        lp100k = None

        try:
            data = get_piped(self._redis, R_KEYS)
            state = try_int(data[ObdRedisKeys.KEY_ALIVE])
            self.set_status(ValueDisplayScreen.get_status_text(state))

            if state == 1 or state == 10:
                has_dtcs = data[ObdRedisKeys.KEY_MIL_STATUS].decode('utf-8') == str(True)
                spd = ceil(try_int(data[ObdRedisKeys.KEY_VEHICLE_SPEED], 0) * SPEED_OFFSET_FACTOR)
                rpm = try_int(data[ObdRedisKeys.KEY_ENGINE_RPM])
                intmp = try_int(data[ObdRedisKeys.KEY_INTAKE_TEMP])
                inmap = try_int(data[ObdRedisKeys.KEY_INTAKE_MAP])

                lph = min(calculate_fuel_usage(rpm, inmap, intmp, 0.85, 1.390, 745), 99.9)
                lp100k = min(calculate_fuel_efficiency(spd, lph), 99.9) if spd > 0 else 0
        except:
            self.set_status('DATA ERR')

        self.set_fuel_ecp(lph, lp100k, spd)
        self.set_rpm(rpm)
        self.set_spd(spd)
        self.set_dtcs(has_dtcs)

        self._dtc_indicator.is_visible = self._had_dtcs and now.second % 2 == 0

        super().update(now, app)

    def _render(self, draw: ImageDraw.ImageDraw, image: Image.Image):
        super()._render(draw, image)
        if self._dtc_dialog.is_visible:
            blink = datetime.now().second % 2 == 0
            backlight.set_all(255, 100 if blink else 0, 100 if blink else 0)
        else:
            backlight.set_all(255, 0, 0)
        backlight.show()

    def set_status(self, status: str):
        self._status_label.text = status

    def set_fuel_ecp(self, lph: float, lp100k: float, spd: int):
        if lph is None:
            self._fuel_usage_bar.p_value = 0
            self._fuel_economy_bar.p_value = 0
            self._fuel_usage_label.text = '--.-'
            return

        self._fuel_usage_bar.p_value = lph
        self._fuel_economy_bar.p_value = lp100k

        self._fuel_usage_label.text = '{:0.1f}'.format(lp100k if spd >= LP100K_BREAK_POINT else lph)
        self._fuel_usage_unit_label.text = 'l/100km' if spd >= LP100K_BREAK_POINT else 'l/h'

    def set_rpm(self, rpm: int):
        self._rpm_label.text = '{:>4.0f} RPM'.format(rpm) if rpm is not None else '---- RPM'
        self._rpm_bar.p_value = rpm or 0

    def set_spd(self, spd: int):
        self._spd_label.text = '{:.0f} KM/H'.format(spd) if spd is not None else '--- KM/H'
        self._spd_bar.p_value = -spd if spd else 0

    def set_dtcs(self, has_dtcs: bool):
        if has_dtcs and not self._had_dtcs:
            self._had_dtcs = True
            self._dtc_dialog.show()
        elif not has_dtcs and self._had_dtcs:
            self._had_dtcs = False
            self._dtc_dialog.hide()

    def on_plus_pressed(self, app):
        if self._dtc_dialog.is_visible:
            self._dtc_dialog.on_plus_pressed(app)
        else:
            app.navigate_to('value_display')

    def on_back_pressed(self, app: GfxApp):
        if self._dtc_dialog.is_visible:
            return
        app.navigate_to('dialog-shutdown')

    def on_enter_pressed(self, app: GfxApp):
        if self._dtc_dialog.is_visible:
            return
        app.navigate_to('main-menu')
