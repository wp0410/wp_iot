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
import wp_configuration


class IotAgentConfiguration(wp_configuration.DictConfigWrapper):
    def __init__(self, config_dict: dict):
        super().__init__(config_dict)
        self.mandatory_str('host', [6])
        self.optional_int('port', 1883)


class IotHardwareAgent:
    def __init__(self, broker_config: dict):
        self._broker_config = IotAgentConfiguration(broker_config)
