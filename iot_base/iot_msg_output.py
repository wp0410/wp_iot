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

class OutputData(wp_queueing.IConvertToDict):
    """ IOT Messages to be sent to an output device.

    Attributes:
        component_id : str, optional
            Unique identifier of the component that sent the message.
        component_type : str, optional
            Type of the component that sent the message.
        output_port : str, optional
            Output port of the output device to which the required action applies.
        output_time : datetime, optional
            Date and time when the message was created by the sender.
        output_data : Any, optional
            Specifies the action and output data for the output device.

    Methods:
        OutputData : None
            Constructor.
        to_dict : dict
            Converts the output data message to a dictionary.
        from_dict : None
            Converts a dictionary to an OutputData instance, if possible.
    """
    def __init__(self, component_id: str = "", component_type: str = "", output_port: str = "",
                 output_time: datetime = None, output_data: Any = None):
        self.component_id = component_id
        self.component_type = component_type
        self.output_port = output_port
        self.output_data = output_data
        self.output_time = datetime.now() if output_time is None else output_time

    def to_dict(self) -> dict:
        """ Converts the OutputData message to a dictionary.

        returns:
            dict : The attributes of the object as members of a dictionary.
        """
        return {
            'class': 'OutputData',
            'component_type': self.component_type,
            'component_id': self.component_id,
            'output_time': self.output_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
            'output_port': self.output_port,
            'output_data' : str(self.output_data)
        }

    def from_dict(self, msg_dict: dict) -> None:
        """ Converts a dictionary to an OutputState instance, if possible.

        Parameters:
            msg_dict : dict
                Dictionary to be converted.
        """
        if not isinstance(msg_dict, dict):
            raise TypeError(f'OutputData.from_dict(): invalid parameter type "{type(msg_dict)}"')
        mandatory_attr = ['class', 'component_type', 'component_id', 'output_time', 'output_data']
        for attr in mandatory_attr:
            if attr not in msg_dict:
                raise ValueError(f'OutputData.from_dict(): missing mandatory element "{attr}"')
        if msg_dict['class'] != 'OutputData':
            raise ValueError(f'OutputData.from_dict(): invalid dict class "{msg_dict["class"]}"')
        self.component_id = msg_dict['component_id']
        self.component_type = msg_dict['component_type']
        st_time = msg_dict['output_time']
        if st_time.find('.') < 0:
            self.output_time = datetime.strptime(st_time, "%Y-%m-%d %H:%M:%S")
        else:
            self.output_time = datetime.strptime(st_time, "%Y-%m-%d %H:%M:%S.f")
        self.output_port = None if 'output_port' not in msg_dict else msg_dict['output_port']
        self.output_data = msg_dict['output_data']
