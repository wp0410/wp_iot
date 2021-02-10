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
import json
import wp_queueing
import iot_handler_base
import iot_msg_input
import iot_hardware_device
import iot_hardware_input

class IotOutputDeviceHandler(iot_handler_base.IotHandlerBase):
    """ Handler for an output hardware device.

    Attributes:
        logger : logging.Logger
            Logger to be used.
        _device : iot_hardware_input.InputDevice
            Input device driver that handles the connected hardware component.

    Properties:
        device_id : str
            Getter for the unique identifier of the controlled input device.
        device_type : str
            Getter for the device type of the controlled input device.
        device_model : str
            Getter for the device model of the controlled input device.

    Methods:
        InputDeviceHandler
            Constructor.
    """
    def __init__(self, device: iot_hardware_device.IotHardwareDevice, logger: logging.Logger,
                 polling_interval: int, mqtt_input: tuple, mqtt_health: tuple = None,
                 health_check_interval: int = 0):
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self._device = device
        self.logger = logger
        self.logger.debug('{}: device_id="{}", device_type="{}", model="{}"'.format(
            mth_name, self.device_id, self.device_type, self.device_model))
        super().__init__(polling_interval, health_check_interval, mqtt_input = mqtt_input, mqtt_health = mqtt_health)

    @property
    def device_id(self) -> str:
        """ Getter for the unique identifier of the controlled input device. """
        if self._device is None:
            return None
        return self._device.device_id

    @property
    def device_type(self) -> str:
        """ Getter for the device type of the controlled input device. """
        if self._device is None:
            return None
        return self._device.device_type

    @property
    def device_model(self) -> str:
        """ Getter for the device model of the controlled input device. """
        if self._device is None:
            return None
        return self._device.model


class IotInputDeviceHandler(iot_handler_base.IotHandlerBase):
    """ Handler for an input hardware device.

    Attributes:
        logger : logging.Logger
            Logger to be used.
        _device : iot_hardware_input.InputDevice
            Input device driver that handles the connected hardware component.

    Properties:
        device_id : str
            Getter for the unique identifier of the controlled input device.
        device_type : str
            Getter for the device type of the controlled input device.
        device_model : str
            Getter for the device model of the controlled input device.

    Methods:
        InputDeviceHandler
            Constructor.
    """
    def __init__(self, device: iot_hardware_input.IotInputDevice, logger: logging.Logger,
                 polling_interval: int, mqtt_data: tuple, mqtt_health: tuple = None,
                 health_check_interval: int = 0):
        """ Constructor.

        Parameters:
            device : iot_hardware_input.IotInputDevice
                Device object to be controlled by the IotInputDeviceHandler instance.
            logger : logging.Logger
                Logger for log messages.
            polling_interval : int
                Interval in seconds to poll the input device.
            mqtt_data : tuple
                MQTT broker information (broker session and topic) for publishing input probe
                messages.
            mqtt_health : tuple, optional
                MQTT broker information (broker session and topic) for publishing health check
                messages.
            health_check_interval : int, optional
                Interval in seconds for health checking of the input device.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self._device = device
        self.logger = logger
        self.logger.debug('{}: device_id="{}", device_type="{}", model="{}"'.format(
            mth_name, self.device_id, self.device_type, self.device_model))
        super().__init__(polling_interval, health_check_interval, mqtt_data = mqtt_data, mqtt_health = mqtt_health)

    @property
    def device_id(self) -> str:
        """ Getter for the unique identifier of the controlled input device. """
        if self._device is None:
            return None
        return self._device.device_id

    @property
    def device_type(self) -> str:
        """ Getter for the device type of the controlled input device. """
        if self._device is None:
            return None
        return self._device.device_type

    @property
    def device_model(self) -> str:
        """ Getter for the device model of the controlled input device. """
        if self._device is None:
            return None
        return self._device.model

    def _data_topic(self, probe: iot_msg_input.InputProbe) -> str:
        """ Constructs the MTTQ message topic for a MQTT message to be published to the broker.

        Parameters:
            probe : probe result generated by the underlying hardware device.

        Returns:
            str : MQTT topic.
        """
        return "{}/{}/{}".format(self.mqtt_data[1], self.device_id, probe.channel_no)

    def _health_topic(self) -> str:
        return "{}/{}".format(self.mqtt_health[1], self.device_id)

    def polling_timer_event(self) -> None:
        """ Indicates that the polling timer has expired and the underlying device must be probed.
        """
        super().polling_timer_event()
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.logger.debug(mth_name)
        if self._device is None or self.mqtt_data is None:
            return
        poll_result = self._device.probe()
        for probe in poll_result:
            msg = wp_queueing.QueueMessage(self._data_topic(probe))
            msg.msg_payload = probe
            self.mqtt_data[0].publish_single(msg)

    def health_timer_event(self) -> None:
        """ Indicates the the health check timer has expired and health check information must be published. """
        super().health_timer_event()
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.logger.debug(mth_name)
        if self._device is None or self.mqtt_health is None:
            return
        health_result = self._device.check_health()
        msg = wp_queueing.QueueMessage(self._health_topic())
        msg.msg_payload = health_result
        self.mqtt_health[0].publish_single(msg)
        self.logger.debug('{}: publish "{}"'.format(mth_name, json.dumps(msg.msg_payload)))
