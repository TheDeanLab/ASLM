import tkinter as tk
from tkinter import *
from tkinter import ttk
from tkinter.font import Font

from view.custom_widgets.LabelInputWidgetFactory import LabelInput

class framerate_info(ttk.LabelFrame):
    '''
    # This class generates the framerate label frame. 
    Widgets can be adjusted below. Entry values need to be set in the controller.
    The widgets can be found in the dictionary by using the first word in the label, after using get_widgets
    The variables tied to each widget can be accessed via the widget directly or with the dictionary generated by get_variables.
    '''
    def __init__(self, settings_tab, *args, **kwargs):

        #Init Frame
        text_label = 'Framerate Info'
        ttk.LabelFrame.__init__(self, settings_tab, text=text_label, *args, **kwargs)

        #Holds widgests, this is done in case more widgets are to be added in a different frame, these can be grouped together
        content_frame = ttk.Frame(self)
        content_frame.grid(row=0, column=0, sticky=(NSEW))

        #Dictionary for all the variables, this will be used by the controller
        self.inputs = {}
        self.labels = ['Temp1 ms', 'Temp2 ms', 'Temp3 Hz', 'Exposure(s):', '# of Integrations']
        self.names = ['Temp1', 'Temp2', 'Temp3', 'Exposure', 'Integration']

        #Dropdown loop
        for i in range(5):
            if i < 4:
                self.inputs[self.names[i]] = LabelInput(parent=content_frame,
                                                        label=self.labels[i],
                                                        input_class=ttk.Entry,
                                                        input_var=tk.StringVar()                                          
                                                        )
                self.inputs[self.names[i]].grid(row=i, column=0, pady=1)
            else:
                self.inputs[self.names[i]] = LabelInput(parent=content_frame,
                                                        label=self.labels[i],
                                                        input_class=ttk.Spinbox,
                                                        input_var=tk.IntVar(),
                                                        input_args={"from_": 1, "to": 1000, "increment": 1.0}                                          
                                                        )
                self.inputs[self.names[i]].grid(row=i, column=0, pady=1)

    def get_variables(self):
        '''
        # This function returns a dictionary of all the variables that are tied to each widget name.
        The key is the widget name, value is the variable associated.
        '''
        variables = {}
        for key, widget in self.inputs.items():
            variables[key] = widget.get()
        return variables
    
    def get_widgets(self):
        '''
        # This function returns the dictionary that holds the widgets.
        The key is the widget name, value is the LabelInput class that has all the data.
        '''
        return self.inputs