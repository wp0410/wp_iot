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
import wp_queueing
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn

class DigitalInputProbe(wp_queueing.IConvertToDict):
    """ Result of reading an input channel of a Digitial Input device.

    Attributes:
        device_id : str
            Unique name or identifier of the Digital Input device.
        device_type : str
            Type of the digital input device.
        probe_time : datetime
            Timestamp of the sensor probe.
        channel_no : int
            Number of the Digital Input channel read.
        value : int
            Read Digital Input value.
        voltage : float
            Read input voltage.

    Methods:
        DigitalInputProbe()
            Constructor.
        to_dict : dict
            Converts the Digital Input probe into a dictionary.
    """
    def __init__(self, device_type, device_id, probe_time, channel_no, value = 0, voltage = 0.0):
        """ Constructor.

        Parameters:
            device_type : str
                Type of the digital input device.
            device_id : str
                Unique name or identifier of the Digital Input device.
            probe_time : datetime
                Timestamp of the sensor probe.
            channel_no : int
                Number of the Digital Input channel read.
            value : int, optional
                Read Digital Input value.
            voltage : float, optional
                Read input voltage.
        """
        self.device_id = device_id
        self.device_type = device_type
        self.probe_time = probe_time
        self.channel_no = channel_no
        self.value = value
        self.voltage = voltage

    def to_dict(self) -> dict:
        """ Converts the Digital Input probe into a dictionary.

        returns:
            dict : The attributes of the object as members of a dictionary.
        """
        return {
            'class': 'DigitalInputProbe',
            'device_type': self.device_type,
            'device_id': self.device_id,
            'probe_time': self.probe_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
            'channel_no': self.channel_no,
            'value': self.value,
            'voltage': self.voltage
        }


class DigitalInputHealth(wp_queueing.IConvertToDict):
    """ Data object to report the health status of a digital input device.

    Attributes:
        device_id : str
            Unique name or identifier of the Digital Input device.
        device_type : str
            Type of the digital input device.
        health_time : datetime
            Timestamp of the health check.
        health_status : int
            Health status of the input device.
        last_probe_time : datetime
            Timestamp of last probe request.
        num_probe_total : int
            Number of probe requests.
        num_probe_detail : list
            List containing the number of successfully created probe results per input channel.

    Methods:
        DigitalInputHealth():
            Constructor
        to_dict : dict
            Converts the object to a dictionary.
    """
    def __init__(self, device_type, device_id, health_status, health_time = None):
        """ Constructor.

        Parameters:
            device_type : str
                Type of the digital input device.
            device_id : str
                Unique name or identifier of the Digital Input device.
            health_status : int
                Health status of the input device.
            health_time : datetime, optional
                Timestamp of the health check.
        """
        self.device_type = device_type
        self.device_id = device_id
        if health_time is None:
            self.health_time = datetime.now()
        else:
            self.health_time = health_time
        self.health_status = health_status
        self.last_probe_time = None
        self.num_probe_total = 0
        self.num_probe_detail = None

    def to_dict(self) -> dict:
        """ Converts the object to a dictionary.

        Returns:
            Contents of the object as dictionary.
        """
        return {
            'class': 'DigitalInputHealth',
            'device_type': self.device_type,
            'device_id': self.device_id,
            'health_time': self.health_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
            'health_status': self.health_status,
            'last_probe_time': self.last_probe_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
            'num_probe_total': self.num_probe_total,
            'num_probe_detail': self.num_probe_detail
        }



class DigitalInputDevice:
    """ Base class for digital input components.

    Attributes:
        logger : logging.Logger
            Logger to be used.
        last_probe_time : datetime
            Timestamp of most recent probing of the digital input channels.
        num_probes : int
            Number of probe requests executed.
        device_type : str
            Type of device. Value is 'ADS1115'.
        device_id : str
            Unique name or identifier of the Digital Input device.

    Methods:
        DigitalInputDevice()
            Constructor
        probe : list
            Returns an empty list.
        check_health : dict
            Returns an empty dictionary.
    """
    def __init__(self, config_dict, logger):
        """ Constructor.

        Parameters:
            config_dict : dict
                Dictionary containing the configuration settings for accessing the ADS1115 component. The
                following elements are mandatory:

                'device_id' : Unique name or identifier of the Digital Input device.
            logger : logging.Logger
                Logger to be used.
        """
        self.logger = logger
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.logger.debug(mth_name)
        self.device_type = "DIGITAL_IN"
        self.last_probe_time = None
        self.num_probes = 0
        try:
            config_elem = 'device_id'
            self.device_id = config_dict[config_elem]
        except KeyError as key_except:
            self.logger.error('%s: Exception "%s"', mth_name, str(key_except))
            self.logger.error('%s: Missing configuration element: "%s"', mth_name, config_elem)
            raise key_except

    def probe(self) -> list:
        """ Returns an empty list. """
        # pylint: disable=no-self-use
        return []

    def check_health(self) -> dict:
        """ Returns an empty dictionary. """
        # pylint: disable=no-self-use
        return dict()



