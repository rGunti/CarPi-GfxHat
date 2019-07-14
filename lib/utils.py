from os import path

from PIL import ImageFont
from PIL.ImageFont import FreeTypeFont
from gfxhat import fonts

def init_fonts(dir: str=None):
    if not dir:
        dir = path.abspath(path.join(path.dirname(__file__), '..', 'fonts'))

    fonts.font_directory = dir
    fonts.font_files = {}
    fonts.load_fonts("bdf")

def get_font(key: str):
    return fonts.font_files[key]

def get_new_font(key: str, size: int) -> FreeTypeFont:
    return ImageFont.truetype(get_font(key), size=size)
