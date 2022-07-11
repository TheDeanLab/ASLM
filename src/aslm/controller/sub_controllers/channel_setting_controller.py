"""
ASLM sub-controller for the channel settings.

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
from aslm.controller.sub_controllers.widget_functions import validate_wrapper
from aslm.controller.sub_controllers.gui_controller import GUI_Controller
import logging

# Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)

"""
TODO Create a dictionary for widgets that holds a list of widgets for each column.Will attempt after formatting.
"""


class Channel_Setting_Controller(GUI_Controller):
    def __init__(self, view, parent_controller=None, verbose=False):
        super().__init__(view, parent_controller, verbose)

        # num: numbers of channels
        # TODO: Put in configuration file?
        self.num = 5
        # 'live': acquire mode is set to 'continuous'
        self.mode = 'stop'
        self.channel_controllers = []
        self.in_initialization = True
        self.event_id = None

        # add validation functions to spinbox
        for i in range(self.num):
            validate_wrapper(self.view.exptime_pulldowns[i])
            validate_wrapper(self.view.interval_spins[i])
            validate_wrapper(self.view.laserpower_pulldowns[i])

        # widget command binds
        for i in range(self.num):
            channel_vals = self.get_vals_by_channel(i)
            for name in channel_vals:
                channel_vals[name].trace_add('write', self.channel_callback(i, name))

    def set_num(self, num):
        self.num = num

    def set_mode(self, mode='stop'):
        self.mode = mode
        state = 'normal' if mode == 'stop' else 'disabled'
        state_readonly = 'readonly' if mode == 'stop' else 'disabled'
        for i in range(5):
            self.view.channel_checks[i].config(state=state)
            self.view.interval_spins[i].config(state=state)
            self.view.laser_pulldowns[i]['state'] = state_readonly
            if self.mode != 'live' or (self.mode == 'live' and not self.view.channel_variables[i].get()):
                self.view.exptime_pulldowns[i].config(state=state)
            if not self.view.channel_variables[i].get():
                self.view.laserpower_pulldowns[i].config(state=state)
                self.view.filterwheel_pulldowns[i]['state'] = state_readonly
                self.view.filterwheel_pulldowns[i]['state'] = state
                self.view.defocus_spins[i].config(state=state)

    def initialize(self, config):
        r"""Populates the laser and filter wheel options in the View.

        Parameters
        ----------
        config : object
            ASLM_Configuration_Controller - config.configuration is session instance of configuration.
        """
        setting_dict = config.get_channels_info()
        for i in range(self.num):
            self.view.laser_pulldowns[i]['values'] = setting_dict['laser']
            self.view.filterwheel_pulldowns[i]['values'] = setting_dict['filter']
        self.show_verbose_info('channel has been initialized')

    def set_experiment_values(self, setting_dict):
        """
        # set channel values according to channel id
        # the value should be a dict {
        # 'channel_id': {
            'is_selected': True(False),
            'laser': ,
            'filter': ,
            'camera_exposure_time': ,
            'laser_power': ,
            'interval_time':}
        }
        """
        prefix = 'channel_'
        for channel in setting_dict:
            channel_id = int(channel[len(prefix):]) - 1
            channel_vals = self.get_vals_by_channel(channel_id)
            if not channel_vals:
                return
            channel_value = setting_dict[channel]
            for name in channel_vals:
                channel_vals[name].set(channel_value[name])
            # validate exposure_time, interval, laser_power
            self.view.exptime_pulldowns[channel_id].validate()
            self.view.interval_spins[channel_id].validate()
            self.view.laserpower_pulldowns[channel_id].validate()

        self.show_verbose_info('channel has been set new value')

    def get_values(self):
        """
        # return all the selected channels' setting values
        # for example, if channel_1 and channel_2 is selected, it will return
        # { 'channel_1': {
        #           'is_selected': True,
        #           'laser': ,
        #           'laser_index': ,
        #           'filter': ,
        #           'filter_position': ,
        #           'camera_exposure_time': ,
        #           'laser_power': ,
        #           'interval_time': 
        #        },
        # 'channel_2': {
        #           'is_selected': True,
        #           'laser': ,
        #           'laser_index': ,
        #           'filter': ,
        #           'filter_position': ,
        #           'camera_exposure_time': ,
        #           'laser_power': ,
        #           'interval_time': ,
        #           'defocus': ,
        #        }
        # }
        """
        prefix = 'channel_'
        channel_settings = {}
        for i in range(self.num):
            channel_vals = self.get_vals_by_channel(i)
            # if this channel is selected, then get all the settings of it
            if channel_vals['is_selected'].get():
                try:
                    temp = {
                        'is_selected': True,
                        'laser': channel_vals['laser'].get(),
                        'laser_index': self.get_index('laser', channel_vals['laser'].get()),
                        'filter': channel_vals['filter'].get(),
                        'filter_position': self.get_index('filter', channel_vals['filter'].get()),
                        'camera_exposure_time': float(channel_vals['camera_exposure_time'].get()),
                        'laser_power': channel_vals['laser_power'].get(),
                        'interval_time': channel_vals['interval_time'].get(),
                        'defocus': channel_vals['defocus'].get()
                    }
                except:
                    return None
                channel_settings[prefix+str(i+1)] = temp
        return channel_settings

    def set_spinbox_range_limits(self, settings):
        """
        # this function will set the spinbox widget's values of from_, to, step
        """
        temp_dict = {
            'laser_power': self.view.laserpower_pulldowns,
            'camera_exposure_time': self.view.exptime_pulldowns,
            'interval_time': self.view.interval_spins
        }
        for k in temp_dict:
            widgets = temp_dict[k]
            for i in range(self.num):
                widgets[i].configure(from_=settings[k]['min'])
                widgets[i].configure(to=settings[k]['max'])
                widgets[i].configure(increment=settings[k]['step'])

    def channel_callback(self, channel_id, widget_name):
        """
        # in 'live' mode (when acquire mode is set to 'continuous') and a channel is selected,
        # any change of the channel setting will influence devices instantly
        # this function will call the central controller to response user's request
        """
        channel_vals = self.get_vals_by_channel(channel_id)

        def func(*args):
            if self.in_initialization:
                return
            if widget_name != 'is_selected' and channel_vals['is_selected'].get() is False:
                return
            if widget_name == 'camera_exposure_time':
                self.parent_controller.execute('recalculate_timepoint')
            if self.mode == 'live':
                # validate values: all the selected channel should not be empty if 'is_selcted'
                if channel_vals['is_selected'].get():
                    try:
                        assert(channel_vals['laser'].get() and channel_vals['filter'].get())
                        float(channel_vals['laser_power'].get())
                        float(channel_vals['camera_exposure_time'].get())
                        float(channel_vals['interval_time'].get())
                    except:
                        if self.event_id:
                            self.view.after_cancel(self.event_id)
                        return
                # call central controller
                if self.event_id:
                    self.view.after_cancel(self.event_id)
                self.event_id = self.view.after(500, lambda: self.parent_controller.execute('update_setting', 'channel', self.get_values()))

            self.show_verbose_info('channel setting has been changed')
        return func

    def get_vals_by_channel(self, index):
        """
        # this function return all the variables according channel_id
        """
        if index < 0 or index >= self.num:
            return {}
        result = {
            'is_selected': self.view.channel_variables[index],
            'laser': self.view.laser_variables[index],
            'filter': self.view.filterwheel_variables[index],
            'camera_exposure_time': self.view.exptime_variables[index],
            'laser_power': self.view.laserpower_variables[index],
            'interval_time': self.view.interval_variables[index],
            'defocus': self.view.defocus_variables[index]
        }
        return result

    def get_index(self, dropdown_name, value):
        if not value:
            return -1
        if dropdown_name == 'laser':
            return self.view.laser_pulldowns[0]['values'].index(value)
        elif dropdown_name == 'filter':
            return self.view.filterwheel_pulldowns[0]['values'].index(value)
        return -1
