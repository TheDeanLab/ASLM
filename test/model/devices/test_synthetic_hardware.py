from email.mime import base
from pathlib import Path

from numpy import triu_indices
from src.model.aslm_model_config import Session as session

# Set up the model, experiment, ETL dictionaries
base_directory = Path(__file__).resolve().parent.parent.parent.parent
configuration_directory = Path.joinpath(base_directory, 'src', 'config')

model = session(Path.joinpath(configuration_directory, 'configuration.yml'))
experiment = session(Path.joinpath(configuration_directory, 'experiment.yml'))
etl_constants = session(Path.joinpath(configuration_directory, 'etl_constants.yml'))

def test_synthetic_daq():
    from src.model.devices.daq import SyntheticDAQ

    sd = SyntheticDAQ(model, experiment, etl_constants)

    return True

def test_synthetic_camera():
    from src.model.devices.cameras import SyntheticCamera

    sc = SyntheticCamera(0, model, experiment)

    return True

def test_synthetic_filter_wheel():
    from src.model.devices.filter_wheels import SyntheticFilterWheel

    sf = SyntheticFilterWheel(model, False)

    return True

def test_synthetic_stage():
    from src.model.devices.stages import SyntheticStage

    ss = SyntheticStage(model, False)

def test_synthetic_zoom():
    from src.model.devices.zoom import SyntheticZoom

    sz = SyntheticZoom(model, False)

    return True

def test_synthetic_shutter():
    from src.model.devices.laser_shutters import SyntheticShutter

    ss = SyntheticShutter(model, experiment)

    return True

def test_synthetic_laser():
    from src.model.devices.lasers.SyntheticLaser import SyntheticLaser

    sl = SyntheticLaser(model, False)

    return True
