"""
    Copyright 2021 Walter Pachlinger (walter.pachlinger@gmail.com)

    Licensed under the EUPL, Version 1.2 or - as soon they will be approved by the European
    Commission - subsequent versions of the EUPL (the LICENSE). You may not use this work except
    in compliance with the LICENSE. You may obtain a copy of the LICENSE at:

        https://joinup.ec.europa.eu/software/page/eupl

    Unless required by applicable law or agreed to in writing, software distributed under the
    LICENSE is distributed on an "AS IS" basis, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
    either express or implied. See the LICENSE for the specific language governing permissions
    and limitations under the LICENSE.
"""
import inspect
import logging
import iot_msg_input
import iot_msg_sensor

class IotSensor:
    """ Base class for an IOT sensor.

    Attributes:
        _logger : logging.Logger
            Logger to be used.
        _sensor_id : str
            Unique identification of the sensor.
        _sensor_type : str
            Type of the sensor.
        _last_msmt_time : datetime
            Timestamp of last measurement.
        _last_msmt_value : float
            Most recently measured sensor value.
        msmt_unit : str
            Unit of the measurement value.

    Methods:
        IotSensor()
            Constructor
        measure: SensorMeasurement
            Calculates a measured value from an input probe and returns it as a SensorMeasurement object.
        calculate_msmt_value : tuple
            Sensor specific calculation of the measurement value from the input probe. To be overloaded
            in child classes.
    """
    def __init__(self, sensor_id: str, sensor_type: str, logger: logging.Logger):
        """ Constructor.

        Parameters:
            sensor_id : str
                Unique identifier of the sensor.
            sensor_type : str
                Type (model) of the sensor.
            logger : logging.Logger
                Logger to be used.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self._logger = logger
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        self._last_msmt_time = None
        self._last_msmt_value = None
        self.msmt_unit = None
        self._logger.debug('{}: Initialized sensor ID = "{}", TYPE = "{}"'.format(
            mth_name, self.sensor_id, self.sensor_type))

    def measure(self, hardware_input: iot_msg_input.InputProbe) -> iot_msg_sensor.SensorMsmt:
        """ Calculates a measured value from an input probe and returns it as a SensorMsmt object.

        Parameters:
            hardware_input : iot_msg_input.InputProbe
                Input probe received from a hardware element that contains the base value for the measurement.

        Returns:
            iot_msg_sensor.SensorMeasurement:
                Result of the measurement calculation.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self._logger.debug('{}(hw_value = {}, hw_voltage = {:.5f})'.format(
            mth_name, hardware_input.value, hardware_input.voltage))
        m_res = iot_msg_sensor.SensorMsmt(self.sensor_id, self.sensor_type)
        m_res.hw_value = hardware_input.value
        m_res.hw_voltage = hardware_input.voltage
        m_res.msmt_value, m_res.msmt_unit = self.calculate_msmt_value(m_res.hw_value, m_res.hw_voltage)
        self._last_msmt_time = m_res.msmt_time
        self._last_msmt_value = m_res.msmt_value
        self._logger.debug('{}: msmt_value = {:.2f} {}', mth_name, m_res.msmt_value, m_res.msmt_unit)
        return m_res

    def calculate_msmt_value(self, hw_value: int, hw_voltage: float = 0.0) -> tuple:
        """  Sensor specific calculation of the measurement value from the input probe. To be overloaded
            in child classes.

        Parameters:
            hw_value : int
                Probe value received from a hardware element.
            hw_voltage : float, optional
                Probe voltage received from a hardware element.

        Returns:
            tuple : a tuple (value, unit) where value is the calculated measurement value and unit refers to
                the unit of the value (m, sec, kg, pct).
        """
        #pylint: disable=unused-argument
        return (hw_value, self.msmt_unit)



class IotSensorHumKYES516(IotSensor):
    """ Special measurement calculation for a KEYS516 soil humidity sensor.

    Attributes:
        msmt_unit : str
            Measurement unit, fixed value 'pct' (percent).

    Methods:
        IotSensorHumKYES516()
            Constructor
        calculate_msmt_value : tuple
            Sensor specific calculation of the measurement value from the input probe.
    """
    def __init__(self, sensor_id: str, sensor_type: str, logger: logging.Logger):
        """ Constructor

        Parameters:
            sensor_id : str
                Unique identifier of the sensor.
            sensor_type : str
                Type (model) of the sensor.
            logger : logging.Logger
                Logger to be used.
        """
        super().__init__(sensor_id, sensor_type, logger)
        self.msmt_unit = 'pct'

    def calculate_msmt_value(self, hw_value, hw_voltage=0.0) -> tuple:
        """ Sensor specific calculation of the measurement value from the input probe.

        Parameters:
            hw_value : int
                Probe value received from a hardware element.
            hw_voltage : float, optional
                Probe voltage received from a hardware element.

        Returns:
            tuple : a tuple (value, 'pct') where value is the calculated humidity value in 'percent'.
        """
        humidity = 100.0 * (30000.0 - float(hw_value)) / 30000.0
        return (humidity, self.msmt_unit)
