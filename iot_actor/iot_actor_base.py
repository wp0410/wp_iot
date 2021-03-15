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
from datetime import datetime, timedelta
import uuid
import iot_msg_output
import iot_msg_actor

class IotActor:
    """ An "Actor" is an object to which an ActorCommand can be sent to be executed by the actor.

    Attributes:
        actor_id : str
            Unique identifier of the actor.
        actor_type : str
            Type of the actor.
        model : str
            Actor model, if necessary to distinguish. Defaults to the actor type.
        logger : logging.Logger
            Logger to be used.

    Methods:
        process_command : iot_msg_output.OutputData
            Processes an ActorCommand received from a MQTT broker.
        revert_command: iot_msg_output.OutputData
            Reverts the most recently executed command.
        timer_tick : iot_msg_output.OutputData
            Notifies the actor about timer ticks to look for expired command timers.
        create_timer : None
            Creates a new "timer" for a command that needs to be reverted after a given time interval.
    """
    def __init__(self, actor_id: str, actor_type: str, logger: logging.Logger):
        """ Constructor.

        Parameters:
            actor_id : str
                Unique identifier of the actor.
            actor_type : str
                Type of the actor.
            logger : logging.Logger
                Logger to be used.
        """
        self.logger = logger
        self.actor_id = actor_id
        self.actor_type = actor_type
        self.model = actor_type
        self._timers = dict()

    def process_command(self, cmd: iot_msg_actor.ActorCommand) -> iot_msg_output.OutputData:
        """ Processes an ActorCommand received from a MQTT broker.

        Parameters:
            cmd : iot_msg_actor.ActorCommand
                The command to be executed.

        Returns:
            iot_msg_output.OutputData
                Output data to be sent to the MQTT broker causing an action on the associated
                hardware device.
        """

    def revert_command(self) -> iot_msg_output.OutputData:
        """ Reverts the most recently executed command, e.g. if the most recent command switched an actor ON,
            then this command will switch it OFF.

        Returns:
            iot_msg_output.OutputData
                Output data to be sent to the MQTT broker causing an action on the associated
                hardware device.
        """

    def timer_tick(self) -> list:
        """ Notifies the actor about timer ticks to look for expired command timers.

        Returns:
            list
                Output data to be sent to the MQTT broker causing an action on the associated
                hardware device.
        """
        res_data = []
        cur_time = datetime.now()
        for timer_id in self._timers:
            if (self._timers[timer_id] - cur_time).total_seconds() <= 0:
                res_data.append(self.revert_command())
                self._timers.pop(timer_id)
        return res_data

    def create_timer(self, timeout_sec: int) -> None:
        """ Creates a new "timer" for a command that needs to be reverted after a given time interval.

        Parameters:
            timeout_sec : int
                Number of seconds after which the "timer" shall expire.
        """
        timer_id = str(uuid.uuid4()).replace('-', '')
        self._timers[timer_id] = datetime.now() + timedelta(seconds = timeout_sec)

