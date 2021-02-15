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
import wp_queueing
import iot_handler_base
import iot_msg_input
import iot_sensor_base


class IotSensorHandler(iot_handler_base.IotHandlerBase):
    """ Handler for an IOT sensor.

    Attributes:
        logger : logging.Logger
            Logger to be used.
        sensor_id : str
            Unique identifier of the sensor.
        sensor_type : str
            Type of the sensor.
        _sensor : iot_sensor_base.IotSensor
            Reference to the controlled IOT sensor element.

    Properties:
        sensor_id : str
            Getter for the unique identifier of the controlled sensor.
        sensor_type : str
            Getter for the type (model) of the controlled sensor.
        _output_topic: str
            Getter for the topic string to be used for publishing sensor measurements.

    Methods:
        IotSensorHandler()
            Constructor
        polling_timer_event : None
            Indicates that the polling timer has expired. Overloaded method from super() class.
        message : None
            Handle an incoming message containing a hardware probe.
    """
    def __init__(self, sensor: iot_sensor_base.IotSensor, logger: logging.Logger,
                 mqtt_data: tuple, mqtt_input: tuple, mqtt_health: tuple = None,
                 health_check_interval: int = 0):
        """ Constructor.

        Parameters:
            sensor : iot_sensor_base.IotSensor
                Sensor object to be controlled by the sensor handler.
            logger : logging.Logger
                Logger to be used by the handler and the sensor.
            mqtt_data : tuple
                MQTT broker information (broker session and topic) for publishing measurement
                messages.
            mqtt_input : tuple
                MQTT broker information (broker session and topic) for receiving input probe
                messages from the associated hardware device.
            mqtt_health : tuple, optional
                MQTT broker information (broker session and topic) for publishing health check
                messages.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self._sensor = sensor
        self.logger = logger
        self.logger.debug(f'{mth_name}: sensor_id="{self.sensor_id}", sensor_type="{self.sensor_type}"')
        super().__init__(1, health_check_interval if health_check_interval > 0 else 900,
                         mqtt_data = mqtt_data, mqtt_input = mqtt_input, mqtt_health = mqtt_health)
        if self.mqtt_input is not None:
            self.mqtt_input[0].owner = self
            self.mqtt_input[0].topics = [(self.mqtt_input[1], 0)]

    @property
    def sensor_id(self) -> str:
        """ Getter for the unique identifier of the controlled sensor. """
        return None if self._sensor is None else self._sensor.sensor_id

    @property
    def sensor_type(self) -> str:
        """ Getter for the type (model) of the controlled sensor. """
        return None if self._sensor is None else self._sensor.sensor_type

    def polling_timer_event(self):
        """ Indicates that the polling timer has expired and the MQTT broker must be queried for new
            messages.
        """
        super().polling_timer_event()
        self.mqtt_input[0].receive()

    def message(self, msg: wp_queueing.QueueMessage) -> None:
        """ Handle an incoming message containing a hardware probe.

        Parameters:
            msg : wp_queueing.QueueMessage
                Message received from the message broker containing the digital input probe.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.logger.debug(f'{mth_name}: "{str(msg)}"')
        if self.mqtt_data is None or self.mqtt_data[1] is None:
            return
        if msg.msg_topic != self.mqtt_input[1]:
            self.logger.debug(f'{mth_name}: unexpected topic "{msg.msg_topic}"; expected "{self.mqtt_input[1]}"')
            return
        probe = iot_msg_input.InputProbe()
        try:
            probe.from_dict(msg.msg_payload)
        except TypeError as except_:
            self.logger.error(f'{mth_name}: {str(except_)}')
            return
        except ValueError as except_:
            self.logger.error(f'{mth_name}: {str(except_)}')
            return
        # If the probe is too old, we discard it.
        probe_age = (datetime.now() - probe.probe_time).total_seconds()
        if probe_age > 10:
            self.logger.warning('{}: topic="{}", msg_id="{}"'.format(mth_name, msg.msg_topic, msg.msg_id))
            self.logger.warning('{}: probe age = {:.0f} seconds > 10, message discarded'.format(mth_name, probe_age))
            return
        msmt = self._sensor.measure(probe)
        out_msg = wp_queueing.QueueMessage(self._output_topic)
        out_msg.msg_payload = msmt
        self.mqtt_data[0].publish_single(msmt)

    @property
    def _output_topic(self) -> str:
        """ Getter for the topic string to be used for publishing sensor measurements. """
        return f'{self.mqtt_data[1]}/{self.sensor_id}'
