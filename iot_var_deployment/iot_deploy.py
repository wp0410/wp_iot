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
import os
import shutil
from datetime import datetime
import wp_repository
import iot_repository_host
import iot_repository_broker
import iot_repository_hardware
import iot_repository_sensor

class IotDeployment:
    """ Create config database and JSON config file based on  provided deployment information. """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, target_app_name: str, target_host: str, output_path: str = None):
        """ Constructor. """
        self._target_app_name = target_app_name
        self._output_path = output_path if output_path is not None else f"{target_app_name}.{target_host}.dpl"
        if not os.path.exists(self._output_path):
            os.mkdir(self._output_path)
        self._target_host = target_host
        self._config_db_name = f"iot_env_{self._target_host}.sl3"
        self._stat_db_name = f"iot_rec_{self._target_host}.sl3"
        self._host = None
        self._devices = []
        self._sensors = []
        self._process_group = None

    def __enter__(self):
        """ Method that allows for using the class in "with" statements. """
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> bool:
        """ Method that allows for using the class in "with" statements. """
        return True

    @property
    def _config_db_path(self) -> str:
        return f"{self._output_path}/{self._config_db_name}"

    @property
    def _stat_db_path(self) -> str:
        return f"{self._output_path}/{self._stat_db_name}"

    def create_config_db(self, config_db_template: str, force_new: bool = True):
        """ Creates the configuration database from the given template. """
        if not force_new and os.path.exists(self._config_db_path):
            return
        shutil.copyfile(config_db_template, self._config_db_path)

    def create_recorder_db(self, recorder_db_template: str):
        """ Creates the recorder database from the given template. """
        shutil.copyfile(recorder_db_template, self._stat_db_path)

    def host_settings(self, host_name: str):
        """ Creates the host configuration in the configuration database. """
        host_config = [[self._target_host, host_name, self.now()]]
        res_list = self._create_db_items(iot_repository_host.IotHostConfig, host_config)
        self._host = res_list[0]

    def device_settings(self, device_config: list):
        """ Creates the device configuration in the configuration database. """
        self._devices = self._create_db_items(iot_repository_hardware.IotHardwareConfig, device_config)

    def broker_settings(self, broker_config: list):
        """ Creates the broker configuration in the configuration database. """
        _brokers = self._create_db_items(iot_repository_broker.IotMqttBrokerConfig, broker_config)

    def sensor_settings(self, sensor_config: list):
        """ Creates the sensor configuration in the configuration database. """
        self._sensors = self._create_db_items(iot_repository_sensor.IotSensorConfig, sensor_config)

    def host_assignments(self, process_group: int = 0):
        """ Creates the host assignments in the configuration database. """
        self._process_group = process_group
        assignment_config = []
        for device in self._devices:
            assignment_config.append([self._host.host_id, device.device_id, self._process_group, self.now()])
        for sensor in self._sensors:
            assignment_config.append([self._host.host_id, sensor.sensor_id, self._process_group, self.now()])
        _host_assignments = self._create_db_items(iot_repository_host.IotHostAssignedComponent, assignment_config)

    def _create_db_items(self, item_type: type, item_rows: list) -> list:
        """ Inserts items into the database. """
        res_list = []
        with wp_repository.SQLiteRepository(item_type, self._config_db_path) as repository:
            for row in item_rows:
                db_item = item_type()
                db_item.load_row(row)
                repository.insert(db_item)
                res_list.append(db_item)
        return res_list

    def create_config_file(self, logger_config_template: str = None) -> None:
        """ Creates the application config file. """
        with open(f"{self._output_path}/{self._target_app_name}.config.json", "w") as config_fh:
            config_fh.write("{\n")
            config_fh.write(f'"config_db_path": "{self._config_db_name}"')
            if os.path.exists(self._stat_db_path):
                config_fh.write(',\n\n"msg_recorder": {')
                config_fh.write('\n  "start_recorder": 1')
                config_fh.write(f',\n  "statistics_db_path": "{self._stat_db_name}"')
                config_fh.write('\n}')

            config_fh.write(f',\n\n"process_group": {str(self._process_group)}')

            logger_config = None
            if logger_config_template is not None:
                with open(logger_config_template) as logger_fh:
                    logger_config = logger_fh.read()

            if logger_config is not None:
                logger_config = logger_config.replace('<rotating_file_name>',f'{self._target_app_name}.log')
                config_fh.write(f',\n\n"logging": {logger_config}')
            config_fh.write("}")

    @staticmethod
    def now() -> str:
        """ Returns current date and time as str. """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
