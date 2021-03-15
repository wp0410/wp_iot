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
import iot_actor_base

class IotActorRelais(iot_actor_base.IotSwitchActor):
    """ A Relais actor that can be switched ON and OFF, based on super() class IotSwitchActor.

    Attributes:
        Inherited from IotSwitchActor.

    Methods:
        IotActorRelais:
            Constructor
        Inherited from IotSwitchActor.
    """
    def __init__(self, actor_id: str, actor_type: str, port_number: str, logger: logging.Logger):
        """ Constructor.

        Parameters:
            actor_id : str
                Unique identifier of the actor.
            actor_type : str
                Type of the actor.
            port_number : str
                Port of the associated output device to be used for setting the actor state.
            logger : logging.Logger
                Logger to be used.
        """
        super().__init__(actor_id, actor_type, port_number, (0, 1, 1), logger)
        self.model = "RELAIS 4*SRD-05VDC-SL-C"
