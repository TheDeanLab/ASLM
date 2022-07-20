"""Class for mixed digital and analog modulation of laser devices.
Goal is to set the DC value of the laser intensity with the analog voltage, and then rapidly turn it on and off
with the digital signal.

Copyright (c) 2021-2022  The University of Texas Southwestern Medical Center.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted for academic and research use only (subject to the limitations in the disclaimer below)
provided that the following conditions are met:

     * Redistributions of source code must retain the above copyright notice,
     this list of conditions and the following disclaimer.

     * Redistributions in binary form must reproduce the above copyright
     notice, this list of conditions and the following disclaimer in the
     documentation and/or other materials provided with the distribution.

     * Neither the name of the copyright holders nor the names of its
     contributors may be used to endorse or promote products derived from this
     software without specific prior written permission.

NO EXPRESS OR IMPLIED LICENSES TO ANY PARTY'S PATENT RIGHTS ARE GRANTED BY
THIS LICENSE. THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""

# Standard Imports
import logging

# Third Party Imports

# Local Imports

# Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)


class StageBase:
    r"""StageBase Parent Class

    Attributes
    ----------
    configuration : Session
        Global configuration of the microscope
    verbose : bool
        Verbosity
    x_pos : float
        True x position
    y_pos : float
        True y position
    z_pos : float
        True z position
    f_pos : float
        True focus position
    theta_pos : float
        True rotation position
    position_dict : dict
        Dictionary of true stage positions
    int_x_pos : float
        Software x position
    int_y_pos : float
        Software y position
    int_z_pos : float
        Software z position
    int_f_pos : float
        Software focus position
    int_theta_pos : float
        Software theta position
    int_position_dict : dict
        Dictionary of software stage positions
    int_x_pos_offset : float
        x position offset
    int_y_pos_offset : float
        y position offset
    int_z_pos_offset : float
        z position offset
    int_f_pos_offset : float
        focus position offset
    int_theta_pos_offset : float
        theta position offset
    x_max : float
        Max x position
    y_max : float
        Max y position
    z_max : float
        Max y position
    f_max : float
        Max focus positoin
    theta_max : float
        Max rotation position
    x_min : float
        Min x position
    y_min : float
        Min y position
    z_min : float
        Min y position
    f_min : float
        Min focus positoin
    theta_min : float
        Min rotation position
    x_rot_position : float
        Location to move the specimen in x while rotating.
    y_rot_position : float
        Location to move the specimen in y while rotating.
    z_rot_position : float
        Location to move the specimen in z while rotating.
    startfocus : float
        Location to initialize the focusing stage to.

    Methods
    -------
    create_position_dict()
        Creates a dictionary with the hardware stage positions.
    create_internal_position_dict()
        Creates a dictionary with the software stage positions.
    """
    def __init__(self, configuration, verbose, axes=['x', 'y', 'z', 'f', 'theta']):
        self.verbose = verbose
        self.configuration = configuration
        self.position_dict = None
        self.int_position_dict = None
        self.axes = axes

        r"""Initial setting for all positions
        self.x_pos, self.y_pos etc are the true axis positions, no matter whether
        the stages are zeroed or not.
        """
        for ax in self.axes:
            setattr(self, f"{ax}_pos", self.configuration.StageParameters['position'][f'{ax}_pos'])  # True stage position
            setattr(self, f"int_{ax}_pos", 0)                                       # Internal stage position
            setattr(self, f"int_{ax}_pos_offset", 0)                                # Offset between true and internal
            setattr(self, f"{ax}_min", self.configuration.StageParameters[f'{ax}_min'])  # Units are in microns
            setattr(self, f"{ax}_max", configuration.StageParameters[f'{ax}_max'])  # Units are in microns

        self.create_position_dict()
        self.create_internal_position_dict()

        # Sample Position When Rotating
        self.x_rot_position = self.configuration.StageParameters['x_rot_position']
        self.y_rot_position = self.configuration.StageParameters['y_rot_position']
        self.z_rot_position = self.configuration.StageParameters['z_rot_position']

        # Starting Position of Focusing Device
        self.startfocus = self.configuration.StageParameters['startfocus']

    def create_position_dict(self):
        r"""Creates a dictionary with the hardware stage positions.
        """
        self.position_dict = {}
        for ax in self.axes:
            ax_str = f"{ax}_pos"
            self.position_dict[ax_str] = getattr(self, ax_str)

    def create_internal_position_dict(self):
        r"""Creates a dictionary with the software stage positions.
        Internal position includes the offset for each stage position.
        e.g, int_x_pos = x_pos + int_x_pos_offset
        """
        self.int_position_dict = {}
        for ax in self.axes:
            self.int_position_dict[f"{ax}_pos"] = getattr(self,  f"int_{ax}_pos")

    def update_position_dictionaries(self):
        self.create_position_dict()
        for ax in self.axes:
            int_pos = getattr(self, f"{ax}_pos") + getattr(self, f"int_{ax}_pos_offset")
            setattr(self, f"int_{ax}_pos", int_pos)
        self.create_internal_position_dict()
        logger.debug(f"Stage Position:, {self.int_position_dict}")

    def get_abs_position(self, axis, move_dictionary):
        r"""
        Ensure the requested position is within axis bounds and return it.

        Parameters
        ----------
        axis : str
            An axis prefix in move_dictionary. For example, axis='x' corresponds to 'x_abs', 'x_min', etc.
        move_dictionary : dict
            A dictionary of values required for movement. Includes 'x_abs', 'x_min', etc. for one or more axes.
            Expects values in micrometers, except for theta, which is in degrees.

        Returns
        -------
        float
            Position to move the stage to for this axis.
        """
        try:
            # Get all necessary attributes. If we can't we'll move to the error case.
            axis_abs = move_dictionary[f"{axis}_abs"] - getattr(self, f"int_{axis}_pos_offset",
                                                                0)  # TODO: should we default to 0?
            axis_min, axis_max = getattr(self, f"{axis}_min"), getattr(self, f"{axis}_max")

            # Check that our position is within the axis bounds, fail if it's not.
            if (axis_min > axis_abs) or (axis_max < axis_abs):
                log_string = f"Absolute movement stopped: {axis} limit would be reached!" \
                             f"{axis_abs} is not in the range {axis_min} to {axis_max}."
                logger.info(log_string)
                print(log_string)
                # Return a ridiculous value to make it clear we've failed.
                # This is to avoid returning a duck type.
                return -1e50
            return axis_abs
        except (KeyError, AttributeError):
            return -1e50

    def stop(self):
        r"""Stop all stage movement abruptly.
        """
        pass
