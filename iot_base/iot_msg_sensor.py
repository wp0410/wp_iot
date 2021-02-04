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

class SensorMeasurement(wp_queueing.IConvertToDict):
    """ Class for grouping the result of a sensor measurement.

    Attributes:
        sensor_id : str
            Unique identifier of the sensor that produced the measurement.
        sensor_type : str
            Type of sensor that produced the measurement.
        msmt_time : datetime
            Timestamp of the measurement.
        hw_value : int
            Value delivered by the underlying hardware component.
        hw_voltage : float
            Voltage sensed by the underlying hardware component.
        msmt_unit : str
            Unit of the measured value.
        msmt_value : float
            Measured value.

    Methods:
        SensorMeasurement()
            Constructor
        to_dict : dict
            Converts a sensor measurement object into a dictionary representation.
    """
    def __init__(self, sensor_id, sensor_type, msmt_time: datetime = None):
        """ Constructor

        Parameters:
            sensor_id : str
                Unique identifier of the sensor that produced the measurement.
            sensor_type : str
                Type of sensor that produced the measurement.
            msmt_time : datetime, optional
                Timestamp of the measurement.
        """
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type
        if msmt_time is None:
            self.msmt_time = datetime.now()
        else:
            self.msmt_time = msmt_time
        self.hw_value = 0
        self.hw_voltage = 0
        self.msmt_unit = None
        self.msmt_value = 0

    def to_dict(self) -> dict:
        """ Converts a sensor measurement object into a dictionary representation.

        Returns:
            dict : dictionary representation of the object.
        """
        return {
            'class': 'SensorMeasurement',
            'sensor_id': self.sensor_id,
            'sensor_type': self.sensor_type,
            'msmt_time': self.msmt_time.strftime("%Y-%m-%d %H:%M:%S.%f"),
            'hw_value': self.hw_value,
            'hw_voltage': self.hw_voltage,
            'msmt_unit': self.msmt_unit,
            'msmt_value': self.msmt_value
        }
