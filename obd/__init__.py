
class ObdRedisKeys:
    KEY_ALIVE = 'OBD.State'

    KEY_BATTERY_VOLTAGE = 'OBD.BatteryVoltage'
    KEY_ENGINE_LOAD = 'OBD.EngineLoad'
    KEY_COOLANT_TEMP = 'OBD.CoolantTemp'
    KEY_INTAKE_MAP = 'OBD.IntakeMAP'
    KEY_ENGINE_RPM = 'OBD.RPM'
    KEY_VEHICLE_SPEED = 'OBD.Speed'
    KEY_INTAKE_TEMP = 'OBD.IntakeTemp'
    KEY_O2_SENSOR_FAEQV = 'OBD.O2Sensor.FuelAirEqRatio'
    KEY_O2_SENSOR_CURRENT = 'OBD.O2Sensor.Current'
    KEY_FUELSYS_1_STATUS = 'OBD.FuelSystem1.Status'
    KEY_FUELSYS_2_STATUS = 'OBD.FuelSystem2.Status'
    KEY_MIL_STATUS = 'OBD.MIL'
    KEY_DTC_COUNT = 'OBD.DTCCount'
    KEY_CURRENT_DTCS = 'OBD.DTCs.Current'
    KEY_PENDING_DTCS = 'OBD.DTCs.Pending'

    KEYS = [
        KEY_ALIVE,
        KEY_BATTERY_VOLTAGE,
        KEY_ENGINE_LOAD,
        KEY_INTAKE_MAP,
        KEY_ENGINE_RPM,
        KEY_VEHICLE_SPEED,
        KEY_INTAKE_TEMP,
        KEY_O2_SENSOR_FAEQV,
        KEY_O2_SENSOR_CURRENT
    ]
