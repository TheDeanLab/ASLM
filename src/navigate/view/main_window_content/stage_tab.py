# Copyright (c) 2021-2024  The University of Texas Southwestern Medical Center.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted for academic and research use only
# (subject to the limitations in the disclaimer below)
# provided that the following conditions are met:

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

# Standard Imports
import tkinter as tk
from tkinter import ttk
import logging
from pathlib import Path
from typing import Iterable, Optional

# Third Party Imports

# Local Imports
from navigate.view.custom_widgets.hover import HoverTkButton
from navigate.view.custom_widgets.LabelInputWidgetFactory import LabelInput
from navigate.view.custom_widgets.validation import ValidatedSpinbox
from navigate.view.custom_widgets.validation import ValidatedEntry
import navigate

# Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)


class StageControlNotebook(ttk.Notebook):
    """Notebook for stage control tab."""

    def __init__(
        self,
        frame: "navigate.view.main_window_content."
        "settings_notebook.SettingsNotebook",
        *args: Iterable,
        **kwargs: dict,
    ) -> None:
        """Initialize the stage control notebook.

        Parameters
        ----------
        frame : SettingsNotebook
            The frame to put notebook into.
        *args : Iterable
            Arguments for ttk.Notebook
        **kwargs : Iterable
            Keyword arguments for ttk.Notebook
        """

        super().__init__()
        # super().__init__(self, frame, *args, **kwargs).grid(row=0, column=0)

        #: StageControlTab: Stage control tab.
        self.stage_control_tab = StageControlTab(self)

        # Adding tabs to notebook
        self.add(self.stage_control_tab, text="Stage Control", sticky=tk.NSEW)


class StageControlTab(tk.Frame):
    """Stage Control Tab for stage control notebook."""

    def __init__(
        self, note3: StageControlNotebook, *args: Iterable, **kwargs: dict
    ) -> None:
        """Initialize the stage control tab.

        Parameters
        ----------
        note3 : StageControlNotebook
            Stage control notebook.
        *args : Iterable
            Arguments for tk.Frame
        **kwargs : dict
            Keyword arguments for tk.Frame
        """
        tk.Frame.__init__(self, note3, *args, **kwargs)

        #: int: Index of the stage control tab.
        self.index = 2

        #: PositionFrame: Position frame.
        self.position_frame = PositionFrame(self)
        self.position_frame.grid(row=0, column=0, sticky=tk.NSEW, padx=3, pady=3)

        #: XYFrame: XY frame.
        self.xy_frame = XYFrame(self)
        self.xy_frame.grid(row=0, column=1, sticky=tk.NSEW, padx=3, pady=3)

        #: OtherAxisFrame: Z frame.
        self.z_frame = OtherAxisFrame(stage_control_tab=self, name="Z")
        self.z_frame.grid(row=0, column=2, sticky=tk.NSEW, padx=3, pady=3)

        #: OtherAxisFrame: Theta frame.
        self.theta_frame = OtherAxisFrame(stage_control_tab=self, name="Theta")
        self.theta_frame.grid(row=1, column=2, sticky=tk.NSEW, padx=3, pady=3)

        # OtherAxisFrame: Focus frame.
        self.f_frame = OtherAxisFrame(stage_control_tab=self, name="Focus")
        self.f_frame.grid(row=1, column=0, sticky=tk.NSEW, padx=3, pady=3)

        #: StopFrame: Stop frame.
        self.stop_frame = StopFrame(
            stage_control_tab=self, name="Stage Movement Interrupt"
        )
        self.stop_frame.grid(row=1, column=1, sticky=tk.NSEW, padx=3, pady=3)

    def get_widgets(self) -> dict:
        """Get all widgets in the stage control tab.

        Returns
        -------
        widgets: dict
            Dictionary of widgets
        """
        temp = {**self.position_frame.get_widgets()}
        for axis in ["xy", "z", "theta", "f"]:
            temp[axis + "_step"] = getattr(self, axis + "_frame").get_widget()
        return temp

    def get_variables(self) -> dict:
        """Get all variables in the stage control tab.

        Returns
        -------
        variables: dict
            Dictionary of variables
        """
        temp = self.get_widgets()
        return {k: temp[k].get_variable() for k in temp}

    def get_buttons(self) -> dict:
        """Get all buttons in the stage control tab.

        Returns
        -------
        buttons: dict
            Dictionary of buttons
        """
        result = {**self.xy_frame.get_buttons()}
        for axis in ["z", "theta", "f"]:
            temp = getattr(self, axis + "_frame").get_buttons()
            result.update({k + "_" + axis + "_btn": temp[k] for k in temp})
        result.update(self.stop_frame.get_buttons())
        return result

    def toggle_button_states(
        self, joystick_is_on: bool = False, joystick_axes: Optional[list] = None
    ):
        """Enables/disables buttons and entries in the stage control tab,
        according to joystick axes.

        Parameters
        ----------
        joystick_is_on: bool
            'True' indicates that joystick mode is on
            'False' indicates that joystick mode is off
        joystick_axes: Optional[list]
            A list containing the axes controlled by the joystick, if any
        """
        if joystick_axes is None:
            joystick_axes = []

        self.xy_frame.toggle_button_states(joystick_is_on, joystick_axes)
        self.z_frame.toggle_button_states(joystick_is_on, joystick_axes)
        self.f_frame.toggle_button_states(joystick_is_on, joystick_axes)
        self.theta_frame.toggle_button_states(joystick_is_on, joystick_axes)
        self.position_frame.toggle_entry_states(joystick_is_on, joystick_axes)
        self.stop_frame.toggle_button_states(joystick_is_on, joystick_axes)

    def force_enable_all_axes(self) -> None:
        """Enable all buttons and entries in the stage control tab."""
        self.xy_frame.toggle_button_states(False, ["x", "y"])
        self.z_frame.toggle_button_states(False, ["z"])
        self.f_frame.toggle_button_states(False, ["f"])
        self.theta_frame.toggle_button_states(False, ["theta"])
        self.position_frame.toggle_entry_states(False, ["x", "y", "z", "theta", "f"])
        self.stop_frame.toggle_button_states(False, [])


