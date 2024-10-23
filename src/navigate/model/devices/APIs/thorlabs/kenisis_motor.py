"""
API for connection to Thorlabs.MotionControl.KCube.StepperMotor.dll.
See Thorlabs.MotionControl.KCube.StepperMotor.h for more functions to implement.
"""

"""
2024/10/23 Sheppard: Initialized to control Kinesis Stepper motor in Linux
"""
from pylablib.devices import Thorlabs

def in_enum(value, enum):
    values = set(item.value for item in enum)
    return value in values


def errcheck(result, func, args):
    """
    Wraps the call to DLL functions.

    Parameters
    ----------
    result : ctypes.c_short
        Error code or 0 if successful.
    func : function
        DLL function
    args : tuple
        Arguments passed to the DLL function, defined in argtypes

    Returns
    -------
    result : int
        Error code or 0 if successful.
    """
    
    return 0


def KST_Open(connection):
    """
    Open the device for communications.

    Parmeters
    ---------
    serial_number : str
        Serial number of Thorlabs Kinesis Stepper Motor (KST) device.

    Returns
    -------
    int
        The error code or 0 if successful.
    """
    try:
        stage = Thorlabs.KinesisMotor(("serial", connection), scale="step")
        success = True
    except Exception as e:
        success = False
        raise ConnectionError(f"KST101 stage connection failed! \nError: {e}")
    if success:
        return stage
    
def KST_Close(stage):
    """
    Disconnect and close the device.

    Parmeters
    ---------
    serial_number : str
        Serial number of Thorlabs Kinesis Stepper Motor (KST) device.

    Returns
    -------
    None
    """
    stage.stop()
    stage.close()
    
def KST_MoveToPosition(stage, position, wait_till_done, steps_per_um):
    """Move to position (um)
    """
    stage.get_position(channel=1, scale=False)
    cur_pos = stage.get_position(channel=1, scale=False)
    position_um = cur_pos / steps_per_um
    # calculate the distance needed to move
    distance = position - position_um
    # convert total distance to steps
    steps = steps_per_um * distance
    stage.move_by(steps, channel=1, scale=False)
    if wait_till_done:
        stage.wait_move(channel=1)
    return 0

def KST_GetCurrentPosition(stage, steps_per_um):
    """Get the current position      

    Parmeters
    ---------
    serial_number : str
        Serial number of Thorlabs Kinesis Stepper Motor (KST) device.

    Returns
    -------
    int
        Current position.
    """    
    stage.get_position(channel=1, scale=False)
    position = stage.get_position(channel=1, scale="False")
    position_um = position / steps_per_um 
    return position_um

def KST_MoveStop(stage):
    """
    Halt motion

    Parmeters
    ---------
    serial_number : str
        Serial number of Thorlabs Kinesis Stepper Motor (KST) device.
    channel : int
        The device channel. One of SCC_Channels.

    Returns
    -------
    int
        The error code or 0 if successful.
    """
    stage.stage.stop()
    return 0

def KST_HomeDevice(stage):
    """Home Device
    """
    stage.stage.home()
    return 0

def KST_SetVelocityParams(stage, min_velocity, max_velocity, acceleration):
    """Set velocity profile required for move
    """
    stage.set_move_params(min_velocity, max_velocity, acceleration)
    return 0