class DigitalInputADS1115(DigitalInputDevice):
    """ Class for handling a ADS1115 Digital Input hardware component attached to the I2C bus.

    Attributes:
        _bus_id : int
            Number of the I2C bus to which the ADS1115 component is connected (0 or 1).
        _bus_address : int
            Address of the ADS1115 component on the I2C bus.
        _active_ports : list
            List of active port numbers.

    Methods:
        DigitalInputADS1115()
            Constructor.
        probe : list
            Reads the active digital input channels and returns the result as a list of DigitalInputProbe
            objects.
        check_health : dict
            Performs a health check and returns information about the current status of the ADS1115
            component.
    """
    def __init__(self, config_dict, logger):
        """ Constructor.

        Parameters:
            config_dict : dict
                Dictionary containing the configuration settings for accessing the ADS1115 component. The
                following elements are mandatory:

                'device_id' : Unique name or identifier of the Digital Input device.
                'i2c': Dictionary containing the I2C bus settings:
                    'bus_id' : Number of the I2C bus to which the component is connected.
                    'bus_address': Address of the ADS1115 component on the I2C bus.
                'active_ports': List of active port numbers.

                Example:
                    {'device_id': 'DigitalIn.1', 'i2c': {'bus': 0, 'address': 64}, 'active_ports': [0, 1]}
            logger : logging.Logger
                Logger to be used.
        """
        super().__init__(config_dict, logger)
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.logger.debug(mth_name)
        self.device_type = 'ADS1115'
        self.num_probe_list = [0, 0, 0, 0]
        try:
            config_elem = 'i2c'
            i2c_settings = config_dict[config_elem]
            config_elem = 'bus'
            self._bus_id = i2c_settings[config_elem]
            config_elem = 'address'
            self._bus_address = i2c_settings[config_elem]
            config_elem = 'active_ports'
            self._active_ports = config_dict[config_elem]
        except KeyError as key_except:
            self.logger.error('{}: Exception "{}"'.format(mth_name, str(key_except)))
            self.logger.error('{}: Missing configuration element: "{}"'.format(mth_name, config_elem))
            raise key_except
        self.logger.debug('{}: Initialized Hardware Element:'.format(mth_name))
        self.logger.debug('   deviceId:    {}'.format(self.device_id))
        self.logger.debug('   bus_id:      {}'.format(self._bus_id))
        self.logger.debug('   bus_address: {}'.format(self._bus_address))

    def probe(self) -> list:
        """ Reads the active digital input channels and returns the result as a list of DigitalInputProbe
            objects.

        Returns:
            list : List of DigitialInputProbe objects containing the probing results for the active
                   input channels.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.logger.debug(mth_name)
        probe_result = []
        probe_time = datetime.now()
        i2c_bus = busio.I2C(board.SCL, board.SDA)
        ads_handle = ADS.ADS1115(i2c_bus, self._bus_address)
        for channel_number in self._active_ports:
            ads_channel = AnalogIn(ads_handle, channel_number)
            val_read = ads_channel.value
            volt_read = ads_channel.voltage
            self.logger.debug('{}: channel = {}: value = {}, voltage = {}'.format(
                mth_name, channel_number, val_read, volt_read))
            p_res = DigitalInputProbe(self.device_type, self.device_id, probe_time, channel_number)
            p_res.value = val_read
            p_res.voltage = volt_read
            probe_result.append(p_res)
            self.num_probe_list[channel_number] += 1
        i2c_bus.deinit()
        self.num_probes += 1
        self.last_probe_time = probe_time
        return probe_result

    def health(self) -> DigitalInputHealth:
        """ Performs a health check and returns information about the current status of the ADS1115
            component.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.logger.debug(mth_name)
        h_res = DigitalInputHealth(self.device_type, self.device_id, 0)
        h_res.last_probe_time = self.last_probe_time
        h_res.num_probe_total = self.num_probes
        h_res.num_probe_detail = self.num_probe_list
        return h_res
