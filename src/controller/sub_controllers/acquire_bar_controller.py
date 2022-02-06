"""
Sub-controller for the acquire popup window
When the mode is changed, we need to communicate this to the central controller.
Central controller then communicates these changes to the channel_setting_controller.
"""
import sys

from controller.sub_controllers.gui_controller import GUI_Controller
from view.main_window_content.acquire_bar_frame.acquire_popup import Acquire_PopUp as acquire_popup


class Acquire_Bar_Controller(GUI_Controller):
    def __init__(self, view, parent_controller, verbose=False):
        super().__init__(view, parent_controller, verbose)

        # acquisition image mode variable
        self.mode = 'continuous'
        self.is_save = False
        self.saving_settings = {
            'root_directory': 'E:\\',
            'save_directory': '',
            'user': '',
            'tissue': '',
            'celltype': '',
            'label': ''
        }

        self.mode_dict = {
            'Continuous Scan': 'continuous',
            'Z-Stack': 'z-stack',
            'Single Acquisition': 'single',
            'Projection': 'projection'
        }

        # gui event bind
        self.view.acquire_btn.config(command=self.launch_popup_window)

        self.view.pull_down.bind('<<ComboboxSelected>>', self.update_microscope_mode)

        self.view.exit_btn.config(command=self.exit_program)

    def set_mode(self, mode):
        """
        # set image mode
        # mode could be: 'continuous', 'z-stack', 'single', 'projection'
        """
        self.mode = mode
        # update pull down combobox
        reverse_dict = dict(map(lambda v: (v[1], v[0]), self.mode_dict.items()))
        self.view.pull_down.set(reverse_dict[mode])

        self.show_verbose_info('image mode is set to', mode)
    
    def get_mode(self):
        """
        # return right now image mode setting
        """
        return self.mode

    def set_save_option(self, is_save):
        """
        # set whether the image will be saved
        """
        self.is_save = is_save

        self.show_verbose_info('set save data option:', is_save)

    def set_saving_settings(self, saving_settings):
        """
        # set saving settings
        # right now it is a reference to the model.exprement.Saving
        """
        self.saving_settings = saving_settings

        self.show_verbose_info('set saving settings')
    
    def launch_popup_window(self):
        """
        # The popup window should only be launched if the microscope is set to save the data,
        # with the exception of the continuous acquisition mode.
        # The popup window provides the user with the opportunity to fill in fields that describe the experiment and
        # also dictate the save path of the data in a standardized format.
        """
        if self.is_save and self.mode != 'continuous':
            popup_window = acquire_popup(self.view)

            # Configure the button callbacks on the popup window
            popup_window.content.cancel_btn.config(command=lambda: popup_window.dismiss(self.verbose))
            popup_window.content.done_btn.config(command=lambda: self.launch_acquisition(popup_window))

            initialize_popup_window(popup_window, self.saving_settings)
        elif self.view.acquire_btn['text'] == 'Stop':
            # change the button to 'Acquire'
            self.view.acquire_btn.configure(text='Acquire')
            # tell the controller to stop acquire(continuous mode)
            self.parent_controller.execute('stop_acquire')
        else:
            # if the mode is 'continuous'
            if self.mode == 'continuous':
                self.view.acquire_btn.configure(text='Stop')
            self.parent_controller.execute('acquire')

    def update_microscope_mode(self, *args):
        """
        # Gets the state of the pull-down menu and tell the central controller

        """
        self.mode = self.mode_dict[self.view.pull_down.get()]
        self.parent_controller.execute('image_mode', self.mode)
        
        self.show_verbose_info("The Microscope State is now:", self.get_mode())

    def launch_acquisition(self, popup_window):
        """
        # Once the popup window has been filled out, we first create the save path using the create_save_path function.
        # This automatically removes spaces and replaces them with underscores.
        # Then it makes the directory.
        # Thereafter, the experiment is ready to go.
        """
        # update saving settings according to user's input
        self.update_saving_settings(popup_window)
        
        is_valid = True
        # Verify user's input is non-zero.
        if len(self.saving_settings['user']) == 0:
            is_valid = False
            raise ValueError('Please provide a User Name')

        if len(self.saving_settings['tissue']) == 0:
            is_valid = False
            raise ValueError('Please provide a Tissue Type')

        if len(self.saving_settings['celltype']) == 0:
            is_valid = False
            raise ValueError('Please provide a Cell Type')

        if len(self.saving_settings['label']) == 0:
            is_valid = False
            raise ValueError('Please provide a Label Type')

        # TODO: the popup GUI should have a label or something to show the error message
        # after GUI add such thing, then I will update here -- Annie

        if is_valid:
            # tell central controller, save the image/data
            self.parent_controller.execute('acquire_and_save', self.saving_settings)
            # Close the window
            popup_window.dismiss(self.verbose)

    def exit_program(self):
        self.show_verbose_info("Exiting Program")
        sys.exit()

    def update_saving_settings(self, popup_window):
        popup_values = get_popup_values(popup_window)
        for name in popup_values:
            self.saving_settings[name] = popup_values[name]


def get_popup_vals(popup_window):
    popup_vals = {
        'root_directory': popup_window.content.root_entry_string,
        'save_directory': None,
        'user': popup_window.content.user_string,
        'tissue': popup_window.content.tissue_string,
        'celltype': popup_window.content.celltype_string,
        'label': popup_window.content.label_string
    }
    return popup_vals


def get_popup_values(popup_window):
    popup_vals = get_popup_vals(popup_window)
    settings = {}
    for name in popup_vals:
        if popup_vals[name]:
            settings[name] = popup_vals[name].get()
    return settings


def initialize_popup_window(popup_window, values):
    """
    # this function will initialize popup window
    # values should be a dict {
    #    'root_directory':,
    #    'save_directory':,
    #    'user':,
    #    'tissue':,
    #    'celltype':,
    #    'label':
    # }
    """
    popup_vals = get_popup_vals(popup_window)

    for name in values:
        if popup_vals.get(name, None):
            popup_vals[name].set(values[name])
