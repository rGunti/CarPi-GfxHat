from typing import Dict, List, Tuple
from PIL import ImageDraw, Image
from PIL.ImageFont import FreeTypeFont
from datetime import datetime
from math import ceil

from lib.exceptions import ScreenStillActiveException
from lib import input

TEXT_ALIGN_LEFT = 0
TEXT_ALIGN_CENTER = -0.5
TEXT_ALIGN_RIGHT = -1

TEXT_VALIGN_TOP = 0
TEXT_VALIGN_CENTER = -0.5
TEXT_VALIGN_BOTTOM = -1


class RenderObject(object):
    def __init__(self, xy: tuple):
        self._position = xy
        self._is_visible = True

    @property
    def is_visible(self):
        return self._is_visible

    @is_visible.setter
    def is_visible(self, value):
        self._is_visible = value

    @property
    def position(self) -> Tuple[int, int]:
        return self._position

    @position.setter
    def position(self, value: Tuple[int, int]):
        self._position = value

    def render(self, draw: ImageDraw.ImageDraw, image: Image.Image):
        if self._is_visible:
            self._render(draw, image)

    def _render(self, draw: ImageDraw.ImageDraw, image: Image.Image):
        raise NotImplementedError()

    def update(self, now: datetime, app):
        pass

    def __str__(self) -> str:
        return '{}'.format(type(self).__name__)


class RenderObjectArray(RenderObject):
    def __init__(self,
                 *args: RenderObject):
        super(RenderObjectArray, self).__init__((-1, -1))
        self._children = []
        for child in args:
            self.add_object(child)

    def add_objects(self, *args: RenderObject):
        for obj in args:
            self.add_object(obj)

    def add_object(self, obj: RenderObject) -> RenderObject:
        self._children.append(obj)
        return obj

    def _render(self, draw: ImageDraw.ImageDraw, image: Image.Image):
        for child in self._children:
            child.render(draw, image)

    def update(self, now: datetime, app):
        for child in self._children:
            child.update(now, app)


class Screen(RenderObjectArray):
    def __init__(self, screen_id: str, *args: RenderObject):
        super(Screen, self).__init__(*args)
        self._id = screen_id

    @property
    def screen_id(self):
        return self._id

    def __str__(self) -> str:
        return "Screen \"{}\" ({} object(s))".format(self.screen_id, len(self._children))

    def on_navigate_away(self, to_screen: str = None):
        pass

    def on_navigate_to(self, from_screen: str = None):
        pass

    def on_button_pressed(self, app, button: int):
        pass

    def on_button_released(self, app, button: int):
        pass

    def on_plus_pressed(self, app):
        pass

    def on_minus_pressed(self, app):
        pass

    def on_enter_pressed(self, app):
        pass

    def on_up_pressed(self, app):
        pass

    def on_down_pressed(self, app):
        pass

    def on_back_pressed(self, app):
        pass

    def on_plus_released(self, app):
        pass

    def on_minus_released(self, app):
        pass

    def on_enter_released(self, app):
        pass

    def on_up_released(self, app):
        pass

    def on_down_released(self, app):
        pass

    def on_back_released(self, app):
        pass


class Line(RenderObject):
    def __init__(self,
                 xy: tuple,
                 x2y2: tuple,
                 filled=True,
                 width=1):
        super(Line, self).__init__(xy)
        self._2nd_position = x2y2
        self._filled = filled
        self._width = width

    def _render(self, draw: ImageDraw.ImageDraw, image: Image.Image):
        draw.line((self._position[0], self._position[1], self._2nd_position[0], self._2nd_position[1]),
                  fill=255 if self._filled else 0,
                  width=self._width)


class Rectangle(RenderObject):
    def __init__(self,
                 xy: tuple,
                 wh: tuple,
                 filled=True):
        super(Rectangle, self).__init__(xy)
        self._width, self._height = wh
        self._filled = filled

    def _render(self, draw: ImageDraw.ImageDraw, image: Image.Image):
        rect = (self._position[0], self._position[1],
                self._position[0] + self._width, self._position[1] + self._height)

        draw.rectangle(rect,
                       fill=255 if self._filled else 0)