class OtherAxisFrame(ttk.Labelframe):
    """Frame for the other axis movement buttons.

    This frame is used for the z, theta, and focus axis movement buttons.
    """

    def __init__(
        self,
        stage_control_tab: StageControlTab,
        name: str,
        *args: Iterable,
        **kwargs: dict,
    ) -> None:
        """Initialize the other axis frame.

        Parameters
        ----------
        stage_control_tab : StageControlTab
            The stage control tab that the other axis frame is in
        name : str
            The name of the axis that the frame is for
        *args : Iterable
            Positional arguments for the ttk.Labelframe
        **kwargs : Iterable
            Keyword arguments for the ttk.Labelframe
        """

        ttk.Labelframe.__init__(
            self,
            stage_control_tab,
            text=name + " Movement",
            labelanchor="n",
            *args,
            **kwargs,
        )

        #: str: Name of the axis.
        self.name = name
        image_directory = Path(__file__).resolve().parent

        #: tk.PhotoImage: Image for the up button.
        self.up_image = tk.PhotoImage(
            file=image_directory.joinpath("images", "up.png")
        ).subsample(2, 2)

        #: tk.PhotoImage: Image for the 5x up button.
        self.up_5x_image = tk.PhotoImage(
            file=image_directory.joinpath("images", "5x_up.png")
        ).subsample(2, 2)

        #: tk.PhotoImage: Image for the down button.
        self.down_image = tk.PhotoImage(
            file=image_directory.joinpath("images", "down.png")
        ).subsample(2, 2)

        #: tk.PhotoImage: Image for the 5x up button.
        self.down_5x_image = tk.PhotoImage(
            file=image_directory.joinpath("images", "5x_down.png")
        ).subsample(2, 2)

        #: tk.PhotoImage: Image for the disabled up button.
        self.d_up_image = tk.PhotoImage(
            file=image_directory.joinpath("images", "greyup_disabled.png")
        ).subsample(2, 2)

        #: tk.PhotoImage: Image for the disabled down button.
        self.d_down_image = tk.PhotoImage(
            file=image_directory.joinpath("images", "greydown_disabled.png")
        ).subsample(2, 2)

        #: list: List of images for the normal state.
        self.normal_images = [
            self.up_image,
            self.down_image,
            self.up_5x_image,
            self.down_5x_image,
        ]

        self.disabled_images = [
            self.d_up_image,
            self.d_down_image,
        ]

        # Setting up buttons for up, down and increment spinbox

        #: HoverTkButton: Up button.
        self.up_btn = HoverTkButton(self, image=self.up_image, borderwidth=0)

        #: HoverTkButton: 5x Up button.
        self.up_5x_btn = HoverTkButton(self, image=self.up_5x_image, borderwidth=0)

        #: HoverTkButton: Down button.
        self.down_btn = HoverTkButton(self, image=self.down_image, borderwidth=0)

        #: HoverTkButton: 5x Down button.
        self.down_5x_btn = HoverTkButton(self, image=self.down_5x_image, borderwidth=0)

        #: LabelInput: Increment spinbox.
        self.increment_box = LabelInput(
            parent=self,
            input_class=ValidatedSpinbox,
            input_var=tk.DoubleVar(),
            input_args={"width": 5},
        )

        # Center the widgets.
        self.columnconfigure(index=0, weight=1)
        self.columnconfigure(index=1, weight=1)
        self.columnconfigure(index=2, weight=1)

        # Adding space between buttons
        space_1 = ttk.Label(self, borderwidth=0)
        space_2 = ttk.Label(self, borderwidth=0)

        # Griding out buttons
        self.up_5x_btn.grid(row=0, column=1, rowspan=1, columnspan=1, padx=2, pady=2)
        self.up_btn.grid(row=1, column=1, rowspan=1, columnspan=1, padx=2, pady=2)
        space_1.grid(row=2, column=1, rowspan=1, columnspan=1, padx=2, pady=2)
        self.increment_box.grid(
            row=3, column=1, rowspan=1, columnspan=1, padx=2, pady=2
        )
        space_2.grid(row=4, column=1, rowspan=1, columnspan=1, padx=2, pady=2)
        self.down_btn.grid(row=5, column=1, rowspan=1, columnspan=1, padx=2, pady=2)
        self.down_5x_btn.grid(row=6, column=1, rowspan=1, columnspan=1, padx=2, pady=2)

    def get_widget(self) -> LabelInput:
        """Returns the frame widget

        Returns
        -------
        increment_box: LabelInput
            The increment widget
        """
        return self.increment_box

    def get_buttons(self) -> dict:
        """Returns the buttons in the frame

        Returns
        -------
        buttons: dict
            A dictionary of the buttons
        """
        return {
            "up": self.up_btn,
            "down": self.down_btn,
            # "5x_up": self.up_5x_btn,
            # "5x_down": self.down_5x_btn
        }

    def toggle_button_states(
        self, joystick_is_on: bool = False, joystick_axes: Optional[list] = None
    ):
        """Switches the images used as buttons between two states

        Parameters
        ----------
        joystick_is_on : bool
            'True' indicates that joystick mode is on
            'False' indicates that joystick mode is off
        joystick_axes : Optional[list]
            A list containing the axes controlled by the joystick, if any
        """

        if joystick_axes is None:
            joystick_axes = []
        buttons = [self.up_btn, self.down_btn, self.up_5x_btn, self.down_5x_btn]
        button_state = "normal"
        image_list = self.normal_images
        hover_list = self.normal_hover_texts

        if joystick_is_on:
            if (self.name.lower() in joystick_axes) or (
                self.name.lower() == "focus" and "f" in joystick_axes
            ):
                button_state = "disabled"
                image_list = self.disabled_images
                hover_list = self.disabled_hover_texts

        for k in range(len(buttons)):
            buttons[k]["state"] = button_state
            buttons[k].config(image=image_list[k])
            buttons[k].hover.setdescription(hover_list[k])


