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
#

#  Standard Library Imports
import logging

# Third Party Imports
import nidaqmx
from nidaqmx.constants import AcquisitionType

# Local Imports
from aslm.model.devices.galvo.galvo_base import GalvoBase

# # Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)


class GalvoNI(GalvoBase):
    """GalvoNI Class

    This class is the NI DAQ implementation of the GalvoBase class.

    Parameters
    ----------
    microscope_name : str
        The name of the microscope
    device_connection : object
        The device connection object
    configuration : dict
        The configuration dictionary
    galvo_id : int
        The galvo id

    Attributes
    ----------
    task : object
        The NI DAQ task object
    trigger_source : str
        The trigger source for the galvo

    Methods
    -------
    initialize_task()
        Initialize the NI DAQ task for the galvo
    __del__()
        Deletes the task.
    adjust(exposure_times, sweep_times)
        Adjust the galvo to the readout time
    prepare_task(channel_key)
        Prepare the task for the given channel
    start_task()
        Start the NI DAQ task
    stop_task()
        Stop the NI DAQ task
    close_task()
        Close the NI DAQ task

    Examples
    --------
    >>> galvo = GalvoNI(microscope_name, device_connection, configuration, galvo_id=0)
    >>> galvo.adjust(exposure_times, sweep_times)
    >>> galvo.prepare_task(channel_key)
    >>> galvo.start_task()
    >>> galvo.stop_task(force=False)
    >>> galvo.close_task()

    """

    def __init__(self, microscope_name, device_connection, configuration, galvo_id=0):
        super().__init__(microscope_name, device_connection, configuration, galvo_id)

        self.task = None

        self.trigger_source = configuration["configuration"]["microscopes"][
            microscope_name
        ]["daq"]["trigger_source"]

        # self.initialize_task()

        self.daq = device_connection

    def initialize_task(self):
        """Initialize the NI DAQ task for the galvo

        Parameters
        ----------
        None

        Returns
        -------
        None

        Examples
        --------
        >>> galvo.initialize_task()
        """

        # TODO: make sure the task is reusable, Or need to create and close each time.
        self.task = nidaqmx.Task()
        channel = self.device_config["hardware"]["channel"]
        self.task.ao_channels.add_ao_voltage_chan(channel)
        print(
            f"Initializing galvo with sample rate {self.sample_rate} and"
            f"{self.samples} samples"
        )
        # TODO: does it work with confo-projection?
        self.task.timing.cfg_samp_clk_timing(
            rate=self.sample_rate,
            sample_mode=AcquisitionType.FINITE,
            samps_per_chan=self.samples,
        )
        self.task.triggers.start_trigger.cfg_dig_edge_start_trig(self.trigger_source)

    def __del__(self):
        """Deletes the task.
        This method deletes the task.
        Parameters
        ----------
        None
        Returns
        -------
        None
        Examples
        --------
        >>> del galvo
        """

        self.stop_task()
        self.close_task()

    def adjust(self, exposure_times, sweep_times):
        """Adjust the galvo to the readout time

        Parameters
        ----------
        exposure_times : dict
            Dictionary of exposure times for each selected channel
        sweep_times : dict
            Dictionary of sweep times for each selected channel

        Returns
        -------
        None

        Examples
        --------
        >>> galvo.adjust(exposure_times, sweep_times)
        """
        waveform_dict = super().adjust(exposure_times, sweep_times)

        self.daq.analog_outputs[self.device_config["hardware"]["channel"]] = {
            "sample_rate": self.sample_rate,
            "samples": self.samples,
            "trigger_source": self.trigger_source,
            "waveform": waveform_dict,
        }
        return waveform_dict

    def prepare_task(self, channel_key):
        """Prepare the task for the given channel

        Parameters
        ----------
        channel_key : str
            The channel key for the task

        Returns
        -------
        None

        Examples
        --------
        >>> galvo.prepare_task(channel_key)
        """

        # write waveform
        # self.task.write(self.waveform_dict[channel_key])
        pass

    def start_task(self):
        """Start the NI DAQ task for the galvo

        Parameters
        ----------
        None

        Returns
        -------
        None

        Examples
        --------
        >>> galvo.start_task()
        """

        # self.task.start()
        pass

    def stop_task(self, force=False):
        """Stop the NI DAQ task for the galvo

        Parameters
        ----------
        force : bool
            Force stop the task

        Returns
        -------
        None

        Examples
        --------
        >>> galvo.stop_task()
        """

        # if not force:
        #     self.task.wait_until_done()
        # self.task.stop()
        pass

    def close_task(self):
        """Close the NI DAQ task for the galvo

        Parameters
        ----------
        None

        Returns
        -------
        None

        Examples
        --------
        >>> galvo.close_task()
        """

        # self.task.close()
        pass