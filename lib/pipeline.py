from typing import List, Tuple

from PIL import Image, ImageDraw, ImageChops
from datetime import datetime, timedelta
from gfxhat import lcd, touch
from time import sleep

from lib.objects import RenderObject, GfxApp

PIPETIME_UPDATE = 0
PIPETIME_CLEAR = 1
PIPETIME_PROCESS = 2
PIPETIME_RENDER = 3
PIPETIME_COMPLETE = 10


ORIENT_LANDSCAPE = 0b00
ORIENT_PORTRAIT = 0b10

ORIENT_INVERT = 0b01
ORIENT_LANDSCAPE_INVERT = ORIENT_LANDSCAPE | ORIENT_INVERT
ORIENT_PORTRAIT_INVERT = ORIENT_PORTRAIT | ORIENT_INVERT

ORIENT_DEFAULT = ORIENT_LANDSCAPE


MODIFIER_NONE = 0b0
MODIFIER_COLOR_INVERTED = 0b1
MODIFIER_DRAW_IN_DIFF_MODE = 0b10

LCD_SIZE = lcd.dimensions()

PT = ([0] + ([255] * 255))


def is_portrait(orient: int) -> bool:
    return not (not orient & ORIENT_PORTRAIT)


def is_landscape(orient: int) -> bool:
    return not (not orient & ORIENT_LANDSCAPE)


def is_inverted(orient: int) -> bool:
    return not (not orient & ORIENT_INVERT)


def is_color_inverted(modifier: int) -> bool:
    return not (not modifier & MODIFIER_COLOR_INVERTED)


def is_using_diff(modifier: int) -> bool:
    return not (not modifier & MODIFIER_DRAW_IN_DIFF_MODE)


class RenderPipelineTimings(object):
    def __init__(self):
        self._timing_start = datetime.now()
        self._timing_update = datetime.min
        self._timing_clear = datetime.min
        self._timing_process = datetime.min
        self._timing_render = datetime.min
        self._timing_completed = datetime.min

    def hit_clear(self):
        self._timing_clear = datetime.now()

    def hit_update(self):
        self._timing_update = datetime.now()

    def hit_process(self):
        self._timing_process = datetime.now()

    def hit_render(self):
        self._timing_render = datetime.now()

    def hit_complete(self):
        self._timing_completed = datetime.now()

    @property
    def start_time(self):
        return self._timing_start

    @property
    def total_time(self):
        return (self._timing_completed - self._timing_start).total_seconds() * 1000

    @property
    def update_time(self):
        return (self._timing_update - self._timing_start).total_seconds() * 1000

    @property
    def clear_time(self):
        return (self._timing_clear - self._timing_update).total_seconds() * 1000

    @property
    def process_time(self):
        return (self._timing_process - self._timing_clear).total_seconds() * 1000

    @property
    def render_time(self):
        return (self._timing_render - self._timing_process).total_seconds() * 1000

    @property
    def complete_time(self):
        return (self._timing_completed - self._timing_render).total_seconds() * 1000

    def __str__(self) -> str:
        if self._timing_completed != datetime.min:
            return 'Cycle completed in {:0.1f} ms (slept for {:0.1f} ms)'.format(self.total_time, self.complete_time)
        if self._timing_render != datetime.min:
            return 'Rendered in {:0.1f} ms'.format(self.render_time)
        if self._timing_process != datetime.min:
            return 'Processed in {:0.1f} ms'.format(self.process_time)
        if self._timing_clear != datetime.min:
            return 'Cleared in {:0.1f} ms'.format(self.clear_time)
        if self._timing_update != datetime.min:
            return 'Updated in {:0.1f} ms'.format(self.update_time)

        return 'Started at {}'.format(self._timing_start)


