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
import wp_queueing

class InputProbe(wp_queueing.IConvertToDict):
    """ Result of reading an input channel of an Input device.

    Attributes:
        device_id : str
            Unique name or identifier of the Digital Input device.
        device_type : str
            Type of the digital input device.
        probe_time : datetime
            Timestamp of the sensor probe.
        channel_no : int
            Number of the Digital Input channel read.
        value : int
            Read Digital Input value.
        voltage : float
            Read input voltage.

    Methods:
        InputProbe()
            Constructor.
        to_dict : dict
            Converts the Digital Input probe into a dictionary.
    """
    def __init__(self, device_type = None, device_id = None, probe_time = None, channel_no = -1,
                 value = 0, voltage = 0.0):
        """ Constructor.

        Parameters:
            device_type : str, optional
                Type of the digital input device.
            device_id : str, optional
                Unique name or identifier of the Digital Input device.
            probe_time : datetime, optional
                Timestamp of the sensor probe.
            channel_no : int
                Number of the Digital Input channel read.
            value : int, optional
                Read Digital Input value.
            voltage : float, optional
                Read input voltage.
        """
        self.device_id = device_id
        self.device_type = device_type
        if probe_time is None:
            self.probe_time = datetime.now()
        else:
            self.probe_time = probe_time
        self.channel_no = channel_no
        self.value = value
        self.voltage = voltage

    def to_dict(self) -> dict:
        """ Converts the input probe into a dictionary.

        returns:
            dict : The attributes of the object as members of a dictionary.
        """
        return {
            'class': 'InputProbe',
            'device_type': self.device_type,
            'device_id': self.device_id,
            'probe_time': self.probe_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
            'channel_no': self.channel_no,
            'value': self.value,
            'voltage': self.voltage
        }

    def from_dict(self, msg_dict: dict) -> None:
        """ Converts a dictionary into an InputProbe instance, if possible.

        Parameters:
            msg_dict : dict
                Dictionary to be converted.
        """
        if not isinstance(msg_dict, dict):
            raise TypeError('InputProbe.from_dict(): invalid parameter type "{}"'.format(type(msg_dict)))
        mandatory_attr = ['class', 'device_type', 'device_id', 'probe_time', 'channel_no', 'value']
        for attr in mandatory_attr:
            if attr not in msg_dict:
                raise ValueError('InputProbe.from_dict(): missing mandatory element "{}"'.format(attr))
        if msg_dict['class'] != 'InputProbe':
            raise ValueError('InputProbe.from_dict(): invalid dict class "{}"'.format(msg_dict['class']))
        self.device_id = msg_dict['device_id']
        self.device_type = msg_dict['device_type']
        probe_time = msg_dict['probe_time']
        if probe_time.find('.') < 0:
            self.probe_time = datetime.strptime(probe_time, "%Y-%m-%d %H:%M:%S")
        else:
            self.probe_time = datetime.strptime(probe_time, "%Y-%m-%d %H:%M:%S.%f")
        self.channel_no = msg_dict['channel_no']
        self.value = msg_dict['value']
        if 'voltage' in msg_dict:
            self.voltage = msg_dict['voltage']


class InputHealth(wp_queueing.IConvertToDict):
    """ Data object to report the health status of an input device.

    Attributes:
        device_id : str
            Unique name or identifier of the Digital Input device.
        device_type : str
            Type of the digital input device.
        health_time : datetime
            Timestamp of the health check.
        health_status : int
            Health status of the input device.
        last_probe_time : datetime
            Timestamp of last probe request.
        num_probe_total : int
            Number of probe requests.
        num_probe_detail : list
            List containing the number of successfully created probe results per input channel.

    Methods:
        InputHealth():
            Constructor
        to_dict : dict
            Converts the object to a dictionary.
        from_dict : None
            Converts a dictionary into an InputHealth instance, if possible.
    """
    def __init__(self, device_type = None, device_id = None, health_status = 0, health_time = None):
        """ Constructor.

        Parameters:
            device_type : str, optional
                Type of the digital input device.
            device_id : str, optional
                Unique name or identifier of the Digital Input device.
            health_status : int
                Health status of the input device.
            health_time : datetime, optional
                Timestamp of the health check.
        """
        self.device_type = device_type
        self.device_id = device_id
        if health_time is None:
            self.health_time = datetime.now()
        else:
            self.health_time = health_time
        self.health_status = health_status
        self.last_probe_time = None
        self.num_probe_total = 0
        self.num_probe_detail = None

    def to_dict(self) -> dict:
        """ Converts the object to a dictionary.

        Returns:
            Contents of the object as dictionary.
        """
        return {
            'class': 'InputHealth',
            'device_type': self.device_type,
            'device_id': self.device_id,
            'health_time': self.health_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
            'health_status': self.health_status,
            'last_probe_time': self.last_probe_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
            'num_probe_total': self.num_probe_total,
            'num_probe_detail': self.num_probe_detail
        }

    def from_dict(self, msg_dict: dict) -> None:
        """ Converts a dictionary into an InputHealth instance, if possible.

        Parameters:
            msg_dict : dict
                Dictionary to be converted.
        """
        if not isinstance(msg_dict, dict):
            raise TypeError('InputHealth.from_dict(): invalid parameter type "{}"'.format(type(msg_dict)))
        mandatory_attr = ['class', 'device_type', 'device_id', 'health_time',
                          'health_status', 'last_probe_time', 'num_probe_total']
        for attr in mandatory_attr:
            if attr not in msg_dict:
                raise ValueError('InputHealth.from_dict(): missing mandatory element "{}"'.format(attr))
        if msg_dict['class'] != 'InputHealth':
            raise ValueError('InputHealth.from_dict(): invalid dict class "{}"'.format(msg_dict['class']))
        self.device_type = msg_dict['device_type']
        self.device_id = msg_dict['device_id']
        temp_time = msg_dict['health_time']
        if temp_time.find('.') < 0:
            self.health_time = datetime.strptime(temp_time, "%Y-%m-%d %H:%M:%S")
        else:
            self.health_time = datetime.strptime(temp_time, "%Y-%m-%d %H:%M:%S.%f")
        self.health_status = msg_dict['health_status']
        temp_time = msg_dict['last_probe_time']
        if temp_time.find('.') < 0:
            self.last_probe_time = datetime.strptime(temp_time, "%Y-%m-%d %H:%M:%S")
        else:
            self.last_probe_time = datetime.strptime(temp_time, "%Y-%m-%d %H:%M:%S.%f")
        self.num_probe_total = msg_dict['num_probe_total']
        if 'num_probe_detail' in msg_dict:
            self.num_probe_detail = msg_dict['num_probe_detail']
