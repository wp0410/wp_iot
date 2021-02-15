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
import logging
import wp_queueing
import iot_repository_sensor
import iot_handler_base
import iot_sensor_base
import iot_sensor_handler

class IotSensorFactory:
    """ Factory class for creating sensors and sensor handlers.

    Methods:
        create_sensor : iot_sensor_base.IotSensor, static
            Creates a sensor object based on the given configuration.
        create_sensor_handler : iot_handler_base.IotHandlerBase, static
            Creates a sensor handler using the given brokers and controlling the given device.
    """
    @staticmethod
    def create_sensor(sensor_config: iot_repository_sensor.IotSensorConfig,
                      logger: logging.Logger) -> iot_sensor_base.IotSensor:
        """ Creates a sensor object based on the given configuration.

        Parameters:
            sensor_config : iot_repository_sensor.IotSensorConfig
                Configuration settings for the sensor to be created as retrieved from the settings repository.
            logger : logging.Logger
                Logger to be used by the sensor.

        Returns:
            iot_sensor_base.IotSensor
                The new IotSensor object or None if the sensor type is unknown.
        """
        if sensor_config.sensor_type == "KYES516":
            new_sensor = iot_sensor_base.IotSensorHumKYES516(sensor_config.sensor_id, sensor_config.sensor_type, logger)
        else:
            new_sensor = None
        return new_sensor

    @staticmethod
    def create_sensor_handler(brokers: dict,
                              se_config: iot_repository_sensor.IotSensorConfig,
                              sensor: iot_sensor_base.IotSensor,
                              logger: logging.Logger) -> iot_handler_base.IotHandlerBase:
        """ Creates a sensor handler using the given brokers and controlling the given device.

        Parameters:
            brokers : dict
                Dictionary containing the broker settings. Format:
                    { 'broker_id_1' : <iot_repository_broker.IotMqttBrokerConfig>,
                      'broker_id_2' : <iot_repository_broker.IotMqttBrokerConfig>,
                      ...
                      'broker_id_N' : <iot_repository_broker.IotMqttBrokerConfig> }
            se_config : iot_repository_sensor.IotSensorConfig
                Settings for the MQTT brokers and topics to be used to publish and subscribe to.
            sensor : iot_sensor_base.IotSensor
                Sensor object to be controlled by the handler.
            logger : logging.Logger
                Logger to be used by the handler.
        """
        mqtt_input = None
        mqtt_data = None
        mqtt_health = None
        if len(se_config.input_broker_id) > 0 and len(se_config.input_topic) > 0:
            broker = brokers[se_config.input_broker_id]
            consumer = wp_queueing.MQTTConsumer(broker_host = broker.broker_host,
                                                broker_port = broker.broker_port,
                                                logger = logger)
            mqtt_input = (consumer, se_config.input_topic)
        if len(se_config.data_broker_id) > 0 and len(se_config.data_topic) > 0:
            broker = brokers[se_config.data_broker_id]
            producer = wp_queueing.MQTTProducer(broker_host = broker.broker_host,
                                                broker_port = broker.broker_port,
                                                logger = logger)
            mqtt_data = (producer, se_config.data_topic)
        if len(se_config.health_broker_id) > 0 and len(se_config.health_topic) > 0:
            if se_config.health_broker_id == se_config.data_broker_id:
                producer = mqtt_data[0]
            else:
                broker = brokers[se_config.data_broker_id]
                producer = wp_queueing.MQTTProducer(broker_host = broker.broker_host,
                                                    broker_port = broker.broker_port,
                                                    logger = logger)
            mqtt_health = (producer, se_config.health_topic)
        new_handler = iot_sensor_handler.IotSensorHandler(sensor, logger,
                                                          mqtt_data = mqtt_data,
                                                          mqtt_input = mqtt_input,
                                                          mqtt_health = mqtt_health)
        return new_handler
