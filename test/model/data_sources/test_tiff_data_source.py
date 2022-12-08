import pytest 

def tiff_write_read(is_ome=False, multiposition=False, per_stack=True):
    import os
    import numpy as np

    from aslm.model.dummy import DummyModel
    from aslm.model.data_sources.tiff_data_source import TiffDataSource

    # Set up model with a random number of z-steps to modulate the shape
    model = DummyModel()
    z_steps = np.random.randint(1,10)
    model.configuration['experiment']['MicroscopeState']['image_mode'] = 'z-stack'
    model.configuration['experiment']['MicroscopeState']['number_z_steps'] = z_steps
    model.configuration['experiment']['MicroscopeState']['is_multiposition'] = multiposition
    if per_stack:
        model.configuration['experiment']['MicroscopeState']['stack_cycling_mode'] == 'per_stack'
    else:
        model.configuration['experiment']['MicroscopeState']['stack_cycling_mode'] == 'per_slice'

    # Establish a TIFF data source
    if is_ome:
        fn = 'test.ome.tif'
    else:
        fn = ''
    ds = TiffDataSource(fn)
    ds.set_metadata_from_configuration_experiment(model.configuration)

    # Populate one image per channel per timepoint per position
    n_images = ds.shape_c*ds.shape_z*ds.shape_t*ds.positions
    data = np.random.rand(n_images, ds.shape_x, ds.shape_y)
    file_names = []
    for i in range(n_images):
        ds.write(data[i,...].squeeze())
        c, z, _, _ = ds._cztp_indices(i, per_stack)
        if c == 0 and z == 0:
            file_names.extend(ds.file_name)
    ds.close()

    # For each file...
    for i, fn in enumerate(file_names):
        ds2 = TiffDataSource(fn, 'r')
        # Make sure XYZ size is correct (and C and T are each of size 1)
        assert((ds2.shape_x == ds.shape_x) and (ds2.shape_y == ds.shape_y) \
                and (ds2.shape_c == 1) and (ds2.shape_z == ds.shape_z) \
                and (ds2.shape_t == 1))
        # Make sure the data copied properly
        np.testing.assert_equal(ds2.data, data[i*ds.shape_z:(i+1)*ds.shape_z,...].squeeze())
        ds2.close()

    try:
        # Clean up
        dirs = []
        for fn in file_names:
            os.remove(fn)
            dirs.append(os.path.dirname(fn))
        for dn in list(set(dirs)):
            os.rmdir(dn)
    except PermissionError:
        # Windows seems to think these files are still open
        pass

@pytest.mark.parametrize("is_ome", [True, False])
@pytest.mark.parametrize("multiposition", [True, False])
@pytest.mark.parametrize("per_stack", [True, False])
def test_tiff_write_read(is_ome, multiposition, per_stack):
    tiff_write_read(is_ome=is_ome, multiposition=multiposition, per_stack=per_stack)
