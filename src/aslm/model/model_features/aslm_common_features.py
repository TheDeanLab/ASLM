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
import numpy as np
from scipy.stats import linregress

from aslm.tools.beams import centroid_image_intensity_by_max, support_psf_width

class ChangeResolution:
    def __init__(self, model, resolution_mode='high'):
        self.model = model

        self.config_table={'signal': {'main': self.signal_func},
                           'node': {'device_related': True}}

        self.resolution_mode = resolution_mode

        
    def signal_func(self):
        self.model.logger.debug('prepare to change resolution')
        self.model.pause_data_ready_lock.acquire()
        self.model.ask_to_pause_data_thread = True
        self.model.logger.debug('wait to change resolution')
        self.model.pause_data_ready_lock.acquire()
        self.model.change_resolution(self.resolution_mode)
        self.model.logger.debug('changed resolution')
        self.model.ask_to_pause_data_thread = False
        self.model.prepare_acquisition(False)
        self.model.pause_data_event.set()
        self.model.logger.debug('wake up data thread ')
        self.model.pause_data_ready_lock.release()
        return True

    def generate_meta_data(self, *args):
        # print('This frame: change resolution', self.resolution_mode, self.model.frame_id)
        return True


class Snap:
    def __init__(self, model):
        self.model = model

        self.config_table = {'data': {'main': self.data_func}}

    def data_func(self, frame_ids):
        print('the camera is:', self.model.camera.serial_number, frame_ids, self.model.frame_id)
        return True

    def generate_meta_data(self, *args):
        # print('This frame: snap one frame', self.model.frame_id)
        return True

class WaitToContinue:
    def __init__(self, model):
        self.model = model
        self.can_continue = False
        self.target_frame_id = -1

        self.config_table = {'signal': {'main': self.signal_func},
                             'data':   {'pre-main': self.data_func}}

    def signal_func(self):
        self.can_continue = True
        self.target_frame_id = self.model.frame_id
        print('--wait to continue:', self.target_frame_id)
        return True

    def data_func(self, frame_ids):
        print('??continue??', self.target_frame_id, frame_ids)
        return self.can_continue and (self.target_frame_id in frame_ids)


