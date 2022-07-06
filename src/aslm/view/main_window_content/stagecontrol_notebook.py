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
# Standard Imports
from tkinter import *
from tkinter import ttk
import logging
from pathlib import Path
# Logger Setup
p = __name__.split(".")[0]
logger = logging.getLogger(p)
from tkinter.font import Font

# Local Imports
from view.main_window_content.stage_control.stage_control_tab import stage_control_tab
from view.main_window_content.stage_control.minimized_control import minimized_control
from view.main_window_content.tabs.stage_control.maximum_intensity_projection_tab import maximum_intensity_projection_tab

class stagecontrol_maxintensity_notebook(ttk.Notebook):
    def __init__(self, frame_bot_right, parent, *args, **kwargs):
        #Init notebook
        ttk.Notebook.__init__(self, frame_bot_right, *args, **kwargs)
        
        self.parent = parent
        
        # Formatting
        Grid.columnconfigure(self, 'all', weight=1)
        Grid.rowconfigure(self, 'all', weight=1)

        #Putting notebook 3 into bottom right frame
        self.grid(row=0, column=0)

        #Creating Stage Control Tab
        self.stage_control_tab = stage_control_tab(self)
        
        #Creating Minimized Stage Control Tab
        self.minimized_control = minimized_control(self)

        #Creating Max intensity projection Tab
        self.maximum_intensity_projection_tab = maximum_intensity_projection_tab(self)
        
        #Adding tabs to self notebook
        self.add(self.stage_control_tab, text='Stage Control', sticky=NSEW)
        self.add(self.minimized_control, text='Stage Control', sticky=NSEW)
        #self.hide(minimized_control)
        self.add(self.maximum_intensity_projection_tab, text='MIPs', sticky=NSEW)
        
        #Create State Tracker for minimization
        self.minimized = False
        
    def swap_view(self):
        if self.minimized==True:
            #self.hide()
            print()
        


class goto_frame(ttk.Frame):
    def __init__(goto_frame, stage_control_tab, *args, **kwargs):
        #Init Frame
        ttk.Frame.__init__(goto_frame, stage_control_tab, *args, **kwargs) 

'''
End of Stage Control Tab Frame Classes
'''