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
# Standard Imports
import tkinter as tk
from tkinter import ttk
import logging

# Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)

from aslm.view.custom_widgets.DockableNotebook import DockableNotebook

# Import Sub-Frames
from aslm.view.main_window_content.camera_display.camera_settings.camera_settings_tab import camera_settings_tab
from aslm.view.main_window_content.channel_settings.channels_tab import channels_tab
from aslm.view.main_window_content.stage_control.stage_control_tab import stage_control_tab
from aslm.view.main_window_content.multiposition.multiposition_tab import multiposition_tab


class settings_notebook(DockableNotebook):
    def __init__(self, frame_left, root, *args, **kwargs):
        
        #Init notebook
        DockableNotebook.__init__(self, frame_left, root, *args, **kwargs)

        #Putting notebook 1 into left frame
        self.grid(row=0,column=0)

        #Creating the Channels tab
        self.channels_tab = channels_tab(self)

        #Creating the Camera tab
        self.camera_settings_tab = camera_settings_tab(self)

        #Creating Stage Control Tab
        self.stage_control_tab = stage_control_tab(self)

        #Creating Multiposition Table Tab
        self.multiposition_tab = multiposition_tab(self)

        # Tab list
        tab_list = [self.channels_tab, self.camera_settings_tab, self.stage_control_tab, self.multiposition_tab]
        self.set_tablist(tab_list)


        #Adding tabs to settings notebook
        self.add(self.channels_tab, text='Channels', sticky=tk.NSEW)
        self.add(self.camera_settings_tab, text='Camera Settings', sticky=tk.NSEW)
        self.add(self.stage_control_tab, text='Stage Control', sticky=tk.NSEW)
        self.add(self.multiposition_tab, text='Multiposition', sticky=tk.NSEW)
