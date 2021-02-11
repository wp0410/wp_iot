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
import logging
import time
import threading
import uuid
import iot_handler_base

class IotAgent:
    """ Agent controlling the thread that hosts a handler for a hardware component, sensor or actor.

    Attributes:

    Properties:
        agent_id : str
            Getter for the unique identifier of the controlled element.
        is_running : bool
            Indicates whether or not the agent's worker thread is running.

    Methods:
        IotAgent:
            Constructor.
    """
    def __init__(self, iot_handler: iot_handler_base.IotHandlerBase, logger: logging.Logger = None):
        """ Constructor.
        """
        self._thread = None
        self._stop_event = None
        self._handler = iot_handler
        if logger is None:
            self._logger = logging.getLogger(f'IOT.{self._handler.device_id}.{self._handler.device_type}')
        self._logger = logger
        self._agent_id = f'A.{self._handler.device_id}.{str(uuid.uuid4()).replace("-","")}'

    @property
    def agent_id(self) -> str:
        """ Getter for the unique identifier of the controlled element. """
        return self._agent_id

    def do_processing(self) -> None:
        """ Does the work of the agent interacting with the controlled handler. """
        if self._handler is None or self._stop_event is None:
            return
        self._handler.init_time()
        while not self._stop_event.wait(0.1):
            time.sleep(0.9)
            self._handler.time_tick()


    def start(self) -> None:
        """ Starts the thread executing the do_processing() loop. """
        self._stop_event = threading.Event()
        self._stop_event.clear()
        self._thread = threading.Thread(target=self.do_processing, name='agent_{}'.format(self.agent_id), daemon=True)
        self._thread.start()

    @property
    def is_running(self) -> bool:
        """ Indicates whether or not the agent's worker thread is running.

        Returns:
            bool : True if the worker thread is running, False otherwise.
        """
        if self._thread is None or self._stop_event is None:
            return False
        return self._thread.is_alive()

    def stop(self) -> bool:
        """ Stops the agent, meaning that the internal worker thread will be stopped.

        Returns:
            bool : Indication whether or not the agent has been successfully stopped.
                True ... agent thread stopped;
                False .. agent thread is still running.
        """
        if self._thread is None or self._stop_event is None:
            return True
        self._stop_event.set()
        self._thread.join(3)
        return not self._thread.is_alive()

    def kill(self) -> None:
        """ Kills the agent's internal worker thread. In the current implementation,
            a re-try is made to stop the thread.
        """
        self.stop()
