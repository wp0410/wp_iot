import os
import shutil
import socket
from datetime import datetime
import unittest
import wp_repository
import iot_repository_host
import iot_repository_hardware
import iot_repository_broker
import iot_repository_sensor

DB_TEMPLATE = "../iot_repository/iot.sl3"
HOST_ID = "pi1.lcl"

def fill_db_host(sqlite_path: str) -> iot_repository_host.IotHostConfig:
    hconf = iot_repository_host.IotHostConfig()
    hconf.host_id = HOST_ID
    hconf.host_ip = socket.gethostbyname(socket.gethostname())
    with wp_repository.SQLiteRepository(iot_repository_host.IotHostConfig, sqlite_path) as repository:
        repository.insert(hconf)
    return hconf

def fill_db_hw_comp(sqlite_path: str) -> list:
    comp_list = []
    hw_rows = [['hw_comp_01','DigitalInput','ADS1115','I2C',0,0x40,60,'broker.1','data/hw',None,None,'broker.1','health/hw',datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")],
               ['hw_comp_02','DigitalOutput','MCP23017','I2C',0,0x60,10,None,None,'broker.2','input/hw','broker.1','health/hw',datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")],
               ['hw_comp_03','DigitalInput','ADS1115','I2C',0,0x41,60,'broker.1','data/hw',None,None,'broker.1','health/hw',datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")]]
    with wp_repository.SQLiteRepository(iot_repository_hardware.IotHardwareConfig, sqlite_path) as repository:
        for hw_row in hw_rows:
            hw_comp = iot_repository_hardware.IotHardwareConfig()
            hw_comp.load_row(hw_row)
            repository.insert(hw_comp)
            comp_list.append(hw_comp)
    return comp_list

def fill_db_host_assign(sqlite_path: str) -> list:
    assign_list = []
    assign_rows = [['pi1.lcl', 'hw_comp_01', 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")],
                   ['pi1.lcl', 'hw_comp_02', 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")],
                   ['pi1.lcl', 'hw_comp_03', 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")]]
    with wp_repository.SQLiteRepository(iot_repository_host.IotHostAssignedComponent, sqlite_path) as repository:
        for assign_row in assign_rows:
            a_row = iot_repository_host.IotHostAssignedComponent()
            a_row.load_row(assign_row)
            repository.insert(a_row)
            assign_list.append(a_row)
    return assign_list

def fill_db_broker(sqlite_path: str) -> list:
    broker_list = []
    broker_rows = [['broker_01', '192.168.1.249', 1883, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")],
                   ['broker_02', '192.168.1.250', 1883, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")]]
    with wp_repository.SQLiteRepository(iot_repository_broker.IotMqttBrokerConfig, sqlite_path) as repository:
        for row in broker_rows:
            broker = iot_repository_broker.IotMqttBrokerConfig()
            broker.load_row(row)
            repository.insert(broker)
            broker_list.append(broker)
    return broker_list

def fill_db_sensor(sqlite_path: str) -> list:
    sensor_list = []
    sensor_rows = [['sensor.01', 'KYES516', 'hw_comp_01', 0, 60, 'broker_01', 'data/sensor', None, None, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")],
                   ['sensor.02', 'KYES516', 'hw_comp_01', 1, 60, 'broker_01', 'data/sensor', None, None, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")],
                   ['sensor.03', 'KYES516', 'hw_comp_01', 2, 60, 'broker_01', 'data/sensor', None, None, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")],
                   ['sensor.04', 'KYES516', 'hw_comp_03', 0, 60, 'broker_02', 'data/sensor', None, None, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")]]
    with wp_repository.SQLiteRepository(iot_repository_sensor.IotSensorConfig, sqlite_path) as repository:
        for row in sensor_rows:
            sensor = iot_repository_sensor.IotSensorConfig()
            sensor.load_row(row)
            repository.insert(sensor)
            sensor_list.append(sensor)
    return sensor_list

class TestIotRepository(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self._sqlite_path = f"./test_iot_rep.{datetime.now().strftime('%Y%m%d.%H%M%S.%f')}.sl3"
        shutil.copyfile(DB_TEMPLATE, self._sqlite_path)

    def tearDown(self):
        super().tearDown()
        os.remove(self._sqlite_path)

    def test01_host(self):
        print('')
        host_1 = fill_db_host(self._sqlite_path)
        print('>>> HOST: ', str(host_1))
        self.assertIsNotNone(host_1)
        with wp_repository.SQLiteRepository(iot_repository_host.IotHostConfig, self._sqlite_path) as repository:
            host_2 = repository.select_by_key(host_1)
            hosts_1 = repository.select_where([("host_id", "=", HOST_ID)])
            hosts_2 = repository.select_where([("host_ip", "=", host_1.host_ip)])
        # Test host_2
        self.assertIsNotNone(host_2)
        self.assertEqual(str(host_1), str(host_2))
        self.assertIsNotNone(hosts_1)
        self.assertIsNotNone(hosts_2)

    def _compare_lists(self, l1: list, l2: list) -> bool:
        self.assertEqual(len(l1), len(l2))
        for elem1 in l1:
            self.assertTrue(elem1 in l2)
        return True

    def test02_hardware(self):
        print('')
        hw_comp_list = fill_db_hw_comp(self._sqlite_path)
        id_list = []
        for hw_comp in hw_comp_list:
            id_list.append(hw_comp.device_id)
        self.assertIsNotNone(hw_comp_list)
        self.assertIsInstance(hw_comp_list, list)
        self.assertEqual(len(hw_comp_list),3)
        with wp_repository.SQLiteRepository(iot_repository_hardware.IotHardwareConfig, self._sqlite_path) as repository:
            # SELECT ALL
            print('IotHardwareConfig: SELECT ALL')
            hw_res_1 = repository.select_all()
            self.assertIsNotNone(hw_res_1)
            self.assertIsInstance(hw_res_1, list)
            res_id_list = []
            for res in hw_res_1:
                self.assertIsInstance(res, iot_repository_hardware.IotHardwareConfig)
                res_id_list.append(res.device_id)
            self._compare_lists(id_list, res_id_list)
            # SELECT BY KEY
            print('IotHardwareConfig: SELECT BY KEY')
            for hw_comp in hw_comp_list:
                hw_res_2 = repository.select_by_key(hw_comp)
                self.assertIsNotNone(hw_res_2)
                self.assertIsInstance(hw_res_2, iot_repository_hardware.IotHardwareConfig)
                self.assertEqual(str(hw_comp), str(hw_res_2))
            # SELECT WHERE
            print('IotHardwareConfig: SELECT WHERE')
            hw_res_3 = repository.select_where([("device_type", "like", "%INPUT%")])
            self.assertIsNotNone(hw_res_3)
            self.assertEqual(len(hw_res_3), 2)
            for res in hw_res_3:
                self.assertIsInstance(res, iot_repository_hardware.IotHardwareConfig)
                self.assertTrue(res.device_id in ['hw_comp_01','hw_comp_03'])

            hw_res_3 = repository.select_where([("model", "=", "ADS1115")])
            self.assertIsNotNone(hw_res_3)
            self.assertEqual(len(hw_res_3), 2)
            for res in hw_res_3:
                self.assertIsInstance(res, iot_repository_hardware.IotHardwareConfig)
                self.assertTrue(res.device_id in ['hw_comp_01','hw_comp_03'])

            hw_res_3 = repository.select_where([("if_type", "!=", "I2C")])
            self.assertIsNotNone(hw_res_3)
            self.assertEqual(len(hw_res_3), 0)

            hw_res_3 = repository.select_where([("polling_interval", "<", 30)])
            self.assertIsNotNone(hw_res_3)
            self.assertEqual(len(hw_res_3), 1)
            self.assertIsInstance(hw_res_3[0], iot_repository_hardware.IotHardwareConfig)
            self.assertEqual(hw_res_3[0].device_id, 'hw_comp_02')

    def test_03_assignment(self):
        print('')
        host_1 = fill_db_host(self._sqlite_path)
        self.assertIsNotNone(host_1)

        hw_comp_list = fill_db_hw_comp(self._sqlite_path)
        self.assertIsNotNone(hw_comp_list)
        self.assertIsInstance(hw_comp_list, list)
        self.assertEqual(len(hw_comp_list),3)

        ass_list = fill_db_host_assign(self._sqlite_path)
        self.assertIsNotNone(ass_list)
        self.assertIsInstance(ass_list, list)
        self.assertEqual(len(ass_list), 3)

        with wp_repository.SQLiteRepository(iot_repository_host.IotHostAssignedComponent, self._sqlite_path) as repository:
            # SELECT BY KEY
            for ass_comp in ass_list:
                ass_res_1 = repository.select_by_key(ass_comp)
                self.assertIsNotNone(ass_res_1)
                self.assertIsInstance(ass_res_1, iot_repository_host.IotHostAssignedComponent)
                self.assertEqual(str(ass_res_1), str(ass_comp))

    def test_04_broker(self):
        print('')
        brokers = fill_db_broker(self._sqlite_path)
        self.assertIsNotNone(brokers)
        self.assertEqual(len(brokers), 2)

        with wp_repository.SQLiteRepository(iot_repository_broker.IotMqttBrokerConfig, self._sqlite_path) as repository:
            # SELECT BY KEY
            for broker in brokers:
                brk_res_1 = repository.select_by_key(broker)
                self.assertIsNotNone(brk_res_1)
                self.assertIsInstance(brk_res_1, iot_repository_broker.IotMqttBrokerConfig)
                self.assertEqual(str(brk_res_1), str(broker))

            # SELECT WHERE (broker_port)
            brk_res_2 = repository.select_where([("broker_port", "=", 1883)])
            self.assertIsNotNone(brk_res_2)
            self.assertIsInstance(brk_res_2, list)
            self.assertEqual(len(brk_res_2), 2)
            for brk_res in brk_res_2:
                self.assertIsInstance(brk_res, iot_repository_broker.IotMqttBrokerConfig)
                self.assertTrue(brk_res.broker_id in [brokers[0].broker_id, brokers[1].broker_id])

            # SELECT WHERE (broker_host)
            brk_res_3 = repository.select_where([("broker_host", "=", brokers[1].broker_host)])
            self.assertIsNotNone(brk_res_3)
            self.assertIsInstance(brk_res_3, list)
            self.assertEqual(len(brk_res_3), 1)
            brk_res = brk_res_3[0]
            self.assertIsInstance(brk_res, iot_repository_broker.IotMqttBrokerConfig)
            self.assertEqual(str(brk_res), str(brokers[1]))

    def test_05_sensor(self):
        print('')
        hw_components = fill_db_hw_comp(self._sqlite_path)
        brokers = fill_db_broker(self._sqlite_path)
        sensors = fill_db_sensor(self._sqlite_path)
        self.assertIsNotNone(sensors)
        self.assertIsInstance(sensors, list)
        self.assertEqual(len(sensors), 4)

        with wp_repository.SQLiteRepository(iot_repository_sensor.IotSensorConfig, self._sqlite_path) as repository:
            # SELECT BY KEY
            for sensor in sensors:
                s_res_1 = repository.select_by_key(sensor)
                self.assertIsNotNone(s_res_1)
                self.assertIsInstance(s_res_1, iot_repository_sensor.IotSensorConfig)
                self.assertEqual(str(s_res_1), str(sensor))

            # SELECT BY device_id
            for hw in hw_components:
                num_ref = 0
                for sensor in sensors:
                    if sensor.device_id == hw.device_id:
                        num_ref += 1
                s_res_2 = repository.select_where([("device_id", "=", hw.device_id)])
                self.assertIsNotNone(s_res_2)
                self.assertIsInstance(s_res_2, list)
                self.assertEqual(len(s_res_2), num_ref)


if __name__ == '__main__':
    unittest.main(verbosity=5)
 