class Label(RenderObject):
    def __init__(self,
                 xy: tuple, font: FreeTypeFont, text: str,
                 align = TEXT_ALIGN_LEFT, valign = TEXT_VALIGN_TOP,
                 fill = 1):
        super(Label, self).__init__(xy)
        self._font = font
        self._text = text
        self._align = align
        self._valign = valign
        self._fill = fill

    @property
    def filled(self) -> int:
        return self._fill

    @filled.setter
    def filled(self, value: int):
        self._fill = value

    def _render(self, draw: ImageDraw.ImageDraw, image: Image.Image):
        pos = self._position

        if self._align != TEXT_ALIGN_LEFT or self._valign != TEXT_VALIGN_TOP:
            render_size = draw.textsize(text=self._text,
                                        font=self._font)
            pos_x = self._position[0] + (self._align * render_size[0])
            pos_y = self._position[1] + (self._valign * render_size[1])

            pos = (ceil(pos_x), ceil(pos_y))

        draw.text(xy=pos, text=self._text,
                  fill=self._fill, font=self._font)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value: str):
        self._text = value

    def __str__(self) -> str:
        return '{}: {}'.format(super().__str__(),
                               self._text)


class DateTimeLabel(Label):
    def __init__(self,
                 xy: tuple,
                 font: FreeTypeFont,
                 format: str = '%x %X',
                 align=TEXT_ALIGN_LEFT,
                 valign=TEXT_VALIGN_TOP, fill=1):
        super().__init__(xy, font, '', align, valign, fill)
        self._format = format

    def update(self, now: datetime, app):
        self._text = now.strftime(self._format)


class SpinnerLabel(Label):
    SEQUENCE = ['\\', '|', '/', '-', '\\', '|', '/', '-']

    def __init__(self, xy: tuple, font: FreeTypeFont,
                 align=TEXT_ALIGN_LEFT, valign=TEXT_VALIGN_TOP, fill=1):
        super().__init__(xy, font, '|', align, valign, fill)
        self._frame = 0

    def update(self, now: datetime, app):
        self.text = SpinnerLabel.SEQUENCE[self._frame]
        self._frame = (self._frame + 1) % len(SpinnerLabel.SEQUENCE)


class BarGraph(RenderObject):
    def __init__(self,
                 xy: tuple, wh: tuple, value=0,
                 min_value=0, max_value=100,
                 interval=0):
        super(BarGraph, self).__init__(xy)
        self._width, self._height = wh
        self._value = value
        self._min_value = min_value
        self._max_value = max_value
        self._interval = interval

    @property
    def p_value(self):
        return self._value

    @p_value.setter
    def p_value(self, value):
        self._value = max(min(value, self._max_value), self._min_value)

    def _render(self, draw: ImageDraw.ImageDraw, image: Image.Image):
        rect = (self._position[0], self._position[1],
                self._position[0] + self._width, self._position[1] + self._height)
        # Border
        draw.rectangle(rect, fill=0, outline=1)

        # Fill
        p_range = abs(self._min_value) + abs(self._max_value)
        zero_pct = (0 + abs(self._min_value)) / p_range
        zero_pt = (self._position[0] + 2 + (zero_pct * (self._width - 4)),
                   self._position[1] + 2)
        val_pct = self._value / (self._max_value - self._min_value)
        fill_rect = (zero_pt[0], zero_pt[1],
                     zero_pt[0] + (val_pct * (self._width - 4)), zero_pt[1] + self._height - 4)
        draw.rectangle(fill_rect, fill=1)

        # Draw Zero Indicator
        draw.line((zero_pt[0], zero_pt[1] - 1,
                   zero_pt[0], zero_pt[1] + self._height - 2),
                  fill=255, width=1)

        # Draw Intervals
        if self._interval > 0:
            for i in range(0, self._max_value + 1, self._interval):
                itv_pct = i / p_range
                itv_pos = (zero_pt[0] + (itv_pct * (self._width - 4)), zero_pt[1] + (self._height / 2))
                draw.line((itv_pos[0], itv_pos[1], itv_pos[0], zero_pt[1] + self._height - 3),
                          fill=255, width=1)

            for i in range(0, self._min_value - 1, -self._interval):
                itv_pct = i / p_range
                itv_pos = (zero_pt[0] + (itv_pct * (self._width - 4)), zero_pt[1] + (self._height / 2))
                draw.line((itv_pos[0], itv_pos[1], itv_pos[0], zero_pt[1] + self._height - 3),
                          fill=255, width=1)


IMAGE_RMODE_CONVERT_TO_R_MODE = 0b00000
IMAGE_RMODE_RENDER_NON_ALPHA = 0b00001
IMAGE_RMODE_DEFAULT = IMAGE_RMODE_CONVERT_TO_R_MODE


class BaseImage(RenderObject):
    def __init__(self, xy: tuple, wh: tuple):
        super().__init__(xy)
        self._preprocessed_image: Image.Image = Image.new('P', wh) if wh else None

    def _preprocess_image(self) -> Image.Image:
        raise NotImplementedError()

    def _render(self, draw: ImageDraw.ImageDraw, image: Image.Image):
        if not self._preprocessed_image:
            self._preprocessed_image = self._preprocess_image()
        image.paste(self._preprocessed_image.copy(), self._position)


