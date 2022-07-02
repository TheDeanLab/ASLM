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
from tkinter import *
from tkinter import ttk
import logging
from pathlib import Path
# Logger Setup
p = __name__.split(".")[0]
logger = logging.getLogger(p)
from tkinter.font import Font
import numpy as np


class stack_acq_frame(ttk.Labelframe):
    def __init__(stack_acq, settings_tab, *args, **kwargs):
        # Init Frame
        text_label = 'Stack Acquisition Settings (' + "\N{GREEK SMALL LETTER MU}" + 'm)'
        ttk.Labelframe.__init__(stack_acq, settings_tab, text=text_label, *args, **kwargs)
        
        # Formatting
        Grid.columnconfigure(stack_acq, 'all', weight=1)
        Grid.rowconfigure(stack_acq, 'all', weight=1)

        # Step Size Frame (Vertically oriented)
        stack_acq.step_size_frame = ttk.Frame(stack_acq)
        stack_acq.step_size_label = ttk.Label(stack_acq.step_size_frame, text='Step Size')
        stack_acq.step_size_label.grid(row=0, column=0, sticky=(S), padx=(4,3), pady=(4,1))
        stack_acq.step_size_spinval = DoubleVar()
        stack_acq.step_size_spinbox = ttk.Spinbox(
            stack_acq.step_size_frame,
            from_=0,
            to=500.0,
            textvariable=stack_acq.step_size_spinval,
            increment=0.5,
            width=14
        )
        stack_acq.step_size_spinbox.state(["disabled"])
        stack_acq.step_size_spinbox.grid(row=1, column=0, sticky=(N), padx=(4,3), pady=(3,6))

    # Start Pos Frame (Vertically oriented)
        stack_acq.start_pos_frame = ttk.Frame(stack_acq)
        stack_acq.start_pos_label = ttk.Label(stack_acq.start_pos_frame, text='Start Pos')
        stack_acq.start_pos_label.grid(row=0, column=0, sticky=(S), padx=3, pady=(4,1))
        stack_acq.start_pos_spinval = DoubleVar()
        stack_acq.start_pos_spinbox = ttk.Spinbox(
            stack_acq.start_pos_frame,
            from_=0,
            to=500.0,
            textvariable=stack_acq.start_pos_spinval,
            increment=0.5,
            width=14
        )
        stack_acq.start_pos_spinbox.state(["disabled"])
        stack_acq.start_pos_spinbox.grid(row=1, column=0, sticky=(N), padx=3, pady=(3,6))


    # End Pos Frame (Vertically oriented)
        stack_acq.end_pos_frame = ttk.Frame(stack_acq)
        stack_acq.end_pos_label = ttk.Label(stack_acq.end_pos_frame, text='End Pos')
        stack_acq.end_pos_label.grid(row=0, column=0, sticky=(S), padx=3, pady=(4,1))
        stack_acq.end_pos_spinval = DoubleVar()
        stack_acq.end_pos_spinbox = ttk.Spinbox(
            stack_acq.end_pos_frame,
            from_=0,
            to=500.0,
            textvariable=stack_acq.end_pos_spinval,
            increment=0.5,
            width=14
        )
        stack_acq.end_pos_spinbox.state(['disabled'])
        stack_acq.end_pos_spinbox.grid(row=1, column=0, sticky=(N), padx=3, pady=(3,6))

    # Slice Frame (Vertically oriented)
        stack_acq.slice_frame = ttk.Frame(stack_acq)
        stack_acq.slice_label = ttk.Label(stack_acq.slice_frame, text='Slice')
        stack_acq.slice_label.grid(row=0, column=0, sticky=(S), padx=3, pady=(4,1))
        stack_acq.slice_spinval = DoubleVar()
        stack_acq.slice_spinbox = ttk.Spinbox(
            stack_acq.slice_frame,
            from_=0,
            to=500.0,
            textvariable=stack_acq.slice_spinval,
            increment=0.5,
            width=14
        )
        stack_acq.slice_spinbox.state(['disabled'])
        stack_acq.slice_spinbox.grid(row=1, column=0, sticky=(N), padx=3, pady=(3,6))

        # Gridding Each Holder Frame
        stack_acq.step_size_frame.grid(row=0, column=0, sticky=(NSEW))
        stack_acq.start_pos_frame.grid(row=0, column=1, sticky=(NSEW))
        stack_acq.end_pos_frame.grid(row=0, column=2, sticky=(NSEW))
        stack_acq.slice_frame.grid(row=0, column=3, sticky=(NSEW))


