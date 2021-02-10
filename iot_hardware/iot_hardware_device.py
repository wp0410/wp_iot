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
import logging

class IotHardwareDevice:
    """ Generic hardware device (super class for all hardware device classes).

    Attributes:
        device_id : str
            Unique identifier of the hardware device.
        device_type : str
            Type of the hardware device.
        model : str
            Device model.
        logger : logging.Logger
            Logger to be used by the methods of the hardware device.

    Methods:
        IotHardwareDevice : None
            Constructor.
        check_health : iot_msg_input.InputHealth
            Method called by the hander when a health check shall be executed. Must be overloaded
            by derived classes to do something useful.
    """
    def __init__(self, device_id: str, logger: logging.Logger):
        """ Constructor.

        Parameters:
            device_id : str
                Unique identifier of the input device.
            logger : logging.Logger
                Logger to be used.
        """
        self.device_id = device_id
        self.logger = logger
        self.device_type = "GenericDevice"
        self.model = "GenericDevice"

    def check_health(self) -> object:
        """ Returns an empty dictionary. """
        # pylint: disable=no-self-use
        return None
