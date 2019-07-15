from datetime import datetime
from typing import List

from math import floor

from app import FONTS
from gfxlib.objects import Screen, Line, Label, TEXT_ALIGN_CENTER, ArrayImage, Rectangle, GfxApp

IMG_ARROW_UP = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
    [0, 0, 1, 1, 1, 0, 0],
    [0, 1, 1, 1, 1, 1, 0],
    [1, 1, 1, 1, 1, 1, 1],
]
IMG_ARROW_DOWN = [
    [0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 1, 1, 1],
    [0, 1, 1, 1, 1, 1, 0],
    [0, 0, 1, 1, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0],
]


class BaseMenu(Screen):
    def __init__(self,
                 screen_id: str,
                 screen_title: str,
                 menu_items: List[str],
                 actions: List[any]):
        super().__init__(screen_id)

        self._selection_pos = 0

        self._menu_items = menu_items
        self._menu_actions = actions

        self.add_objects(Line((0, 8), (128, 8)),
                         Label((64, 0), FONTS['small'], screen_title or screen_id,
                               align=TEXT_ALIGN_CENTER),
                         Line((0, 55), (128, 55)),
                         Line((42, 55), (42, 64)),
                         Line((85, 55), (85, 64)),
                         Label((64, 56), FONTS['small'], 'OK',
                               align=TEXT_ALIGN_CENTER),
                         ArrayImage((18, 56), IMG_ARROW_UP),
                         ArrayImage((103, 56), IMG_ARROW_DOWN)
                         )

        self._menu_elements = [
            Label((10, 11), FONTS['med'], ''),
            Label((10, 22), FONTS['med'], ''),
            Label((10, 33), FONTS['med'], ''),
            Label((10, 44), FONTS['med'], '')
        ]
        self._selection_rect = Rectangle((0, 10), (128, 11))
        self.add_object(self._selection_rect)
        self.add_objects(*self._menu_elements)

    def update(self, now: datetime, app):
        select_i = self._selection_pos % 4
        first_visible_i = floor(self._selection_pos / 4) * 4

        self._set_visible_items(self._menu_items[first_visible_i:first_visible_i + 4])
        self._set_item_colors(select_i)

        select_rect_y = ((select_i + 1) * 11) - 1
        rect = self._selection_rect
        rect.position = (rect.position[0], select_rect_y)

        super().update(now, app)

    def _set_visible_items(self, items: List[str]):
        for i in range(len(self._menu_elements)):
            if i < len(items):
                self._menu_elements[i].text = items[i]
            else:
                self._menu_elements[i].text = ''

    def _set_item_colors(self, highlighted: int):
        for i in range(len(self._menu_elements)):
            self._menu_elements[i].filled = highlighted != i

    def on_plus_pressed(self, app):
        self._selection_pos = (self._selection_pos + 1) % len(self._menu_items)

    def on_minus_pressed(self, app):
        self._selection_pos = (self._selection_pos - 1) % len(self._menu_items)

    def on_enter_pressed(self, app):
        self._on_item_selected(self._selection_pos, app)

    def _on_item_selected(self, index: int, app: GfxApp):
        action = self._menu_actions[index] \
            if index < len(self._menu_actions) \
            else self._empty_callback
        if action:
            action(index, app)
        else:
            self._empty_callback(index, app)

    def _empty_callback(self, index: int, app: GfxApp):
        print('[!] Unhandled menu action at Index {}'.format(index))