class ArrayImage(BaseImage):
    def __init__(self, xy: tuple, image_data: List[List[int]]):
        super().__init__(xy, None)
        self._image_data = image_data

    def _preprocess_image(self) -> Image.Image:
        data = self._image_data
        img = Image.new('P', (len(data[0]), len(data)))
        draw = ImageDraw.Draw(img)

        for x in range(img.size[0]):
            for y in range(img.size[1]):
                p = data[y][x]
                if p:
                    draw.point((x, y), p)

        return img


class FileImage(BaseImage):
    def __init__(self,
                 xy: tuple,
                 file: str,
                 render_mode: int = IMAGE_RMODE_DEFAULT):
        super().__init__(xy, None)
        self._render_mode = render_mode
        self._source_image: Image.Image = Image.open(file)
        self._source_image_path = file

    def _preprocess_image(self) -> Image.Image:
        src = self._source_image
        rmode = self._render_mode

        img = Image.new('P', src.size)
        draw = ImageDraw.Draw(img)

        if rmode & IMAGE_RMODE_RENDER_NON_ALPHA:
            for x in range(src.size[0]):
                for y in range(src.size[1]):
                    p = src.getpixel((x, y))
                    if p[3] > 128:
                        draw.point((x, y), fill=True)
        elif rmode & IMAGE_RMODE_CONVERT_TO_R_MODE:
            img.paste(src.convert('R').copy())

        return img

    def __str__(self) -> str:
        return '{} {}'.format(super().__str__(), self._source_image_path)


class GfxApp(object):
    def __init__(self,
                 screens: List[Screen] = None,
                 active_screen: str = None):
        self._screens: Dict[str, Screen] = {}
        self._active_screen: str = active_screen
        self._alive = True

        if screens:
            self.add_screens(screens)

        for button in input.BUTTONS:
            input.on_touch(button, self.handle_input)

    @property
    def alive(self):
        return self._alive

    @property
    def active_screen_id(self):
        return self._active_screen

    @property
    def active_screen(self):
        return self._screens[self._active_screen]

    def stop(self):
        self._alive = False

    def add_screens(self, screens: List[Screen]):
        for screen in screens:
            self.add_screen(screen)

    def add_screen(self, screen: Screen):
        self._screens[screen.screen_id] = screen
        if not self.active_screen_id:
            self.navigate_to(screen.screen_id)

    def remove_screen(self, screen_id: str):
        if screen_id == self.active_screen_id:
            raise ScreenStillActiveException()
        del self._screens[screen_id]

    def navigate_to(self, screen_id: str, skip_events: bool = False):
        if screen_id not in self._screens:
            raise KeyError()

        if not skip_events and self.active_screen_id:
            self.active_screen.on_navigate_away(screen_id)

        old_screen_id = self.active_screen.screen_id if self._active_screen \
            else None
        self._active_screen = screen_id

        if not skip_events:
            self.active_screen.on_navigate_to(old_screen_id)

    def render(self, draw: ImageDraw.ImageDraw, image: Image.Image):
        self.active_screen.render(draw, image)

    def update(self, now: datetime):
        self.active_screen.update(now, self)

    def handle_input(self, button, event):
        if event == input.EVT_PRESS:
            #self.active_screen.on_button_pressed(self, button)
            self._handle_button_pressed(button)
        elif event == input.EVT_RELEASE:
            #self.active_screen.on_button_released(self, button)
            self._handle_button_released(button)

    def _handle_button_pressed(self, button: int):
        screen = self.active_screen
        if button == input.BTN_UP:
            screen.on_up_pressed(self)
        elif button == input.BTN_DOWN:
            screen.on_down_pressed(self)
        elif button == input.BTN_BACK:
            screen.on_back_pressed(self)
        elif button == input.BTN_MINUS:
            screen.on_minus_pressed(self)
        elif button == input.BTN_ENTER:
            screen.on_enter_pressed(self)
        elif button == input.BTN_PLUS:
            screen.on_plus_pressed(self)

    def _handle_button_released(self, button: int):
        screen = self.active_screen
        if button == input.BTN_UP:
            screen.on_up_released(self)
        elif button == input.BTN_DOWN:
            screen.on_down_released(self)
        elif button == input.BTN_BACK:
            screen.on_back_released(self)
        elif button == input.BTN_MINUS:
            screen.on_minus_released(self)
        elif button == input.BTN_ENTER:
            screen.on_enter_released(self)
        elif button == input.BTN_PLUS:
            screen.on_plus_released(self)
