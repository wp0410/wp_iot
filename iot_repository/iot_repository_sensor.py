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

class IotSensorConfig(wp_repository.RepositoryElement):
    """ Database mapping class for IOT sensors.

    Attributes:
        sensor_id : str
            Unique identification of the IOT sensor.
        broker_id : str
            Unique identification of the MQTT broker to be used to publish and subscribe to
            messages.
        sensor_type : str
            Type of the sensor.
        device_id : str
            Unique identification of the hardware component the IOT sensor is connected to.
        hw_channel : int
            Number of the input channel of the hardware component the IOT sensor is connected to.
        polling_interval : int
            Interval (in seconds) for polling the MQTT for messages on the input queue.
        topic_input : str
            Topic to subscribe to for receiving input data from the IOT hardware component the
            sensor is connected to.
        topic_data : str
            Topic for publishing the measurement results of the IOT sensor.
        topic_health : str
            Topic for publishing health and statistics messages.
        store_date : str
            Date and time when the object was stored in the database.

    Properties:
        store_date_str : str
            Getter for the last change date and time as string.

    Methods:
        IotSensorConfig()
            Constructor.
    """
    # pylint: disable=too-many-instance-attributes, too-few-public-methods
    _attribute_map = wp_repository.AttributeMap(
        "iot_sensor",
        [wp_repository.AttributeMapping(0,  "sensor_id", "sensor_id", str, db_key = 1),
         wp_repository.AttributeMapping(1,  "sensor_type", "sensor_type", str),
         wp_repository.AttributeMapping(2,  "device_id", "device_id", str),
         wp_repository.AttributeMapping(3,  "hw_channel", "hw_channel", int),
         wp_repository.AttributeMapping(4,  "polling_interval", "polling_interval", int),
         wp_repository.AttributeMapping(5,  "input_broker_id", "input_broker_id", str),
         wp_repository.AttributeMapping(6,  "input_topic", "input_topic", str),
         wp_repository.AttributeMapping(7,  "data_broker_id", "data_broker_id", str),
         wp_repository.AttributeMapping(8,  "data_topic", "data_topic", str),
         wp_repository.AttributeMapping(9,  "health_broker_id", "health_broker_id", str),
         wp_repository.AttributeMapping(10, "health_topic", "health_topic", str),
         wp_repository.AttributeMapping(11, "store_date", "store_date", datetime)])

    def __init__(self):
        """ Constructor. """
        super().__init__()
        self.sensor_id = ""
        self.host_id = ""
        self.sensor_type = ""
        self.device_id = ""
        self.hw_channel = 0
        self.polling_interval = 15
        self.input_broker_id = ""
        self.input_topic = "sensor/input"
        self.data_broker_id = ""
        self.data_topic = "sensor/data"
        self.health_broker_id = ""
        self.health_topic = "sensor/health"
        self.store_date = datetime.now()

    @property
    def store_date_str(self) -> str:
        """ Getter for the last change date and time as string.

        Returns:
            store_date converted to a string.
        """
        return self.store_date.strftime("%Y-%m-%d %H:%M:%S")
