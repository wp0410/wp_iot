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
import json
import wp_repository
import wp_queueing
import iot_msg_input
import iot_msg_sensor

class IotRecorderMsg(wp_repository.RepositoryElement):
    """ Model for the general part of received messages to be stored in a repository. Derived from
        wp_repository.RepositoryElement.

    Attributes:
        msg_id : str
            Unique identifier of a received queueing message.
        msg_topic : str
            Topic from which the message was retrieved.
        msg_timestamp : str
            Date and time when the message was published.
        msg_class : str
            Class name of the message payload.
        store_date : datetime
            Date and time when the record was stored in the repository.

    Properties:
        store_date_str : str
            Getter for the last change date and time as string.

    Methods:
        IotRecorderMsg : None
            Constructor.
        __str__ : str
            Create printable character string from object.
    """
    _attribute_map = wp_repository.AttributeMap(
        "iot_recorder_msg",
        [wp_repository.AttributeMapping(0, "msg_id", "msg_id", str, db_key = 1),
         wp_repository.AttributeMapping(1, "msg_topic", "msg_topic", str),
         wp_repository.AttributeMapping(2, "msg_timestamp", "msg_timestamp", str),
         wp_repository.AttributeMapping(3, "msg_class", "msg_class", str),
         wp_repository.AttributeMapping(4, "store_date", "store_date", datetime)])

    def __init__(self, qmsg: wp_queueing.QueueMessage = None):
        """ Constructor. """
        super().__init__()
        if qmsg is None:
            self.msg_id = ""
            self.msg_topic = ""
            self.msg_timestamp = None
        else:
            self.msg_id = qmsg.msg_id
            self.msg_topic = qmsg.msg_topic
            self.msg_timestamp = qmsg.msg_timestamp
        self.msg_class = ""
        self.store_date = datetime.now()

    @property
    def store_date_str(self) -> str:
        """ Getter for the last change date and time as string.

        Returns:
            store_date converted to a string.
        """
        return self.store_date.strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self) -> str:
        """ Create printable character string from object. """
        return 'IotRecorderMsg({}, {}, {}, {})'.format(
            f'msg_id: "{self.msg_id}"', f'msg_topic: "{self.msg_topic}"',
            f'msg_timestamp: "{self.msg_timestamp}"', f'store_date: "{self.store_date_str}"')


class IotRecorderGenericMsg(wp_repository.RepositoryElement):
    """ Model for messages received from the MQTT broker the type of which can not be identfied or that can't
        be converted to the corresponding message class.

    Attributes:
        msg_id : str
            Unique identifier of a received queueing message.
        msg_payload : str
            Payload of the received message.
        store_date : datetime
            Date and time when the record was stored in the repository.

    Properties:
        store_date_str : str
            Getter for the last change date and time as string.

    Methods:
        IotRecorderGenericMsg : None
            Constructor.
        __str__ : str
            Create printable character string from object.
    """
    _attribute_map = wp_repository.AttributeMap(
        "iot_recorder_generic",
        [wp_repository.AttributeMapping(0, "msg_id", "msg_id", str, db_key = 1),
         wp_repository.AttributeMapping(1, "msg_payload", "msg_payload", str),
         wp_repository.AttributeMapping(2, "store_date", "store_date", datetime)])

    def __init__(self, msg_id: str, msg_payload: dict):
        """ Constructor. """
        super().__init__()
        self.msg_id = msg_id
        if msg_payload is None:
            self.msg_payload = ""
        else:
            self.msg_payload = json.dumps(msg_payload)
        self.store_date = datetime.now()

    @property
    def store_date_str(self) -> str:
        """ Getter for the last change date and time as string.

        Returns:
            store_date converted to a string.
        """
        return self.store_date.strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self) -> str:
        """ Create printable character string from object. """
        return 'IotRecorderGenericMsg({}, {}, {})'.format(
            f'msg_id: "{self.msg_id}"', f'msg_payload: "{self.msg_payload}"',
            f'store_date: "{self.store_date_str}"')