class ZStackAcquisition:
    def __init__(self, model):
        self.model = model

        self.number_z_steps = 0
        self.start_z_position = 0
        self.start_focus = 0
        self.z_step_size = 0
        self.focus_step_size = 0
        self.timepoints = 0

        self.positions = {}
        self.current_position_idx = 0
        self.current_z_position = 0
        self.current_focus_position = 0
        self.need_to_move_new_position = True
        self.need_to_move_z_position = True
        self.z_position_moved_time = 0

        self.stack_cycling_mode = 'per_stack'
        self.channels = [1]

        self.config_table = {'signal': {'init': self.pre_signal_func,
                                        'main': self.signal_func,
                                        'end': self.signal_end},
                             'node': {'node_type': 'multi-step',
                                      'device_related': True}}

    def pre_signal_func(self):
        microscope_state = self.model.experiment.MicroscopeState

        self.stack_cycling_mode = microscope_state['stack_cycling_mode']
        # get available channels
        prefix_len = len('channel_')
        self.channels = [int(channel_key[prefix_len:]) for channel_key in microscope_state['channels']]
        self.current_channel_in_list = 0

        self.number_z_steps = int(microscope_state['number_z_steps'])

        self.start_z_position = float(microscope_state['start_position'])
        end_z_position = float(microscope_state['end_position'])
        self.z_step_size = float(microscope_state['step_size'])
        
        self.start_focus = float(microscope_state['start_focus'])
        end_focus = float(microscope_state['end_focus'])
        self.focus_step_size = (end_focus - self.start_focus) / self.number_z_steps
        
        self.timepoints = int(microscope_state['timepoints'])

        if bool(microscope_state['is_multiposition']):
            self.positions = microscope_state['stage_positions']
        else:
            self.positions = dict({
                    0 : {
                        'x': float(self.model.experiment.StageParameters['x']),
                        'y': float(self.model.experiment.StageParameters['y']),
                        'z': float(microscope_state.get('stack_z_origin', self.model.experiment.StageParameters['z'])),
                        'theta': float(self.model.experiment.StageParameters['theta']),
                        'f': float(microscope_state.get('stack_focus_origin', self.model.experiment.StageParameters['f']))
                    }
                })
        self.current_position_idx = 0
        self.z_position_moved_time = 0
        self.need_to_move_new_position = True
        self.need_to_move_z_position = True
        self.current_z_position = self.start_z_position + self.positions[self.current_position_idx]['z']
        self.current_focus_position = self.start_focus + self.positions[self.current_position_idx]['f']

        self.restore_z = -1

        if not bool(microscope_state['is_multiposition']):
            # TODO: Make relative to stage coordinates.
            self.model.get_stage_position()
            self.restore_z = self.model.stages.z_pos
    
    def signal_func(self):
        if self.model.stop_acquisition:
            return False
        # move stage X, Y, Theta
        if self.need_to_move_new_position:
            self.need_to_move_new_position = False

            self.model.pause_data_ready_lock.acquire()
            self.model.ask_to_pause_data_thread = True
            self.model.pause_data_ready_lock.acquire()

            pos_dict = dict(map(lambda ax: (f'{ax}_abs', self.positions[self.current_position_idx][ax]), ['x', 'y', 'theta']))
            self.model.move_stage(pos_dict, wait_until_done=True)

            self.model.ask_to_pause_data_thread = False
            self.model.pause_data_event.set()
            self.model.pause_data_ready_lock.release()
            
            # self.z_position_moved_time = 0
            # # calculate first z, f position
            # self.current_z_position = self.start_z_position + self.positions[self.current_position_idx]['z']
            # self.current_focus_position = self.start_focus + self.positions[self.current_position_idx]['f']

        if self.need_to_move_z_position:
            # move z, f
            self.model.pause_data_ready_lock.acquire()
            self.model.ask_to_pause_data_thread = True
            self.model.pause_data_ready_lock.acquire()

            self.model.move_stage({'z_abs': self.current_z_position, 'f_abs': self.current_focus_position}, wait_until_done=True)

            self.model.ask_to_pause_data_thread = False
            self.model.pause_data_event.set()
            self.model.pause_data_ready_lock.release()

        if self.stack_cycling_mode != 'per_stack':
            # update channel for each z position in 'per_slice'
            self.update_channel()
            self.need_to_move_z_position = (self.current_channel_in_list == 0)

        # in 'per_slice', move to next z position if all the channels have been acquired
        if self.need_to_move_z_position:
            # next z, f position
            self.current_z_position += self.z_step_size
            self.current_focus_position += self.focus_step_size

            # update z position moved time
            self.z_position_moved_time += 1

        return True

    def signal_end(self):
        # end this node
        if self.model.stop_acquisition:
            return True
        
        # decide whether to move X,Y,Theta
        if self.z_position_moved_time >= self.number_z_steps:
            self.z_position_moved_time = 0
            # calculate first z, f position
            self.current_z_position = self.start_z_position + self.positions[self.current_position_idx]['z']
            self.current_focus_position = self.start_focus + self.positions[self.current_position_idx]['f']

            # after running through a z-stack, update channel
            if self.stack_cycling_mode == 'per_stack':
                self.update_channel()
                # if run through all the channels, move to next position
                if self.current_channel_in_list == 0:
                    self.need_to_move_new_position = True
            else:
                self.need_to_move_new_position = True

            if self.need_to_move_new_position:
                # move to next position
                self.current_position_idx += 1
            
            if self.need_to_move_new_position and self.current_position_idx == len(self.positions):
                self.timepoints -= 1
                self.current_position_idx = 0

        if self.timepoints == 0:
            # restore z if need
            if self.restore_z >= 0:
                self.model.move_stage({'z_abs': self.restore_z}, wait_until_done=True)  # Update position
            return True
        return False

    def generate_meta_data(self, *args):
        # print('This frame: z stack', self.model.frame_id)
        return True

    def update_channel(self):
        self.current_channel_in_list = (self.current_channel_in_list+1) % len(self.channels)
        self.model.target_channel = self.channels[self.current_channel_in_list]