class PositionFrame(ttk.Labelframe):
    """Frame for the stage position entries.

    This frame is used for the x, y, z, theta, and focus position entries.
    """

    def __init__(
        self, stage_control_tab: StageControlTab, *args: Iterable, **kwargs: dict
    ) -> None:
        """Initialize the position frame.

        Parameters
        ----------
        stage_control_tab : StageControlTab
            The stage control tab that the position frame is in
        *args : Iterable
            Positional arguments for the ttk.Labelframe
        **kwargs : Iterable
            Keyword arguments for the ttk.Labelframe
        """

        ttk.Labelframe.__init__(
            self, stage_control_tab, text="Stage Positions", *args, **kwargs
        )

        #: dict: Dictionary of the label input widgets for the position entries.
        self.inputs = {}

        #: list: List of frames for the position entries.
        entry_names = ["x", "y", "z", "theta", "f"]

        #: list: List of labels for the position entries.
        entry_labels = ["X", "Y", "Z", "\N{Greek Capital Theta Symbol}", "F"]

        #: list: List of frames for the position entries.
        self.frame_back_list = []
        for i in range(len(entry_names)):
            self.inputs[entry_names[i]] = LabelInput(
                parent=self,
                label=entry_labels[i],
                input_class=ValidatedEntry,
                input_var=tk.StringVar(),
                input_args={
                    "required": True,
                    "precision": 0.1,
                    "width": 10,
                    "takefocus": False,
                },
            )
            self.frame_back_list.append(
                tk.Frame(self, bg="#f0f0f0", width=60, height=26)
            )
            self.frame_back_list[i].grid(row=i, column=0)
            self.inputs[entry_names[i]].grid(row=i, column=0)
            self.frame_back_list[i].lower()

    def get_widgets(self) -> dict:
        """Get all widgets in the position frame

        Returns
        -------
        inputs: dict
            A dictionary of the label input widgets for the position entries
        """

        return self.inputs

    def get_variables(self) -> dict:
        """Get all variables in the position frame

        Returns
        -------
        variables: dict
            A dictionary of the variables for the position entries
        """

        variables = {}
        for name in self.inputs:
            variables[name] = self.inputs[name].get_variable()
        return variables

    def toggle_entry_states(
        self, joystick_is_on: bool = False, joystick_axes: Optional[list] = None
    ) -> None:
        """Switches the images used as buttons between two states

        Parameters
        ----------
        joystick_is_on : bool
            'True' indicates that joystick mode is on
            'False' indicates that joystick mode is off
        joystick_axes : Optional[list]
            A list containing the axes controlled by the joystick, if any
        """

        if joystick_axes is None:
            joystick_axes = []

        frame_back_counter = 0
        if joystick_is_on:
            entry_state = "disabled"
            frame_back_color = "#ee868a"
        else:
            entry_state = "normal"
            frame_back_color = "#f0f0f0"

        for variable in self.get_variables():
            if variable in joystick_axes:
                self.frame_back_list[frame_back_counter]["bg"] = frame_back_color
                try:
                    self.inputs[f"{variable}"].widget["state"] = entry_state

                except KeyError:
                    pass
            frame_back_counter += 1