class RenderPipeline(object):
    def __init__(self,
                 app: GfxApp,
                 screen_size: tuple=None,
                 enable_timing=False,
                 enable_reinit=False,
                 fps_limit=0,
                 orientation=ORIENT_DEFAULT,
                 modifiers=MODIFIER_NONE
                 ):
        if not screen_size:
            screen_size = lcd.dimensions()
        if orientation == ORIENT_PORTRAIT or orientation == ORIENT_PORTRAIT_INVERT:
            screen_size = (screen_size[1], screen_size[0])

        self._orientation = orientation
        self._modifiers = modifiers

        self._image_size = screen_size
        self._image = Image.new('P', self._image_size)
        self._draw = ImageDraw.Draw(self._image)

        self._last_image = Image.new('P', self._image_size)

        self._app: GfxApp = app

        self._current_timing: RenderPipelineTimings = None
        self._last_timing: RenderPipelineTimings = None

        self._use_reinit = enable_reinit
        self._frame_sleep_time = 0 if fps_limit <= 0 else 1 / fps_limit
        self._enable_timing = enable_timing or (fps_limit > 0)

        self._frame_counter = 0

    @property
    def frame_time(self):
        return self._last_timing

    @property
    def is_timing_enabled(self):
        return self._enable_timing

    def _start_timing(self):
        if self._enable_timing:
            self._current_timing = RenderPipelineTimings()

    def _register_timing(self, pos):
        if self._enable_timing and self._current_timing:
            if pos == PIPETIME_UPDATE:
                self._current_timing.hit_update()
            elif pos == PIPETIME_CLEAR:
                self._current_timing.hit_clear()
            elif pos == PIPETIME_PROCESS:
                self._current_timing.hit_process()
            elif pos == PIPETIME_RENDER:
                self._current_timing.hit_render()
            elif pos == PIPETIME_COMPLETE:
                self._current_timing.hit_complete()

    def _finish_timing(self):
        if self._enable_timing and self._current_timing:
            self._last_timing = self._current_timing
            print(self._last_timing)

    def _update(self):
        now = datetime.now()
        self._app.update(now)
        self._register_timing(PIPETIME_UPDATE)

    def _clear(self):
        for x in range(self._image_size[0]):
            for y in range(self._image_size[1]):
                self._image.putpixel((x, y), 0)
        self._register_timing(PIPETIME_CLEAR)

    def _reinit(self):
        if is_using_diff(self._modifiers):
            self._last_image = self._image

        self._image = Image.new('P', self._image_size)
        self._draw = ImageDraw.Draw(self._image)
        self._register_timing(PIPETIME_CLEAR)

    def _process(self):
        self._app.render(self._draw, self._image)
        self._register_timing(PIPETIME_PROCESS)

    #def _run_image_dif(self) -> Image:
    #    orig = self._last_image
    #    updated = self._image
    #
    #    diff = ImageChops.difference(orig, updated).getbbox()\
    #        .convert('L')\
    #        .point(PT)
    #    new = diff.convert('P')
    #    new.paste(updated, mask=diff)
    #    return new

    def _get_changed_pixels(self) -> List[Tuple[int, int]]:
        orig = self._last_image
        updated = self._image
        coords = []
        for x in range(orig.size[0]):
            for y in range(orig.size[1]):
                orig_pix = orig.getpixel((x, y))
                updated_pix = updated.getpixel((x, y))
                if orig_pix != updated_pix:
                    coords.append((x, y))
        return coords

    def _render(self):
        portrait = is_portrait(self._orientation)
        inverted = is_inverted(self._orientation)

        color_inverted = is_color_inverted(self._modifiers)
        use_diff = is_using_diff(self._modifiers)

        if use_diff:
            delta_list = self._get_changed_pixels()
            for coord in delta_list:
                lcd_coords = self._process_screen_coord(coord, portrait)
                pix_coords = self._process_image_coord(coord, inverted)
                self._render_pixel(lcd_coords, pix_coords,
                                   color_inverted)
        else:
            for x in range(0, self._image_size[0], 1):
                for y in range(0, self._image_size[1], 1):
                    lcd_coords = self._process_screen_coord((x, y), portrait)
                    pix_coords = self._process_image_coord((x, y), inverted)

                    self._render_pixel(lcd_coords, pix_coords, color_inverted)

        # Flush Display Buffer
        lcd.show()

        # Do the timing
        self._register_timing(PIPETIME_RENDER)
        if self._frame_sleep_time > 0:
            delta = datetime.now() - self._current_timing.start_time
            sleep_dur = self._frame_sleep_time - (delta.total_seconds() * 1000 / 1000) - 0.001
            if sleep_dur > 0:
                sleep(sleep_dur)
        self._register_timing(PIPETIME_COMPLETE)

    def _process_screen_coord(self,
                              coord: Tuple[int, int],
                              portrait: bool = False):
        if portrait:
            coord = (min(coord[1], LCD_SIZE[0]),
                     min(self._image_size[0] - coord[0] - 1, LCD_SIZE[1]))
        return coord

    def _process_image_coord(self,
                             coord: Tuple[int, int],
                             inverted: bool = False):
        if inverted:
            coord = (self._image_size[0] - 1 - coord[0],
                     self._image_size[1] - 1 - coord[1])
        return coord

    def _render_pixel(self,
                      screen_coord: Tuple[int, int],
                      image_coord: Tuple[int, int],
                      color_inverted: bool = False):
        pix = self._image.getpixel(image_coord)
        if color_inverted:
            pix = 0 if pix else 1
        lcd.set_pixel(screen_coord[0], screen_coord[1], pix)

    def loop_step(self):
        self._start_timing()

        self._update()
        self._clear() if not self._use_reinit else self._reinit()
        self._process()
        self._render()

        self._finish_timing()
        self._frame_counter += 1
