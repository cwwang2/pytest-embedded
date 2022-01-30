import copy
import logging
from typing import Dict, Union

import serial as pyserial
from pytest_embedded.log import DuplicateStdoutMixin, PexpectProcess


class Serial(DuplicateStdoutMixin):
    """
    Custom serial class

    Attributes:
        port_config (dict[str, Any]): port configs
        proc (serial.Serial): process created by `serial.serial_for_url()`
    """

    DEFAULT_PORT_CONFIG = {
        'baudrate': 115200,
        'bytesize': pyserial.EIGHTBITS,
        'parity': pyserial.PARITY_NONE,
        'stopbits': pyserial.STOPBITS_ONE,
        'timeout': 0.05,  # read timeout
        'xonxoff': False,
        'rtscts': False,
    }

    occupied_ports: Dict[str, None] = dict()

    def __init__(self, pexpect_proc: PexpectProcess, port: Union[str, pyserial.Serial], **kwargs):
        """
        Args:
            pexpect_proc: `PexpectProcess` instance
            port: port string or pyserial Serial instance
        """
        super().__init__()

        if port is None:
            raise ValueError('Please specify port')

        if isinstance(port, str):
            self.port = port
            self.port_config = copy.deepcopy(self.DEFAULT_PORT_CONFIG)
            self.port_config.update(**kwargs)
            self.proc = pyserial.serial_for_url(self.port, **self.port_config)
        elif isinstance(port, pyserial.Serial):  # pyserial instance
            self.proc = port
            self.proc.timeout = self.DEFAULT_PORT_CONFIG['timeout']  # set read timeout
            self.port = self.proc.port
        else:
            raise ValueError('Port should be a string or a pyserial.Serial instance')

        self.pexpect_proc = pexpect_proc
        self.occupied_ports[self.port] = None
        logging.debug(f'occupied {self.port}')

        self._start()

    def _start(self):
        pass

    def _forward_io(self, pexpect_proc: PexpectProcess) -> None:
        while self.proc.is_open:
            try:
                s = self.proc.read_all()
                pexpect_proc.write(s)
            except:  # noqa daemon thread may run at any case
                break
