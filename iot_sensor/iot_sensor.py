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
from datetime import datetime
from typing import Any
import logging
import wp_queueing
import iot_hardware_digital_input as iot_hardware


class SensorMeasurement(wp_queueing.IConvertToDict):
    """ Class for grouping the result of a sensor measurement.

    Attributes:
        sensor_id : str
            Unique identifier of the sensor that produced the measurement.
        sensor_type : str
            Type of sensor that produced the measurement.
        msmt_time : datetime
            Timestamp of the measurement.
        hw_value : int
            Value delivered by the underlying hardware component.
        hw_voltage : float
            Voltage sensed by the underlying hardware component.
        msmt_unit : str
            Unit of the measured value.
        msmt_value : float
            Measured value.

    Methods:
        SensorMeasurement()
            Constructor
        to_dict : dict
            Converts a sensor measurement object into a dictionary representation.
    """
    def __init__(self, sensor_id, sensor_type, msmt_time: datetime = None):
        """ Constructor

        Parameters:
            sensor_id : str
                Unique identifier of the sensor that produced the measurement.
            sensor_type : str
                Type of sensor that produced the measurement.
            msmt_time : datetime, optional
                Timestamp of the measurement.
        """
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        if msmt_time is None:
            self.msmt_time = datetime.now()
        else:
            self.msmt_time = msmt_time
        self.hw_value = 0
        self.hw_voltage = 0
        self.msmt_unit = None
        self.msmt_value = 0

    def to_dict(self) -> dict:
        """ Converts a sensor measurement object into a dictionary representation.

        Returns:
            dict : dictionary representation of the object.
        """
        return {
            'class': 'SensorMeasurement',
            'sensor_id': self.sensor_id,
            'sensor_type': self.sensor_type,
            'msmt_time': self.msmt_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
            'hw_value': self.hw_value,
            'hw_voltage': self.hw_voltage,
            'msmt_unit': self.msmt_unit,
            'msmt_value': self.msmt_value
        }


