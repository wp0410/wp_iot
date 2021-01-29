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

class IotMqttBrokerConfig(wp_repository.RepositoryElement):
    """ Database mapping class for IOT broker settings.

    Attributes:
        broker_id : str
            Unique identification of a MQTT broker.
        broker_host : str
            IP-address or host name of the MQTT broker.
        broker_port : int
            Listening port number of the MQTT broker on "broker_host".
        store_date : datetime
            Date and time of last change in the database.

    Properties:
        store_date_str : str
            Getter for the last change date and time as string.

    Methods:
        IotMqttBrokerConfig()
            Constructor.
    """
    # pylint: disable=too-many-instance-attributes, too-few-public-methods
    _attribute_map = wp_repository.AttributeMap(
        "iot_mqtt_broker",
        [wp_repository.AttributeMapping(0, "broker_id", "broker_id", str, db_key = 1),
         wp_repository.AttributeMapping(1, "broker_host", "broker_host", str),
         wp_repository.AttributeMapping(2, "broker_port", "broker_port", int),
         wp_repository.AttributeMapping(3, "store_date", "store_date", datetime)])

    def __init__(self):
        """ Constructor. """
        super().__init__()
        self.broker_id = ""
        self.broker_host = "localhost"
        self.broker_port = 1883
        self.store_date = datetime.now()

    @property
    def store_date_str(self) -> str:
        """ Getter for the last change date and time as string.

        Returns:
            store_date converted to a string.
        """
        return self.store_date.strftime("%Y-%m-%d %H:%M:%S")
