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
from datetime import datetime
from datetime import timedelta

class IotHandlerBase:
    """ A 'handler' is a controlling element for a hardware element, a sensor or an actor.

    Attributes:
        _polling_interval : int
            Interval in seconds for firing the polling event.
        _polling_timer : int
            Number of seconds to wait for the next polling event to be fired.
        _last_tick_tm : datetime
            Timestamp of last 'time_tick' received.

    Methods:
        IotHandlerBase():
            Constructor.
        init_time : None
            Initializes the internal time information and the polling timer.
        time_tick : None
            To be called (in regular intervals) to adjust the internal time information and the polling timer.
        stop : None
            Stops the handler. To clean up internal components, this method must be overloaded in sub-classes.
        polling_timer_event : None
            Indicates that the polling timer has expired. Must be overloaded by sub-classes.
        health_timer_event : None
            Indicates that the health check timer has expird. Must be overloaded in sub-classes.
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, polling_interval: int, health_check_interval: int,
                 mqtt_data: tuple = None, mqtt_input: tuple = None, mqtt_health: tuple = None):
        """ Constructor.

        Parameters:
            polling_interval: int
                Interval in seconds for the invocation of the polling timer event.
            mqtt_data : tuple
                Tuple containing two elements (<broker>, <prefix>), where:
                    <broker>: wp_queueing.MqttProducer
                        Session to a broker for publishing data messages.
                    <prefix>: str
                        Prefix for constructing the topic to which data messages shall be published.
            mqtt_input : tuple
                Tuple containing two elements (<broker>, <prefix>), where:
                    <broker>: wp_queueing.MqttConsumer
                        Session to a broker for subscribing to input messages.
                    <prefix>: str
                        Prefix for constructing the topic to subsribe to for receiving input messages.
            mqtt_health : tuple
                Tuple containing two elements (<broker>, <prefix>), where:
                    <broker>: wp_queueing.MqttProducer
                        Session to a broker for publishing health check messages.
                    <prefix>: str
                        Prefix for constructing the topic to which health check messages shall be published.
        """
        self._polling_interval = polling_interval
        self._polling_timer = -1
        self._health_check_int = health_check_interval
        self._health_check_timer = -1
        self._last_tick_tm = None
        self._stopped = False
        self.mqtt_data = mqtt_data
        self.mqtt_health = mqtt_health
        self.mqtt_input = mqtt_input

    def init_time(self) -> None:
        """ Initializes the internal time information and the polling timer.
        """
        if self._stopped:
            return
        self._last_tick_tm = datetime.now()
        first_ev_time = datetime(self._last_tick_tm.year, self._last_tick_tm.month, self._last_tick_tm.day,
                                 self._last_tick_tm.hour, self._last_tick_tm.minute, 0) + timedelta(seconds = 60)
        self._polling_timer = (first_ev_time - self._last_tick_tm).seconds
        if self._health_check_int > 0:
            self._health_check_timer = self._polling_timer

    def time_tick(self) -> None:
        """ To be called (in regular intervals) to adjust the internal time information and the polling timer.
        """
        if self._stopped:
            return
        cur_tm = datetime.now()
        tick_delta = cur_tm - self._last_tick_tm
        num_sec = tick_delta.seconds
        self._polling_timer -= num_sec
        self._last_tick_tm = cur_tm
        if self._polling_timer <= 0:
            self.polling_timer_event()
        if self._health_check_int > 0:
            self._health_check_timer -= num_sec
            if self._health_check_timer <= 0:
                self.health_timer_event()

    def stop(self) -> None:
        """ Stops the handler. To clean up internal components, this method must be overloaded in sub-classes.
        """
        self._stopped = True

    def polling_timer_event(self):
        """ Indicates that the polling timer has expired. Must be overloaded by sub-classes.
        """
        self._polling_timer = self._polling_interval

    def health_timer_event(self):
        """ Indicates that the health check timer has expird. Must be overloaded in sub-classes.
        """
        self._health_check_timer = self._health_check_int
