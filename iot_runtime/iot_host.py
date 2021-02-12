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
import socket
import logging
import iot_config
import iot_hardware_factory
import iot_recorder
import iot_agent

class IotHost:
    """ Initiated once for every process group per host where IOT components are deployed.
        Starts the controllers for these IOT components in seperate agent threads.

    Methods:
        IotHost
            Constructor
        start_agents: None
            Starts the agent threads for all IOT components attached to the host, belonging to the
            correct process group.
        stop_agents : None
            Stops all currently running agent threads.
        stop_hardware_agents: None
            Stops all currently running hardware agent threads.
        start_hardware_agents : None
            Starts the agent threads for the hardware components attached to the host.
        start_data_recording : None
            Starts the recorders for recording of messages published to data topics.
        stop_data_recording : None
            Stops the recorders for recording of messsages published to data topics.
    """
    def __init__(self, sqlite_db_path: str, process_group: int = 0):
        """ Constructor.

        Parameters:
            sqlite_db_path : str
                Path name of the SQLite database file containing the configuration settings.
            process_group : int, optional
                Allows for agents to be started on a specific hosts to be split into separate process
                groups.
        """
        ip_address = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
                      if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)),
                      s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET,
                      socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
        self._config = iot_config.IotConfiguration(ip_address, sqlite_db_path, process_group)
        self._agents = dict()
        self._data_recording_started = False

    def __del__(self):
        """ Destructor. """
        self.stop_agents()

    def start_data_recording(self, recorder_db_path: str) -> None:
        """ Starts the recorders for recording of messages published to data topics.

        Parameters:
            recorder_db_path : str
                Full path name of the SQLite database to store the recorded messages.
        """
        if self._data_recording_started:
            return
        brokers = self._config.brokers
        recorder_config = dict()
        for broker_id in brokers:
            recorder_config[broker_id] = []
        hw_devices = self._config.hardware_components
        for device_id in hw_devices:
            device_conf = hw_devices[device_id][0]
            if device_conf.data_topic is not None and len(device_conf.data_topic.strip()) > 0:
                recorder_config[device_conf.data_broker_id].append(f'{device_conf.data_topic}/#')
        recorder_agents = []
        for broker_id in recorder_config:
            if len(recorder_config[broker_id]) > 0:
                logger = logging.getLogger(f'IOT.REC.{broker_id}')
                recorder = iot_recorder.IotMessageRecorder(
                    brokers[broker_id], recorder_config[broker_id], recorder_db_path, logger)
                rec_agent = iot_agent.IotAgent(recorder, logger)
                recorder_agents.append(rec_agent)
                rec_agent.start()
        self._agents['data_recorder'] = recorder_agents
        self._data_recording_started = True

    def stop_data_recording(self) -> None:
        """ Stops the recorders for recording of messsages published to data topics. """
        if self._data_recording_started:
            recorders = self._agents['data_recorder']
            for agent in recorders:
                if not agent.stop():
                    agent.kill()
            self._agents['data_recorder'] = []

    def start_hardware_agents(self) -> None:
        """ Starts the agent threads for the hardware components attached to the host. """
        hw_agents = []
        brokers = self._config.brokers
        hw_components = self._config.hardware_components
        for device_id in hw_components:
            component_config, extra_info = hw_components[device_id]
            logger = logging.getLogger(f'IOT.HW.{component_config.device_id}')
            device = iot_hardware_factory.IotHardwareFactory.create_hardware_device(
                component_config, extra_info, logger)
            handler = iot_hardware_factory.IotHardwareFactory.create_hardware_handler(
                brokers, component_config, device, logger)
            hw_agent = iot_agent.IotAgent(handler, logger)
            hw_agents.append(hw_agent)
            hw_agent.start()
        self._agents['hardware'] = hw_agents

    def stop_hardware_agents(self) -> None:
        """ Stops all currently running hardware agent threads. """
        hw_agents = self._agents['hardware']
        for agent in hw_agents:
            if not agent.stop():
                agent.kill()
        self._agents['hardware'] = []

    def start_agents(self) -> None:
        """ Starts the agent threads for all IOT components attached to the host, belonging to the
            correct process group. """
        self.start_hardware_agents()

    def stop_agents(self) -> None:
        """ Stops all currently running agent threads. """
        self.stop_hardware_agents()
        self.stop_data_recording()
