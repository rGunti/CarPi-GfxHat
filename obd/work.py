"""
CARPI DASH DAEMON
(C) 2018, Raphael "rGunti" Guntersweiler
Licensed under MIT
"""

GAS_CONSTANT: float = 8.3144598  # J/mol.K
AIR_MOL_MASS: float = 28.9644    # g/mol


def _to_kelvin(deg_c: int):
    return deg_c + 273.15


def calculate_fuel_usage(rpm: int,
                         map: int,
                         in_tmp: int,
                         v_E: float,
                         v_H: float,
                         p_F: int) -> float:
    """
    :param rpm: RPM [RPM] (OBD 010C)
    :param map: Manifold Absolute Pressure [kPa] (OBD 010B)
    :param in_tmp: Intake Air Temperature [°C] (OBD 010F)
    :param v_E: Volumetric Efficiency [0-1, %] (default is 85% => 0.85)
    :param v_H: Engine Volume [l] (ccm / 1000)
    :param p_F: Fuel density [g/l] (E10 = 745 g/l, Gas = 720 - 775 g/l)
    :return: Fuel usage in [l/h]
    """
    # Volumetric Efficiency is a value between 0 and 1 (% value)
    assert 0 <= v_E <= 1
    # Engine Volume should be in a "sensible" range (0.5l / 500ccm - 5l / 5000ccm)
    assert 0.5 <= v_H <= 5

    imap = (rpm * map) / _to_kelvin(in_tmp)
    maf = ((imap / 120) * v_E * v_H * AIR_MOL_MASS) / GAS_CONSTANT

    lps = (maf / 14.7) / p_F
    return lps * 3600


def calculate_fuel_efficiency(spd: int, lph: float) -> float:
    """
    :param spd: Vehicle Speed [km/h] (OBD 010D or GPS, used only for efficiency over distance, 0 to disable)
    :param lph: Fuel usage in [l/h]
    :return: Fuel efficiency in [l/100km]
             Returns 0, if speed is reported as 0 km/h (or lower) or fuel usage is 0 l/h (or lower)
    """
    if spd <= 0 or lph <= 0:
        return float(0)
    return (lph / spd) * 100
