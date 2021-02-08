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
import iot_sensor


class IotSensorHandler(iot_handler_base.IotHandlerBase):
    """ Handler for an IOT sensor.

    Attributes:
        logger : logging.Logger
            Logger to be used.
        sensor_id : str
            Unique identifier of the sensor.
        sensor_type : str
            Type of the sensor.
        _sensor : iot_sensor.IotSensor
            Reference to the controlled IOT sensor element.

    Properties:
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
    # pylint: disable=too-many-instance-attributes
    def __init__(self, sensor_config: dict, logger: logging.Logger):
        """ Constructor.

        Parameters:
            config_dict : dict
                Dictionary containing the configuration settings for the handler and the sensor.
            logger : logging.Logger
                Logger to be used by the handler and the sensor.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.sensor_id = sensor_config['sensor_id']
        self.sensor_type = sensor_config['sensor_type']
        self.logger = logger
        self.logger.debug(f'{mth_name}: sensor_id="{self.sensor_id}", sensor_type="{self.sensor_type}"')

        data_topic = None
        input_topic = None
        health_topic = None
        if 'data_topic' in sensor_config:
            data_topic = sensor_config['data_topic']
        if 'input_topic' in sensor_config:
            input_topic = sensor_config['input_topic']
        if 'health_topic' in sensor_config:
            health_topic = sensor_config['health_topic']

        super().__init__(sensor_config['polling_interval'],
                         min(sensor_config['polling_interval'] * 30, 300),
                         data_topic = data_topic, input_topic = input_topic, health_topic = health_topic)

        if self.sensor_type == 'KYES516':
            self._sensor = iot_sensor.IotSensorHumKYES516(sensor_config, logger)
        else:
            self._sensor = None

    def polling_timer_event(self):
        """ Indicates that the polling timer has expired and the MQTT broker must be queried for new
            messages.
        """
        super().polling_timer_event()
        if self.input_topic is not None and isinstance(self.input_topic, tuple):
            self.input_topic[1].receive()

    def message(self, msg: wp_queueing.QueueMessage) -> None:
        """ Handle an incoming message containing a hardware probe.

        Parameters:
            msg : wp_queueing.QueueMessage
                Message received from the message broker containing the digital input probe.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.logger.debug('{}: topic="{}", msg_id="{}"'.format(mth_name, msg.msg_topic, msg.msg_id))
        if msg.msg_topic != self.input_topic[0]:
            self.logger.debug(f'{mth_name}: unexpected topic "{msg.msg_topic}"; expected "{self.input_topic[0]}"')
            return
        if self.data_topic is None or self.data_topic[1] is None:
            return
        probe = iot_msg_input.InputProbe("UNDEFINED", "UNDEFINED", None, None)
        try:
            probe.from_dict(msg.msg_payload)
        except TypeError as except_:
            self.logger.error(f'{mth_name}: {str(except_)}')
            return
        except ValueError as except_:
            self.logger.error(f'{mth_name}: {str(except_)}')
            return
        # If the probe is too old, we discard it.
        tdelta = datetime.now() - probe.probe_time
        probe_age = tdelta.days * 86400 + tdelta.seconds
        if probe_age > 30:
            self.logger.warning('{}: topic="{}", msg_id="{}"'.format(mth_name, msg.msg_topic, msg.msg_id))
            self.logger.warning('{}: probe age = {}, message discarded'.format(mth_name, probe_age.seconds))
            return
        msmt = self._sensor.measure(probe)
        out_msg = wp_queueing.QueueMessage(self._output_topic)
        out_msg.msg_payload = msmt
        self.data_topic[1].publish_single(msmt)

    @property
    def _output_topic(self) -> str:
        """ Getter for the topic string to be used for publishing sensor measurements. """
        return f'{self.data_topic[0]}/{self.sensor_id}'