class XYFrame(ttk.Labelframe):
    """Frame for the x and y movement buttons.

    This frame is used for the up, down, left, right, and increment buttons.
    """

    def __init__(
        self, stage_control_tab: StageControlTab, *args: Iterable, **kwargs: dict
    ) -> None:
        """Initialize the XY frame.

        Parameters
        ----------
        stage_control_tab : StageControlTab
            The stage control tab that the XY frame is in
        *args : Iterable
            Positional arguments for the ttk.Labelframe
        **kwargs : dict
            Keyword arguments for the ttk.Labelframe
        """

        ttk.Labelframe.__init__(
            self,
            stage_control_tab,
            text="X Y Movement",
            labelanchor="n",
            *args,
            **kwargs,
        )

        # Path to arrows
        image_directory = Path(__file__).resolve().parent

        #: tk.PhotoImage: Image for the up button.
        self.up_image = tk.PhotoImage(
            file=image_directory.joinpath("images", "up.png")
        ).subsample(2, 2)

        #: tk.PhotoImage: Image for the 5x up button.
        self.up_5x_image = tk.PhotoImage(
            file=image_directory.joinpath("images", "5x_up.png")
        ).subsample(2, 2)

        #: tk.PhotoImage: Image for the down button.
        self.down_image = tk.PhotoImage(
            file=image_directory.joinpath("images", "down.png")
        ).subsample(2, 2)

        #: tk.PhotoImage: Image for the down button.
        self.down_5x_image = tk.PhotoImage(
            file=image_directory.joinpath("images", "5x_down.png")
        ).subsample(2, 2)

        #: tk.PhotoImage: Image for the left button.
        self.left_image = tk.PhotoImage(
            file=image_directory.joinpath("images", "left.png")
        ).subsample(2, 2)

        #: tk.PhotoImage: Image for the left button.
        self.left_5x_image = tk.PhotoImage(
            file=image_directory.joinpath("images", "5x_left.png")
        ).subsample(2, 2)

        #: tk.PhotoImage: Image for the right button.
        self.right_image = tk.PhotoImage(
            file=image_directory.joinpath("images", "right.png")
        ).subsample(2, 2)

        #: tk.PhotoImage: Image for the left button.
        self.right_5x_image = tk.PhotoImage(
            file=image_directory.joinpath("images", "5x_right.png")
        ).subsample(2, 2)

        #: tk.PhotoImage: Image for the disabled up button.
        self.d_up_image = tk.PhotoImage(
            file=image_directory.joinpath("images", "greyup_disabled.png")
        ).subsample(2, 2)

        #: tk.PhotoImage: Image for the disabled down button.
        self.d_down_image = tk.PhotoImage(
            file=image_directory.joinpath("images", "greydown_disabled.png")
        ).subsample(2, 2)

        #: tk.PhotoImage: Image for the disabled left button.
        self.d_left_image = tk.PhotoImage(
            file=image_directory.joinpath("images", "greyleft_disabled.png")
        ).subsample(2, 2)

        #: tk.PhotoImage: Image for the disabled right button.
        self.d_right_image = tk.PhotoImage(
            file=image_directory.joinpath("images", "greyright_disabled.png")
        ).subsample(2, 2)

        #: list: List of images for the normal state.
        self.normal_images = [
            self.right_image,
            self.left_image,
            self.up_image,
            self.down_image,
        ]

        #: list: List of hover texts for the normal state.
        self.normal_hover_texts = [
            "Decreases the X value of the stage's position",
            "Increases the X value of the stage's position",
            "Increases the Y value of the stage's position",
            "Decreases the Y value of the stage's position",
        ]

        #: list: List of images for the disabled state.
        self.disabled_images = [
            self.d_right_image,
            self.d_left_image,
            self.d_up_image,
            self.d_down_image,
        ]

        #: list: List of hover texts for the disabled state.
        self.disabled_hover_texts = [
            "Turn off Joystick Mode to enable" for i in range(4)
        ]

        #: HoverTkButton: Up button.
        self.up_y_btn = HoverTkButton(self, image=self.up_image, borderwidth=0)

        #: HoverTkButton: Up button.
        self.up_5y_btn = HoverTkButton(self, image=self.up_5x_image, borderwidth=0)

        #: HoverTkButton: Down button.
        self.down_y_btn = HoverTkButton(self, image=self.down_image, borderwidth=0)

        #: HoverTkButton: Down button.
        self.down_5y_btn = HoverTkButton(self, image=self.down_5x_image, borderwidth=0)

        #: HoverTkButton: Right button.
        self.up_x_btn = HoverTkButton(self, image=self.right_image, borderwidth=0)

        #: HoverTkButton: Right 5x button.
        self.up_5x_btn = HoverTkButton(self, image=self.right_5x_image, borderwidth=0)

        #: HoverTkButton: Left button.
        self.down_x_btn = HoverTkButton(self, image=self.left_image, borderwidth=0)

        #: HoverTkButton: Left 5x button.
        self.down_5x_btn = HoverTkButton(self, image=self.left_5x_image, borderwidth=0)

        #: LabelInput: Increment spinbox.
        self.increment_box = LabelInput(
            parent=self,
            input_class=ValidatedSpinbox,
            input_var=tk.DoubleVar(),
            input_args={"width": 5},
        )

        #: dict: Dictionary of the buttons for the x and y movement buttons.
        self.button_axes_dict = {
            "x": [self.up_x_btn, self.down_x_btn],
            "y": [self.up_y_btn, self.down_y_btn],
        }

        # Up
        self.up_5y_btn.grid(row=0, column=4, rowspan=2, columnspan=2, padx=2, pady=2)

        self.up_y_btn.grid(row=2, column=4, rowspan=2, columnspan=2, padx=2, pady=2)

        # Increment box.
        self.increment_box.grid(
            row=4, column=4, rowspan=3, columnspan=2, padx=2, pady=2
        )

        # Down
        self.down_y_btn.grid(row=7, column=4, rowspan=2, columnspan=2, padx=2, pady=2)

        self.down_5y_btn.grid(row=9, column=4, rowspan=2, columnspan=2, padx=2, pady=2)

        # Left
        self.down_5x_btn.grid(row=5, column=0, rowspan=2, columnspan=2, padx=2, pady=2)

        self.down_x_btn.grid(
            row=5,
            column=2,
            rowspan=2,
            columnspan=2,
            padx=2,
            pady=2,
        )

        # Right
        self.up_x_btn.grid(row=5, column=6, rowspan=2, columnspan=2, padx=2, pady=2)
        self.up_5x_btn.grid(row=5, column=8, rowspan=2, columnspan=2, padx=2, pady=2)

        # Increment spinbox
        self.increment_box.widget.set_precision(-1)

    def get_widget(self) -> LabelInput:
        """Returns the frame widget

        Returns
        -------
        increment_box: LabelInput
            The frame widget
        """

        return self.increment_box

    def get_buttons(self) -> dict:
        """Returns the buttons in the frame

        Returns
        -------
        buttons: dict
            A dictionary of the buttons
        """

        names = [
            "up_x_btn",
            "down_x_btn",
            "up_y_btn",
            "down_y_btn",
            "up_5x_btn",
            "down_5x_btn",
            "up_5y_btn",
            "down_5y_btn",
        ]
        return {k: getattr(self, k) for k in names}

    def toggle_button_states(
        self, joystick_is_on: bool = False, joystick_axes: Optional[list] = None
    ) -> None:
        """Switches the images used as buttons between two states

        joystick_is_on : bool
            False if buttons are normal, True if buttons are disabled
        joystick_axes : Optional[list]
            A list of the joystick axes
        """

        if joystick_axes is None:
            joystick_axes = []

        for axis in self.button_axes_dict.keys():
            if axis in joystick_axes:
                buttons = self.button_axes_dict[axis]
                axis_ascii = ord(axis)
                if joystick_is_on:
                    button_state = "disabled"
                    image_list = self.disabled_images
                    hover_list = self.disabled_hover_texts
                else:
                    button_state = "normal"
                    image_list = self.normal_images
                    hover_list = self.normal_hover_texts
                for k in range(len(buttons)):
                    buttons[k]["state"] = button_state
                    buttons[k].config(image=image_list[2 * (axis_ascii % 2) + k])
                    buttons[k].hover.setdescription(
                        hover_list[2 * (axis_ascii % 2) + k]
                    )


