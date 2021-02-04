import unittest
from datetime import datetime
import time
import logging
import logging.config
import iot_hardware_input
import iot_hardware_handler
import iot_message
import wp_queueing

LOGGER_CONFIG = {
        "version": 1,
        "formatters": {
            "default": {
                "format": "%(asctime)s-%(name)s-%(levelname)s-%(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG",
                "formatter": "default",
                "stream": "ext://sys.stdout"
            }
        },
        "loggers": {
            "Test": {
                "level": "DEBUG",
                "handlers": [
                    "console"
                ],
                "propagate": "no"
            }
        }
    }


class TestIotHardware(unittest.TestCase):
    def setUp(self):
        super().setUp()
        logging.config.dictConfig(LOGGER_CONFIG)
        self._logger = logging.getLogger('Test.Hardware')

    def tearDown(self):
        super().tearDown()

    def test_01_hw_component(self):
        test_target = iot_hardware_input.IotInputDevice("test.01", self._logger)
        self.assertIsNotNone(test_target)
        self.assertEqual(len(test_target.probe()), 0)
        self.assertIsNone(test_target.check_health())

        test_active_channels = [0,1,3]
        test_target = iot_hardware_input.DigitalInputADS1115("test.02", 0, 0x40, test_active_channels, self._logger)
        self.assertIsNotNone(test_target)
        probes = test_target.probe()
        self.assertIsNotNone(probes)
        self.assertEqual(len(probes), len(test_active_channels))
        for p in probes:
            self.assertTrue(p.channel_no in test_active_channels)
            self.assertIsInstance(p, iot_message.InputProbe)
        h = test_target.check_health()
        self.assertIsNotNone(h)
        self.assertIsInstance(h, iot_message.InputHealth)

    def test_02_hw_handler(self):
        broker = wp_queueing.MQTTProducer('192.168.1.250', self._logger)

        dev_config = {
            'device_id':        'test.03',
            'device_type':      'DigitalInput',
            'model':            'ADS1115',
            'polling_interval': 10,
            'last_change':      datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'data_topic':       (broker, 'test/hw'),
            'health_topic':     (broker, 'test/health'),
            'i2c': {
                'bus_id': 0,
                'bus_address': 0x40
            },
            'active_ports': [1,3]
        }
        test_target = iot_hardware_handler.IotInputDeviceHandler(dev_config, self._logger)
        self.assertIsNotNone(test_target)
        self.assertIsInstance(test_target, iot_hardware_handler.IotInputDeviceHandler)
        self.assertEqual(test_target.device_id, dev_config['device_id'])
        self.assertEqual(test_target.device_type, dev_config['device_type'])
        self.assertEqual(test_target.device_model, dev_config['model'])
        self.assertEqual(test_target.data_topic, dev_config['data_topic'])
        self.assertEqual(test_target.health_topic, dev_config['health_topic'])
        self.assertIsNone(test_target.input_topic)
        test_target.polling_timer_event()
        test_target.health_timer_event()
        time.sleep(2)

if __name__ == '__main__':
    unittest.main(verbosity=5)
