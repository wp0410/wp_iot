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
import wp_queueing
import iot_hardware_handler
from iot_handler import IotHandlerBase

class IotAgent:
    """ Agent controlling the thread that hosts a handler for a hardware component, sensor or actor.

    Attributes:
        _broker_config : list
            Configuration settings for the MQTT brokers.
        _logger : logging.Logger
            Logger to be used.
        _handler_config : dict
            Configuration settings for the controlled handler.
        _handler : iot_base.IotHandlerBase
            Controlled handler.

    Properties:
        agent_id : str
            Getter for the unique identifier of the controlled element.
        is_running : bool
            Indicates whether or not the agent's worker thread is running.

    Methods:
        do_processing : None
            Does the work of the agent interacting with the controlled handler.
        start : None
            Starts the thread executing the do_processing() loop.
        stop : bool
            Stops the agent, meaning that the internal worker thread will be stopped.
        kill : None
            Kills the agent's internal worker thread. In the current implementation,
            this method has no effect.
        _create_logger : logging.Logger, static
            Creates the logger for the controlled handler and its internal component.
        _create_hardware_config : dict
            Converts the handler configuration settings passed as parameter to the constructor into
            a configuration dictionary for a hardware handler.
        _create_handler : iot_base.IotHandlerBase
            Creates the controlled handler instance.
    """
    def __init__(self, broker_config: dict, handler_config: dict):
        """ Constructor.

        Parameters:
            broker_config: dict
                 A dictionary containing the broker configurations. Format:
                { 'broker_id_1' : {
                     'broker_id': 'broker_id_1',
                     'host': <name or ip>,
                     'port': <port>,
                     'last_change': <date> },
                  'broker_id_2' : {
                     'broker_id': 'broker_id_2',
                     'host': <name or ip>,
                     'port': <port>,
                     'last_change': <date> },
                  ... }
        """
        self._broker_config = broker_config
        self._logger = None
        self._handler_config = None
        self._handler = self._create_handler(handler_config)
        self._agent_id = None
        self._thread = None
        self._stop_event = None

    @property
    def agent_id(self) -> str:
        """ Getter for the unique identifier of the controlled element.

        Returns:
            str : Unique identifier of the controlled element.
        """
        return self._agent_id

    @staticmethod
    def _create_logger(config_type: str, device_id: str) -> logging.Logger:
        """ Creates the logger for the controlled handler and its internal component.

        Parameters:
            config_type : str
                Type of the configuration element. Legal values:
                    "HardwareDevice" : element contains settings for a hardware handler.
                    "Sensor" : element contains settings for a sensor handler (not implemented yet).
                    "Actor" : element contains settings for an actor handler (not implemented yet).
                    "Filter" : element contains settings for a filter handler (not implemented yet).
            element_id : str
                Unique identification of the controlled element.

        Returns:
            logging.Logger
                Logger to be used by the controlled handler and its internal components.
        """
        return logging.getLogger('IOT.{}.{}'.format(config_type, device_id))

    def _create_hardware_config(self, handler_config: dict) -> dict:
        """ Converts the handler configuration settings passed as parameter to the constructor into
            a configuration dictionary for a hardware handler.

        Parameters:
            handler_config : dict
                Input configuration settings.

        Returns:
            dict : dictionary containing the settings for the harware handler and its internal components.
        """
        hardware_config = {
            'device_id': handler_config['device_id'],
            'device_type' : handler_config['device_type'],
            'polling_interval': handler_config['polling_interval'],
            'last_change': handler_config['last_change']
        }
        # Create MQTT broker session for "data" messages
        if 'data_topic' in handler_config:
            data_topic = handler_config['data_topic']
            broker_config = self._broker_config[data_topic['broker']]
            if 'mqtt_client' not in broker_config:
                broker_config['mqtt_client'] = wp_queueing.MQTTProducer(broker_config, self._logger)
            hardware_config['data_topic'] = (broker_config['mqtt_client'], data_topic['topic'])
        # Create MQTT broker session for "input" messages
        if 'input_topic' in handler_config:
            input_topic = handler_config['input_topic']
            broker_config = self._broker_config[input_topic['broker']]
            if 'mqtt_client' not in broker_config:
                broker_config['mqtt_client'] = wp_queueing.MQTTConsumer(broker_config, self._logger)
            hardware_config['input_topic'] = (broker_config['mqtt_client'], input_topic['topic'])
        # Create MQTT broker session for "health check" messages
        if 'health_topic' in handler_config:
            health_topic = handler_config['health_topic']
            broker_config = self._broker_config[data_topic['broker']]
            if 'mqtt_client' not in broker_config:
                broker_config['mqtt_client'] = wp_queueing.MQTTProducer(broker_config, self._logger)
            hardware_config['health_topic'] = (broker_config['mqtt_client'], health_topic['topic'])
        return hardware_config

    def _create_handler(self, handler_config: dict) -> IotHandlerBase:
        """ Creates the controlled handler instance.

        Parameters:
            handler_config : dict
                Input configuration settings.

        Returns:
            iot_base.IotHandlerBase : the controlled handler instance.
        """
        handler = None
        config_type = handler_config['config_type']
        if config_type == "HardwareDevice":
            self._logger = self._create_logger(config_type, handler_config['device_id'])
            self._handler_config = self._create_hardware_config(handler_config)
            device_type = self._handler_config['device_type']
            if device_type.find('Input') >= 0:
                handler = iot_hardware_handler.IotInputDeviceHandler(self._handler_config, self._logger)
                self._agent_id = handler_config['device_id']
            elif device_type.find('Output') >= 0:
                pass
            else:
                raise ValueError(
                    'IotAgent._create_handler("HardwareDevice"): invalid device_type: "{}"'.format(device_type))
        elif config_type == "Sensor":
            pass
        elif config_type == "Actor":
            pass
        else:
            raise ValueError(
                'IotAgent._create_handler(): invalid config_type: "{}"'.format(config_type))
        return handler

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