class IotSwitchActor(IotActor):
    """ Actor that can be switched between two states (ON / OFF). When initializing the actor, the numeric values
        corresponding to the two states must be specified, as well as the state to be initially set.

    Attributes:
        _port_number : str
            Port number of the associated hardware device that will be used for pin output.
        _on_state : int
            Numeric value to be set for the hardware device pin to switch the actor ON.
        _off_state : int
            Numeric value to be set for the hardware device pin to switch the actor OFF.
        _init_state : int
            Numeric value to be initially set.
        _last_output : Any
            Most recent output object created by the actor.
        _last_output_time : datetime
            Date and time when most recent output object was created by the actor.

    Properties:
        is_on : bool
            Indicates whether the actor state is ON (True) of OFF (False).

    Methods:
        IotSwitchActor : None
            Constructor
        set_init_state : iot_msg_output.OutputData
            Generates the output record to set the hardware device pin to the initial state.
        toggle_state : iot_msg_output.OutputData
            Toggles the state of the actor.
        switch : iot_msg_output.OutputData
            Switches the actor to a specific state.
        switch_on : iot_msg_output.OutputData
            Creates the MQTT message to switch the state of the actor to ON.
        switch_off : iot_msg_output.OutputData
            Creates the MQTT message to switch the state of the actor to OFF.
        process_command : iot_msg_output.OutputData
            Processes an ActorCommand received from a MQTT broker.
        revert_command : iot_msg_output.OutputData
            Makes sure that the actor state will be set to OFF, which is the safe state for a
            SwitchActor.
    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, actor_id: str, actor_type: str, port_number: str, states: tuple, logger: logging.Logger):
        """ Constructor.

        Parameters:
            actor_id : str
                Unique identifier of the actor.
            actor_type : str
                Type of the actor.
            port_number : str
                Port of the associated output device to be used for setting the actor state.
            states : tuple
                Specifies the integer values to be set in the underlying hardware device for the different states of
                the actor. Passed values must be tuples (on_state, off_state, init_state) where:
                    on_state ..... value to be sent to hardware device to switch the actor state to ON;
                    off_state .... value to be sent to hardware device to switch the actor state to OFF;
                    init_state ... initial state of the hardware device output port.
            logger : logging.Logger
                Logger to be used.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        super().__init__(actor_id, actor_type, logger)
        self._port_number = port_number
        self._on_state, self._off_state, self._init_state = states
        self._last_output = None
        self._last_output_time = None
        self.logger.debug(f'{mth_name}: Initialized Actor(ID = "{self.actor_id}", TYPE = "{self.actor_type}")')

    @property
    def is_on(self) -> bool:
        """ Indicates whether the actor state is ON (True) of OFF (False). """
        return self._last_output is not None and self._last_output.output_data == self._on_state

    def set_init_state(self) -> iot_msg_output.OutputData:
        """ Creates the MQTT message to set the initial state of the actor by setting the pin of the associated
            output device accordingly.

        Returns:
             iot_msg_output.OutputData:
                MQTT message containing the command for the associated hardware device.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.logger.debug(f'{mth_name}: Actor(ID="{self.actor_id}") initial state = "{self._init_state}"')
        return self.switch(self._init_state)

    def toggle_state(self) -> iot_msg_output.OutputData:
        """ Creates the MQTT message to toggle the current state of the actor.

        Returns:
             iot_msg_output.OutputData:
                MQTT message containing the command for the associated hardware device.
        """
        if self._last_output is None:
            return None
        if self._last_output.output_data == self._off_state:
            return self.switch(self._on_state)
        return self.switch(self._off_state)

    def switch_on(self) -> iot_msg_output.OutputData:
        """ Creates the MQTT message to switch the state of the actor to ON.

        Returns:
             iot_msg_output.OutputData:
                MQTT message containing the command for the associated hardware device.
        """
        return self.switch(self._on_state)

    def switch_off(self) -> iot_msg_output.OutputData:
        """ Creates the MQTT message to switch the state of the actor to OFF.

        Returns:
             iot_msg_output.OutputData:
                MQTT message containing the command for the associated hardware device.
        """
        return self.switch(self._off_state)

    def switch(self, state: int) -> iot_msg_output.OutputData:
        """ Creates the MQTT message to switch the assocated device port to the value corresponding to the requested
            state.

        Returns:
             iot_msg_output.OutputData:
                MQTT message containing the command for the associated hardware device.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.logger.debug(f'{mth_name}: Actor(ID="{self.actor_id}") switching to "{state}"')
        out_data_cmd = iot_msg_output.OutputData(
            component_id = self.actor_id, component_type = self.actor_type, output_data = state)
        out_data_cmd.output_port = self._port_number
        self._last_output = out_data_cmd
        self._last_output_time = datetime.now()
        return out_data_cmd

    def process_command(self, cmd: iot_msg_actor.ActorCommand) -> iot_msg_output.OutputData:
        """ Processes an ActorCommand received from a MQTT broker.

        Parameters:
            cmd : iot_msg_actor.ActorCommand
                The command to be executed.

        Returns:
            iot_msg_output.OutputData
                Output data to be sent to the MQTT broker causing an action on the associated
                hardware device.
        """
        if cmd.cmd_duration > 0:
            self.create_timer(cmd.cmd_duration)
        if cmd.cmd_detail == "ON":
            return self.switch_on()
        return self.switch_off()

    def revert_command(self) -> iot_msg_output.OutputData:
        """ Makes sure that the actor state will be set to OFF, which is the safe state for a
            SwitchActor.

        Returns:
            iot_msg_output.OutputData
                Output data to be sent to the MQTT broker causing an action on the associated
                hardware device.
        """
        return self.switch_off()
