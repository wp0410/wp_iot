# pylint: disable=line-too-long,missing-module-docstring,missing-class-docstring,missing-function-docstring

import unittest
import logging
import logging.config
from datetime import datetime
import time
import iot_repository_broker
import iot_repository_hardware
import iot_hardware_factory
import iot_hardware_input
import iot_hardware_handler
import iot_agent

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
logging.config.dictConfig(LOGGER_CONFIG)


class TestIotAgent(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self._logger = logging.getLogger("Test.IotAgent")
        broker = iot_repository_broker.IotMqttBrokerConfig()
        broker.load_row(['broker.1', '192.168.1.250', 1883, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")])
        self._brokers = {'broker.1': broker}
        self._device_config = iot_repository_hardware.IotHardwareConfig()
        self._device_config.load_row(['device.01','DigitalInput','ADS1115','I2C',1,0x40,30,'broker.1','data/hw',None,None,'broker.1','health/hw',datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")])

    def test_01_agent(self):
        device = iot_hardware_factory.IotHardwareFactory.create_hardware_device(self._device_config, [0,1,2], self._logger)
        self.assertIsNotNone(device)
        self.assertIsInstance(device, iot_hardware_input.DigitalInputADS1115)
        self.assertEqual(device.device_id, self._device_config.device_id)
        self.assertEqual(device.device_type, self._device_config.device_type)
        self.assertEqual(device.model, self._device_config.model)

        handler = iot_hardware_factory.IotHardwareFactory.create_hardware_handler(self._brokers, self._device_config, device, self._logger)
        self.assertIsNotNone(handler)
        self.assertIsInstance(handler, iot_hardware_handler.IotInputDeviceHandler)
        self.assertEqual(handler.device_id, self._device_config.device_id)
        self.assertEqual(handler.device_type, self._device_config.device_type)
        self.assertEqual(handler.device_model, self._device_config.model)

        agent = iot_agent.IotAgent(handler, self._logger)
        self.assertIsNotNone(agent)
        self.assertIsInstance(agent, iot_agent.IotAgent)
        self.assertIsInstance(agent.agent_id, str)
        agent.start()
        self.assertTrue(agent.is_running)
        time.sleep(120)
        agent.stop()
        time.sleep(3)
        self.assertFalse(agent.is_running)


if __name__ == '__main__':
    unittest.main(verbosity=5)
