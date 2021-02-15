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
from typing import Any
import logging
import wp_queueing
import iot_repository_hardware
import iot_handler_base
import iot_hardware_device
import iot_hardware_input
import iot_hardware_handler

class IotHardwareFactory:
    """ Factory class for creating hardware components and hardware handlers.

    Methods:
        create_hardware_device : iot_hardware_device.IotHardwareDevice, static
            Creates a hardware device object based on the given configuration.
        create_hardware_handler : iot_handler_base.IotHandlerBase, static.
            Creates a hardware handler using the given brokers and controlling the given device.
    """
    @staticmethod
    def create_hardware_device(hw_config: iot_repository_hardware.IotHardwareConfig,
                               extra_info: Any,
                               logger: logging.Logger) -> iot_hardware_device.IotHardwareDevice:
        """ Creates a hardware device object based on the given configuration.

        Parameters:
            hw_config : iot_repository_hardware.IotHardwareConfig
                Configuration settings for the hardware component as retrieved from the settings repository.
            extra_info : Any
                Extra info to be passed to the hardware component upon instantiation.
            logger : logging.Logger
                Logger to be used by the hardware component.

        Returns:
            iot_hardware_device.IotHardwareDevice
                The new hardware component.
        """
        if hw_config.device_type.find('Input') >= 0:
            # Create an input device
            if hw_config.model == "ADS1115":
                new_device = iot_hardware_input.DigitalInputADS1115(
                    hw_config.device_id, hw_config.i2c_bus_id, hw_config.i2c_bus_address, extra_info, logger)
            else:
                new_device = None
        else:
            new_device = None
        return new_device

    @staticmethod
    def create_hardware_handler(brokers: dict,
                                hw_config: iot_repository_hardware.IotHardwareConfig,
                                device: iot_hardware_device.IotHardwareDevice,
                                logger: logging.Logger) -> iot_handler_base.IotHandlerBase:
        """ Creates a hardware handler using the given brokers and controlling the given device.

        Parameters:
            brokers : dict
                Dictionary containing the broker settings. Format:
                    { 'broker_id_1' : <iot_repository_broker.IotMqttBrokerConfig>,
                      'broker_id_2' : <iot_repository_broker.IotMqttBrokerConfig>,
                      ...
                      'broker_id_N' : <iot_repository_broker.IotMqttBrokerConfig> }
            hw_config : iot_repository_hardware.IotHardwareConfig
                Configuration of the controlled hardware component.
            device : iot_hardware_device.IotHardwareDevice
                The controlled hardware device.
            logger : logging.Logger
                The logger to be used by the hardware handler.

        Returns:
            iot_handler_base.IotHandlerBase
                The new hardware handler.
        """
        if hw_config.device_type.find('Input') >= 0:
            mqtt_data = None
            mqtt_health = None
            if hw_config.data_broker_id is not None:
                broker_config = brokers[hw_config.data_broker_id]
                mqtt_data = (wp_queueing.MQTTProducer(broker_host = broker_config.broker_host,
                                                      broker_port = broker_config.broker_port,
                                                      logger = logger),
                             hw_config.data_topic)
            if hw_config.health_broker_id is not None:
                if hw_config.health_broker_id == hw_config.data_broker_id:
                    mqtt_health = (mqtt_data[0], hw_config.health_topic)
                else:
                    broker_config = brokers[hw_config.health_broker_id]
                    mqtt_health = (wp_queueing.MQTTProducer(broker_host = broker_config.broker_host,
                                                            broker_port = broker_config.broker_port,
                                                            logger = logger),
                                   hw_config.health_topic)
            new_handler = iot_hardware_handler.IotInputDeviceHandler(device, logger, hw_config.polling_interval,
                                                                     mqtt_data = mqtt_data, mqtt_health = mqtt_health,
                                                                     health_check_interval = 15 * 60)
        else:
            mqtt_input = None
            mqtt_health = None
            if hw_config.input_broker_id is not None:
                broker_config = brokers[hw_config.data_broker_id]
                mqtt_input = (wp_queueing.MQTTConsumer(broker_host = broker_config.broker_host,
                                                       broker_port = broker_config.broker_port,
                                                       logger = logger),
                              hw_config.input_topic)
            if hw_config.health_broker_id is not None:
                broker_config = brokers[hw_config.health_broker_id]
                mqtt_health = (wp_queueing.MQTTProducer(broker_host = broker_config.broker_host,
                                                        broker_port = broker_config.broker_port,
                                                        logger = logger),
                               hw_config.health_topic)
            new_handler = iot_hardware_handler.IotOutputDeviceHandler(device, logger, hw_config.polling_interval,
                                                                      mqtt_input = mqtt_input,
                                                                      mqtt_health = mqtt_health,
                                                                      health_check_interval = 15 * 60)
        return new_handler
