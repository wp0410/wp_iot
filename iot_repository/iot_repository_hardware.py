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

class IotHardwareComponent(wp_repository.RepositoryElement):
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
        topic_data : str
            Prefix for the topic to be used for publishing hardware input to the
            MQTT broker.
        topic_cmd : str
            Prefix for the topic to be subscribed for outputs to the hardare component.
        topic_health : str
            Prefix of the topic to be used for publishing health check messages.
        store_date : datetime
            Date and time when the instance was stored in the database.

    Methods:
        IotHardwareComponent()
            Constructor.
    """
    # pylint: disable=too-many-instance-attributes, too-few-public-methods
    _attribute_map = wp_repository.AttributeMap(
        "iot_hardware_component",
        [wp_repository.AttributeMapping(0, "hardware_id", "hardware_id", str, db_key = 1),
         wp_repository.AttributeMapping(1, "hardware_type", "hardware_type", str),
         wp_repository.AttributeMapping(2, "if_type", "if_type", str),
         wp_repository.AttributeMapping(3, "i2c_bus_id", "i2c_bus_id", int),
         wp_repository.AttributeMapping(4, "i2c_bus_address", "i2c_bus_addr", int),
         wp_repository.AttributeMapping(5, "polling_interval", "polling_interval", int),
         wp_repository.AttributeMapping(6, "topic_data", "topic_data", str),
         wp_repository.AttributeMapping(7, "topic_cmd", "topic_cmd", str),
         wp_repository.AttributeMapping(8, "topic_health", "topic_health", str),
         wp_repository.AttributeMapping(9, "store_date", "store_date", datetime)])

    def __init__(self):
        """ Constructor. """
        super().__init__()
        self.hardware_id = ""
        self.hardware_type = ""
        self.if_type = "I2C"
        self.i2c_bus_id = 0
        self.i2c_bus_address = 0
        self.polling_interval = 30
        self.topic_data = "hw/input"
        self.topic_cmd = "hw/output"
        self.topic_health = "hw/health"
        self.store_date = datetime.now()
