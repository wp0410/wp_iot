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
from datetime import datetime
import logging
import smbus2

class OutputPortState:
    """ State of an output port on a IotPortOutput device.

    Attributes:
        port_number : int
            Port number of the output port (0 ... 7).
        current_val : int
            Current value of the output port (0, 1).
        last_state_change : datetime
            Date and time of last state change of the port.
        total_state_time : list
            For states (0 and 1), total time of port being in the respective state.

    Methods:
        OutputPortState : Constructor
    """
    def __init__(self, port_number: int, init_val: int):
        """ Constructor.

        Parameters:
            port_number : int
                Port number of the output port (0 ... 7).
            init_val : int
                Initial value of the output port (0, 1).
        """
        self.port_number = port_number
        self.current_val = init_val
        self.last_state_change = None
        self.total_state_time = [0, 0]

class IotPortOutputMCP23017:
    """ MCP23017 port extender as an output device (selected ports can be switched on and off).

    Attributes:
        device_id : str
            Unique identifier of the hardware device.
        device_type : str
            Type of the hardware device ("PortOutput")
        model : str
            Model of the hardware device ("MCP23017")
        i2c_bus : smbus2.SMBus
            Handle to the I2C bus to which the device is connected.
        i2c_bus_address : int
            Address of the hardware device on the I2C bus.
        logger : logging.Logger
            Logger to be used.
        _port_states : dict
            Dictionary holding the current states of the MCP23017 ports to be used for output.

    Methods:
        IotPortOutputMCP23017 : None
            Constructor
        switch_to_state : int
            Changes the state of an output port to a given target state. Has no effect if the port is already in
            this state.
        switch : int
            Changes the state of an output port. If the port is currently ON, it will be switched OFF and
            vice versa.
        switch_on : int
            Changes the state of an output port to ON. Has no effect if the port is already ON.
        switch_off : int
            Changes the state of an output port to OFF. Has no effect if the port is already OFF.
        _calc_setup_mask : int
            Calculates the value to be written to a SETUP register to define the used ports as
            output ports.
        _calc_output_mask : int
            Calculates the value to be written to an OUTPUT register to set the requested states
            of the used output ports.
        _initialize_output_ports : None
            Setup and initialize the used output ports.
        _write_port_states : None
            Write the current states of all ports on a port register (A, B).
    """
    _device_register = {
        'A' : {
            'SETUP': 0x00,
            'OUTPUT': 0x14
        },
        'B' : {
            'SETUP': 0x01,
            'OUTPUT': 0x15
        }
    }

    def __init__(self, device_id: str, i2c_bus_id: int, i2c_bus_address: int,
                 output_ports: list, logger: logging.Logger):
        """ Constructor.

        Parameters:
            device_id : str
                Unique identifier of the hardware device.
            i2c_bus_id : int
                Number of the I2C bus to which the device is connected.
            i2c_bus_address : int
                Address of the hardware device on the I2C bus.
            output_ports : list
                List of ports to be defined as output ports.
            logger : logging.Logger
                Logger to be used.
        """
        self.logger = logger
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.device_id = device_id
        self.device_type = 'PortOutput'
        self.model = 'MCP23017'
        self.i2c_bus = smbus2.SMBus(i2c_bus_id)
        self.i2c_bus_address = i2c_bus_address
        self._port_states = {'A': dict(), 'B': dict()}
        self.logger.debug(f'{mth_name}: Initializing Hardware Device:')
        self.logger.debug(f'   deviceId:   "{self.device_id}"')
        self.logger.debug(f'   deviceType: "{self.device_type}"')
        self.logger.debug(f'   model:      "{self.model}"')
        self.logger.debug(f'   busAddress: "{self.i2c_bus_address}"')
        for out_port in output_ports:
            port, init_value = out_port
            register = port[:1].upper()
            self._port_states[register][port[1:]] = OutputPortState(int(port[1:]), int(init_value))
        self._initialize_output_ports()

    @staticmethod
    def _calc_setup_mask(port_dict: dict) -> int:
        """ Calculates the value to be written to a SETUP register to define the used ports as
            output ports.

        Parameters:
            port_dict : dict
                Dictionary containing the states of the used ports.

        Returns:
            int : calculated value to be written to the SETUP register.
        """
        setup_mask = 0
        for port_key in port_dict:
            setup_mask = setup_mask | 2**port_dict[port_key].port_number
        return setup_mask

    @staticmethod
    def _calc_output_mask(port_dict: dict) -> int:
        """ Calculates the value to be written to an OUTPUT register to set the requested states
            of the used output ports.

        Parameters:
            port_dict : dict
                Dictionary containing the states of the used ports.

        Returns:
            int : calculated value to be written to the OUTPUT register.
        """
        output_mask = 0
        for port_key in port_dict:
            output_mask = output_mask | 2**port_dict[port_key].current_val
        return output_mask

    def _initialize_output_ports(self):
        """ Setup and initialize the used output ports. """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        for sub_key in self._port_states:
            setup_mask = self._calc_setup_mask(self._port_states[sub_key])
            self.logger.debug(f'{mth_name}: setup mask = "{setup_mask}"')
            self.i2c_bus.write_byte_data(self.i2c_bus_address, self._device_register[sub_key]['SETUP'], setup_mask)
            self._write_port_states(sub_key)
            for state_key in self._port_states[sub_key]:
                self._port_states[sub_key][state_key].last_state_change = datetime.now()

    def _write_port_states(self, register: str) -> None:
        """ Write the current states of all ports on a port register (A, B).

        Parameters:
            register : str
                Port register (A, B).
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        output_mask = self._calc_output_mask(self._port_states[register])
        self.logger.debug(f'{mth_name}: output mask = "{output_mask}"')
        self.i2c_bus.write_byte_data(self.i2c_bus_address, self._device_register[register]['OUTPUT'], output_mask)

    def switch_to_state(self, port_number: str, to_state: int) -> int:
        """ Changes the state of an output port to a given target state. Has no effect if the port is already in
            this state.

        Parameters:
            port_number : str
                Identification of the port ("A0", ... "A7", "B0", ... "B7").
            to_state : int
                Target state (0, 1).

        Returns:
            int : state of the port after switching.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.logger.debug(f'{mth_name}: port = "{port_number}", to_state = "{to_state}"')
        register = port_number[:1].upper()
        port_state = self._port_states[register][port_number[1:]]
        if port_state.current_val == to_state:
            return to_state
        prev_state_change = port_state.last_state_change
        port_state.last_state_change = datetime.now()
        timediff = port_state.last_state_change - prev_state_change
        port_state.total_state_time[port_state.current_val] += timediff.total_seconds()
        port_state.current_val = to_state
        self._write_port_states(register)
        return to_state

    def switch(self, port_number : str) -> int:
        """ Changes the state of an output port. If the port is currently ON, it will be switched OFF and
            vice versa.

        Parameters:
            port_number : str
                Identification of the port ("A0", ... "A7", "B0", ... "B7").

        Returns:
            int : state of the port after switching.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.logger.debug(f'{mth_name}: port = "{port_number}"')
        register = port_number[:1].upper()
        port_state = self._port_states[register][port_number[1:]]
        return self.switch_to_state(port_number, (port_state.current_val + 1) % 2)

    def switch_on(self, port_number: str) -> int:
        """ Changes the state of an output port to ON. Has no effect if the port is already ON.

        Parameters:
            port_number : str
                Identification of the port ("A0", ... "A7", "B0", ... "B7").

        Returns:
            int : state of the port after switching.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.logger.debug(f'{mth_name}: port = "{port_number}"')
        return self.switch_to_state(port_number, 1)

    def switch_off(self, port_number: str) -> int:
        """ Changes the state of an output port to OFF. Has no effect if the port is already OFF.

        Parameters:
            port_number : str
                Identification of the port ("A0", ... "A7", "B0", ... "B7").

        Returns:
            int : state of the port after switching.
        """
        mth_name = "{}.{}()".format(self.__class__.__name__, inspect.currentframe().f_code.co_name)
        self.logger.debug(f'{mth_name}: port = "{port_number}"')
        return self.switch_to_state(port_number, 0)
