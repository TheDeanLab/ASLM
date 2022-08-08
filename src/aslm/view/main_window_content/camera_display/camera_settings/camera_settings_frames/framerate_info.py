"""
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
import logging
import tkinter as tk
from tkinter import ttk


from aslm.view.custom_widgets.LabelInputWidgetFactory import LabelInput
from aslm.view.custom_widgets.validation import ValidatedEntry, ValidatedSpinbox

# Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)

class framerate_info(ttk.LabelFrame):
    """
    # This class generates the framerate label frame. 
    Widgets can be adjusted below. Entry values need to be set in the controller.
    The widgets can be found in the dictionary by using the first word in the label, after using get_widgets
    The variables tied to each widget can be accessed via the widget directly or with the dictionary generated by get_variables.
    """
    def __init__(self, settings_tab, *args, **kwargs):
        #Init Frame
        text_label = 'Framerate Info'
        ttk.LabelFrame.__init__(self, settings_tab, text=text_label, *args, **kwargs)

        #  Holds widgests, this is done in case more widgets are to be added in a different frame, these can be grouped together
        content_frame = ttk.Frame(self)
        content_frame.grid(row=0, column=0, sticky=(tk.NSEW), pady=5, padx=5)
        
        # Formatting
        tk.Grid.columnconfigure(self, 'all', weight=1)
        tk.Grid.rowconfigure(self, 'all', weight=1)
        tk.Grid.columnconfigure(content_frame, 'all', weight=1)
        tk.Grid.rowconfigure(content_frame, 'all', weight=1)

        #  Dictionary for all the variables, this will be used by the controller
        self.inputs = {}
        self.labels = ['Exposure Time (ms)', 'Readout Time (ms)', 'Max Framerate (Hz)', 'Images to Average']
        self.names = ['exposure_time', 'readout_time', 'max_framerate', 'frames_to_average']
        self.read_only = [True, True, True, False]

        #  Dropdown loop
        for i in range(len(self.labels)):
            if self.read_only[i]:
                self.inputs[self.names[i]] = LabelInput(parent=content_frame,
                                                        label=self.labels[i],
                                                        input_class=ValidatedEntry,
                                                        input_var=tk.DoubleVar(),
                                                        input_args={'width': 6}                                          
                                                        )
                self.inputs[self.names[i]].widget['state'] = 'readonly'
                self.inputs[self.names[i]].grid(row=i, column=0, pady=1)
            else:
                self.inputs[self.names[i]] = LabelInput(parent=content_frame,
                                                        label=self.labels[i],
                                                        input_class=ValidatedSpinbox,
                                                        input_var=tk.DoubleVar(),
                                                        input_args={"from_": 1, "to": 1000, "increment": 1.0, 'width': 6}                                          
                                                        )
                self.inputs[self.names[i]].grid(row=i, column=0, pady=1)
            
        self.inputs['exposure_time'].label.grid(padx=(0,10))
        self.inputs['readout_time'].label.grid(padx=(0,14))
        self.inputs['max_framerate'].label.grid(padx=(0,10))
        self.inputs['frames_to_average'].label.grid(padx=(0,16))

    def get_variables(self):
        """
        # This function returns a dictionary of all the variables that are tied to each widget name.
        The key is the widget name, value is the variable associated.
        """
        variables = {}
        for key, widget in self.inputs.items():
            variables[key] = widget.get()
        return variables
    
    def get_widgets(self):
        """
        # This function returns the dictionary that holds the widgets.
        The key is the widget name, value is the LabelInput class that has all the data.
        """
        return self.inputs