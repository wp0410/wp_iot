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
import wp_queueing
import wp_configuration
import iot_hardware_digital_input as iot_hw


class IotHardwareConfig(wp_configuration.wp_configuration.DictConfigWrapper):
    """ Class for validation of configuration settings for a hardware handler and the associated
        hardware element.

    Methods:
        IotSensorConfig():
            Constructor.
    """
    def __init__(self, config_dict: dict):
        """ Constructor.

        Parameters:
            config_dict : dict
                Dictionary containing the configuration settings for the hardware handler and the
                associated hardware.
        """
        super().__init__(config_dict)
        self.mandatory_str('device_type', [6])
        self.mandatory_str('device_id', [6])
        self.mandatory_dict('topics', ['data_prefix', 'health_prefix'])
        self.mandatory_int('polling_interval', [1])



class DigitalInputHandler:
    """ Handler for a digital input hardware device (ADS1115).

    Attributes:
        _logger : logging.Logger
            Logger to be used.
        _device_type : str
            Type of the digital input device. Currently allowed values:
                "ADS1115"
        _polling_interval : int
            Interval (in seconds) for polling the digital input device.
        _mqtt_publish : wp_queueing.MQTTProducer
            Producer to publish the polled input values.
        _device : object
            Object class implementing a digital input device.

    Methods:
        DigitalInputHandler
            Constructor.
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, config_dict: dict, logger: logging.Logger, mqtt_publish: wp_queueing.MQTTProducer):
        """ Constructor.

        Parameters:
            config_dict: dict
                Dictionary containing the configuration settings for the hardware device.
            logger : logging.Logger
                Logger to be used by the object.
            mqtt_publish : wp_queueing.MQTTProducer
                Producer to be used to publish the polled values.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self._logger = logger
        self._logger.debug(mth_name)
        self._config = IotHardwareConfig(config_dict)
        self._device_type = config_dict['device_type']
        self._polling_interval = config_dict['polling_interval']
        topic_prefixes = config_dict['topics']
        self._prefix_data = topic_prefixes['data_prefix']
        self._prefix_health = topic_prefixes['health_prefix']

        if self._device_type == 'ADS1115':
            self._device = iot_hw.DigitalInputADS1115(config_dict, logger)
        else:
            self._device = None
        self._mqtt_publish = mqtt_publish
        self._tick_min = -1
        self._tick_sec = -1
        self._polling_timer = -1

    def init_time(self, minutes, seconds) -> None:
        """ Initializes the internal time information and the polling timer.

        Parameters:
            minutes : int
                MIN part of current time.
            seconds : int
                SEC part of current time.
        """
        self._tick_min = minutes
        self._tick_sec = seconds
        tmin = int((self._tick_min * 60 + self._polling_interval) / self._polling_interval)
        tmin *= int(self._polling_interval / 60)
        tsec = 0
        self._polling_timer = tmin * 60 + tsec - self._tick_min * 60 - self._tick_sec

    def time_tick(self, num_sec = 1) -> None:
        """ Reports a number of passed seconds to adjust the internal time information and the polling timer.

        Parameters:
            num_sec : int, optional, default = 1
                Number of seconds passed since most recent time tick.
        """
        self._tick_sec += num_sec
        self._polling_timer -= num_sec
        if self._tick_sec >= 60:
            self._tick_min += int(self._tick_sec / 60)
            self._tick_sec %= 60
        if self._polling_timer <= 0:
            self._polling_timer = self._polling_interval
            self._polling_timer_event()

    def _data_topic(self, probe: iot_hw.DigitalInputProbe) -> str:
        """ Constructs the MTTQ message topic for a MQTT message to be published to the broker.

        Parameters:
            probe : probe result generated by the underlying hardware device.

        Returns:
            str : MQTT topic.
        """
        return "{}/{}/{}".format(self._prefix_data, probe.device_id, probe.channel_no)

    def _health_topic(self) -> str:
        return "{}/{}".format(self._prefix_health, self._device.device_id)

    def _polling_timer_event(self) -> None:
        """ Indicates that the polling timer has expired and the underlying device must be probed.
        """
        if self._device is None:
            return
        poll_result = self._device.probe()
        for probe in poll_result:
            msg = wp_queueing.QueueMessage(self._data_topic(probe))
            msg.msg_payload = probe.to_dict()
            self._mqtt_publish.publish_single(msg)

    def _health_timer_event(self) -> None:
        """ Indicates the the health check timer has expired and health check information must be published. """
        if self._device is None:
            return
        health_result = self._device.health()
        msg = wp_queueing.QueueMessage(self._health_topic())
        msg.msg_payload = health_result.to_dict()
        self._mqtt_publish.publish_single(msg)
