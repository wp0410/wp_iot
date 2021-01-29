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

class IotHostConfig(wp_repository.RepositoryElement):
    """ Database mapping class for IOT host settings.

    Attributes:
        host_id : str
            Unique identification of a MQTT broker.
        host_ip : str
            IP-address or host name of the MQTT broker.
        store_date : datetime
            Date and time of last change in the database.

    Properties:
        store_date_str : str
            Getter for the last change date and time as string.

    Methods:
        IotHost()
            Constructor.
    """
    _attribute_map = wp_repository.AttributeMap(
        "iot_host",
        [wp_repository.AttributeMapping(0, "host_id", "host_id", str, db_key = 1),
         wp_repository.AttributeMapping(1, "host_ip", "host_ip", str),
         wp_repository.AttributeMapping(2, "store_date", "store_date", datetime)])

    def __init__(self):
        """ Constructor. """
        super().__init__()
        self.host_id = ""
        self.host_ip = ""
        self.store_date = datetime.now()

    @property
    def store_date_str(self) -> str:
        """ Getter for the last change date and time as string.

        Returns:
            store_date converted to a string.
        """
        return self.store_date.strftime("%Y-%m-%d %H:%M:%S")

class IotHostAssignedComponent(wp_repository.RepositoryElement):
    """ Database mapping class for components that are assigned to an IOT host.

    Attributes:
        host_id : str
            Unique identification of the IOT host. Foreign key to IotHost.host_id.
        comp_id : str
            Unique identifier of the assigned component (hardware device, sensor, etc.)
        process_group : int
            Number of the process group within which the component shall be handled.
            All components havint the same process_group value are started as threads
            within the same process.
        store_date : datetime
            Date and time of the last change in the database.

    Properties:
        store_date_str : str
            Getter for the last change date and time as string.

    Methods:
        IotHostAssignedComponent()
            Constructor.
    """
    _attribute_map = wp_repository.AttributeMap(
        "iot_host_component",
        [wp_repository.AttributeMapping(0, "host_id", "host_id", str, db_key = 1),
         wp_repository.AttributeMapping(1, "comp_id", "comp_id", str, db_key = 1),
         wp_repository.AttributeMapping(2, "process_group", "process_group", int),
         wp_repository.AttributeMapping(3, "store_date", "store_date", datetime)])

    def __init__(self):
        """ Constructor. """
        super().__init__()
        self.host_id = ""
        self.comp_id = ""
        self.store_date = datetime.now()

    @property
    def store_date_str(self) -> str:
        """ Getter for the last change date and time as string.

        Returns:
            store_date converted to a string.
        """
        return self.store_date.strftime("%Y-%m-%d %H:%M:%S")
