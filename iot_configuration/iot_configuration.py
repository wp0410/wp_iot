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
from wp_repository import SQLiteRepository
import iot_repository

class IotConfiguration:
    """ Class for creating dictionaries containing settings for the various IOT components from the configuration
        data stored in the repository.

    Attributes:
        _host_id : str
            Unique identifier of the IOT host requesting the configuration. This will limit access to components
            assigned to this host only.
        _host_ip : str
            IP address or dns name of the host requesting the configuration.
        _last_change : str
            Date and time of the most recent change of the configuration settings for the IOT host.
        _sqlite_db_path : str
            Full path name of the SQLite database file containing the settings.

    Properties:
        host_id : str
            Getter for the unique identification of the current IOT host.
        brokers : dict
            Getter for the configuration settings for all MQTT brokers defined in the IOT system.

    Methods:
        hardware_components : list
            Retrieves configuration setting dictionaries for all hardware components that are assigned to the
            current host and a specific process group.
    """
    def __init__(self, host_ip_address: str, sqlite_db_path: str):
        self._host_ip = host_ip_address
        self._sqlite_db_path = sqlite_db_path
        with SQLiteRepository(iot_repository.IotHostConfig, self._sqlite_db_path) as host_repo:
            host_list = host_repo.select_where([("host_ip", "=", self._host_ip)])
        if len(host_list) == 0:
            raise ValueError('host(ip_address="{}": no configuration data found'.format(self._host_ip))
        db_host = host_list[0]
        self._host_id = db_host.host_id
        self._last_change = db_host.store_date_str

    @property
    def host_id(self) -> str:
        """ Getter for the unique identification of the current IOT host.

        Returns:
            Unique identification of the current IOT host.
        """
        return self._host_id

    @property
    def brokers(self) -> dict:
        """ Getter for the configuration settings for all MQTT brokers defined in the IOT system.

        Returns:
            dict:
                A dictionary containing the broker configurations. Format:
                { 'broker_id_1' : {
                     'broker_id': 'broker_id_1',
                     'broker_host': <name or ip>,
                     'broker_port': <port>,
                     'last_change': <date> },
                  'broker_id_2' : {
                     'broker_id': 'broker_id_2',
                     'broker_host': <name or ip>,
                     'broker_port': <port>,
                     'last_change': <date> },
                  ... }
        """
        with SQLiteRepository(iot_repository.IotMqttBrokerConfig, self._sqlite_db_path) as brk_repo:
            db_brokers = brk_repo.select_all()
        broker_config = dict()
        for db_broker in db_brokers:
            broker_config[db_broker.broker_id] = {
                'broker_id':   db_broker.broker_id,
                'host': db_broker.broker_host,
                'port': db_broker.broker_port,
                'last_change': db_broker.store_date_str
            }
        return broker_config

    def hardware_components(self, process_group: int) -> list:
        """ Retrieves configuration setting dictionaries for all hardware components that are assigned to the
            current host and a specific process group.

        Parameters:
            process_group : int
                Process group to retrieve hardware components for.

        Returns:
            list
                List of dictionaries containing the configuration setting for a hardware handler and its
                associated hardware component.
        """
        with SQLiteRepository(iot_repository.IotHostAssignedComponent, self._sqlite_db_path) as comp_repo:
            db_assigned_comps = comp_repo.select_where(
                [("host_id", "=", self._host_id), ("process_group", "=", process_group)])
        hw_components = []
        with SQLiteRepository(iot_repository.IotHardwareConfig, self._sqlite_db_path) as hw_repo:
            with SQLiteRepository(iot_repository.IotSensorConfig, self._sqlite_db_path) as sensor_repo:
                for db_assigned_comp in db_assigned_comps:
                    db_hw_component = hw_repo.select_by_key(db_assigned_comp.comp_id)
                    if db_hw_component is None:
                        continue
                    hw_config = {
                        'config_type':      'HardwareDevice',
                        'device_id':        db_hw_component.device_id,
                        'host_id':          db_hw_component.host_id,
                        'device_type':      db_hw_component.device_type,
                        'model':            db_hw_component.model,
                        'polling_interval': db_hw_component.polling_interval,
                        'data_topic':       { 'broker': db_hw_component.data_broker_id,
                                              'topic': db_hw_component.data_topic },
                        'input_topic':      { 'broker': db_hw_component.input_broker_id,
                                              'topic': db_hw_component.input_topic },
                        'health_topic':     { 'broker': db_hw_component.health_broker_id,
                                              'topic': db_hw_component.health_topic },
                        'last_change':      db_hw_component.store_date_str
                    }
                    if db_hw_component.if_type == "I2C":
                        hw_config['i2c'] = {
                            'bus_id': db_hw_component.i2c_bus_id, 'bus_address': db_hw_component.i2c_bus_address
                        }
                    db_sensors = sensor_repo.select_where(
                        [("device_id", "=", db_hw_component.device_id)])
                    active_ports = []
                    for db_sensor in db_sensors:
                        active_ports.append(db_sensor.hw_channel)
                    hw_config['active_ports'] = active_ports
                    hw_components.append(hw_config)
        return hw_components
