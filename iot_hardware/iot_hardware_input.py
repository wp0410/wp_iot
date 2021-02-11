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
import logging
import iot_msg_input
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import iot_hardware_device

class IotInputDevice(iot_hardware_device.IotHardwareDevice):
    """ Base class to handle input devices connected to the host. An InputDevice instance connects to exactly
        one hardware device having hardware sensors connected to its input channels. Upon request, these
        channels will be probed and the result will be returned as InputProbe objects.

    Attributes:
        device_id : str
            Unique name or identifier of the input device.
        device_type : str
            Type of the hardware device. Defaults to "DigitalInput".
        model : str
            Model of the input device. Defaults to "GenericInputDevice".
        logger : logging.Logger
            Logger to be used.
        last_probe_time : datetime
            Timestamp of most recent probing of the digital input channels.
        num_probes : int
            Number of probe requests executed.

    Methods:
        InputDevice()
            Constructor
        probe : list
            Method for probing the active channels of the input device. Must be overloaded in sub-classes for
            specific hardware components.
        check_health : InputHealth
            Hethod for checking the health of the input device. Must be overloaded in sub-classes for specific
            harware components.
    """
    def __init__(self, device_id: str, logger: logging.Logger):
        """ Constructor.

        Parameters:
            device_id : str
                Unique identifier of the input device.
            logger : logging.Logger
                Logger to be used.
        """
        super().__init__(device_id, logger)
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.logger.debug(mth_name)
        self.device_type = "DigitalInput"
        self.model = "GenericInputDevice"
        self.last_probe_time = None
        self.num_probes = 0

    def probe(self) -> list:
        """ Returns an empty list. """
        # pylint: disable=no-self-use
        return []



class DigitalInputADS1115(IotInputDevice):
    """ Class for handling a ADS1115 Digital Input hardware component attached to the I2C bus.

    Attributes:
        device_type : str
            Make/model of the device. Fixed value is "ADS1115".
        i2c_bus_id : int
            Number of the I2C bus to which the ADS1115 component is connected (0 or 1).
        i2c_bus_address : int
            Address of the ADS1115 component on the I2C bus.
        active_ports : list
            List of active port numbers.

    Methods:
        DigitalInputADS1115()
            Constructor.
        probe : list
            Reads the active digital input channels and returns the result as a list of DigitalInputProbe
            objects.
        check_health : InputHealth
            Performs a health check and returns information about the current status of the ADS1115
            component.
    """
    def __init__(self, device_id: str, i2c_bus_id: int, i2c_bus_address: int,
                 active_ports: list, logger: logging.Logger):
        """ Constructor.

        Parameters:
            logger : logging.Logger
                Logger to be used.
        """
        super().__init__(device_id, logger)
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.logger.debug(mth_name)
        self.model = 'ADS1115'
        self.i2c_bus_id = i2c_bus_id
        self.i2c_bus_address = i2c_bus_address
        self.active_ports = active_ports
        self.num_probe_list = [0, 0, 0, 0]
        self.logger.debug('{}: Initialized Hardware Element:'.format(mth_name))
        self.logger.debug('   deviceId:    {}'.format(self.device_id))
        self.logger.debug('   bus_id:      {}'.format(self.i2c_bus_id))
        self.logger.debug('   bus_address: {}'.format(self.i2c_bus_address))

    def probe(self) -> list:
        """ Reads the active digital input channels and returns the result as a list of DigitalInputProbe
            objects.

        Returns:
            list : List of InputProbe objects containing the probing results for the active
                   input channels.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.logger.debug(mth_name)
        probe_result = []
        probe_time = datetime.now()
        i2c_bus = busio.I2C(board.SCL, board.SDA)
        ads_handle = ADS.ADS1115(i2c_bus, address=self.i2c_bus_address)
        for channel_number in self.active_ports:
            ads_channel = AnalogIn(ads_handle, channel_number)
            val_read = ads_channel.value
            volt_read = ads_channel.voltage
            self.logger.debug('{0}: channel = {1}: value = {2}, voltage = {3:.5f}'.format(
                mth_name, channel_number, val_read, volt_read))
            p_res = iot_msg_input.InputProbe(
                device_type = self.model, device_id = self.device_id,
                probe_time = probe_time, channel_no = channel_number)
            p_res.value = val_read
            p_res.voltage = volt_read
            probe_result.append(p_res)
            self.num_probe_list[channel_number] += 1
        i2c_bus.deinit()
        self.num_probes += 1
        self.last_probe_time = probe_time
        return probe_result

    def check_health(self) -> iot_msg_input.InputHealth:
        """ Performs a health check and returns information about the current status of the ADS1115
            component.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.logger.debug(mth_name)
        h_res = iot_msg_input.InputHealth(device_type = self.model, device_id = self.device_id)
        h_res.last_probe_time = self.last_probe_time
        h_res.num_probe_total = self.num_probes
        h_res.num_probe_detail = self.num_probe_list
        self.logger.debug('{}: num_probe_total = {}; num_probe_detail = {}'.format(
            mth_name, h_res.num_probe_total, str(h_res.num_probe_detail)))
        return h_res