class FindTissueSimple2D:
    def __init__(self, model, overlap=0.1, target_resolution='high'):
        """
        Detect tissue and grid out the space to image.
        """
        self.model = model

        self.config_table = {'signal': {},
                             'data': {'main': self.data_func}}

        self.overlap = overlap
        self.target_resolution = target_resolution

    def data_func(self, frame_ids):
        from skimage import filters
        from skimage.transform import downscale_local_mean
        import numpy as np
        from aslm.tools.multipos_table_tools import compute_tiles_from_bounding_box, calc_num_tiles
        import tifffile

        for idx in frame_ids:
            img = self.model.data_buffer[idx]

            # Get current mag
            if self.model.experiment.MicroscopeState['resolution_mode'] == 'high':
                curr_pixel_size = self.model.configuration.ZoomParameters['high_res_zoom_pixel_size']
                curr_mag = 300/(12.19/1.56)  # TODO: Don't hardcode
            else:
                zoom = self.model.experiment.MicroscopeState['zoom']
                curr_pixel_size = self.model.configuration.ZoomParameters['low_res_zoom_pixel_size'][zoom]
                curr_mag = float(zoom[:-1])

            # get target mag
            if self.target_resolution == 'high':
                pixel_size = self.model.configuration.ZoomParameters['high_res_zoom_pixel_size']
                mag = 300/(12.19/1.56)  # TODO: Don't hardcode
            else:
                pixel_size = self.model.configuration.ZoomParameters['low_res_zoom_pixel_size'][self.target_resolution]
                mag = float(self.target_resolution)

            # Downsample according to the desired magnification change. Note, we could downsample by whatever we want.
            ds = int(mag/curr_mag)
            ds_img = downscale_local_mean(img, (ds, ds))

            # Threshold
            thresh_img = ds_img > filters.threshold_otsu(img)

            tifffile.imwrite("C:\\Users\\MicroscopyInnovation\\Desktop\\Data\\Zach\\thresh.tiff", thresh_img)

            # Find the bounding box
            # In the real-deal, non-transposed image, x increase corresponds to a decrease in row number
            # y increase responds to an increase in row number
            # This means the smallest x coordinate is actually the largest
            x, y = np.where(thresh_img)
            # + 0.5 accounts for center of FOV
            x_start, x_end = -curr_pixel_size*ds*(np.max(x)+0.5), -curr_pixel_size*ds*(np.min(x)+0.5)
            y_start, y_end = curr_pixel_size*ds*(np.min(y)+0.5), curr_pixel_size*ds*(np.max(y)+0.5)
            xd, yd = abs(x_start - x_end), y_end - y_start

            # grab z, theta, f starting positions
            z_start = self.model.experiment.StageParameters['z']
            r_start = self.model.experiment.StageParameters['theta']
            if self.target_resolution == 'high':
                f_start = 0  # very different range of focus values in high-res
            else:
                f_start = self.model.experiment.StageParameters['f']

            # Update x and y start to initialize from the upper-left corner of the current image, since this is
            # how np.where indexed them. The + 0.5 in x_start/y_start calculation shifts their starts back to the
            # center of the field of view.
            curr_fov_x = float(self.model.experiment.CameraParameters['x_pixels']) * curr_pixel_size
            curr_fov_y = float(self.model.experiment.CameraParameters['y_pixels']) * curr_pixel_size
            x_start += self.model.experiment.StageParameters['x'] + curr_fov_x/2
            y_start += self.model.experiment.StageParameters['y'] - curr_fov_y/2

            if self.target_resolution == 'high':
                x_start += float(self.model.configuration.StageParameters['x_r_offset']) \
                           - float(self.model.configuration.StageParameters['x_l_offset'])
                y_start += float(self.model.configuration.StageParameters['y_r_offset']) \
                           - float(self.model.configuration.StageParameters['y_l_offset'])
                z_start += float(self.model.configuration.StageParameters['z_r_offset']) \
                           - float(self.model.configuration.StageParameters['z_l_offset'])
                r_start += float(self.model.configuration.StageParameters['theta_r_offset']) \
                           - float(self.model.configuration.StageParameters['theta_l_offset'])
            else:
                x_start += -float(self.model.configuration.StageParameters['x_r_offset']) \
                           + float(self.model.configuration.StageParameters['x_l_offset'])
                y_start += -float(self.model.configuration.StageParameters['y_r_offset']) \
                           + float(self.model.configuration.StageParameters['y_l_offset'])
                z_start += -float(self.model.configuration.StageParameters['z_r_offset']) \
                           + float(self.model.configuration.StageParameters['z_l_offset'])
                r_start += -float(self.model.configuration.StageParameters['theta_r_offset']) \
                           + float(self.model.configuration.StageParameters['theta_l_offset'])

            # grid out the 2D space
            fov_x = float(self.model.experiment.CameraParameters['x_pixels']) * pixel_size
            fov_y = float(self.model.experiment.CameraParameters['y_pixels']) * pixel_size
            x_tiles = calc_num_tiles(xd, self.overlap, fov_x)
            y_tiles = calc_num_tiles(yd, self.overlap, fov_y)

            table_values = compute_tiles_from_bounding_box(x_start, x_tiles, fov_x, self.overlap,
                                                           y_start, y_tiles, fov_y, self.overlap,
                                                           z_start, 1, 0, self.overlap,
                                                           r_start, 1, 0, self.overlap,
                                                           f_start, 1, 0, self.overlap)

            self.model.event_queue.put(('multiposition', table_values))