class IotRecorderInputProbe(wp_repository.RepositoryElement):
    """ Model for "InputProbe" messages received from the MQTT broker.

    Attributes:
        msg_id : str
            Unique identifier of a received queueing message.
        device_type : str
            Type of the device that created the InputProble message.
        device_id : str
            Unique identifier of the device that created the InputProbe message.
        probe_time : str
            Date and time when the InputProbe message was generated.
        channel_no : int
            Number of the input channel read for the probe.
        value : int
            Value read from the input channel.
        voltage : float
            Voltage detected on the input channel.
        store_date : datetime
            Date and time when the record was stored in the repository.

    Properties:
        store_date_str : str
            Getter for the last change date and time as string.

    Methods:
        IotRecorderInputProbe : None
            Constructor.
        __str__ : str
            Create printable character string from object.
    """
    # pylint: disable=too-many-instance-attributes
    _attribute_map = wp_repository.AttributeMap(
        "iot_recorder_input_probe",
        [wp_repository.AttributeMapping(0, "msg_id", "msg_id", str, db_key = 1),
         wp_repository.AttributeMapping(1, "device_type", "device_type", str),
         wp_repository.AttributeMapping(2, "device_id", "device_id", str),
         wp_repository.AttributeMapping(3, "probe_time", "probe_time", str),
         wp_repository.AttributeMapping(4, "channel_no", "channel_no", int),
         wp_repository.AttributeMapping(5, "value", "value", int),
         wp_repository.AttributeMapping(6, "voltage", "voltage", float),
         wp_repository.AttributeMapping(7, "store_date", "store_date", datetime)])

    def __init__(self, msg_id: str, msg: iot_msg_input.InputProbe):
        """ Constructor. """
        self.msg_id = msg_id
        self.device_type =  msg.device_type
        self.device_id = msg.device_id
        self.probe_time = msg.probe_time
        self.channel_no = msg.channel_no
        self.value = msg.value
        self.voltage = msg.voltage
        self.store_date = datetime.now()

    @property
    def store_date_str(self) -> str:
        """ Getter for the last change date and time as string.

        Returns:
            store_date converted to a string.
        """
        return self.store_date.strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self) -> str:
        """ Create printable character string from object. """
        return 'IotRecorderInputProbe({}, {}, {}, {}, {}, {}, {}, {})'.format(
            f'msg_id: "{self.msg_id}"', f'device_type: "{self.device_type}"',
            f'device_id: "{self.device_id}"', f'probe_time: "{self.probe_time}"',
            f'channel_no: "{self.channel_no}"', f'value: "{self.value}"',
            f'voltage: "{self.voltage:.5f}"', f'store_date: "{self.store_date_str}"')


class IotRecorderSensorMsg(wp_repository.RepositoryElement):
    """ Model for "SensorMeasurement" messages received from the MQTT broker.

    Attributes:
        msg_id : str
            Unique identifier of a received queueing message.
        sensor_type : str
            Type of the sensor that created the measurement message.
        sensor_id : str
            Unique identifier of the sensor that created the measurement message.
        msmt_time : str
            Date and time when the measurement values were calculated.
        hw_value : int
            Input value for the sensor measurement.
        hw_voltage : float
            Measured voltage.
        msmt_unit : str
            Unit of the measurement value.
        msmt_value : float
            Calculated measurement value in the given unit.
        store_date : datetime
            Date and time when the record was stored in the repository.

    Properties:
        store_date_str : str
            Getter for the last change date and time as string.

    Methods:
        IotRecorderSensorMsg
            Constructor.
        __str__ : str
            Create printable character string from object.
    """
    # pylint: disable=too-many-instance-attributes
    _attribute_map = wp_repository.AttributeMap(
        "iot_recorder_sensor_msmt",
        [wp_repository.AttributeMapping(0, "msg_id", "msg_id", str, db_key = 1),
         wp_repository.AttributeMapping(1, "sensor_type", "sensor_type", str),
         wp_repository.AttributeMapping(2, "sensor_id", "sensor_id", str),
         wp_repository.AttributeMapping(3, "msmt_time", "msmt_time", str),
         wp_repository.AttributeMapping(4, "hw_value", "hw_value", int),
         wp_repository.AttributeMapping(5, "hw_voltage", "hw_voltage", float),
         wp_repository.AttributeMapping(6, "msmt_unit", "msmt_unit", str),
         wp_repository.AttributeMapping(7, "msmt_value", "msmt_value", float),
         wp_repository.AttributeMapping(8, "store_date", "store_date", datetime)])

    def __init__(self, msg_id: str, msg: iot_msg_sensor.SensorMsmt):
        """ Constructor.

        Parameters:
            msg_id : str
                Unique identifier of the received QueueMessage.
            msg : iot_msg_sensor.SensorMeasurement
                Payload of the received QueueMessage to be stored in the repository.
        """
        self.msg_id = msg_id
        self.sensor_type = msg.sensor_type
        self.sensor_id = msg.sensor_id
        self.msmt_time = msg.msmt_time
        self.hw_value = msg.hw_value
        self.hw_voltage = msg.hw_voltage
        self.msmt_unit = msg.msmt_unit
        self.msmt_value = msg.msmt_value
        self.store_date = datetime.now()

    @property
    def store_date_str(self) -> str:
        """ Getter for the last change date and time as string.

        Returns:
            store_date converted to a string.
        """
        return self.store_date.strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self) -> str:
        """ Create printable character string from object. """
        return 'IotRecorderSensorMsg({} {} {} {} {} {} {} {} {})'.format(
            f'msg_id: "{self.msg_id}"', f'sensor_type: "{self.sensor_type}"',
            f'sensor_id: "{self.sensor_id}"', f'msmt_time: "{self.msmt_time}"',
            f'hw_value: "{self.hw_value}"', f'hw_voltage: "{self.hw_voltage:.5f}"',
            f'msmt_unit: "{self.msmt_unit}"', f'msmt_value: "{self.msmt_value:.2f}"',
            f'store_date: "{self.store_date_str}"')


