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
import iot_repository_host
import iot_repository_broker
import iot_repository_hardware
import iot_repository_sensor

class IotConfiguration:
    """ Class for creating dictionaries containing settings for the various IOT components from the configuration
        data stored in the repository.

    Attributes:

    Properties:
        host_id : str
            Getter for the unique identification of the current IOT host.
        host_ip : str
            Getter for the IP address of the current IOT host.
        last_change_date : str
            Getter for the last change date of the host configuration in the repository.
        process_group : int
            Getter for the current process group.
        brokers : dict
            Getter for the configuration settings for all MQTT brokers defined in the IOT system.
        hardware_components : dict
            Retrieves configuration settings for all hardware components that are assigned to the
            current host and the current process group.
        sensors : dict
            Retrieves configuration settings for all sensors that are assigned to the current host and the current
            process group.
    """
    def __init__(self, host_ip_address: str, sqlite_db_path: str, process_group: int = 0):
        self._host = None
        self._process_group = process_group
        self._sqlite_db_path = sqlite_db_path
        with SQLiteRepository(iot_repository_host.IotHostConfig, self._sqlite_db_path) as host_repo:
            host_list = host_repo.select_where([("host_ip", "=", host_ip_address)])
        if len(host_list) == 0:
            raise ValueError('host(ip_address="{}": no configuration data found'.format(self.host_ip))
        self._host = host_list[0]

    @property
    def host_id(self) -> str:
        """ Getter for the unique identification of the current IOT host. """
        if self._host is None:
            return None
        return self._host.host_id

    @property
    def host_ip(self) -> str:
        """ Getter for the IP address of the current IOT host. """
        if self._host is None:
            return None
        return self._host.host_ip

    @property
    def last_change_date(self) -> str:
        """ Getter for the last change date of the host configuration in the repository. """
        if self._host is None:
            return None
        return self._host.store_date_str

    @property
    def process_group(self) -> int:
        """ Getter for the current process group. """
        return self._process_group

    @property
    def brokers(self) -> dict:
        """ Getter for the configuration settings for all MQTT brokers defined in the IOT system.

        Returns:
            dict:
                A dictionary containing the broker configurations. Format:
                { 'broker_id_1' : <iot_repository_broker.IotMqttBrokerConfig>,
                  'broker_id_2' : <iot_repository_broker.IotMqttBrokerConfig>,
                  ...
                  'broker_id_N' : <iot_repository_broker.IotMqttBrokerConfig> }
        """
        with SQLiteRepository(iot_repository_broker.IotMqttBrokerConfig, self._sqlite_db_path) as brk_repo:
            db_brokers = brk_repo.select_all()
        broker_config = dict()
        for db_broker in db_brokers:
            broker_config[db_broker.broker_id] = db_broker
        return broker_config

    @property
    def hardware_components(self) -> dict:
        """ Retrieves configuration settings for all hardware components that are assigned to the
            current host and the current process group.

        Returns:
            dict
                Dictionary containing the configuration setting for a hardware handler and its
                associated hardware component. Dictionary format:
                {
                    'hw_elem_1.device_id': tuple(<iot_repository_hardware.IotHardwareConfig>, <extra_info>),
                    'hw_elem_2.device_id': tuple(<iot_repository_hardware.IotHardwareConfig>, <extra_info>),
                    ...
                    'hw_elem_N'.device_id: tuple(<iot_repository_hardware.IotHardwareConfig>, <extra_info>) }
        """
        with SQLiteRepository(iot_repository_host.IotHostAssignedComponent, self._sqlite_db_path) as comp_repo:
            db_assigned_comps = comp_repo.select_where(
                [("host_id", "=", self.host_id), ("process_group", "=", self.process_group)])
        hw_components = dict()
        hw_template = iot_repository_hardware.IotHardwareConfig()
        with SQLiteRepository(iot_repository_hardware.IotHardwareConfig, self._sqlite_db_path) as hw_repo:
            with SQLiteRepository(iot_repository_sensor.IotSensorConfig, self._sqlite_db_path) as sensor_repo:
                for db_assigned_comp in db_assigned_comps:
                    hw_template.device_id = db_assigned_comp.comp_id
                    db_hw_component = hw_repo.select_by_key(hw_template)
                    if db_hw_component is None:
                        continue
                    db_sensors = sensor_repo.select_where(
                        [("device_id", "=", db_hw_component.device_id)])
                    active_ports = []
                    for db_sensor in db_sensors:
                        active_ports.append(db_sensor.device_channel)
                    hw_components[db_hw_component.device_id] = (db_hw_component, active_ports)
        return hw_components

    @property
    def all_hardware_components(self) -> dict:
        """ Retrieves configuration settings for all hardware components defined in the configuration
            database.

        Returns:
            dict
                Dictionary containing the configuration setting the defined hardware component.
                Dictionary format:
                {
                    'hw_elem_1.device_id': tuple(<iot_repository_hardware.IotHardwareConfig>, <extra_info>),
                    'hw_elem_2.device_id': tuple(<iot_repository_hardware.IotHardwareConfig>, <extra_info>),
                    ...
                    'hw_elem_N'.device_id: tuple(<iot_repository_hardware.IotHardwareConfig>, <extra_info>) }
        """
        hw_components = dict()
        with SQLiteRepository(iot_repository_hardware.IotHardwareConfig, self._sqlite_db_path) as hw_repo:
            hw_comp_list = hw_repo.select_all()
        with SQLiteRepository(iot_repository_sensor.IotSensorConfig, self._sqlite_db_path) as sensor_repo:
            for db_hw_component in hw_comp_list:
                db_sensors = sensor_repo.select_where([("device_id", "=", db_hw_component.device_id)])
                active_ports = []
                for db_sensor in db_sensors:
                    active_ports.append(db_sensor.device_channel)
                hw_components[db_hw_component.device_id] = (db_hw_component, active_ports)
        return hw_components

    @property
    def sensors(self) -> dict:
        """ Retrieves configuration settings for all sensors that are assigned to the current host and the current
            process group.

        Returns:
            dict
                Dictionary containing the configuration settings for a sensor handler and its associated
                IotSensor. Dictionary format:
                {
                    'sensor_1.sensor_id': <iot_repository_sensor.IotSensorConfig>,
                    'sensor_2.sensor_id': <iot_repository_sensor.IotSensorConfig>,
                    ...
                    'sensor_N.sensor_id': <iot_repository_sensor.IotSensorConfig> }
        """
        with SQLiteRepository(iot_repository_host.IotHostAssignedComponent, self._sqlite_db_path) as comp_repo:
            db_assigned_comps = comp_repo.select_where(
                [("host_id", "=", self.host_id), ("process_group", "=", self.process_group)])
        sensors = dict()
        sensor_template = iot_repository_sensor.IotSensorConfig()
        hw_template = iot_repository_hardware.IotHardwareConfig()
        with SQLiteRepository(iot_repository_sensor.IotSensorConfig, self._sqlite_db_path) as sensor_repo:
            with SQLiteRepository(iot_repository_hardware.IotHardwareConfig, self._sqlite_db_path) as hw_repo:
                for db_assigned_comp in db_assigned_comps:
                    sensor_template.sensor_id = db_assigned_comp.comp_id
                    db_sensor = sensor_repo.select_by_key(sensor_template)
                    if db_sensor is None:
                        continue
                    hw_template.device_id = db_sensor.device_id
                    db_hw = hw_repo.select_by_key(hw_template)
                    if db_hw is None:
                        continue
                    db_sensor.input_broker_id = db_hw.data_broker_id
                    db_sensor.input_topic = db_hw.data_topic_full(db_sensor.device_channel)
                    sensors[db_sensor.sensor_id] = db_sensor
        return sensors
