# Copyright (c) 2021-2022  The University of Texas Southwestern Medical Center.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted for academic and research use only (subject to the
# limitations in the disclaimer below) provided that the following conditions are met:
#
#      * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.
#
#      * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#      * Neither the name of the copyright holders nor the names of its
#      contributors may be used to endorse or promote products derived from this
#      software without specific prior written permission.
#
# NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY
# THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Standard Imports
import logging

# Third Party Imports

# Local Imports
from aslm.model.devices.dichroic.dichroic_base import DichroicBase
from aslm.model.devices.APIs.asi.asi_tiger_controller import (
    TigerController,
    TigerException,
)

# Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)


def build_ASI_dichroic_connection(com_port, baud_rate=115200):
    """Connect to the ASI Stage

    Parameters
    ----------
    com_port : str
        Communication port for ASI Tiger Controller - e.g., COM1
    baud_rate : int
        Baud rate for ASI Tiger Controller - e.g., 9600

    Returns
    -------
    asi_dichroic : object
        Successfully initialized stage object.
    """

    # wait until ASI device is ready
    asi_dichroic = TigerController(com_port, baud_rate)
    asi_dichroic.connect_to_serial()
    if not asi_dichroic.is_open():
        raise Exception("ASI stage connection failed.")

    return asi_dichroic


class DichroicASI(DichroicBase):
    """ASI Dichroic Class."""

    def __init__(self, microscope_name, device_connection, configuration, device_id=0):
        """Initialize the dichroic.

        Parameters
        ----------
        microscope_name : str
            Name of the microscope.
        device_connection : str
            Connection string for the device.
        configuration : dict
            Configuration dictionary for the device.
        device_id : int
            Device ID for the device.
        """
        super().__init__(microscope_name, device_connection, configuration, device_id)

        print("ASI Dichroic Initialized")