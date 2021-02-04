import unittest
from datetime import datetime
import shutil
import wp_repository
import iot_configuration
import iot_repository_host
import iot_repository_hardware
import iot_repository_broker
import iot_repository_sensor

DB_TEMPLATE = "../iot_repository/iot.sl3"
HOST_IP = "pi1.lcl"


class Test01Configuration(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self._sqlite_path = f"./test_iot_rep.{datetime.now().strftime('%Y%m%d.%H%M%S.%f')}.sl3"
        shutil.copyfile(DB_TEMPLATE, self._sqlite_path)

    def tearDown(self):
        super().tearDown()

    def _fill_db(self) -> None:
        # Create HOST entry
        self._host = iot_repository_host.IotHostConfig()
        self._host.load_row(["host.01", HOST_IP, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")])
        with wp_repository.SQLiteRepository(iot_repository_host.IotHostConfig, self._sqlite_path) as repository:
            res = repository.insert(self._host)
        self.assertEqual(res, 1)
        # Create hardware components
        hw_rows = [['hw_comp_01','DigitalInput','ADS1115','I2C',0,0x40,60,'broker.1','data/hw',None,None,'broker.1','health/hw',datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")],
                   ['hw_comp_02','DigitalOutput','MCP23017','I2C',0,0x60,10,None,None,'broker.2','input/hw','broker.1','health/hw',datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")],
                   ['hw_comp_03','DigitalInput','ADS1115','I2C',0,0x41,60,'broker.1','data/hw',None,None,'broker.1','health/hw',datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")]]
        self._hw_components = []
        with wp_repository.SQLiteRepository(iot_repository_hardware.IotHardwareConfig, self._sqlite_path) as repository:
            for row in hw_rows:
                hw_component = iot_repository_hardware.IotHardwareConfig()
                hw_component.load_row(row)
                res = repository.insert(hw_component)
                self.assertEqual(res, 1)
                self._hw_components.append(hw_component)
        # Create host assignments
        assign_rows = [['host.01', 'hw_comp_01', 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")],
                       ['host.01', 'hw_comp_02', 2, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")],
                       ['host.01', 'hw_comp_03', 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")]]
        self._host_components = []
        with wp_repository.SQLiteRepository(iot_repository_host.IotHostAssignedComponent, self._sqlite_path) as repository:
            for row in assign_rows:
                host_comp = iot_repository_host.IotHostAssignedComponent()
                host_comp.load_row(row)
                res = repository.insert(host_comp)
                self.assertEqual(res, 1)
                self._host_components.append(host_comp)
        # Create brokers
        self._brokers = []
        brk_rows = [['broker.1', '192.168.1.250', 1883, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")],
                    ['broker.2', '192.168.1.250', 1883, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")]]
        with wp_repository.SQLiteRepository(iot_repository_broker.IotMqttBrokerConfig, self._sqlite_path) as repository:
            for row in brk_rows:
                broker = iot_repository_broker.IotMqttBrokerConfig()
                broker.load_row(row)
                res = repository.insert(broker)
                self.assertEqual(res, 1)
                self._brokers.append(broker)
        # Create sensors
        self._sensors = []
        sensor_rows = [['sensor.01', 'KYES516', 'hw_comp_01', 0, 60, 'broker.1', 'data/sensor', None, None, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")],
                       ['sensor.02', 'KYES516', 'hw_comp_01', 1, 60, 'broker.1', 'data/sensor', None, None, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")],
                       ['sensor.03', 'KYES516', 'hw_comp_01', 2, 60, 'broker.1', 'data/sensor', None, None, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")],
                       ['sensor.04', 'KYES516', 'hw_comp_03', 0, 60, 'broker.2', 'data/sensor', None, None, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")]]
        with wp_repository.SQLiteRepository(iot_repository_sensor.IotSensorConfig, self._sqlite_path) as repository:
            for row in sensor_rows:
                sensor = iot_repository_sensor.IotSensorConfig()
                sensor.load_row(row)
                res = repository.insert(sensor)
                self.assertEqual(res, 1)
                self._sensors.append(sensor)

    def test_1_configuration(self):
        print('')
        self._fill_db()

        # Test CONSTRUCTOR
        print('CONSTRUCTOR ...')
        conf = iot_configuration.IotConfiguration(HOST_IP, self._sqlite_path)
        self.assertIsNotNone(conf)
        self.assertEqual(self._host.host_id, conf.host_id)
        
        # Test BROKERS
        print('BROKERS ...')
        broker_config = conf.brokers
        self.assertIsNotNone(broker_config)
        self.assertIsInstance(broker_config, dict)
        self.assertEqual(len(broker_config), 2)
        for broker in self._brokers:
            brk_conf = broker_config[broker.broker_id]
            self.assertIsInstance(brk_conf, dict)
            self.assertEqual(brk_conf['host'], broker.broker_host)
            self.assertEqual(brk_conf['port'], broker.broker_port)
            self.assertEqual(brk_conf['last_change'], broker.store_date_str)

        # Test HARDWARE
        print('HARDWARE ...')
        hw_config_list = conf.hardware_components(1)
        self.assertIsNotNone(hw_config_list)
        self.assertIsInstance(hw_config_list, list)
        self.assertEqual(len(hw_config_list), 2)
        for hw_config in hw_config_list:
            self.assertIsInstance(hw_config, dict)
            self.assertEqual(hw_config['config_type'], 'HardwareDevice')
            hw_comp = self._find_device(hw_config['device_id'])
            self.assertIsNotNone(hw_comp)
            self.assertIsInstance(hw_comp, iot_repository_hardware.IotHardwareConfig)
            self.assertEqual(hw_config['device_id'], hw_comp.device_id)
            self.assertEqual(hw_config['device_type'], hw_comp.device_type)
            self.assertEqual(hw_config['model'], hw_comp.model)
            self.assertEqual(hw_config['polling_interval'], hw_comp.polling_interval)
            self.assertEqual(hw_config['data_topic']['broker'], hw_comp.data_broker_id)
            self.assertEqual(hw_config['data_topic']['topic'], hw_comp.data_topic)
            self.assertEqual(hw_config['input_topic']['broker'], hw_comp.input_broker_id)
            self.assertEqual(hw_config['input_topic']['topic'], hw_comp.input_topic)
            self.assertEqual(hw_config['health_topic']['broker'], hw_comp.health_broker_id)
            self.assertEqual(hw_config['health_topic']['topic'], hw_comp.health_topic)
            self.assertEqual(hw_config['i2c']['bus_id'], hw_comp.i2c_bus_id)
            self.assertEqual(hw_config['i2c']['bus_address'], hw_comp.i2c_bus_address)
            for sensor in self._sensors:
                if sensor.device_id == hw_comp.device_id:
                    self.assertTrue(sensor.device_channel in hw_config['active_ports'])
            self.assertEqual(hw_config['last_change'], hw_comp.store_date_str)

    def _find_device(self, device_id: str) -> iot_repository_hardware.IotHardwareConfig:
        for hw_comp in self._hw_components:
            if hw_comp.device_id == device_id:
                return hw_comp
        return None

if __name__ == '__main__':
    unittest.main(verbosity=5)

