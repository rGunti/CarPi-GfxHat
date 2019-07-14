from datetime import datetime
from typing import Tuple

from math import ceil

from app import FONTS, CONFIG
from lib.objects import Screen, Label, TEXT_ALIGN_RIGHT, Line, SpinnerLabel, \
    GfxApp, TEXT_VALIGN_BOTTOM
from obd import ObdRedisKeys
from obd.redis import get_redis, get_piped
from utils import try_int

R_KEYS = [
    ObdRedisKeys.KEY_ALIVE,
    ObdRedisKeys.KEY_ENGINE_RPM,
    ObdRedisKeys.KEY_INTAKE_TEMP,
    ObdRedisKeys.KEY_INTAKE_MAP,
    ObdRedisKeys.KEY_VEHICLE_SPEED,
    ObdRedisKeys.KEY_FUELSYS_1_STATUS,
    ObdRedisKeys.KEY_FUELSYS_2_STATUS
]

SPEED_OFFSET_FACTOR = 1.03


def _new_label(xy: Tuple[int, int], text: str) -> Label:
    return Label(xy, FONTS['small'], text)


def _new_value_label(xy: Tuple[int, int], text: str) -> Label:
    return Label(xy, FONTS['default'], text,
                 align=TEXT_ALIGN_RIGHT,
                 valign=TEXT_VALIGN_BOTTOM)


class ValueDisplayScreen(Screen):
    ID = 'value_display'

    def __init__(self):
        super().__init__(ValueDisplayScreen.ID)

        self.add_objects(Line((0, 8), (128, 8)),
                         Line((43, 8), (43, 64)),
                         Line((85, 8), (85, 64)),
                         Line((0, 36), (128, 36))
                         )

        self.add_objects(_new_label((0, 9), 'Speed'),
                         _new_label((0, 37), 'RPM'),
                         _new_label((45, 9), 'Int.Temp'),
                         _new_label((45, 37), 'Int.MAP'),
                         _new_label((87, 9), 'FuelS1'),
                         _new_label((87, 37), 'FuelS2')
                         )

        self._status_label = _new_label((0, 0), 'AWAIT INIT')
        self._spinner_label = SpinnerLabel((128, 0), FONTS['small'],
                                           align=TEXT_ALIGN_RIGHT)

        self._speed_label = _new_value_label((43, 37), '----')
        self._rpm_label = _new_value_label((43, 65), '----')

        self._intake_tmp = _new_value_label((85, 37), '----')
        self._intake_map = _new_value_label((85, 65), '----')

        self._fuel_status_1 = _new_value_label((127, 37), '----')
        self._fuel_status_2 = _new_value_label((127, 65), '----')

        self.add_objects(self._status_label,
                         self._spinner_label,
                         self._speed_label,
                         self._rpm_label,
                         self._intake_tmp,
                         self._intake_map,
                         self._fuel_status_1,
                         self._fuel_status_2)

        self._redis = get_redis(CONFIG)

    def update(self, now: datetime, app):
        try:
            data = get_piped(self._redis, R_KEYS)
            state = try_int(data[ObdRedisKeys.KEY_ALIVE])
            self.set_status(ValueDisplayScreen.get_status_text(state))

            spd = 0
            rpm = 0
            intmp = 0
            inmap = 0
            fuel_st1 = 0
            fuel_st2 = 0

            if state == 1 or state == 10:
                spd = try_int(data[ObdRedisKeys.KEY_VEHICLE_SPEED])
                rpm = try_int(data[ObdRedisKeys.KEY_ENGINE_RPM])
                intmp = try_int(data[ObdRedisKeys.KEY_INTAKE_TEMP])
                inmap = try_int(data[ObdRedisKeys.KEY_INTAKE_MAP])
                fuel_st1 = try_int(data[ObdRedisKeys.KEY_FUELSYS_1_STATUS])
                fuel_st2 = try_int(data[ObdRedisKeys.KEY_FUELSYS_2_STATUS])
            else:
                pass

            self.set_speed(ceil(spd * SPEED_OFFSET_FACTOR))
            self.set_rpm(rpm)
            self.set_intake_temp(intmp)
            self.set_intake_map(inmap)
            self.set_fuel_status_1(fuel_st1)
            self.set_fuel_status_2(fuel_st2)
        except:
            self.set_status('DATA ERR')

        super().update(now, app)

    @staticmethod
    def get_status_text(state: int):
        if state is None:
            return 'OFFLINE'
        elif state == 0:
            return 'SRC INIT'
        elif state == 1:
            return 'OK'
        elif state == 10:
            return 'SRC SIM'
        else:
            return '???'

    def set_status(self, status: str):
        self._status_label.text = status

    def set_speed(self, speed: int):
        self._speed_label.text = '{:.0f}'.format(speed)

    def set_rpm(self, rpm: int):
        self._rpm_label.text = '{:.0f}'.format(rpm)

    def set_intake_temp(self, temp: int):
        self._intake_tmp.text = '{:.0f}'.format(temp)

    def set_intake_map(self, i_map: int):
        self._intake_map.text = '{:.0f}'.format(i_map)

    def set_fuel_status_1(self, fuel_status: int):
        self._fuel_status_1.text = '{:.0f}'.format(fuel_status)

    def set_fuel_status_2(self, fuel_status: int):
        self._fuel_status_2.text = '{:.0f}'.format(fuel_status)

    def on_minus_pressed(self, app: GfxApp):
        app.navigate_to('fuel-stats')
