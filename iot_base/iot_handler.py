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
    """
    def __init__(self, polling_interval: int):
        self._polling_interval = polling_interval
        self._polling_timer = -1
        self._last_tick_tm = None

    def init_time(self) -> None:
        """ Initializes the internal time information and the polling timer.
        """
        self._last_tick_tm = datetime.now()
        tmin = int((self._last_tick_tm.minute * 60 + self._polling_interval) / self._polling_interval)
        tmin *= int(self._polling_interval / 60)
        tsec = 0
        self._polling_timer = tmin * 60 + tsec - self._last_tick_tm.minute * 60 - self._last_tick_tm.second

    def time_tick(self) -> None:
        """ To be called (in regular intervals) to adjust the internal time information and the polling timer.
        """
        cur_tm = datetime.now()
        tick_delta = self._last_tick_tm - cur_tm
        num_sec = tick_delta.seconds
        self._polling_timer -= num_sec
        self._last_tick_tm = cur_tm
        if self._polling_timer <= 0:
            self.polling_timer_event()

    def polling_timer_event(self):
        """ Indicates that the polling timer has expired. Must be overloaded by sub-classes.
        """
        self._polling_timer = self._polling_interval
