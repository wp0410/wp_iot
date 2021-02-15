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
import shutil
from datetime import datetime
import wp_repository
import iot_repository_host
import iot_repository_broker
import iot_repository_hardware
import iot_repository_sensor

class IotDeployment01:
    """ Database and Config File for Test Deployment on PI-249 with one KYES516 sensor connected to an ADS1115 """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, config_db_template: str, statistics_db_template: str = None,
                 logger_config_template: str = None, target_app_name: str = None):
        """ Constructor. """
        self._output_path = "Output Files"
        self._config_db_path = "iot_env_01.sl3"
        shutil.copyfile(config_db_template, f"{self._output_path}/{self._config_db_path}")
        if statistics_db_template is not None:
            self._stat_db_path = "iot_statistics.sl3"
            shutil.copyfile(statistics_db_template, f"{self._output_path}/{self._stat_db_path}")
        else:
            self._stat_db_path = None
        if logger_config_template is not None:
            with open(logger_config_template) as logger_fh:
                self._logger_config = logger_fh.read()
        else:
            self._logger_config = None
        self._target_app_name = target_app_name
        self._host = None
        self._brokers = []
        self._hardware_components = []
        self._host_assignments = []
        self._sensors = []
        self._process_groups = [0]

    def create_db_hardware_components(self) -> None:
        """ Creates the ADS1115 settings in the DB. """
        hw_rows = [['PI-249.ADS1115.1', 'DigitalInput', 'ADS1115', 'I2C', 1, 0x48, 60,
                    'PI-250-1883', 'data/device', None, None, 'PI-250-1883', 'health/device', self._now()]]
        self._hardware_components = self._create_db_items(iot_repository_hardware.IotHardwareConfig, hw_rows)

    def create_db_host(self) -> None:
        """ Creates the DB host settings for PI-249. """
        host_row = [['PI-249', '192.168.1.249', self._now()]]
        res_list = self._create_db_items(iot_repository_host.IotHostConfig, host_row)
        self._host = res_list[0]

    def create_db_broker(self) -> None:
        """ Creates the settings for the Mosquitto broker on PI-250. """
        broker_rows = [['PI-250-1883', '192.168.1.250', 1883, self._now()]]
        self._brokers = self._create_db_items(iot_repository_broker.IotMqttBrokerConfig, broker_rows)

    def create_db_host_components(self) -> None:
        """ Assigns the ADS1115 to PI-249. """
        host_comp_rows = [['PI-249', 'PI-249.ADS1115.1', 0, self._now()]]
        self._host_assignments = self._create_db_items(iot_repository_host.IotHostAssignedComponent, host_comp_rows)
        for assigned in self._host_assignments:
            if assigned.process_group not in self._process_groups:
                self._process_groups.append(assigned.process_group)

    def create_db_sensors(self) -> None:
        """ Creates an entry for the KEYS516 sensor (needed to calculate the active port list of the ADS1115). """
        sensor_rows = [['PI-249.KYES516.1', 'KYES516', 'PI-249.ADS1115.1', 0, 30,
                        'PI-250-1883', 'data/sensor', 'PI-250-1883', 'health/sensor', self._now()]]
        self._sensors = self._create_db_items(iot_repository_sensor.IotSensorConfig, sensor_rows)

    def create_config_db(self):
        """ Creates the database. """
        self.create_db_broker()
        self.create_db_host()
        self.create_db_hardware_components()
        self.create_db_host_components()
        self.create_db_sensors()

    def _create_db_items(self, item_type: type, item_rows: list) -> list:
        """ Inserts items into the database. """
        res_list = []
        with wp_repository.SQLiteRepository(item_type, f"{self._output_path}/{self._config_db_path}") as repository:
            for row in item_rows:
                db_item = item_type()
                db_item.load_row(row)
                repository.insert(db_item)
                res_list.append(db_item)
        return res_list

    def create_config_file(self) -> None:
        """ Creates the application config file. """
        if self._target_app_name is None:
            return
        with open(f'{self._output_path}/{self._target_app_name}.config.json', "w") as config_fh:
            config_fh.write("{\n")
            config_fh.write(f'"config_db_path": "{self._config_db_path}"')
            if self._stat_db_path is not None:
                config_fh.write(f',\n"statistics_db_path": "{self._stat_db_path}"')
            if self._process_groups is None:
                config_fh.write(',\n"process_groups": [0]')
            else:
                config_fh.write(f',\n"process_groups": {str(self._process_groups)}')
            if self._logger_config is not None:
                self._logger_config = self._logger_config.replace('<rotating_file_name>',f'{self._target_app_name}.log')
                config_fh.write(f',\n"logging": {self._logger_config}')
            config_fh.write("\n}")

    @staticmethod
    def _now() -> str:
        """ Returns current date and time as str. """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


if __name__ == "__main__":
    deployment = IotDeployment01(
        config_db_template = "../iot_repository/iot.sl3",
        statistics_db_template = "../iot_recorder/iot_rec.sl3",
        logger_config_template = "logger_config.json",
        target_app_name = "iot_base_app")
    deployment.create_config_db()
    deployment.create_config_file()
