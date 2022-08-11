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
import platform
import sys
import tkinter as tk
import logging

# Third Party Imports
import cv2
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import numpy as np

# Local Imports
from aslm.controller.sub_controllers.gui_controller import GUI_Controller
from aslm.tools.decorators import function_timer
# Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)


class Camera_View_Controller(GUI_Controller):
    def __init__(self,
                 view,
                 parent_controller=None):

        super().__init__(view,
                         parent_controller)

        # Logging
        self.logger = logging.getLogger(p)

        # Getting Widgets/Buttons
        self.image_metrics = view.image_metrics.get_widgets()
        self.image_palette = view.scale_palette.get_widgets()
        self.canvas = self.view.canvas

        # Get canvas width and height. Accounts for padding.
        self.canvas_height = self.view.canvas.winfo_height()-4
        self.canvas_width = self.view.canvas.winfo_width()-4

        # Binding for adjusting the lookup table min and max counts.
        # keys = ['Autoscale', 'Min','Max']
        self.image_palette['Autoscale'].widget.config(command=self.toggle_min_max_buttons)
        self.image_palette['Min'].widget.config(command=self.update_min_max_counts)
        self.image_palette['Max'].widget.config(command=self.update_min_max_counts)

        # Bindings for changes to the LUT
        # keys = ['Gray','Gradient','Rainbow']
        self.image_palette['Gray'].widget.config(command=self.update_LUT)
        self.image_palette['Gradient'].widget.config(command=self.update_LUT)
        self.image_palette['Rainbow'].widget.config(command=self.update_LUT)

        # Transpose and live bindings
        self.image_palette['Flip XY'].widget.config(command=self.transpose_image)
        self.view.live_frame.live.bind("<<ComboboxSelected>>", self.update_display_state)

        # Left Click Binding
        # self.canvas.bind("<Button-1>", self.left_click)

        # Slider Binding
        # self.view.slider.slider_widget.bind("<Button-1>", self.slider_update)

        # Mouse Wheel Binding
        # if platform.system() == 'Windows':
        #     self.canvas.bind("<MouseWheel>", self.mouse_wheel)
        # elif platform.system() == 'Linux':
        #     self.canvas.bind("<Button-4>", self.mouse_wheel)
        #     self.canvas.bind("<Button-5>", self.mouse_wheel)

        # Right-Click Binding
        self.menu = tk.Menu(self.canvas, tearoff=0)
        self.menu.add_command(label="Move Here", command=self.move_stage)
        self.menu.add_command(label="Reset Display", command=self.reset_display)
        # self.canvas.bind("<Button-3>", self.popup_menu)
        self.move_to_x = None
        self.move_to_y = None

        #  Stored Images
        self.tk_image = None
        self.image = None
        self.cross_hair_image = None
        self.saturated_pixels = None
        self.down_sampled_image = None
        self.zoom_image = None

        # Widget Defaults
        self.autoscale = True
        self.max_counts = None
        self.min_counts = None
        self.apply_cross_hair = True
        self.mode = 'stop'
        self.transpose = False
        self.display_state = "Live"

        # Colormap Information
        self.colormap = 'gray'
        self.gray_lut = plt.get_cmap('gist_gray')
        self.gradient_lut = plt.get_cmap('plasma')
        self.rainbow_lut = plt.get_cmap('afmhot')

        self.image_count = 0
        self.temp_array = None
        self.rolling_frames = 1
        self.bit_depth = 8  # bit-depth for PIL presentation.
        self.zoom_value = 1
        self.zoom_x_pos = 0
        self.zoom_y_pos = 0
        self.original_image_height = None
        self.original_image_width = None
        self.number_of_slices = 0
        self.image_volume = None
        self.total_images_per_volume = 0
        self.number_of_channels = 0
        self.image_counter = 0
        self.slice_index = 0
        self.channel_index = 0

    def slider_update(self, event):
        slider_index = self.view.slider.get()
        channel_display_index = 0
        self.retrieve_image_slice_from_volume(slider_index=slider_index,
                                              channel_display_index=channel_display_index)
        self.reset_display()

    def update_display_state(self, event):
        r"""Image Display Combobox Called.

        Sets self.display_state to desired display format.  Toggles state of slider widget. Sets number of
        positions.

        Parameters
        ----------
        event : tk.event
            Tk event object.

        """
        self.display_state = self.view.live_frame.live.get()
        # Slice in the XY Dimension.
        if self.display_state == 'XY Slice':
            print("XY Slice")
            try:
                slider_length = np.shape(self.image_volume)[2] - 1
            except IndexError:
                slider_length = self.parent_controller.experiment.MicroscopeState['number_z_steps'] - 1
        if self.display_state == 'YZ Slice':
            try:
                slider_length = np.shape(self.image_volume)[0] - 1
            except IndexError:
                slider_length = self.parent_controller.experiment.CameraParameters['y_pixels'] - 1
        if self.display_state == 'YZ Slice':
            try:
                slider_length = np.shape(self.image_volume)[1] - 1
            except IndexError:
                slider_length = self.parent_controller.experiment.CameraParameters['x_pixels'] - 1

        if self.display_state.find('Slice') != -1:
            self.view.slider.slider_widget.configure(to=slider_length,
                                                     tickinterval=(slider_length / 5),
                                                     state='normal')
        else:
            self.view.slider.slider_widget.configure(state='disabled')

    def get_absolute_position(self):
        x = self.parent_controller.view.winfo_pointerx()
        y = self.parent_controller.view.winfo_pointery()
        return x, y

    def popup_menu(self,
                   event):
        r"""Right-Click Popup Menu

        Parameters
        ----------
        event : tkinter.Event
            x, y location.  0,0 is top left corner.

        """
        try:
            self.move_to_x = event.x
            self.move_to_y = event.y
            x, y = self.get_absolute_position()
            self.menu.tk_popup(x, y)
        finally:
            self.menu.grab_release()

    def initialize(self,
                   name,
                   data):
        r"""Sets widgets based on data given from main controller/config.

        Parameters
        ----------
        name : str
            'minmax', 'image'.
        data : list
            Min and max intensity values.
        """
        # Pallete section (colors, autoscale, min/max counts)
        # keys = ['Frames to Avg', 'Image Max Counts', 'Channel']
        if name == 'minmax':
            min = data[0]
            max = data[1]

            # Invoking defaults
            self.image_palette['Gray'].widget.invoke()
            self.image_palette['Autoscale'].widget.invoke()

            # Populating defaults
            self.image_palette['Min'].set(min)
            self.image_palette['Max'].set(max)
            self.image_palette['Min'].widget['state'] = 'disabled'
            self.image_palette['Max'].widget['state'] = 'disabled'

        self.image_palette['Flip XY'].widget.invoke()

        # Image Metrics section
        if name == 'image':
            frames = data[0]
            # Populating defaults
            self.image_metrics['Frames'].set(frames)

    #  Set mode for the execute statement in main controller

    def set_mode(self,
                 mode=''):
        r"""Sets mode of camera_view_controller.

        Parameters
        ----------
        mode : str
            camera_view_controller mode.
        """
        self.mode = mode

    def move_stage(self):
        r"""Move the stage according to the position the user clicked."""
        # TODO: Account for the digital zoom value when calculating these values.
        height_scaling_factor = self.original_image_height / self.canvas_height
        width_scaling_factor = self.original_image_width / self.canvas_width
        print("Move stage to pixel:", height_scaling_factor * self.move_to_y, width_scaling_factor * self.move_to_x)

    def reset_display(self):
        r"""Set the display back to the original digital zoom."""
        self.zoom_value = 1
        self.process_image()

    def process_image(self):
        self.digital_zoom()  # self.image -> self.zoom_image.
        self.detect_saturation()  # self.zoom_image -> self.zoom_image
        self.down_sample_image()  # self.zoom_image -> self.down_sampled_image
        self.scale_image_intensity()  # self.down_sampled_image  -> self.down_sampled_image
        self.add_crosshair()  # self_down_sampled_image -> self.cross_hair_image
        self.apply_LUT()  # self_cross_hair_image -> self.cross_hair_image)
        self.populate_image()  # self.cross_hair_image -> display...

    def mouse_wheel(self,
                    event):
        r"""Digitally zooms in or out on the image upon scroll wheel event.

        Sets the self.zoom_value between 0.05 and 1 in .05 unit steps.

        Parameters
        ----------
        event : tkinter.Event
            num = 4 is zoom out.
            num = 5 is zoom in.
            x, y location.  0,0 is top left corner.

        """
        self.zoom_x_pos = int(event.x)
        self.zoom_y_pos = int(event.y)
        delta = 120 if platform.system() != 'Darwin' else 1
        threshold = event.delta/delta
        if (event.num == 4) or (threshold > 0):
            # Zoom out event.
            if self.zoom_value < 1:
                self.zoom_value = self.zoom_value + .05
        if (event.num == 5) or (threshold < 0):
            # Zoom in event.
            if self.zoom_value > 0.05:
                self.zoom_value = self.zoom_value - .05

        self.process_image()

    def digital_zoom(self):
        r"""Apply digital zoom.

        The x and y positions are between 0 and the canvas width and height respectively.

        """
        # New image size. Should be an integer value that is divisible by 2.
        new_image_height = int(np.floor(self.zoom_value * self.original_image_height))
        if new_image_height % 2 == 1:
            new_image_height = new_image_height - 1

        new_image_width = int(np.floor(self.zoom_value * self.original_image_width))
        if new_image_width % 2 == 1:
            new_image_width = new_image_width - 1

        # zoom_x_pos and y_pos are between 0 and 512.
        scaling_factor_x = int(self.original_image_width / self.canvas_width)
        scaling_factor_y = int(self.original_image_height / self.canvas_height)
        x_start_index = (self.zoom_x_pos * scaling_factor_x) - (new_image_width / 2)
        x_end_index = (self.zoom_x_pos * scaling_factor_x) + (new_image_width / 2)
        y_start_index = (self.zoom_y_pos * scaling_factor_y) - (new_image_height / 2)
        y_end_index = (self.zoom_y_pos * scaling_factor_y) + (new_image_height / 2)

        if y_start_index < 0:
            y_start_index = 0
            y_end_index = new_image_height

        if x_start_index < 0:
            x_start_index = 0
            x_end_index = new_image_width

        if y_end_index > self.original_image_height:
            y_start_index = self.original_image_height - new_image_height
            y_end_index = self.original_image_height

        if x_end_index > self.original_image_width:
            x_start_index = self.original_image_width - new_image_width
            x_end_index = self.original_image_width

        # Guarantee type int.
        x_start_index = int(x_start_index)
        x_end_index = int(x_end_index)
        y_start_index = int(y_start_index)
        y_end_index = int(y_end_index)
        self.zoom_image = self.image[y_start_index:y_end_index, x_start_index:x_end_index]

    def left_click(self,
                   event):
        r"""Toggles cross-hair on image upon left click event."""
        if self.image is not None:
            # If True, make False. If False, make True.
            self.apply_cross_hair = not self.apply_cross_hair
            self.add_crosshair()
            self.apply_LUT()
            self.populate_image()

    def update_max_counts(self):
        """Update the max counts in the camera view.
        Function gets the number of frames to average from the VIEW.
         If frames to average == 0 or 1, provides the maximum value from the last acquired data.
         If frames to average >1, initializes a temporary array, and appends each subsequent image to it.
         Once the number of frames to average has been reached, deletes the first image in.
         Reports the rolling average.
        """
        self.rolling_frames = int(self.image_metrics['Frames'].get())
        if self.rolling_frames == 0:
            # Cannot average 0 frames. Set to 1, and report max intensity
            self.image_metrics['Frames'].set(1)
            self.image_metrics['Image'].set(self.max_counts)

        elif self.rolling_frames == 1:
            self.image_metrics['Image'].set(self.max_counts)

        else:
            #  Rolling Average
            self.image_count = self.image_count + 1
            if self.image_count == 1:
                # First frame of the rolling average
                self.temp_array = self.down_sampled_image
                self.image_metrics['Image'].set(self.max_counts)
            else:
                # Subsequent frames of the rolling average
                self.temp_array = np.dstack((self.temp_array, self.down_sampled_image))
                if np.shape(self.temp_array)[2] > self.rolling_frames:
                    self.temp_array = np.delete(self.temp_array, 0, 2)

                # Update GUI
                self.image_metrics['Image'].set(np.max(self.temp_array))

    def down_sample_image(self, factor=4, fast=True):
        r"""Down-sample the data for image display according to widget size.."""
        if fast:
            # Approx. 3800x faster than cv2.resize(), but no interpolation
            self.down_sampled_image = self.zoom_image[::factor, ::factor]
        else:
            sx, sy = self.original_image_width//factor, self.original_image_height//factor
            self.down_sampled_image = cv2.resize(self.zoom_image, (sx, sy))

    def scale_image_intensity(self):
        r"""Scale the data to the min/max counts, and adjust bit-depth."""
        if self.autoscale is True:
            self.max_counts = np.max(self.down_sampled_image)
            self.min_counts = np.min(self.down_sampled_image)
            scaling_factor = 1
            self.down_sampled_image = scaling_factor * ((self.down_sampled_image - self.min_counts) /
                                                        (self.max_counts - self.min_counts))
        else:
            self.update_min_max_counts()
            scaling_factor = 1
            self.image = scaling_factor * ((self.down_sampled_image - self.min_counts) /
                                           (self.max_counts - self.min_counts))
            self.down_sampled_image[self.down_sampled_image < 0] = 0
            self.down_sampled_image[self.down_sampled_image > scaling_factor] = scaling_factor

    def populate_image(self):
        r"""Converts image to an ImageTk.PhotoImage and populates the Tk Canvas"""
        self.tk_image = ImageTk.PhotoImage(Image.fromarray(self.cross_hair_image.astype(np.uint8)))
        self.canvas.create_image(0, 0, image=self.tk_image, anchor='nw')

    def initialize_non_live_display(self,
                                    buffer,
                                    microscope_state,
                                    camera_parameters):
        r"""Starts image and slice counter, number of channels, number of slices, images per volume, and image volume.

        Parameters
        ----------
        microscope_state : dict
            State of the microscope
        """
        self.image_counter = 0
        self.slice_index = 0
        self.number_of_channels = len(microscope_state['channels'])
        self.number_of_slices = int(microscope_state['number_z_steps'])
        self.total_images_per_volume = self.number_of_channels * self.number_of_slices
        self.original_image_width = int(camera_parameters['x_pixels'])
        self.original_image_height = int(camera_parameters['y_pixels'])
        self.image_volume = np.zeros((self.original_image_width,
                                      self.original_image_height,
                                      self.number_of_slices,
                                      self.number_of_channels))


    def identify_channel_index_and_slice(self,
                                         microscope_state,
                                         images_received):
        R"""As images arrive, identify channel index and slice.

        Parameters
        ----------
        microscope_state : dict
            State of the microscope
        """
        # Reset the image counter after the full acquisition of an image volume.
        if self.image_counter == self.total_images_per_volume:
            self.image_counter = 0

        # Store each image to the pre-allocated memory.
        if microscope_state['stack_cycling_mode'] == 'per_stack':
            if 0 * self.number_of_slices <= self.image_counter < 1 * self.number_of_slices:
                self.channel_index = 0
            elif 1 * self.number_of_slices <= self.image_counter < 2 * self.number_of_slices:
                self.channel_index = 1
            elif 2 * self.number_of_slices <= self.image_counter < 3 * self.number_of_slices:
                self.channel_index = 2
            elif 3 * self.number_of_slices <= self.image_counter < 4 * self.number_of_slices:
                self.channel_index = 3
            elif 4 * self.number_of_slices <= self.image_counter < 5 * self.number_of_slices:
                self.channel_index = 4
            else:
                self.channel_index = 0
                print("Camera View Controller - Cannot identify proper channel for per_stack imaging mode.")

            self.slice_index = self.image_counter - (self.channel_index * self.number_of_slices)
            self.image_counter += 1

        elif microscope_state['stack_cycling_mode'] == 'per_z':
            # Every image that comes in will be the next channel.
            self.channel_index = images_received % self.number_of_channels
            self.image_volume[:, :, self.slice_index, self.channel_index] = self.image
            if self.channel_index == (self.number_of_channels - 1):
                self.slice_index += 1
            if self.slice_index == self.total_images_per_volume:
                self.slice_index = 0

        print(self.channel_index, self.slice_index)

    def retrieve_image_slice_from_volume(self,
                                         slider_index,
                                         channel_display_index):
        if self.display_state == 'XY MIP':
            self.image = np.max(self.image_volume[:, :, :, channel_display_index], axis=2)
        if self.display_state == 'YZ MIP':
            self.image = np.max(self.image_volume[:, :, :, channel_display_index], axis=0)
        if self.display_state == 'ZY MIP':
            self.image = np.max(self.image_volume[:, :, :, channel_display_index], axis=1)
        if self.display_state == 'XY Slice':
            self.image = self.image_volume[:, :, slider_index, channel_display_index]
        if self.display_state == 'YZ Slice':
            self.image = self.image_volume[slider_index, :, :, channel_display_index]
        if self.display_state == 'ZY Slice':
            self.image = self.image_volume[:, slider_index, :, channel_display_index]

    def display_image(self,
                      image,
                      microscope_state,
                      images_received=0):
        r"""Displays a camera image using the Lookup Table specified in the View.

        If Autoscale is selected, automatically calculates the min and max values for the data.
        If Autoscale is not selected, takes the user values as specified in the min and max counts.

        Parameters
        ----------
        image: ndarray
            Acquired image.
        microscope_state : dict
            State of the microscope
        images_received : int
            Number of channels received.
        """

        # Identify image identity (e.g., slice #, channel #).
        # self.identify_channel_index_and_slice(microscope_state=microscope_state,
        #                                       images_received=images_received)

        # Place image in memory
        # TODO: This is the slow part
        # self.image_volume[:, :, self.slice_index, self.channel_index] = image[:, ]       # copy

        if self.transpose:
            self.image = image.T
        else:
            self.image = image  # self.image_volume[:, :, self.slice_index, self.channel_index]  # pass by reference

        # MIP and Slice Mode TODO: Consider channels
        # if self.display_state != 'Live':
        #     slider_index = self.view.slider.slider_widget.get()
        #     channel_display_index = 0
        #     self.retrieve_image_slice_from_volume(slider_index=slider_index,
        #                                           channel_display_index=channel_display_index)
        #
        # else:
        self.process_image()
        self.update_max_counts()
        self.image_metrics['Channel'].set(self.channel_index)
        self.image_count = self.image_count + 1

    def add_crosshair(self):
        r"""Adds a cross-hair to the image.

        Params
        -------
        self.image : np.array
            Must be a 2D image.

        Returns
        -------
        self.apply_cross_hair_image : np.arrays
            2D image, scaled between 0 and 1 with cross-hair if self.apply_cross_hair == True
        """
        self.cross_hair_image = np.copy(self.down_sampled_image)
        if self.apply_cross_hair:
            (height, width) = np.shape(self.down_sampled_image)
            height = int(np.floor(height / 2))
            width = int(np.floor(width / 2))
            self.cross_hair_image[:, width] = 1
            self.cross_hair_image[height, :] = 1

    def apply_LUT(self):
        r"""Applies a LUT to the image.

        Red is reserved for saturated pixels.
        self.color_values = ['gray', 'gradient', 'rainbow']
        """
        if self.colormap == 'gradient':
            self.cross_hair_image = self.rainbow_lut(self.cross_hair_image)
        elif self.colormap == 'rainbow':
            self.cross_hair_image = self.gradient_lut(self.cross_hair_image)
        else:
            self.cross_hair_image = self.gray_lut(self.cross_hair_image)

        # Convert RGBA to RGB Image.
        self.cross_hair_image = self.cross_hair_image[:, :, :3]

        # Specify the saturated values in the red channel
        if np.any(self.saturated_pixels):
            # Saturated pixels is an array of True False statements same size as the image.
            # Pull out the red image from the RGBA, set saturated pixels to 1, put back into array.
            red_image = self.cross_hair_image[:, :, 2]
            red_image[self.saturated_pixels] = 1
            self.cross_hair_image[:, :, 2] = red_image

        # Scale back to an 8-bit image.
        self.cross_hair_image = self.cross_hair_image * (2 ** self.bit_depth - 1)

    def update_LUT(self):
        r"""Update the LUT in the Camera View.

        When the LUT is changed in the GUI, this function is called.
        Updates the LUT.
        """
        if self.image is None:
            pass
        else:
            self.colormap = self.view.scale_palette.color.get()
            self.add_crosshair()
            self.apply_LUT()
            self.populate_image()
            logger.debug(f"Updating the LUT, {self.colormap}")

    def detect_saturation(self):
        r"""Look for any pixels at the maximum intensity allowable for the camera. """
        saturation_value = 2**16-1
        self.saturated_pixels = self.zoom_image[self.zoom_image > saturation_value]

    def toggle_min_max_buttons(self):
        r"""Checks the value of the autoscale widget.

        If enabled, the min and max widgets are disabled and the image intensity is autoscaled.
        If disabled, miu and max widgets are enabled, and image intensity scaled.
        """
        self.autoscale = self.image_palette['Autoscale'].get()
        if self.autoscale is True:  # Autoscale Enabled
            self.image_palette['Min'].widget['state'] = 'disabled'
            self.image_palette['Max'].widget['state'] = 'disabled'
            logger.info("Autoscale Enabled")

        elif self.autoscale is False:  # Autoscale Disabled
            self.image_palette['Min'].widget['state'] = 'normal'
            self.image_palette['Max'].widget['state'] = 'normal'
            logger.info("Autoscale Disabled")
            self.update_min_max_counts()

    def transpose_image(self):
        r"""Get Flip XY widget value from the View."""
        self.transpose = self.image_palette['Flip XY'].get()

    def update_min_max_counts(self):
        """Get min and max count values from the View.

        When the min and max counts are toggled in the GUI, this function is called.
        Updates the min and max values.
        """
        self.min_counts = self.image_palette['Min'].get()
        self.max_counts = self.image_palette['Max'].get()
        logger.debug(f"Min and Max counts scaled to, {self.min_counts}, {self.max_counts}")