class IotRecorderInputHealth(wp_repository.RepositoryElement):
    """

    Attributes:
        msg_id : str
            Unique identifier of a received queueing message.
        device_type : str
            Type of the device that created the InputHealth message.
        device_id : str
            Unique identifier of the device that created the InputHealth message.
        health_time : str
            Date and time when the health check was executed.
        health_status : int
            Result of the health check.
        last_probe_time : str
            Date and time of the last probe message sent.
        num_probe_total : int
            Total number of input readings.
        num_probe_detail : list, optional
            Number of input readings per input channel.
        store_date : datetime
            Date and time when the record was stored in the repository.

    Properties:
        store_date_str : str
            Getter for the last change date and time as string.

    Methods:
        IotRecorderInputHealth : None
            Constructor.
        __str__ : str
            Create printable character string from object.
    """
    # pylint: disable=too-many-instance-attributes
    _attribute_map = wp_repository.AttributeMap(
        "iot_recorder_input_health",
        [wp_repository.AttributeMapping(0, "msg_id", "msg_id", str, db_key = 1),
         wp_repository.AttributeMapping(1, "device_type", "device_type", str),
         wp_repository.AttributeMapping(2, "device_id", "device_id", str),
         wp_repository.AttributeMapping(3, "health_time", "health_time", str),
         wp_repository.AttributeMapping(4, "health_status", "health_status", int),
         wp_repository.AttributeMapping(5, "last_probe_time", "last_probe_time", str),
         wp_repository.AttributeMapping(6, "num_probe_total", "num_probe_total", int),
         wp_repository.AttributeMapping(7, "num_probe_detail", "num_probe_detail", str),
         wp_repository.AttributeMapping(8, "store_date", "store_date", datetime)])

    def __init__(self, msg_id: str, msg: iot_msg_input.InputHealth):
        """ Constructor. """
        super().__init__()
        self.msg_id = msg_id
        self.device_type =  msg.device_type
        self.device_id = msg.device_id
        self.health_time = msg.health_time
        self.health_status = msg.health_status
        self.last_probe_time = msg.last_probe_time
        self.num_probe_total = msg.num_probe_total
        self.num_probe_detail = json.dumps(msg.num_probe_detail)
        self.store_date = datetime.now()

    @property
    def store_date_str(self) -> str:
        """ Getter for the last change date and time as string.

        Returns:
            store_date converted to a string.
        """
        return self.store_date.strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self) -> str:
        """ Create printable character string from object. """
        return 'IotRecorderInputHealth({}, {}, {}, {}, {}, {}, {}, {}, {})'.format(
            f'msg_id: "{self.msg_id}"', f'device_type: "{self.device_type}"',
            f'device_id: "{self.device_id}"', f'health_time: "{self.health_time}"',
            f'health_status: "{self.health_status}"', f'last_probe_time: "{self.last_probe_time}"',
            f'num_probe_total: "{self.num_probe_total}"', f'num_probe_detail: "{self.num_probe_detail}"',
            f'store_date: "{self.store_date_str}"')
