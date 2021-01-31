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
import iot_configuration
import iot_agent

class IotHost:
    """ Initiated once for every process group per host where IOT components are deployed.
        Starts the controllers for these IOT components in seperate agent threads.

    Methods:
        IotHost()
            Constructor
        start_hardware_agents : None
            Starts the agent threads for the hardware components attached to the host.
        stop_agents : None
            Stops the currently running agent threads.
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
        self._sqlite_db_path = sqlite_db_path
        self._process_group = process_group
        self._ip_address = socket.gethostbyname(socket.gethostname())
        self._config = iot_configuration.IotConfiguration(self._ip_address, self._sqlite_db_path)
        self._agents = []

    def __del__(self):
        """ Destructor. """
        self.stop_agents()

    def start_hardware_agents(self) -> None:
        """ Starts the agent threads for the hardware components attached to the host. """
        brokers = self._config.brokers
        hw_components = self._config.hardware_components(self._config.host_id, self._process_group)
        for hw_component in hw_components:
            hw_agent = iot_agent.IotAgent(brokers, hw_component)
            self._agents.append(hw_agent)
            hw_agent.start()

    def stop_agents(self) -> None:
        """ Stops the currently running agent threads. """
        for agent in self._agents:
            if not agent.stop():
                agent.kill()
            self._agents.remove(agent)
