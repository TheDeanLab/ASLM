# Copyright (c) 2021-2022  The University of Texas Southwestern Medical Center.
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

# Standard Library Imports
import tkinter as tk
from tkinter import ttk

# Third Party Imports

# Local Imports
from aslm.view.custom_widgets.hover import Hover


class HoverMixin:
    """Adds hover attribute to widget

    This class is meant to be mixed in with other widgets to add a hover attribute

    Methods
    -------
    None

    Attributes
    ----------
    hover : Hover
        Hover object that is added to the widget
    """

    def __init__(self, *args, **kwargs):
        super().__init__(
            *args, **kwargs
        )  # Calls base class that is mixed in with this class

        # Adds hover attribute
        self.hover = Hover(self, text=None, type="free")


class HoverButton(HoverMixin, ttk.Button):
    """Adds hover attribute to ttk.Button

    This class is meant to be mixed in with other widgets to add a hover attribute

    Methods
    -------
    None

    Attributes
    ----------
    hover : Hover
        Hover object that is added to the widget
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HoverTkButton(HoverMixin, tk.Button):
    """Adds hover attribute to tk.Button

    This class is meant to be mixed in with other widgets to add a hover attribute

    Methods
    -------
    None

    Attributes
    ----------
    hover : Hover
        Hover object that is added to the widget
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HoverRadioButton(HoverMixin, ttk.Radiobutton):
    """Adds hover attribute to ttk.Radiobutton

    This class is meant to be mixed in with other widgets to add a hover attribute

    Methods
    -------
    None

    Attributes
    ----------
    hover : Hover
        Hover object that is added to the widget
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HoverCheckButton(HoverMixin, ttk.Checkbutton):
    """Adds hover attribute to ttk.Checkbutton

    This class is meant to be mixed in with other widgets to add a hover attribute

    Methods
    -------
    None

    Attributes
    ----------
    hover : Hover
        Hover object that is added to the widget
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)