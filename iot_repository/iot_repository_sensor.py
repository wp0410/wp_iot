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

class IotSensor(wp_repository.RepositoryElement):
    """ Database mapping class for IOT sensors.

    Attributes:
        sensor_id : str
            Unique identification of the IOT sensor.
        broker_id : str
            Unique identification of the MQTT broker to be used to publish and subscribe to
            messages.
        sensor_type : str
            Type of the sensor.
        hardware_id : str
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
        IotSensor()
            Constructor.
    """
    # pylint: disable=too-many-instance-attributes, too-few-public-methods
    _attribute_map = wp_repository.AttributeMap(
        "iot_sensor",
        [wp_repository.AttributeMapping(0, "sensor_id", "sensor_id", str, db_key = 1),
         wp_repository.AttributeMapping(1, "broker_id", "broker_id", str),
         wp_repository.AttributeMapping(2, "sensor_type", "sensor_type", str),
         wp_repository.AttributeMapping(3, "hardware_id", "hardware_id", str),
         wp_repository.AttributeMapping(4, "hw_channel", "hw_channel", int),
         wp_repository.AttributeMapping(5, "polling_interval", "polling_interval", int),
         wp_repository.AttributeMapping(6, "topic_input", "topic_input", str),
         wp_repository.AttributeMapping(7, "topic_data", "topic_data", str),
         wp_repository.AttributeMapping(8, "topic_health", "topic_health", str),
         wp_repository.AttributeMapping(9, "store_date", "store_date", datetime)])

    def __init__(self):
        """ Constructor. """
        super().__init__()
        self.sensor_id = ""
        self.broker_id = ""
        self.sensor_type = ""
        self.hardware_id = ""
        self.hw_channel = 0
        self.polling_interval = 15
        self.topic_input = ""
        self.topic_data = ""
        self.topic_health = ""
        self.store_date = datetime.now()

    @property
    def store_date_str(self) -> str:
        """ Getter for the last change date and time as string.

        Returns:
            store_date converted to a string.
        """
        return self.store_date.strftime("%Y-%m-%d %H:%M:%S")
