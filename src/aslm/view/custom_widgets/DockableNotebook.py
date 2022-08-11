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
import tkinter as tk
from tkinter import ttk
import logging


# Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)


class DockableNotebook(ttk.Notebook):
    def __init__(self, parent, root, *args, **kwargs):
        ttk.Notebook.__init__(self, parent, *args, **kwargs)

        self.root = root
        self.tab_list = []
        self.cur_tab = None

        # Formatting
        tk.Grid.columnconfigure(self, 'all', weight=1)
        tk.Grid.rowconfigure(self, 'all', weight=1)

         # Popup setup
        self.menu = tk.Menu(self, tearoff=0)
        self.menu.add_command(label="Popout Tab", command=self.popout)

        # Bindings
        self.bind("<ButtonPress-2>", self.find)
        self.bind("<ButtonPress-3>", self.find)

    def set_tablist(self, tab_list):
        self.tab_list = tab_list

    def get_absolute_position(self):
        x = self.root.winfo_pointerx()
        y = self.root.winfo_pointery()
        return x, y

    def find(self, event):
        element = event.widget.identify(event.x, event.y)
        if "label" in element:
            try:
                x, y = self.get_absolute_position()
                self.menu.tk_popup(x, y)
            finally:
                self.menu.grab_release()

    def popout(self):
        # Get ref to correct tab to popout
        tab = self.select()
        tab_text = self.tab(tab)['text']
        for tab_name in self.tab_list:
            if tab_text == self.tab(tab_name)['text']:
                tab = tab_name
                self.tab_list.remove(tab_name)
        self.hide(tab)
        self.root.wm_manage(tab)

        # self.root.wm_title(tab, tab_text)
        tk.Wm.title(tab, tab_text)
        tk.Wm.protocol(tab, "WM_DELETE_WINDOW", lambda: self.dismiss(tab, tab_text))

    def dismiss(self, tab, tab_text):
        self.root.wm_forget(tab)
        tab.grid(row=0, column=0)
        self.add(tab)
        self.tab(tab, text=tab_text)
        self.tab_list.append(tab)