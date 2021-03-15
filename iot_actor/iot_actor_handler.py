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
import inspect
import logging
from datetime import datetime
import wp_queueing
import iot_msg_actor
import iot_handler_base
import iot_actor_base

class IotActorHandler(iot_handler_base.IotHandlerBase):
    """ Handler controlling an IOT actor. Derived from the base class defined in iot_handler_base.

    Attributes:
        _actor : iot_actor_base.IotActor
            The controlled actor element.
        logger : logging.Logger
            The logger to be used.
        For more attributes, see iot_handler_base.IotHandlerBase.

    Properties:
        element_id : str
            Getter for the unique identifier of the controlled actor.
        element_type : str
            Getter for the type (model) of the controlled actor.
        element_model : str
            Getter for the model of the controlled actor.

    Methods:
        polling_timer_event : None
            Indicates that the polling timer has expired and the MQTT broker must be queried for new
            messages.
        message : None
            Handle an incoming message containing an actor command.
    """
    def __init__(self, actor: iot_actor_base.IotActor, logger: logging.Logger,
                 mqtt_data: tuple, mqtt_input: tuple, mqtt_health: tuple = None,
                 health_check_interval: int = 0):
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self._actor = actor
        self.logger = logger
        self.logger.debug(f'{mth_name}: actor_id="{self._actor.actor_id}", actor_type="{self._actor.actor_type}"')
        super().__init__(1, health_check_interval if health_check_interval > 0 else 900,
                         mqtt_data = mqtt_data, mqtt_input = mqtt_input, mqtt_health = mqtt_health)
        if self.mqtt_input is not None:
            self.mqtt_input[0].owner = self
            self.mqtt_input[0].topics = [(self.mqtt_input, 0)]

    @property
    def element_id(self) -> str:
        """ Getter for the unique identifier of the controlled actor. """
        return None if self._actor is None else self._actor.actor_id

    @property
    def element_type(self) -> str:
        """ Getter for the type (model) of the controlled actor. """
        return None if self._actor is None else self._actor.actor_type

    @property
    def element_model(self) -> str:
        """ Getter for the model of the controlled actor. """
        return None if self._actor is None else self._actor.model

    def polling_timer_event(self):
        """ Indicates that the polling timer has expired and the MQTT broker must be queried for new
            messages.
        """
        super().polling_timer_event()
        self.mqtt_input[0].receive()
        out_data_list = self._actor.timer_tick()
        for out_data in out_data_list:
            out_msg = wp_queueing.QueueMessage(self.mqtt_data[1])
            out_msg.msg_payload = out_data
            self.mqtt_data[0].publish_single(out_msg)

    def message(self, msg: wp_queueing.QueueMessage) -> None:
        """ Handle an incoming message containing an actor command.

        Parameters:
            msg : wp_queueing.QueueMessage
                Message received from the message broker containing the actor command.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.logger.debug(f'{mth_name}: "{str(msg)}"')
        if self.mqtt_data is None or self.mqtt_data[1] is None:
            return
        if msg.msg_topic != self.mqtt_input[1]:
            self.logger.debug(f'{mth_name}: unexpected topic "{msg.msg_topic}"; expected "{self.mqtt_input[1]}"')
            return
        actor_cmd = iot_msg_actor.ActorCommand()
        try:
            actor_cmd.from_dict(msg.msg_payload)
        except TypeError as except_:
            self.logger.error(f'{mth_name}: {str(except_)}')
            return
        except ValueError as except_:
            self.logger.error(f'{mth_name}: {str(except_)}')
            return
        # If the command is too old, we discard it.
        cmd_age = (datetime.now() - actor_cmd.cmd_time).total_seconds()
        if cmd_age > 10:
            self.logger.warning('{}: topic="{}", msg_id="{}"'.format(mth_name, msg.msg_topic, msg.msg_id))
            self.logger.warning('{}: command age = {:.0f} seconds > 10, message discarded'.format(mth_name, cmd_age))
            return
        out_data = self._actor.process_command(actor_cmd)
        if out_data is not None and self.mqtt_data is not None:
            out_msg = wp_queueing.QueueMessage(self.mqtt_data[1])
            out_msg.msg_payload = out_data
            self.mqtt_data[0].publish_single(out_msg)
