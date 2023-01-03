"""
ASLM affine transform implementation.

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
# Python Imports
import os
import time

# Second Party Imports
import numpy as np
import tensorflow as tf

import logging
from pathlib import Path

# Logger Setup
p = __name__.split(".")[1]
logger = logging.getLogger(p)


def deskew_image(image_data, shear_angle, z_pixel_size, xy_pixel_size):
    """
    #  This function is designed to deskew an image.
    # return uint16 data to save as tiff
    """

    use_cpu = True  # initiate_gpu()
    time_it = True

    (z_len, y_len, x_len) = image_data.shape
    scaled_shear_angle = (
        np.cos(shear_angle * np.pi / 180) * z_pixel_size / xy_pixel_size
    )
    scale_factor = np.uint16(
        np.ceil(
            z_len * np.cos(shear_angle * np.pi / 180) * z_pixel_size / xy_pixel_size
        )
    )

    #  Create blank image to store the deskewed image.
    scaled_array = np.zeros((z_len, y_len, x_len + scale_factor))
    output_array = np.zeros((z_len, y_len, x_len + scale_factor))

    # Populate the scaled array with the original data
    scaled_array[:z_len, :y_len, :x_len] = image_data
    xF, yF = np.meshgrid(np.arange(x_len + scale_factor), np.arange(y_len))

    if use_cpu:
        if time_it:
            start_time = time.time()

        for k in range(z_len):
            image_slice = scaled_array[k, :, :]
            image_slice_fft = np.fft.fftshift(np.fft.fft2(image_slice))
            image_slice_fft_trans = image_slice_fft * np.exp(
                -1j * 2 * np.pi * xF * scaled_shear_angle * k / (x_len + scale_factor)
            )
            output_array[k, :, :] = np.abs(
                np.fft.ifft2(np.fft.ifftshift(image_slice_fft_trans))
            )

        output_array[output_array < 0] = 0
        if time_it:
            print("Execution Time:", time.time() - start_time)

        return np.uint16(output_array)

    else:
        if time_it:
            start_time = time.time()

        datatype = tf.dtypes.complex64
        scaled_array = tf.convert_to_tensor(scaled_array, dtype=datatype)
        output_array = tf.Variable(output_array, dtype=tf.dtypes.float32)
        for k in range(z_len):
            image_slice = scaled_array[k, :, :]
            image_slice = tf.signal.fftshift(tf.signal.fft2d(image_slice))
            shift_constant = tf.constant(
                -1j * 2 * np.pi * xF * scaled_shear_angle * k / (x_len + scale_factor),
                dtype=datatype,
            )
            image_slice = tf.math.multiply(image_slice, tf.math.exp(shift_constant))
            image_slice = tf.math.abs(
                tf.signal.ifft2d(tf.signal.ifftshift(image_slice))
            )
            output_array[k, :, :].assign(image_slice)

        output_array = output_array.numpy()
        output_array[output_array < 0] = 0
        if time_it:
            print("Execution Time:", time.time() - start_time)

        return np.uint16(output_array)


def initiate_gpu():
    gpus = tf.config.list_physical_devices("GPU")
    if gpus:
        use_cpu = False
        # Create 2 virtual GPUs with 24GB memory each
        try:
            tf.config.set_logical_device_configuration(
                gpus[0],
                [
                    tf.config.LogicalDeviceConfiguration(memory_limit=23000),
                    tf.config.LogicalDeviceConfiguration(memory_limit=23000),
                ],
            )
            logical_gpus = tf.config.list_logical_devices("GPU")
            print(len(gpus), "Physical GPU,", len(logical_gpus), "Logical GPUs")
        except RuntimeError as e:
            # Virtual devices must be set before GPUs have been initialized
            print(e)
    else:
        use_cpu = True
    return use_cpu


if __name__ == "__main__":
    """
    Testing section
    """

    from tifffile import imread, imsave

    image_data = imread(os.path.join("E:", "test_data", "CH01_003b.tif"))
    shear_angle = 30
    z_pixel_size = 0.5
    xy_pixel_size = 0.2
    output_data = deskew_image(image_data, shear_angle, z_pixel_size, xy_pixel_size)
    imsave(os.path.join("E:", "test_data", "CH01_003_sheared.tif"), output_data)