class IotSensorConfig:
    """ Validation of the configuration settings for a sensor.

    Attributes:
        _config_dict : dict
            Dictionary containing the configuration settings.

    Methods:
        IotSensorConfig()
            Constructor
        _check_config_elem: bool
            Checks the dictionary for a mandatory element, its type, and optionally its value range.
        __getitem__: Any
            Accessor for elements of the configuration dictionary.
    """
    def __init__(self, config_dict: dict):
        """ Constructor.

        Parameters:
            config_dict : dict
                Dictionary containing the configuration settings.
        """
        if isinstance(config_dict, dict):
            raise TypeError('Invalid configuration: must be "dict"')
        self._config_dict = config_dict
        self._check_config_elem('sensor_id', str, [1])
        self._check_config_elem('sensor_type', str, [1])
        self._check_config_elem('topics', dict, ['input_prefix', 'output_prefix'])
        self._check_config_elem('sensor_hw', dict, ['id', 'channel'])

    def _check_elem_int(self, elem_name: str, elem_value: int, constraints: list) -> bool:
        """ Checks the constraints on a configuration element of type 'int'.

        Parameters:
            elem_name : str
                Name of the configuration element.
            elem_value : int
                Value of the element.
            constraints : list
                List of value constraints: [min_value: int, max_value: int, optional].

        Returns:
            bool : constraints check result (True = OK).
        """
        # pylint: disable=no-self-use
        if len(constraints) > 0 and elem_value < constraints[0]:
            raise ValueError('Illegal value for int configuration element "{}": min value is {}'.format(
                elem_name, constraints[0]))
        if len(constraints) > 1 and elem_value > constraints[1]:
            raise ValueError('Illegal value for int configuration element "{}": max value is {}'.format(
                elem_name, constraints[1]))
        return True

    def _check_elem_str(self, elem_name: str, elem_value: str, constraints: list) -> bool:
        """ Checks the constraints on a configuration element of type 'str'.

        Parameters:
            elem_name : str
                Name of the configuration element.
            elem_value : str
                Value of the element.
            constraints : list
                List of value constraints: [min_length: int, max_length: int, optional].

        Returns:
            bool : constraints check result (True = OK).
        """
        # pylint: disable=no-self-use
        if len(constraints) > 0 and len(elem_value) < constraints[0]:
            raise ValueError('Illegal value for string configuration element "{}": min length is {}'.format(
                elem_name, constraints[0]))
        if len(constraints) > 1 and len(elem_value) > constraints[1]:
            raise ValueError('Illegal value for string configuration element "{}": max length is {}'.format(
                elem_name, constraints[1]))
        return True

    def _check_elem_list(self, elem_name: str, elem_value: list, constraints: list) -> bool:
        """ Checks the constraints on a configuration element of type 'list'.

        Parameters:
            elem_name : str
                Name of the configuration element.
            elem_value : list
                Value of the element.
            constraints : list
                List of value constraints: [min_length: int, max_length: int, optional].

        Returns:
            bool : constraints check result (True = OK).
        """
        # pylint: disable=no-self-use
        if len(constraints) > 0 and len(elem_value) < constraints[0]:
            raise ValueError('Illegal value for list configuration element "{}": min length is {}'.format(
                elem_name, constraints[0]))
        if len(constraints) > 1 and len(elem_value) > constraints[1]:
            raise ValueError('Illegal value for list configuration element "{}": max length is {}'.format(
                elem_name, constraints[1]))
        return True

    def _check_elem_dict(self, elem_name: str, elem_value: dict, constraints: list) -> bool:
        """ Checks the constraints on a configuration element of type 'dict'.

        Parameters:
            elem_name : str
                Name of the configuration element.
            elem_value : dict
                Value of the element.
            constraints : list
                List of value constraints (names of mandatory elements).

        Returns:
            bool : constraints check result (True = OK).
        """
        # pylint: disable=no-self-use
        for mandatory_elem in constraints:
            if mandatory_elem not in elem_value:
                raise ValueError(
                    'Illegal value for dict configuration element "{}": missing sub-element "{}"'.format(
                        elem_name, mandatory_elem))
        return True

    def _check_config_elem(self, elem_name: str, type_: type, constraints = None) -> bool:
        """ Checks the dictionary for a mandatory element, its type, and optionally its value range.

        Parameters:
            elem_name : str
                Name of the element to be checked.
            type_ : type
                Type the value of the element in the dictionary must be instance of.
            constraints : list
                Array containing 1 or 2 elements for value range checking:
                    Element type is str:  [min_length: int, max_length: int, optional]
                    Element type is int:  [min_value: int, max_value: int, optional]
                    Element type is list: [min_length: int, max_length: int, optional]
                    Element type is dict: all constraints in dict
        """
        if elem_name not in self._config_dict:
            raise KeyError('Missing configuration element: "{}"'.format(elem_name))
        elem_value = self._config_dict[elem_name]
        if not isinstance(elem_value, type_) :
            raise TypeError('Illegal type for configuration element "{}": "{}"'.format(elem_name, type(elem_value)))
        if constraints is None:
            return True
        if type_ is str:
            return self._check_elem_str(elem_name, elem_value, constraints)
        if type_ is int:
            return self._check_elem_int(elem_name, elem_value, constraints)
        if type_ is list:
            return self._check_elem_list(elem_name, elem_value, constraints)
        if type_ is dict:
            return self._check_elem_dict(elem_name, elem_value, constraints)
        return True

    def __getitem__(self, config_key) -> Any:
        """ Accessor for elements of the configuration dictionary.

        Parameters:
            config_key : str
                Name of a configuration element to be retrieved.
        """
        if config_key in self._config_dict:
            return self._config_dict[config_key]
        raise KeyError('Undefined configuration element: "{}"'.format(config_key))



class IotSensor:
    """ Base class for an IOT sensor.

    Attributes:
        _logger : logging.Logger
            Logger to be used.
        _config : IotSensorConfig
            Configuration settings for the sensor.
        _sensor_type : str
            Type of the sensor.
        _sensor_id : str
            Unique identification of the sensor.
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
    def __init__(self, config_dict: dict, logger: logging.Logger):
        """ Constructor.

        Parameters:
            config_dict : dict
                Configuration settings for the sensor.
            logger : logging.Logger
                Logger to be used.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self._logger = logger
        self._config = IotSensorConfig(config_dict)
        self._sensor_type = self._config['sensor_type']
        self._sensor_id = self._config['sensor_id']
        self._last_msmt_time = None
        self._last_msmt_value = None
        self.msmt_unit = None
        self._logger.debug('{}: Initialized sensor ID = "{}", TYPE = "{}"'.format(
            mth_name, self._sensor_id, self._sensor_type))

    def measure(self, hardware_input: iot_hardware.DigitalInputProbe) -> SensorMeasurement:
        """ Calculates a measured value from an input probe and returns it as a SensorMeasurement object.

        Parameters:
            hardware_input : DigitalInputProbe
                Input probe received from a hardware element that contains the base value for the measurement.

        Returns:
            SensorMeasurement : Result of the measurement calculation.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self._logger.debug('{}(hw_value = {}, hw_voltage = {:.5f})'.format(
            mth_name, hardware_input.value, hardware_input.voltage))
        m_res = SensorMeasurement(self._sensor_id, self._sensor_type)
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
    def __init__(self, config_dict: dict, logger: logging.Logger):
        """ Constructor

        Parameters:
            config_dict : dict
                Configuration settings for the sensor.
            logger : logging.Logger
                Logger to be used.
        """
        super().__init__(config_dict, logger)
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
        humidity = 100.0 * (30000.0 - hw_value) / 30000.0
        return (humidity, self.msmt_unit)
