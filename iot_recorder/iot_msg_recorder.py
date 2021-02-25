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
import uuid
import logging
import wp_queueing
import wp_repository
import iot_handler_base
import iot_msg_input
import iot_msg_sensor
import iot_repository_broker
import iot_stat_msg

class IotMessageRecorder(iot_handler_base.IotHandlerBase):
    """ Handler (derived from IotHandlerBased) that subscribes to a MQTT broker and stores received
        messages in a repository.

    Attributes:
        _mqtt_consumer : wp_queueing.MQTTconsumer
            Open session to a MQTT broker.
        _sqlite_db_path : str
            Full path name of the SQLite database where the messages shall be stored.

    Properties:
        device_id : str
            Getter for the unique identifier of the recorder.
        device_type : str
            Getter for the "device type". Implemented for compatibility reasons.
        device_model : str
            Getter for the "device model". Implemented for compatibility reasons.

    Methods:
        IotMessageRecorder : None
            Constructor.
        polling_timer_interval : None
            Function (overloaded from super() class) that will be called when the polling timer expires.
        message : None
            Function called by the MQTT broker session handler when a message is received.
    """
    def __init__(self, broker_config: iot_repository_broker.IotMqttBrokerConfig,
                 topics: Any, sqlite_db_path: str, logger: logging.Logger):
        """ Constructor.

        Parameters:
            broker_config : iot_repository_broker.IotMqttBrokerConfig
                Configuration for the MQTT broker to connect to.
            topics : Any (str or list)
                Topics to subscribe to.
            sqlite_db_path : str
                Full path name of the target SQLite database.
        """
        super().__init__(5, 600, None, None, None)
        self._logger = logger
        self._mqtt_consumer = wp_queueing.MQTTConsumer(
            broker_host = broker_config.broker_host,
            broker_port = broker_config.broker_port,
            logger = self._logger)
        self._mqtt_consumer.owner = self
        if isinstance(topics, list):
            self._mqtt_consumer.topics = topics
        else:
            self._mqtt_consumer.topics = [topics]
        self._sqlite_db_path = sqlite_db_path
        self._recorder_id = f'Rec.{broker_config.broker_id}.{str(uuid.uuid4()).replace("-","")}'

    @property
    def device_id(self) -> str:
        """ Getter for the unique identifier of the recorder. """
        return self._recorder_id

    @property
    def device_type(self) -> str:
        """ Getter for the "device type". Implemented for compatibility reasons. """
        return "IotMessageRecorder"

    @property
    def device_model(self) -> str:
        """ Getter for the "device model". Implemented for compatibility reasons. """
        return self.device_type

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
        msg_base = iot_stat_msg.IotRecorderMsg(msg)
        msg_payload = msg.msg_payload
        try:
            if 'class' in msg_payload:
                msg_base.msg_class = msg_payload['class']
                if msg_payload['class'] == 'InputProbe':
                    conv_msg = iot_msg_input.InputProbe()
                    conv_msg.from_dict(msg_payload)
                    rec_msg = iot_stat_msg.IotRecorderInputProbe(msg_base.msg_id, conv_msg)
                elif msg_payload['class'] == 'InputHealth':
                    conv_msg = iot_msg_input.InputHealth()
                    conv_msg.from_dict(msg_payload)
                    rec_msg = iot_stat_msg.IotRecorderInputHealth(msg_base.msg_id, conv_msg)
                elif msg_payload['class'] == 'SensorMsmt':
                    conv_msg = iot_msg_sensor.SensorMsmt()
                    conv_msg.from_dict(msg_payload)
                    rec_msg = iot_stat_msg.IotRecorderSensorMsg(msg_base.msg_id, conv_msg)
                else:
                    rec_msg = iot_stat_msg.IotRecorderGenericMsg(msg_base.msg_id, msg_payload)
            else:
                rec_msg = iot_stat_msg.IotRecorderGenericMsg(msg_base.msg_id, msg_payload)
        except TypeError:
            rec_msg = iot_stat_msg.IotRecorderGenericMsg(msg_base.msg_id, msg_payload)
        except ValueError:
            rec_msg = iot_stat_msg.IotRecorderGenericMsg(msg_base.msg_id, msg_payload)

        with wp_repository.SQLiteRepository(iot_stat_msg.IotRecorderMsg, self._sqlite_db_path) as repository:
            repository.insert(msg_base)
        with wp_repository.SQLiteRepository(type(rec_msg), self._sqlite_db_path) as repository:
            repository.insert(rec_msg)
