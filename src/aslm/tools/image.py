from PIL import Image, ImageDraw, ImageFont
import numpy as np


def text_array(text: str, offset: tuple = (0, 0), font_size: int = 16):
    """Create a binary array from a piece of text

    Parameters
    ----------
    text : str
        Text to convert
    offset : tuple
        (x,y) offset from upper left of image
    font_size: int
        Size of font in pixels
    """
    font = ImageFont.truetype("arial.ttf", font_size)
    bbox = font.getbbox(text)
    im = Image.new("1", (bbox[2] + offset[0], bbox[3] + offset[1]))
    ImageDraw.Draw(im).text(offset, text, 1, font=font)
    return np.array(im, dtype=bool)
