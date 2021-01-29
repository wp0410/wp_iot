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
from datetime import datetime
import wp_repository

class IotHardwareConfig(wp_repository.RepositoryElement):
    """ Database mapping class for IOT hardware components.

    Attributes:
        hardware_id : str
            Unique identification of an IOT hardware component.
        hardware_type : str
            Describes the type of hardware component, e.g. "ADS1115", "MCP23917".
        if_type : str
            Hardware protocol by which the component is connected ("I2C", "SPI").
        i2c_bus_id : int
            Number of the I2C bus the hardware component is connected to.
        i2c_bus_address : int
            I2C bus address of the hardware component.
        polling_intervale : int
            Interval (in seconds) for the handler software to poll the hardware component
            or to poll the command queue.
        data_broker_id : str
            Unique identification of the MQTT broker to be used to publish data messages.
        data_topic : str
            Prefix for the topic to be used for publishing hardware input to the
            MQTT broker.
        input_broker_id : str
            Unique identification of the MQTT broker to be used to subscribe to command
            messages.
        input_topic : str
            Prefix for the topic to be subscribed for outputs to the hardare component.
        health_broker_id : str
            Unique identification of the MQTT broker to be used to publish health
            messages.
        health_topic : str
            Prefix of the topic to be used for publishing health check messages.
        store_date : datetime
            Date and time when the instance was stored in the database.

    Properties:
        store_date_str : str
            Getter for the last change date and time as string.

    Methods:
        IotHardwareConfig()
            Constructor.
    """
    # pylint: disable=too-many-instance-attributes, too-few-public-methods
    _attribute_map = wp_repository.AttributeMap(
        "iot_hardware_component",
        [wp_repository.AttributeMapping(0,  "device_id", "device_id", str, db_key = 1),
         wp_repository.AttributeMapping(1,  "device_type", "device_type", str),
         wp_repository.AttributeMapping(2,  "model", "model", str),
         wp_repository.AttributeMapping(3,  "if_type", "if_type", str),
         wp_repository.AttributeMapping(4,  "i2c_bus_id", "i2c_bus_id", int),
         wp_repository.AttributeMapping(5,  "i2c_bus_address", "i2c_bus_addr", int),
         wp_repository.AttributeMapping(6,  "polling_interval", "polling_interval", int),
         wp_repository.AttributeMapping(7,  "data_broker_id", "data_broker_id", str),
         wp_repository.AttributeMapping(8,  "data_topic", "data_topic", str),
         wp_repository.AttributeMapping(9,  "input_broker_id", "input_broker_id", str),
         wp_repository.AttributeMapping(10, "input_topic", "input_topic", str),
         wp_repository.AttributeMapping(11, "health_broker_id", "health_broker_id", str),
         wp_repository.AttributeMapping(12, "health_topic", "health_topic", str),
         wp_repository.AttributeMapping(13, "store_date", "store_date", datetime)])

    def __init__(self):
        """ Constructor. """
        super().__init__()
        self.device_id = ""
        self.device_type = ""
        self.if_type = "I2C"
        self.i2c_bus_id = 0
        self.i2c_bus_address = 0
        self.polling_interval = 30
        self.data_broker_id = ""
        self.data_topic = "hw/data"
        self.input_broker_id = ""
        self.input_topic = "hw/cmd"
        self.health_broker_id = ""
        self.health_topic = "hw/health"
        self.store_date = datetime.now()

    @property
    def store_date_str(self) -> str:
        """ Getter for the last change date and time as string.

        Returns:
            store_date converted to a string.
        """
        return self.store_date.strftime("%Y-%m-%d %H:%M:%S")
