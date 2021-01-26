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
import wp_configuration
import iot_base
import iot_hardware
import iot_sensor


class IotSensorConfig(wp_configuration.DictConfigWrapper):
    """ Class for validation of configuration setttings for a sensor handler and the associated
        sensor.

    Methods:
        IotSensorConfig():
            Constructor.
    """
    def __init__(self, config_dict: dict):
        """ Constructor.

        Parameters:
            config_dict : dict
                Dictionary containing the configuration settings for the sensor handler and the
                associated sensor.
        """
        super().__init__(config_dict)
        self.value_error(self.mandatory_str('sensor_id', [6]))
        self.value_error(self.mandatory_str('sensor_type', [6]))
        self.value_error(self.mandatory_dict('hardware', ['id', 'channel']))
        self.value_error(self.mandatory_dict('topics', ['input_prefix', 'data_prefix']))
        self.optional_int('polling_interval', 5)


class IotSensorHandler(iot_base.IotHandlerBase):
    """ Handler for an IOT sensor.

    Attributes:
        _logger : logging.Logger
            Logger to be used.
        _config : iot_sensor.IotSensorConfig
            Configuration settings for the handler and the IOT sensor.
        _sensor_id : str
            Unique identifier of the sensor.
        _sensor_type : str
            Type of the sensor.
        _input_topic : str
            MQTT topic to subscribe to for InputProbe messages from hardware elements.
        _output_topic: str
            MQTT topic for publishing the sensor measurements.
        _sensor : iot_sensor.IotSensor
            Reference to the controlled IOT sensor element.
        _publisher : wp_queueing.MQTTProducer
            Open connection to an MQTT broker for publishing sensor measurements.
        _consumer : wp_queueing.MQTTConsumer
            Open connection to an MQTT broker for receiving hardware probes.

    Methods.
        IotSensorHandler()
            Constructor
        message : None
            Handle an incoming message containing a hardware probe.
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, config_dict: dict, logger: logging.Logger,
                 consumer: wp_queueing.MQTTConsumer, publisher: wp_queueing.MQTTProducer):
        """ Constructor

        Parameters:
            config_dict : dict
                Dictionary containing the configuration settings for the handler and the sensor.
            logger : logging.Logger
                Logger to be used by the handler and the sensor.
            consumer : wp_queueing.MQTTConsumer
                 Open connection to an MQTT broker for receiving hardware probes.
            publisher : wp_queueing.MQTTProducer
                Open connection to an MQTT broker for publishing sensor measurements.
        """
        self._logger = logger
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self._logger.debug(mth_name)
        self._config = IotSensorConfig(config_dict)
        super().__init__(self._config['polling_interval'])
        self._sensor_id = self._config['sensor_id']
        self._sensor_type = self._config['sensor_type']
        topics = self._config['topics']
        hw_settings = self._config['hardware']
        self._input_topic = '{}/{}/{}'.format(topics['input_prefix'], hw_settings['id'], hw_settings['channel'])
        self._output_topic = '{}/{}'.format(topics['data_prefix'], self._sensor_id)

        if self._sensor_type == 'KYES516':
            self._sensor = iot_sensor.IotSensorHumKYES516(config_dict, logger)
        else:
            self._sensor = None

        self._publisher = publisher
        self._consumer = consumer

    def polling_timer_event(self):
        """ Indicates that the polling timer has expired and the MQTT broker must be queried for new
            messages.
        """
        super().polling_timer_event()
        self._consumer.receive()

    def message(self, msg: wp_queueing.QueueMessage) -> None:
        """ Handle an incoming message containing a hardware probe.

        Parameters:
            msg : wp_queueing.QueueMessage
                Message received from the message broker containing the digital input probe.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self._logger.debug('{}: topic="{}", msg_id="{}"'.format(mth_name, msg.msg_topic, msg.msg_id))
        if msg.msg_topic != self._input_topic:
            return
        probe = iot_hardware.DigitalInputProbe("UNDEFINED", "UNDEFINED", None, None)
        try:
            probe.from_dict(msg.msg_payload)
        except TypeError as except_:
            self._logger.error('{}: {}'.format(mth_name, str(except_)))
            return
        except ValueError as except_:
            self._logger.error('{}: {}'.format(mth_name, str(except_)))
            return
        # If the probe is too old, we discard it.
        tdelta = datetime.now() - probe.probe_time
        probe_age = tdelta.days * 86400 + tdelta.seconds
        if probe_age > 30:
            self._logger.warning('{}: topic="{}", msg_id="{}"'.format(mth_name, msg.msg_topic, msg.msg_id))
            self._logger.warning('{}: probe age = {}, message discarded'.format(mth_name, probe_age.seconds))
            return
        msmt = self._sensor.measure(probe)
        out_msg = wp_queueing.QueueMessage(self._output_topic)
        out_msg.msg_payload = msmt
        self._publisher.publish_single(msmt)
