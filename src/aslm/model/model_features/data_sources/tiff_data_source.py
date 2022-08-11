#  Standard Imports
import os
from pathlib import Path

# Third Party Imports
import tifffile
import numpy.typing as npt

# Local imports
from .data_source import DataSource
from ..metadata_sources.metadata import Metadata
from ..metadata_sources.ome_tiff_metadata import OMETIFFMetadata

class TiffDataSource(DataSource):
    def __init__(self, file_name: str = '', mode: str = 'w', is_bigtiff: bool = True) -> None:
        self.image = None
        self._write_mode = None
        super().__init__(file_name, mode)

        self.save_directory = Path(self.file_name).parent

        # Is this an OME-TIFF?
        # TODO: check the header, rather than use the file extension
        if self.file_name.endswith('.ome.tiff') or self.file_name.endswith('.ome.tif'):
            self._is_ome = True
            self.metadata = OMETIFFMetadata()
        else:
            self._is_ome = False
            self.metadata = Metadata()
        
        self._is_bigtiff = is_bigtiff

        # For file writing, do we assume all files end with tiff or tif?
        self.__double_f = self.file_name.endswith('tiff') 
        
        # Keep track of z, time, channel indices
        self._current_frame = 0
        self._current_time = 0

    @property
    def data(self) -> npt.ArrayLike:
        self.mode = 'r'
        
        return self.image.asarray()
    
    @property
    def is_bigtiff(self) -> bool:
        if self._write_mode:
            return self._is_bigtiff
        else:
            return self.image.is_bigtiff

    @property
    def is_ome(self) -> bool:
        if self._write_mode:
            return self._is_ome
        else:
            return self.image.is_ome

    def read(self) -> None:
        self.image = tifffile.TiffFile(self.file_name)

        # TODO: Parse metadata
        for i, ax in enumerate(list(self.image.series[0].axes)):
            setattr(self, f"shape_{ax.lower()}", self.data.shape[i])

    def write(self, data: npt.ArrayLike, **kw) -> None:
        """One channel, all z-position, one timepoint = one stack.
        N channels are opened simultaneously for writing.
        At each time point, a new file is opened for each channel.
        """
        self.mode = 'w'

        c, z, self._current_time = self._czt_indices(self._current_frame, self.metadata.per_stack)  # find current channel
        if (z==0) and (c==0):
            # Make sure we're set up for writing
            self._setup_write_image()

        dx, dy, dz = self.metadata.voxel_size

        md = {'spacing': dz, 'unit': 'um', 'axes': 'ZYX'}
        if len(kw) > 0:
            md['Plane'] = {}
            for k, v in zip(['PositionX', 'PositionY', 'PositionZ'], ['x', 'y', 'z']):
                try:
                    md['Plane'][k] = kw[v]
                except KeyError:
                    pass
        
        self.image[c].write(data,
                            resolution=(1./dx, 1./dy), 
                            metadata=md,
                            contiguous=True)

        self._current_frame += 1

        # Check if this was the last frame to write
        c, z, _ = self._czt_indices(self._current_frame, self.metadata.per_stack)
        if (z==0) and (c==0):
            self.close()

    def generate_image_name(self, current_channel, current_time_point):
        """
        #  Generates a string for the filename
        #  e.g., CH00_000000.tif
        """
        ext = ".ome" if self.is_ome else ""
        ext += ".tiff" if self.__double_f else ".tif"
        image_name = "CH0" + str(current_channel) + "_" + str(current_time_point).zfill(6) + ext
        return image_name

    def _setup_write_image(self) -> None:
        """Setup N channel images for writing."""

        # Grab expected data shape from metadata
        self.shape_x, self.shape_y, self.shape_c, self.shape_z, self.shape_t = self.metadata.shape
        self.dx, self.dy, self.dz = self.metadata.voxel_size
        self.dc, self.dt = self.metadata.dc, self.metadata.dt

        # Initialize one TIFF per channel per time point
        self.image = []
        self.file_name = []
        for ch in range(self.shape_c):
            file_name = os.path.join(self.save_directory, 
                                        self.generate_image_name(ch, self._current_time))
            self.image.append(tifffile.TiffWriter(file_name, bigtiff=self.is_bigtiff,
                                                  ome=self.is_ome))
            self.file_name.append(file_name)

    def _mode_checks(self) -> None:
        self._write_mode = self._mode == 'w'
        self.close()  # if anything was already open, close it
        if self._write_mode:
            self._current_frame = 0
            # self._setup_write_image()
        else:
            self.read()
    
    def close(self) -> None:
        try:
            if self._write_mode:
                for ch in range(self.shape_c):
                    # if self.is_ome:
                    #     # Attach OME metadata at the end of the write 
                    #     tifffile.tiffcomment(self.file_name[ch], self.metadata.to_xml())
                    self.image[ch].close()
            else:
                self.image.close()
        except (TypeError, AttributeError):
            # image wasn't instantiated, no need to close anything
            pass
