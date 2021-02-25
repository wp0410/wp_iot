# pylint: disable=line-too-long,missing-module-docstring,missing-class-docstring,missing-function-docstring

import os
import shutil
import unittest
from datetime import date, datetime
import uuid
import random
import wp_repository
import iot_msg_input
import iot_stat_msg

class TestStatisticsData(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self._stat_db_template = "../iot_recorder/iot_rec.sl3"
        self._stat_db_target = "../../iot_web_app/iot_statistics/iot_statistics_test.sl3"
        self._devices = [
            {'device_id': 'DI.ADS1115.01', 'device_type': 'DigitalInput', 'channels': [0,1]},
            {'device_id': 'DI.ADS1115.02', 'device_type': 'DigitalInput', 'channels': [1,2,3]}]
        self._probe_date = date.today()
        self._probe_hour = [0, 13]
        self._probe_min_step = 3
        self._random = random.Random()

    def test_1_create_db(self):
        self.assertTrue(os.path.exists(self._stat_db_template))
        shutil.copyfile(self._stat_db_template, self._stat_db_target)
        self.assertTrue(os.path.exists(self._stat_db_target))

    def test_2_input_probe(self):
        rec_msg = iot_stat_msg.IotRecorderMsg()

        with wp_repository.SQLiteRepository(iot_stat_msg.IotRecorderMsg, self._stat_db_target) as msg_repo:
            with wp_repository.SQLiteRepository(iot_stat_msg.IotRecorderInputProbe, self._stat_db_target) as prb_repo:
                for hour in range(self._probe_hour[0], self._probe_hour[1]):
                    for min in range(0, 60, self._probe_min_step):
                        for device in self._devices:
                            for channel in device['channels']:
                                sec = self._random.randint(0, 4)
                                msec = self._random.randint(0, 999999)
                                _msg_id = str(uuid.uuid4())
                                _msg_timestamp = f'{self._probe_date.strftime("%Y-%m-%d")} {hour:02d}:{min:02d}:{sec:02d}.{msec}'
                                _msg_topic = f"data/device/{device['device_id']}/{channel}"
                                sec = self._random.randint(sec, sec + 4)
                                _store_timestamp = f'{self._probe_date.strftime("%Y-%m-%d")} {hour:02d}:{min:02d}:{sec:02d}'
                                rec_msg.load_row([_msg_id, _msg_topic, _msg_timestamp, 'InputProbe', _store_timestamp])
                                probe = iot_msg_input.InputProbe(device['device_type'], device['device_id'], _msg_timestamp, channel)
                                probe.value = self._random.randint(8000 + (12 - hour) * 51, 20000 + (12 - hour) * 83)
                                probe.voltage = (3.3 / 29999) * float(probe.value)
                                prb_msg = iot_stat_msg.IotRecorderInputProbe(_msg_id, probe)

                                msg_repo.insert(rec_msg)
                                prb_repo.insert(prb_msg)

if __name__ == '__main__':
    unittest.main(verbosity=5)
