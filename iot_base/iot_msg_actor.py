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
import wp_queueing

class ActorCommand(wp_queueing.IConvertToDict):
    """ IOT message to be sent to an Actor to initiate an action.

    Attributes:
        sender_id : str
            Unique identifier of the sender of the actor command.
        sender_type : str
            Unique identifier of the sender of the actor command.
        cmd_time : datetime
            Date and time when the actor command was created.
        cmd_detail : Any
            Detail information for the actor to executed the command.
        cmd_duration : int
            Time span in seconds after which the actor command shall be automatically cancelled or reverted
            (depending on the feature of the actor).

    Methods:
        ActorCommand:
            Constructor.
        to_dict : dict
            Converts an ActorCommand instance to a dictionary.
        from_dict : None
            Initializes the instance attributes from a dictionary.
    """
    def __init__(self, sender_id: str = "", sender_type: str = "", cmd_time: datetime = None,
                 cmd_detail: Any = "", cmd_duration: int = 0):
        """ Constructor.

        Parameters:
            sender_id : str, optional
                Unique identifier of the sender of the actor command.
            sender_type : str, optional
                Unique identifier of the sender of the actor command.
            cmd_time : datetime, optional
                Date and time when the actor command was created.
            cmd_detail : Any, optional
                Detail information for the actor to executed the command.
            cmd_duration : int, optional
                Time span in seconds after which the actor command shall be automatically cancelled or reverted
                (depending on the feature of the actor).
        """
        self.sender_id = sender_id
        self.sender_type = sender_type
        self.cmd_time = datetime.now() if cmd_time is None else cmd_time
        self.cmd_detail = cmd_detail
        self.cmd_duration = cmd_duration

    def to_dict(self) -> dict:
        """ Converts an ActorCommand instance to a dictionary.

        Returns:
            dict : ActorCommand instance represented as a dictionary.
        """
        return {
            'class': 'ActorCommand',
            'sender_id': self.sender_id,
            'sender_type': self.sender_type,
            'cmd_time': self.cmd_time,
            'cmd_detail': self.cmd_detail,
            'cmd_duration': self.cmd_duration
        }

    def from_dict(self, msg_dict: dict) -> None:
        """ Initializes the instance attributes from a dictionary.

        Returns:
            dict : Dictionary to initialize the instance attributes with.
        """
        if not isinstance(msg_dict, dict):
            raise TypeError(f'ActorCommand.from_dict(): invalid parameter type "{type(msg_dict)}"')
        mandatory_attr = ['class', 'sender_type', 'sender_id', 'cmd_time', 'cmd_detail', 'cmd_duration']
        for attr in mandatory_attr:
            if attr not in msg_dict:
                raise ValueError(f'ActorCommand.from_dict(): missing mandatory element "{attr}"')
        if msg_dict['class'] != 'ActorCommand':
            raise ValueError(f'ActorCommand.from_dict(): invalid dict class "{msg_dict["class"]}"')
        self.sender_id = msg_dict['sender_id']
        self.sender_type = msg_dict['sender_type']
        c_time = msg_dict['cmd_time']
        if c_time.find('.') < 0:
            self.cmd_time = datetime.strptime(c_time, "%Y-%m-%d %H:%M:%S")
        else:
            self.cmd_time = datetime.strptime(c_time, "%Y-%m-%d %H:%M:%S.%f")
        self.cmd_detail = msg_dict['cmd_detail']
        self.cmd_duration = int(msg_dict['cmd_duration'])
