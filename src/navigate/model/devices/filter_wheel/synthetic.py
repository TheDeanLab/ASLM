# Copyright (c) 2021-2022  The University of Texas Southwestern Medical Center.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted for academic and research use only (subject to the
# limitations in the disclaimer below) provided that the following conditions are met:

#      * Redistributions of source code must retain the above copyright notice,
#      this list of conditions and the following disclaimer.

#      * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.

#      * Neither the name of the copyright holders nor the names of its
#      contributors may be used to endorse or promote products derived from this
#      software without specific prior written permission.

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

#  Standard Library Imports
import logging

# Third Party Imports

# Local Imports
from navigate.model.devices.filter_wheel.base import FilterWheelBase

# Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)


class SyntheticFilterWheel(FilterWheelBase):
    """SyntheticFilterWheel Class"""

    def __init__(self, device_connection, device_config):
        """Initialize the SyntheticFilterWheel class.

        Parameters
        ----------
        device_connection : dict
            Dictionary of device connections.
        device_config : dict
            Dictionary of device configuration parameters.
        """
        super().__init__(device_connection, device_config)

    def __del__(self):
        """Close the SyntheticFilterWheel."""
        pass

    def filter_change_delay(self, filter_name):
        """Calculate duration of time necessary to change filter wheel positions

        Parameters
        ----------
        filter_name : str
            Name of the filter that we want to move to
        """
        pass

    def set_filter(self, filter_name, wait_until_done=True):
        """Change the filter wheel to the filter designated by the filter
        position argument.

        Parameters
        ----------
        filter_name : str
            Name of filter to move to.
        wait_until_done : bool
            Waits duration of time necessary for filter wheel to change positions.
        """
        pass