class StopFrame(ttk.Labelframe):
    """Frame for the stop button."""

    def __init__(
        self,
        stage_control_tab: StageControlTab,
        name: str,
        *args: Iterable,
        **kwargs: dict,
    ) -> None:
        """Initialize the stop frame.

        Parameters
        ----------
        stage_control_tab : StageControlTab
            Stage control tab.
        name : str
            Name of the frame.
        *args
            Arguments for ttk.Frame
        **kwargs
            Keyword arguments for ttk.Frame
        """

        # Init Frame
        ttk.Labelframe.__init__(
            self, stage_control_tab, text=name, labelanchor="n", *args, **kwargs
        )

        #: tk.Button: Stop button.
        self.stop_btn = tk.Button(
            self, bg="red", fg="white", text="STOP", width=20, height=6
        )

        #: HoverTkButton: Joystick button.
        self.joystick_btn = HoverTkButton(
            self, bg="white", fg="black", text="Enable Joystick", width=15, height=2
        )

        # Griding out buttons
        self.stop_btn.grid(row=0, column=0, rowspan=2, pady=2)
        self.joystick_btn.grid(row=2, column=0, rowspan=2, pady=2)

    def get_buttons(self) -> dict:
        """Returns the buttons in the frame

        Returns
        -------
        buttons: dict
            A dictionary of the buttons
        """
        return {"stop": self.stop_btn, "joystick": self.joystick_btn}

    def toggle_button_states(
        self, joystick_is_on: bool = False, joystick_axes: Optional[list] = None
    ):
        """Switches the images used as buttons between two states

        Parameters
        ----------
        joystick_is_on : bool
            'True' indicates that joystick mode is on
            'False' indicates that joystick mode is off
        joystick_axes : Optional[list]
            A list containing the axes controlled by the joystick, if any
        """
        if joystick_axes is None:
            # TODO: Look into this...
            _ = []

        if joystick_is_on:
            self.joystick_btn.config(text="Disable Joystick")
        else:
            self.joystick_btn.config(text="Enable Joystick")
