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
from iot_deploy import IotDeployment

if __name__ == "__main__":
    with IotDeployment("iot_base_app", "PI-250") as deployment:
        deployment.create_config_db("../iot_repository/iot.sl3")
        deployment.create_recorder_db("../iot_recorder/iot_rec.sl3")
        deployment.host_settings('192.168.1.250')
        deployment.broker_settings([['PI-250-1883', '192.168.1.250', 1883, deployment.now()]])
        deployment.host_assignments(0)
        deployment.create_config_file("logger_config.json")
