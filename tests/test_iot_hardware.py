# pylint: disable=line-too-long,missing-module-docstring,missing-class-docstring,missing-function-docstring

import unittest
from datetime import datetime
import time
import logging
import logging.config
import wp_queueing
import iot_msg_input
import iot_repository_broker
import iot_repository_hardware
import iot_hardware_input
import iot_hardware_handler
import iot_hardware_factory

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
        for prb in probes:
            self.assertTrue(prb.channel_no in test_active_channels)
            self.assertIsInstance(prb, iot_msg_input.InputProbe)
        hlth = test_target.check_health()
        self.assertIsNotNone(hlth)
        self.assertIsInstance(hlth, iot_msg_input.InputHealth)

    def test_02_hw_handler(self):
        broker = wp_queueing.MQTTProducer('192.168.1.250', self._logger)
        test_dev = iot_hardware_input.DigitalInputADS1115("test.02", 1, 0x40, [0,1], self._logger)
        test_target = iot_hardware_handler.IotInputDeviceHandler(test_dev, self._logger, 10, (broker, 'data/hw'), (broker, 'health/hw'), 15*60)
        self.assertIsNotNone(test_target)
        self.assertIsInstance(test_target, iot_hardware_handler.IotInputDeviceHandler)
        self.assertEqual(test_target.device_id, test_dev.device_id)
        self.assertEqual(test_target.device_type, test_dev.device_type)
        self.assertEqual(test_target.device_model, test_dev.model)
        test_target.polling_timer_event()
        test_target.health_timer_event()
        time.sleep(2)

    def test_03_hw_factory(self):
        device_config = iot_repository_hardware.IotHardwareConfig()
        device_config.load_row(['device.01','DigitalInput','ADS1115','I2C',1,0x40,60,'broker.1','data/hw',None,None,'broker.1','health/hw',datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")])
        device = iot_hardware_factory.IotHardwareFactory.create_hardware_device(device_config, [0,1], self._logger)
        self.assertIsNotNone(device)
        self.assertIsInstance(device, iot_hardware_input.DigitalInputADS1115)
        self.assertEqual(device.device_id, device_config.device_id)
        self.assertEqual(device.device_type, device_config.device_type)
        self.assertEqual(device.model, device_config.model)

        broker = iot_repository_broker.IotMqttBrokerConfig()
        broker.broker_id = 'broker.1'
        broker.broker_host = '192.168.1.250'
        broker.broker_port = 1883
        brokers = {'broker.1': broker}
        handler = iot_hardware_factory.IotHardwareFactory.create_hardware_handler(brokers, device_config, device, self._logger)
        self.assertIsNotNone(handler)
        self.assertIsInstance(handler, iot_hardware_handler.IotInputDeviceHandler)
        self.assertEqual(handler.device_id, device_config.device_id)
        self.assertEqual(handler.device_type, device_config.device_type)
        self.assertEqual(handler.device_model, device_config.model)

        handler.polling_timer_event()
        handler.health_timer_event()
        time.sleep(2)

if __name__ == '__main__':
    unittest.main(verbosity=5)
