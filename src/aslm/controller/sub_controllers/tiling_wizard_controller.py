"""Copyright (c) 2021-2022  The University of Texas Southwestern Medical Center.
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

# Standard Library Imports
import logging

# Third Party Imports

# Local Imports
from aslm.tools.multipos_table_tools import *
from aslm.controller.sub_controllers.gui_controller import GUI_Controller
from aslm.controller.aslm_controller_functions import combine_funcs

# Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)


class Tiling_Wizard_Controller(GUI_Controller):
    """
    Controller for tiling wizard parameters.
    Gathers the FOV from the camera settings tab and will update when user changes this value.
    Set start/end position buttons will grab the stage values for the respective axis when pressed and display in popup
    Number of images we need to acquire with our desired percent overlap is calculated and then displayed in third column


    Parameters
    ----------
    view : object
        GUI element containing widgets and variables to control. Likely tk.Toplevel-derived. In this case tiling_wizard_popup.py
    parent_controller : channels_tab_controller
        The controller that creates the popup/this controller.

    Returns
    -------
    None
    """

    def __init__(self,
                 view,
                 parent_controller):
        super().__init__(view, parent_controller)

        # Getting widgets and buttons and vars of widgets
        self.widgets = self.view.get_widgets()
        self.buttons = self.view.get_buttons()
        self.variables = self.view.get_variables()

        # Init widgets to zero
        self._axes = ['x', 'y', 'z']
        self._percent_overlay = 0.0
        self._fov = dict([(ax, 0.0) for ax in self._axes])
        self.variables['percent_overlay'].set(0.0)
        self.variables['total_tiles'].set(1)

        for ax in self._axes:
            self.variables[f'{ax}_start'].set(0.0)
            self.variables[f'{ax}_end'].set(0.0)
            self.variables[f'{ax}_dist'].set(0.0)
            self.variables[f'{ax}_tiles'].set(1)

        # Ref to widgets in other views (Camera Settings, Stage Control Positions, Stack Acq Settings)
        main_view = self.parent_controller.parent_controller.view  # channels_tab_controller -> aslm_controller -> view
        self.cam_settings_widgets = main_view.settings.camera_settings_tab.camera_roi.get_widgets()
        self.stack_acq_widgets = main_view.settings.channels_tab.stack_acq_frame.get_widgets()
        self.stage_position_vars = main_view.settings.stage_control_tab.position_frame.get_variables()
        self.multipoint_table = main_view.settings.multiposition_tab.multipoint_list.get_table()

        # Setting/Tracing Percent Overlay
        # Overlay change is also handled in update_overlay
        self.variables['percent_overlay'].trace_add('write', lambda *args: self.update_overlay())

        # Trace cam_settings FOV to catch user changes
        # FOV change handled in update_fov
        self.cam_settings_widgets['FOV_X'].get_variable().trace_add('write', lambda *args: self.update_fov())
        self.cam_settings_widgets['FOV_Y'].get_variable().trace_add('write', lambda *args: self.update_fov())
        self.stack_acq_widgets['abs_z_start'].get_variable().trace_add('write', lambda *args: self.update_fov())
        self.stack_acq_widgets['abs_z_end'].get_variable().trace_add('write', lambda *args: self.update_fov())

        # Calculate distances
        # TODO: For reasons that make no sense to me at all, these can't go in a for ax in self._axes loop?
        self.variables['x_start'].trace_add('write', lambda *args: self.calculate_distance('x'))
        self.variables['x_end'].trace_add('write', lambda *args: self.calculate_distance('x'))
        self.variables['y_start'].trace_add('write', lambda *args: self.calculate_distance('y'))
        self.variables['y_end'].trace_add('write', lambda *args: self.calculate_distance('y'))
        self.variables['z_start'].trace_add('write', lambda *args: self.calculate_distance('z'))
        self.variables['z_end'].trace_add('write', lambda *args: self.calculate_distance('z'))

        self.variables['x_start'].trace_add('write', lambda *args: self.update_fov())
        self.variables['x_end'].trace_add('write', lambda *args: self.update_fov())
        self.variables['y_start'].trace_add('write', lambda *args: self.update_fov())
        self.variables['y_end'].trace_add('write', lambda *args: self.update_fov())
        self.variables['z_start'].trace_add('write', lambda *args: self.update_fov())
        self.variables['z_end'].trace_add('write', lambda *args: self.update_fov())

        # Calculating Number of Tiles traces
        # TODO: For reasons that make no sense to me at all, these can't go in a for ax in self._axes loop?
        self.variables['x_dist'].trace_add('write', lambda *args: self.calculate_tiles('x'))
        self.variables['y_dist'].trace_add('write', lambda *args: self.calculate_tiles('y'))
        self.variables['z_dist'].trace_add('write', lambda *args: self.calculate_tiles('z'))

        # Populate Table trace
        self.buttons['set_table'].configure(command=self.set_table)

        for ax in self._axes:
            # Start/End buttons
            self.buttons[f'{ax}_start'].configure(command=self.position_handler(ax, 'start'))
            self.buttons[f'{ax}_end'].configure(command=self.position_handler(ax, 'end'))

            # Calculating total tile traces
            self.variables[f'{ax}_tiles'].trace_add('write', lambda *args: self.update_total_tiles())

        # Hidden focus variables for z-stacking
        # TODO: Don't special case? Idk.
        self._f_start = self.stage_position_vars['f'].get()
        self._f_end = self.stage_position_vars['f'].get()

        # Update widgets to current values in other views
        self.update_fov()

        # Properly Closing Popup with parent controller
        self.view.popup.protocol("WM_DELETE_WINDOW", combine_funcs(self.view.popup.dismiss,
                                                                   lambda: delattr(self.parent_controller,
                                                                                   'tiling_wizard_controller')))

    def set_table(self):
        """
        Sets multiposition table with values from tiling wizard after Populate Multiposition Table button is pressed
        Compute grid will return a list of all position combinations. This list is then converted to a 
        pandas dataframe which is then set as the new table data. The table is then redrawn.

        Parameters
        ----------
        self : object
            Tiling Wizard Controller instance
        

        Returns
        -------
        None
        """

        x_start = float(self.variables['x_start'].get())
        x_stop = float(self.variables['x_end'].get())
        x_tiles = int(self.variables['x_tiles'].get())

        y_start = float(self.variables['y_start'].get())
        y_stop = float(self.variables['y_end'].get())
        y_tiles = int(self.variables['y_tiles'].get())

        # shift z by coordinate origin of local z-stack
        z_start = float(self.variables['z_start'].get()) + float(self.stack_acq_widgets['start_position'].get())
        z_stop = float(self.variables['z_end'].get())
        z_tiles = int(self.variables['z_tiles'].get())

        # Default to fixed theta
        r_start = self.stage_position_vars['theta'].get()
        r_stop = self.stage_position_vars['theta'].get()
        r_tiles = 1

        # for consistency, always go from low to high
        if x_start > x_stop:
            tmp = x_start
            x_start = x_stop
            x_stop = tmp
        if y_start > y_stop:
            tmp = y_start
            y_start = y_stop
            y_stop = tmp
        if z_start > z_stop:
            tmp = z_start
            z_start = z_stop
            z_stop = tmp
        if r_start > r_stop:
            tmp = r_start
            r_start = r_stop
            r_stop = tmp
        if self._f_start > self._f_end:
            tmp = self._f_start
            self._f_start = self._f_end
            self._f_end = tmp

        ov = float(self._percent_overlay) / 100
        table_values = compute_tiles_from_bounding_box(x_start, x_tiles, abs(self._fov['x']), ov,
                                                        y_start, y_tiles, abs(self._fov['y']), ov,
                                                        z_start, z_tiles, abs(self._fov['z']), ov,
                                                        r_start, r_tiles, 0, ov,
                                                        self._f_start, z_tiles, (self._f_end-self._f_start), ov)

        update_table(self.multipoint_table, table_values)

    def update_total_tiles(self):
        """
        Sums the tiles for each axis in the tiling wizard. Will update when any axis has a tile amount change.
        
        Parameters
        ----------
        self : object
            Tiling Wizard Controller instance
        

        Returns
        -------
        None
        """

        x = float(self.variables['x_tiles'].get())
        y = float(self.variables['y_tiles'].get())
        z = float(self.variables['z_tiles'].get())

        total_tiles = x * y * z

        self.variables['total_tiles'].set(total_tiles)

    def calculate_tiles(self, axis=None):
        """
        Calculates the number of tiles of the acquisition for each axis or an individual axis
        Num of Tiles = dist - (overlay * FOV)  /  FOV * (1 - overlay) 
        (D-OF)/(F-OF) = N

        Parameters
        ----------
        self : object
            Tiling Wizard Controller instance
        axis : str
            x, y, z axis of stage to calculate.

        Returns
        -------
        None
        """

        if axis not in self._axes + [None]:
            logger.warning(f"Unknown axis {axis}, skipping calculate_tiles().")
            return

        if axis is not None:
            axis = [axis]
        else:
            axis = self._axes

        overlay = float(self._percent_overlay) / 100

        for ax in axis:
            dist = abs(float(self.variables[f"{ax}_dist"].get()))  # um
            fov = abs(float(self._fov[ax]))                        # um

            num_tiles = calc_num_tiles(dist, overlay, fov)

            self.variables[f"{ax}_tiles"].set(num_tiles)

    def calculate_distance(self, axis):
        """
        This function will calculate the distance for a given axis of the stage when the start or end position is changed via the Set buttons
        
        Parameters
        ----------
        self : object
            Tiling Wizard Controller instance
        axis : str
            x, y, z axis of stage to calculate

        Returns
        -------
        None

        """
        start = float(self.variables[axis + '_start'].get())
        end = float(self.variables[axis + '_end'].get())
        dist = abs(end - start)
        self.variables[axis + '_dist'].set(dist)
    
    def update_overlay(self):
        """
        Updates percent overlay when a user changes the widget in the popup. This value is used for backend calculations.
        The number of tiles will then be recalculated

        Parameters
        ----------
        self : object
            Tiling Wizard Controller instance

        Returns
        -------
        None
        """

        try:
            self._percent_overlay = float(self.variables['percent_overlay'].get())
            self.calculate_tiles()
        except ValueError:
            # most likely an empty string was passed
            pass
    
    def position_handler(self, axis, start_end):
        """
        When the Set [axis] Start/End button is pressed then the stage position is polled from the stage controller

        Parameters
        ----------
        self : object
            Tiling Wizard Controller instance
        axis : str
            x, y, z axis that corresponds to stage axis
        start_end : str
            start or end will signify which spinbox gets updated upon button press

        Returns
        -------
        handler : func
            Function for setting positional spinbox based on parameters passed in

        """
        def handler():
            pos = self.stage_position_vars[axis].get()
            self.widgets[axis + '_' + start_end].widget.set(pos)
            if axis == 'z':
                setattr(self, f"_f_{start_end}", self.stage_position_vars['f'].get())

        return handler

    def update_fov(self):
        """
        Grabs the updated FOV if changed by user, will recalculate num of tiles for each axis after

        Parameters
        ----------
        self : object
            Tiling Wizard Controller instance

        Returns
        -------
        None
        """

        # Calculate signed fov
        x = float(self.cam_settings_widgets['FOV_X'].get()) \
            * sign(float(self.variables['x_end'].get()) - float(self.variables['x_start'].get()))
        y = float(self.cam_settings_widgets['FOV_Y'].get()) \
            * sign(float(self.variables['y_end'].get()) - float(self.variables['y_start'].get()))
        z = float(self.stack_acq_widgets['end_position'].get()) - float(self.stack_acq_widgets['start_position'].get())
        self._fov['x'], self._fov['y'], self._fov['z'] = x, y, z

        self.calculate_tiles()

    def showup(self):
        """
        # this function will let the popup window show in front

        Parameters
        ----------
        self : object
            Tiling Wizard Controller instance

        Returns
        -------
        None
        """
        self.view.popup.deiconify()
        self.view.popup.attributes("-topmost", 1)

