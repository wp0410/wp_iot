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
import wp_repository
import iot_repository

class IotConfiguration:
    """ Creates the configuration for the IOT system from the configuration stored in the repository.

    Attributes:
        _sqlite_file_name : str
            Full path name to the SQLite database file.
        _broker_config_list: list
            List containing the configuration setting dictionary per MQTT broker.

    Methods:
        IotConfiguration()
            Constructor.
        _build_config: dict
            Builds the configuration dictionary for a MQTT broker from the repository.
        _build_hardware_config : list
            Builds the list of configuration dictionaries of hardware elements using the given MQTT broker
            for message subscription/publishing.
        _build_sensor_config : list
            Builds the list of configuration dictionaries of sensors using the given MQTT broker for
            message subscription/publishing.
    """
    def __init__(self, sqlite_file_name: str):
        """ Constructor.

        Parameters:
            sqlite_file_name : str
                Full path name to the SQLite database file.
        """
        self._sqlite_file_name = sqlite_file_name
        self._broker_config_list = []
        with wp_repository.SQLiteRepository(iot_repository.IotMqttBroker, self._sqlite_file_name) as repo:
            broker_list = repo.select_all()
        for broker in broker_list:
            self._broker_config_list.append(self._build_config(broker))

    def _build_config(self, broker: iot_repository.IotMqttBroker) -> dict:
        """ Builds the configuration dictionary for a MQTT broker from the repository.

        Parameters:
            broker : iot_repository.IotMqttBroker
                Broker for which the configuration dictionary shall be created.

        Returns:
            dict : Configuration dictionary for the given MQTT broker.
        """
        result = {
            'broker' : {
                'broker_id': broker.broker_id,
                'host': broker.broker_host,
                'port': broker.broker_port,
                'change_date': broker.store_date_str
            },
            'hardware_components': self._build_hardware_config(broker),
            'sensors': self._build_sensor_config(broker)
        }
        return result

    def _build_hardware_config(self, broker: iot_repository.IotMqttBroker) -> list:
        """ Builds the list of configuration dictionaries of hardware elements using the given MQTT broker
            for message subscription/publishing.

        Parameters:
            broker : iot_repository.IotMqttBroker
                Broker for which the configuration dictionary shall be created.

        Returns:
            list : Configuration dictionaries for the hardware elements using the MQTT broker.
        """
        hw_config = []
        with wp_repository.SQLiteRepository(iot_repository.IotHardwareComponent, self._sqlite_file_name) as repo:
            hw_components = repo.select_where([("broker_id", "=", broker.broker_id)])
        for hw_component in hw_components:
            with wp_repository.SQLiteRepository(iot_repository.IotSensor, self._sqlite_file_name) as repo:
                assigned_sensors = repo.select_where([("hardware_id", "=", hw_component.hardware_id)])
            channels = []
            for sensor in assigned_sensors:
                channels.append(sensor.hw_channel)
            hw_component_config = {
                'device_id': hw_component.hardware_id,
                'device_type': hw_component.hardware_type,
                'interface:': {
                    'if_type': hw_component.if_type,
                    'i2c': {
                        'bus_id': hw_component.i2c_bus_id,
                        'bus_address': hw_component.i2c_bus_address
                    }
                },
                'active_ports': channels,
                'topics': {
                    'data_prefix': hw_component.topic_data,
                    'health_prefix': hw_component.topic_health
                },
                'polling_interval': hw_component.polling_interval,
                'change_date': hw_component.store_date_str
            }
            hw_config.append(hw_component_config)
        return hw_config

    def _build_sensor_config(self, broker: iot_repository.IotMqttBroker) -> list:
        """ Builds the list of configuration dictionaries of sensors using the given MQTT broker for
            message subscription/publishing.

        Parameters:
            broker : iot_repository.IotMqttBroker
                Broker for which the configuration dictionary shall be created.

        Returns:
            list : Configuration dictionaries for the sensors using the MQTT broker.
        """
        sensor_config = []
        with wp_repository.SQLiteRepository(iot_repository.IotSensor, self._sqlite_file_name) as repo:
            sensor_list = repo.select_where([("broker_id", "=", broker.broker_id)])
        for sensor in sensor_list:
            config = {
                'sensor_id': sensor.sensor_id,
                'sensor_type': sensor.sensor_type,
                'hardware': {
                    'id': sensor.hardware_id,
                    'channel': sensor.hw_channel
                },
                'topics': {
                    'input_prefix': sensor.topic_input,
                    'data_prefix': sensor.topic_data,
                    'health_prefix': sensor.topic_health
                },
                'polling_interval': sensor.polling_interval,
                'change_date': sensor.store_date_str
            }
            sensor_config.append(config)
        return sensor_config
