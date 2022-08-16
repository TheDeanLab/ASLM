#  Standard Imports

# Third Party Imports
import h5py
import numpy as np
import numpy.typing as npt

# Local imports
from .data_source import DataSource
from ..metadata_sources.bdv_metadata import BigDataViewerMetadata
from aslm.model.aslm_model_config import Configurator


class BigDataViewerDataSource(DataSource):
    def __init__(self, file_name: str = None, mode: str = 'w') -> None:
        self._resolutions = np.array([[1,1,1],[2,2,2],[4,4,4],[8,8,8]],dtype=int)
        self._subdivisions = None
        self.image = None
        self._views = []

        file_name = '.'.join(file_name.split('.')[:-1])+'.hdf'
        super().__init__(file_name, mode)

        self._current_frame = 0
        self.metadata = BigDataViewerMetadata()

        self._position = -1

    @property
    def resolutions(self) -> npt.ArrayLike:
        return self._resolutions

    @property
    def subdivisions(self) -> npt.ArrayLike:
        if self._subdivisions is None:
            self._subdivisions = np.tile([self.shape_x, self.shape_y, self.shape_z], 
                                        (self._resolutions.shape[0],1))
            self._subdivisions[:,0] = np.gcd(32, self.shapes[:,0])
            self._subdivisions[:,1] = np.gcd(32, self.shapes[:,1])
            self._subdivisions[:,2] = np.gcd(32, self.shapes[:,2])

            # Safety
            self._subdivisions = np.maximum(self._subdivisions, 1)
        return self._subdivisions

    @property
    def shapes(self) -> npt.ArrayLike:
        return np.maximum(np.array([self.shape_x, self.shape_y, self.shape_z])[None,:]//self.resolutions, 1)

    def set_metadata_from_configuration_experiment(self, configuration: Configurator, experiment: Configurator) -> None:
        self._subdivisions = None
        return super().set_metadata_from_configuration_experiment(configuration, experiment)

    def write(self, data: npt.ArrayLike, **kw) -> None:
        self.mode = 'w'

        c, z, t, p = self._cztp_indices(self._current_frame, self.metadata.per_stack)  # find current channel
        if (z==0) and (c==0) and (t==0) and (p==0):
            self._setup_h5()

        time_group_name = f"t{t:05}"
        setup_group_name = f"s{(c*self.positions+p):02}"
        for i in range(self.subdivisions.shape[0]):
            dx, dy, dz = self.resolutions[i,...]
            if z % dz == 0:
                dataset_name = '/'.join([time_group_name, setup_group_name, f"{i}", "cells"])
                # print(z, dz, dataset_name, self.image[dataset_name].shape, data[::dx, ::dy].shape)
                zs = np.minimum(z//dz, self.subdivisions[i,2]-1)  # TODO: Is this necessary?
                self.image[dataset_name][...,zs] = data[::dx, ::dy]
                if len(kw) > 0:
                    self._views.append(kw)
        self._current_frame += 1

        # Check if this was the last frame to write
        c, z, t, p = self._cztp_indices(self._current_frame, self.metadata.per_stack)
        if (z==0) and (c==0) and (t==self.shape_t) and (p==self.positions):
            self.close()

    def read(self) -> None:
        self.mode = 'r'
        self.image = h5py.File(self.file_name, 'r')

    def _setup_h5(self):
        # Create setups
        for i in range(self.shape_c*self.positions):
            setup_group_name = f"s{i:02}"
            if setup_group_name in self.image:
                del self.image[setup_group_name]
            self.image.create_dataset(f"{setup_group_name}/resolutions", data=self.resolutions)
            self.image.create_dataset(f"{setup_group_name}/subdivisions", data=self.subdivisions)

        # Create the datasets to populate
        for t in range(self.shape_t):
            time_group_name = f"t{t:05}"
            for i in range(self.shape_c*self.positions):
                setup_group_name = f"s{i:02}"
                for j in range(self.subdivisions.shape[0]):
                    dataset_name = '/'.join([time_group_name, setup_group_name, f"{j}", "cells"])
                    if dataset_name in self.image:
                        del self.image[dataset_name]
                    # print(f"Creating {dataset_name} with shape {shape}")
                    # TODO chunk on a different size scale than shape
                    self.image.create_dataset(dataset_name,
                                chunks=tuple(self.subdivisions[j,...]),
                                shape=self.shapes[j,...], dtype='uint16')

    def _mode_checks(self) -> None:
        self._write_mode = self._mode == 'w'
        self.close()  # if anything was already open, close it
        if self._write_mode:
            self._current_frame = 0
            self.image = h5py.File(self.file_name, 'a')
            self._setup_h5()
        else:
            self.read()

    def close(self) -> None:
        try:
            self.image.close()
            self.metadata.write_xml(self.file_name, views=self._views)
        except AttributeError:
            # image wasn't instantiated, no need to close anything
            pass