class AutoCenterBeam:
    def __init__(self, model) -> None:
        self.model = model

        self.config_table = {'signal': {'init': self.pre_func_signal,
                                        'main': self.in_func_signal,
                                        'end': self.end_func_signal},
                             'data': {'init': self.pre_func_data,
                                      'main': self.in_func_data,
                                      'end': self.end_func_data},
                             'node': {'node_type': 'multi-step',
                                      'device_related': True },
                            }

        self.total_frame_num = 20
        self.etl_step = 0.05
        self.galvo_step = 0.05
        self.switch_at = int(self.total_frame_num//2)
        self.signal_id = 0
        self.psf_support_size = 6
        self.row = None
        self.col = None
        self.etl_offsets = None
        self.galvo_offsets = None
        self.get_frames_num = 0
        self.target_channel = 1
    
    def pre_func_signal(self):
        self.image_width = self.model.experiment.CameraParameters['x_pixels']
        self.image_height = self.model.experiment.CameraParameters['y_pixels']
        self.resolution = self.model.experiment.MicroscopeState['resolution_mode']
        self.zoom = self.model.experiment.MicroscopeState['zoom']

        self.wvl_string = self.model.experiment.MicroscopeState['channels'][f"channel_{self.target_channel}"]['laser']
        wvl = int((self.wvl_string).split('nm')[0])/1000  # um

        self.etl_dict = self.model.etl_constants.ETLConstants[self.resolution][self.zoom].copy()
        self.etl_dict[self.wvl_string]['offset'] = str(float(self.etl_dict[self.wvl_string]['offset'])-0.25)
        self.etl_dict[self.wvl_string]['amplitude'] = 0
        self.galvo_dict = self.model.experiment.GalvoParameters.copy()

        self.side = "r" if self.resolution == "high" else "l"
        if self.side == "l":
            self.model.experiment.GalvoParameters[f'galvo_{self.side}_amplitude'] = 0
        self.galvo_dict[f'galvo_{self.side}_offset'] = str(float(self.galvo_dict[f'galvo_{self.side}_offset'])-0.25)
        print(f"Galvo offset initially at {self.galvo_dict[f'galvo_{self.side}_offset']}")
        print(f"ETL offset initially at {self.etl_dict[self.wvl_string]['offset']}")
        self.galvo_offsets = float(self.galvo_dict[f'galvo_{self.side}_offset']) + np.arange(self.switch_at) * self.galvo_step
        self.etl_offsets = float(self.etl_dict[self.wvl_string]['offset']) + np.arange(self.switch_at) * self.etl_step
        self.signal_id = 0

        if self.resolution == 'low':
            pixel_size = self.model.configuration.ZoomParameters['low_res_zoom_pixel_size'][self.zoom]
        else:
            pixel_size = self.model.configuration.ZoomParameters['high_res_zoom_pixel_size']
        # TODO: Don't hardcode numerical aperture
        self.psf_support_size = support_psf_width(wvl, 0.15, pixel_size)

    def in_func_signal(self):
        ## Move beam
        if self.signal_id < self.switch_at:
            etl_off = str(float(self.etl_dict[self.wvl_string]['offset']) + self.etl_step)
            galvo_off = str(self.galvo_offsets[self.switch_at//2])
        else:
            etl_off = str(self.etl_offsets[self.switch_at//2])
            galvo_off = str(float(self.model.experiment.GalvoParameters[f'galvo_{self.side}_offset']) + self.galvo_step)

        print(f"ETL offset: {etl_off} Galvo offset: {galvo_off}")
        self.etl_dict[self.wvl_string]['offset'] = etl_off
        self.model.etl_constants.ETLConstants[self.resolution][self.zoom] = self.etl_dict
        self.model.experiment.GalvoParameters[f'galvo_{self.side}_offset'] = galvo_off
        self.signal_id += 1

        return self.signal_id < self.total_frame_num

    def end_func_signal(self):
        return self.signal_id >= self.total_frame_num

    def pre_func_data(self):
        self.row = np.zeros((self.switch_at,))
        self.col = np.zeros((self.switch_at,))
        self.get_frames_num = 0

    def in_func_data(self, frame_ids=[]):
        for i in frame_ids:
            print(f"Considering frame id {i}")
            row, col = centroid_image_intensity_by_max(self.model.data_buffer[i], self.psf_support_size)
            if self.get_frames_num < self.switch_at:
                print(row, col, self.get_frames_num)
                self.row[self.get_frames_num] = row
            else:
                print(row, col, self.get_frames_num - self.switch_at)
                self.col[self.get_frames_num-self.switch_at] = col
            self.get_frames_num += 1

        if self.get_frames_num >= self.total_frame_num:
            return frame_ids

    def end_func_data(self):
        print(self.get_frames_num, self.total_frame_num)
        if self.get_frames_num < self.total_frame_num:
            return False

        # Updates
        print(self.row)
        print(self.etl_offsets)
        print(self.col)
        print(self.galvo_offsets)

        res_row = linregress(self.row, self.etl_offsets)
        res_col = linregress(self.col, self.galvo_offsets)

        etl_off = res_row.intercept + res_row.slope*(self.image_width//2)
        galvo_off = res_col.intercept + res_col.slope*(self.image_height//2)

        print(f"******* Setting ETL to {etl_off}, Galvo to {galvo_off}")

        self.etl_dict[self.wvl_string]['offset'] = str(etl_off)
        self.model.etl_constants.ETLConstants[self.resolution][self.zoom] = self.etl_dict
        self.model.experiment.GalvoParameters[f'galvo_{self.side}_offset'] = str(galvo_off)

        return True
