import os
import shutil
import socket
from datetime import datetime
import unittest
import wp_repository
import iot_repository_host

DB_TEMPLATE = "../iot_repository/iot.sl3"
HOST_ID = "pi1.lcl"

def fill_db_test_set_1(sqlite_path: str) -> iot_repository_host.IotHostConfig:
    hconf = iot_repository_host.IotHostConfig()
    hconf.host_id = HOST_ID
    hconf.host_ip = socket.gethostbyname(socket.gethostname())
    with wp_repository.SQLiteRepository(iot_repository_host.IotHostConfig, sqlite_path) as repository:
        repository.insert(hconf)
    return hconf

class TestIotRepository(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self._sqlite_path = f"./test_iot_rep.{datetime.now().strftime('%Y%m%d.%H%M%S.%f')}.sl3"
        shutil.copyfile(DB_TEMPLATE, self._sqlite_path)

    def tearDown(self):
        super().tearDown()
        os.remove(self._sqlite_path)

    def test1_host(self):
        host_1 = fill_db_test_set_1(self._sqlite_path)
        print('')
        print('ADD:', str(host_1))
        with wp_repository.SQLiteRepository(iot_repository_host.IotHostConfig, self._sqlite_path) as repository:
            host_2 = repository.select_by_key(host_1)
            hosts_1 = repository.select_where([("host_id", "=", HOST_ID)])
            hosts_2 = repository.select_where([("host_ip", "=", host_1.host_ip)])
        # Test host_2
        self.assertIsNotNone(host_2)
        self.assertEqual(str(host_1), str(host_2))
        self.assertIsNotNone(hosts_1)
        self.assertIsNotNone(hosts_2)


if __name__ == '__main__':
    unittest.main(verbosity=5)
 