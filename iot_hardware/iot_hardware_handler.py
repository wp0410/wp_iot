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
from typing import Any
import inspect
import logging
import json
from datetime import datetime
import wp_queueing
import iot_handler_base
import iot_msg_input
import iot_msg_output
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
        IotOutputDeviceHandler
            Constructor.
        polling_timer_event : None
            Indicates that the polling timer has expired and the MQTT broker must be queried for new
            messages.
        message : None
            Handle an incoming message containing an output command.
    """
    def __init__(self, device: iot_hardware_device.IotHardwareDevice, logger: logging.Logger,
                 polling_interval: int, mqtt_input: tuple, mqtt_health: tuple = None,
                 health_check_interval: int = 0):
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self._device = device
        self.logger = logger
        self.logger.debug('{}: device_id="{}", device_type="{}", model="{}"'.format(
            mth_name, self.element_id, self.element_type, self.element_model))
        super().__init__(polling_interval, health_check_interval, mqtt_input = mqtt_input, mqtt_health = mqtt_health)
        if self.mqtt_input is not None:
            self.mqtt_input[0].owner = self
            self.mqtt_input[0].topics = [(self.mqtt_input[1], 0)]

    @property
    def element_id(self) -> str:
        """ Getter for the unique identifier of the controlled input device. """
        if self._device is None:
            return None
        return self._device.device_id

    @property
    def element_type(self) -> str:
        """ Getter for the device type of the controlled input device. """
        if self._device is None:
            return None
        return self._device.device_type

    @property
    def element_model(self) -> str:
        """ Getter for the device model of the controlled input device. """
        if self._device is None:
            return None
        return self._device.model

    def polling_timer_event(self):
        """ Indicates that the polling timer has expired and the MQTT broker must be queried for new
            messages.
        """
        super().polling_timer_event()
        self.mqtt_input[0].receive()

    def message(self, msg: wp_queueing.QueueMessage) -> None:
        """ Handle an incoming message containing an output command.

        Parameters:
            msg : wp_queueing.QueueMessage
                Message received from the message broker containing the output data.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.logger.debug(f'{mth_name}: "{str(msg)}"')
        if self._device is None:
            return
        # if msg.msg_topic != self.mqtt_input[1]:
        #     self.logger.debug(f'{mth_name}: unexpected topic "{msg.msg_topic}"; expected "{self.mqtt_input[1]}"')
        #     return
        output_msg = iot_msg_output.OutputData()
        try:
            output_msg.from_dict(msg.msg_payload)
        except TypeError as except_:
            self.logger.error(f'{mth_name}: {str(except_)}')
            return
        except ValueError as except_:
            self.logger.error(f'{mth_name}: {str(except_)}')
            return
        # If the output command is too old, we discard it.
        output_age = (datetime.now() - output_msg.output_time).total_seconds()
        if output_age > 10:
            self.logger.warning(f'{mth_name}: topic="{msg.msg_topic}", msg_id="{msg.msg_id}"')
            self.logger.warning(f'{mth_name}: state_age={output_age:.2f} > 10 ==> message discarded')
            return
        self.process_output(output_msg.output_port, output_msg.output_data)

    def process_output(self, output_port: str, output_data: Any):
        """ Process the data associated with the received output message. This will output the received
            data according to the type of output.

        Parameters:
            output_port : str
                Output port to send the output data to.
            output_data : Any
                The data to send to the output device.
        """


class IotOutputPinDeviceHandler(IotOutputDeviceHandler):
    """ Handler for an output hardware device allowing for switching dedicated ports on and off.

    Attributes:
        _last_timer_event : datetime
            Date and time when last timer event was triggered.
        _output_timers: dict
            Dictionary containing the timers for re-setting output ports.

    Methods:
        IotOutputStateDeviceHandler:
            Constructor.
        process_output : None
            Method called when a message from the MQTT broker is received, to process the
            requested output operation.
    """
    def __init__(self, device: iot_hardware_device.IotHardwareDevice, logger: logging.Logger,
                 mqtt_input: tuple, mqtt_health: tuple = None, health_check_interval: int = 0):
        """ Constructor. """
        super().__init__(device, logger, 1, mqtt_input, mqtt_health, health_check_interval)

    def process_output(self, output_port: str, output_data: Any):
        """ Process the data associated with the received output message. This will output the received
            data according to the type of output.

        Parameters:
            output_port : str
                Output port to send the output data to.
            output_data : Any
                The data to send to the output device.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        super().process_output(output_port, output_data)
        if self._device is None:
            return
        target_state = int(output_data)
        self.logger.debug(f'{mth_name}: port="{output_port}", switch_to={target_state}')
        self._device.switch_to_state(output_port, target_state)


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
            mth_name, self.element_id, self.element_type, self.element_model))
        super().__init__(polling_interval, health_check_interval, mqtt_data = mqtt_data, mqtt_health = mqtt_health)

    @property
    def element_id(self) -> str:
        """ Getter for the unique identifier of the controlled input device. """
        if self._device is None:
            return None
        return self._device.device_id

    @property
    def element_type(self) -> str:
        """ Getter for the device type of the controlled input device. """
        if self._device is None:
            return None
        return self._device.device_type

    @property
    def element_model(self) -> str:
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
        return "{}/{}/{}".format(self.mqtt_data[1], self.element_id, probe.channel_no)

    def _health_topic(self) -> str:
        return "{}/{}".format(self.mqtt_health[1], self.element_id)

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
