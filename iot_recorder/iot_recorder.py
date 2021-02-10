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
from datetime import datetime
import json
import uuid
import wp_queueing
import wp_repository
import iot_handler_base
import iot_msg_input

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
        wp_repository.AttributeMapping(0, "msg_id", "msg_id", str, db_key = 1),
        wp_repository.AttributeMapping(1, "msg_topic", "msg_topic", str),
        wp_repository.AttributeMapping(2, "msg_timestamp", "msg_timestamp", str),
        wp_repository.AttributeMapping(3, "msg_class", "msg_class", str),
        wp_repository.AttributeMapping(4, "store_date", "store_date", datetime))

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
        "iot_recorder_gen_msg",
        wp_repository.AttributeMapping(0, "msg_id", "msg_id", str, db_key = 1),
        wp_repository.AttributeMapping(1, "msg_payload", "msg_payload", str),
        wp_repository.AttributeMapping(2, "store_date", "store_date", datetime))

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
        wp_repository.AttributeMapping(0, "msg_id", "msg_id", str, db_key = 1),
        wp_repository.AttributeMapping(1, "device_type", "device_type", str),
        wp_repository.AttributeMapping(2, "device_id", "device_id", str),
        wp_repository.AttributeMapping(3, "probe_time", "probe_time", str),
        wp_repository.AttributeMapping(4, "channel_no", "channel_no", int),
        wp_repository.AttributeMapping(5, "value", "value", int),
        wp_repository.AttributeMapping(6, "voltage", "voltage", float),
        wp_repository.AttributeMapping(7, "store_date", "store_date", datetime))

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
            f'voltage: "{self.voltage}"', f'store_date: "{self.store_date_str}"')


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
        "iot_recorder_input_probe",
        wp_repository.AttributeMapping(0, "msg_id", "msg_id", str, db_key = 1),
        wp_repository.AttributeMapping(1, "device_type", "device_type", str),
        wp_repository.AttributeMapping(2, "device_id", "device_id", str),
        wp_repository.AttributeMapping(3, "health_time", "health_time", str),
        wp_repository.AttributeMapping(4, "health_status", "health_status", int),
        wp_repository.AttributeMapping(5, "last_probe_time", "last_probe_time", str),
        wp_repository.AttributeMapping(6, "num_probe_total", "num_probe_total", int),
        wp_repository.AttributeMapping(7, "num_probe_detail", "num_probe_detail", str),
        wp_repository.AttributeMapping(8, "store_date", "store_date", datetime))

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


class IotMessageRecorder(iot_handler_base.IotHandlerBase):
    """ Handler (derived from IotHandlerBased) that subscribes to a MQTT broker and stores received
        messages in a repository.

    Attributes:
        _mqtt_consumer : wp_queueing.MQTTconsumer
            Open session to a MQTT broker.
        _sqlite_db_path : str
            Full path name of the SQLite database where the messages shall be stored.

    Properties:
        handler_id : str
            Getter for the unique identifier of the recorder.

    Methods:
        IotMessageRecorder : None
            Constructor.
        polling_timer_interval : None
            Function (overloaded from super() class) that will be called when the polling timer expires.
        message : None
            Function called by the MQTT broker session handler when a message is received.
    """
    def __init__(self, broker_config: dict, topics: Any, sqlite_db_path: str):
        """ Constructor.

        Parameters:
            broker_config : dict
                Configuration for the MQTT broker to connect to.
            topics : Any (str or list)
                Topics to subscribe to.
            sqlite_db_path : str
                Full path name of the target SQLite database.
        """
        super().__init__(5, 600, None, None, None)
        self._mqtt_consumer = wp_queueing.MQTTConsumer(broker_config['host'], broker_config['port'])
        self._mqtt_consumer.owner = self
        topic_list = []
        if isinstance(topics, list):
            for topic in topics:
                if isinstance(topic, tuple):
                    topic_list.append(topic)
                else:
                    topic_list.append((topic, 0))
        else:
            topic_list.append((topics, 0))
        self._mqtt_consumer.topics = topic_list
        self._sqlite_db_path = sqlite_db_path
        self._recorder_id = f'Rec.{broker_config["broker_id"]}.{str(uuid.uuid4()).replace("-","")}'

    @property
    def handler_id(self) -> str:
        """ Getter for the unique identifier of the recorder. """
        return self._recorder_id

    def polling_timer_event(self) -> None:
        """ Function (overloaded from super() class) that will be called when the polling timer expires. """
        super().polling_timer_event()
        self._mqtt_consumer.receive()

    def message(self, msg: wp_queueing.QueueMessage) -> None:
        """ Function called by the MQTT broker session handler when a message is received.

        Parameters:
            msg : wp_queueing.QueueMessage
                Message received from the MQTT broker.
        """
        msg_base = IotRecorderMsg(msg)
        msg_payload = msg.msg_payload
        try:
            if 'class' in msg_payload:
                msg_base.msg_class = msg_payload['class']
                if msg_payload['class'] == 'InputProbe':
                    conv_msg = iot_msg_input.InputProbe()
                    conv_msg.from_dict(msg_payload)
                    rec_msg = IotRecorderInputProbe(msg_base.msg_id, conv_msg)
                elif msg_payload['class'] == 'InputHealth':
                    conv_msg = iot_msg_input.InputHealth()
                    conv_msg.from_dict(msg_payload)
                    rec_msg = IotRecorderInputHealth(msg_base.msg_id, conv_msg)
                else:
                    rec_msg = IotRecorderGenericMsg(msg_base.msg_id, msg_payload)
            else:
                rec_msg = IotRecorderGenericMsg(msg_base.msg_id, msg_payload)
        except TypeError:
            rec_msg = IotRecorderGenericMsg(msg_base.msg_id, msg_payload)
        except ValueError:
            rec_msg = IotRecorderGenericMsg(msg_base.msg_id, msg_payload)

        with wp_repository.SQLiteRepository(IotRecorderMsg, self._sqlite_db_path) as repository:
            repository.insert(msg_base)
        with wp_repository.SQLiteRepository(type(rec_msg), self._sqlite_db_path) as repository:
            repository.insert(rec_msg)
