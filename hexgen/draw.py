import PIL.Image

from hexgen.hex import HexSide
from PIL import Image, ImageDraw, ImageFont
from hexgen.constants import SIDE_LENGTH, HEX_HEIGHT, HEX_RADIUS, HEX_RECT_HEIGHT, HEX_RECT_WIDTH
from hexgen.util import Timer
import pathlib

FONT_SIZE = 14

cur_file = pathlib.Path(__file__).parent.parent

DRAW_FONT = str(cur_file / "fonts" / "DejaVuSans.ttf")


class HexGridDraw:
    """
    Draws a hexagon grid to an image. For debugging and development purposes
    @todo stop globals and pass HEX_HEX_RADIUS, SIDE_LENGTH etc has param with global default if needed
    @todo clever property use cal allow multiple renders at different sizes
    """

    def __init__(self, grid, color_func, map_name, rivers=True,
                 numbers=False, show_coasts=False, borders=False, text_func=None):
        self.grid = grid
        self.color_func = color_func

        if text_func:
            self.text_func = text_func
            try:
                font = ImageFont.truetype(DRAW_FONT, FONT_SIZE)
            except OSError:
                print(f"Could not load {DRAW_FONT}, loading default font")
                self.font = ImageFont.load_default()
                try:
                    self.font = font.font_variant(size=FONT_SIZE)
                except (OSError, AttributeError):
                    print(f"could not get the default font to size {FONT_SIZE}, keeping {font}")
        else:
            self.text_func = None

        self.numbers = numbers
        self.show_coasts = show_coasts
        self.borders = borders
        self.map_name = map_name
        self.rivers = rivers
        self._image = None
        self._draw_tool = None

    @property
    def image(self):
        if self._image is None:
            self._image = Image.new("RGB", (int(HEX_RECT_WIDTH * (self.grid.hex_grid.size + 0.6)),
                                           int(HEX_RECT_WIDTH * self.grid.hex_grid.size)))
        return self._image

    @property
    def draw_tool(self):
        if self._draw_tool is None:
            self._draw_tool = ImageDraw.Draw(self.image)
        return self._draw_tool

    def render(self) -> tuple[str, PIL.Image.Image]:

        with Timer("Making {}".format(self.map_name), True):
            grid = self.grid
            image = self.image
            draw_tool = self.draw_tool
            for y in range(grid.hex_grid.size):
                for x in range(grid.hex_grid.size):
                    h = grid.hex_grid.find_hex(x, y)
                    self.draw_hexagon(y * HEX_RECT_WIDTH + ((x % 2) * HEX_RADIUS),
                                      x * (SIDE_LENGTH + HEX_HEIGHT), x, y)

                    if self.show_coasts and grid.params.get('hydrosphere'):
                        for e in h.edges:
                            if h.is_land and e.two.is_water:
                                self.draw_hex_edge(x, y, e.side, 4)
                    if self.borders:
                        for e in h.edges:
                            if e.one.is_owned and e.two.is_owned and \
                                    e.one.territory.id != e.two.territory.id:
                                self.draw_hex_edge(x, y, e.side, 2)
                    if self.rivers:
                        cx = y * HEX_RECT_WIDTH + ((x % 2) * HEX_RADIUS)
                        cy = x * (SIDE_LENGTH + HEX_HEIGHT)
                        origin = (cx + HEX_RADIUS, cy)
                        pointer = (cx + HEX_RECT_WIDTH, cy + HEX_HEIGHT)
                        pointer_2 = (cx + HEX_RECT_WIDTH, cy + HEX_HEIGHT + SIDE_LENGTH)
                        pointer_3 = (cx + HEX_RADIUS, cy + HEX_RECT_HEIGHT)
                        pointer_4 = (cx, cy + SIDE_LENGTH + HEX_HEIGHT)
                        pointer_5 = (cx, cy + HEX_HEIGHT)
                        segments = self.grid.find_river(x, y)
                        river_blue = (200, 200, 200)  # (255, 255, 255)
                        for s in segments:
                            # print("RiverSegment {} at {}, {}".format(s, x, y))
                            if s is HexSide.north_east:
                                draw_tool.line([origin, pointer], river_blue, width=3)
                            elif s is HexSide.east:
                                draw_tool.line([pointer, pointer_2], river_blue, width=3)
                            elif s is HexSide.south_east:
                                draw_tool.line([pointer_2, pointer_3], river_blue, width=3)
                            elif s is HexSide.south_west:
                                draw_tool.line([pointer_3, pointer_4], river_blue, width=3)
                            elif s is HexSide.west:
                                draw_tool.line([pointer_4, pointer_5], river_blue, width=3)
                            elif s is HexSide.north_west:
                                draw_tool.line([pointer_5, origin], river_blue, width=3)
            return self.map_name, image

    def draw_hex_edge(self, x, y, side, width=3, color=(0, 0, 0)):
        s = side
        cx = y * HEX_RECT_WIDTH + ((x % 2) * HEX_RADIUS)
        cy = x * (SIDE_LENGTH + HEX_HEIGHT)
        origin = (cx + HEX_RADIUS, cy)
        pointer = (cx + HEX_RECT_WIDTH, cy + HEX_HEIGHT)
        pointer_2 = (cx + HEX_RECT_WIDTH, cy + HEX_HEIGHT + SIDE_LENGTH)
        pointer_3 = (cx + HEX_RADIUS, cy + HEX_RECT_HEIGHT)
        pointer_4 = (cx, cy + SIDE_LENGTH + HEX_HEIGHT)
        pointer_5 = (cx, cy + HEX_HEIGHT)
        draw_tool = self.draw_tool
        if s is HexSide.north_east:
            draw_tool.line([origin, pointer], color, width=width)
        elif s is HexSide.east:
            draw_tool.line([pointer, pointer_2], color, width=width)
        elif s is HexSide.south_east:
            draw_tool.line([pointer_2, pointer_3], color, width=width)
        elif s is HexSide.south_west:
            draw_tool.line([pointer_3, pointer_4], color, width=width)
        elif s is HexSide.west:
            draw_tool.line([pointer_4, pointer_5], color, width=width)
        elif s is HexSide.north_west:
            draw_tool.line([pointer_5, origin], color, width=width)

    def make_line(self, from_coord, to_coord):
        self.draw_tool.line([from_coord, to_coord], (0, 0, 0))

    def draw_hexagon(self, cx, cy, x, y):
        origin = (cx + HEX_RADIUS, cy)
        pointer = (cx + HEX_RECT_WIDTH, cy + HEX_HEIGHT)
        pointer_2 = (cx + HEX_RECT_WIDTH, cy + HEX_HEIGHT + SIDE_LENGTH)
        pointer_3 = (cx + HEX_RADIUS, cy + HEX_RECT_HEIGHT)
        pointer_4 = (cx, cy + SIDE_LENGTH + HEX_HEIGHT)
        pointer_5 = (cx, cy + HEX_HEIGHT)

        h = self.grid.hex_grid.find_hex(x, y)
        self.draw_tool.polygon([origin,
                                pointer,
                                pointer_2,
                                pointer_3,
                                pointer_4,
                                pointer_5],
                               outline=None,
                               fill=self.color_func(h))

        self.make_line(origin, pointer)
        self.make_line(pointer, pointer_2)
        self.make_line(pointer_2, pointer_3)
        self.make_line(pointer_3, pointer_4)
        self.make_line(pointer_4, pointer_5)
        self.make_line(pointer_5, origin)

        if self.numbers:
            self.draw_tool.text((cx + 10, cy + 3), str(h.altitude), fill=(200, 200, 200))
            self.draw_tool.text((cx + 4, cy + 11), str(x), fill=(200, 200, 200))
            self.draw_tool.text((cx + 4, cy + 19), str(y), fill=(200, 200, 200))
            self.draw_tool.text((cx + 18, cy + 11), str(h.moisture), fill=(200, 200, 200))
            self.draw_tool.text((cx + 18, cy + 19), str(h.temperature), fill=(200, 200, 200))

            if self.text_func is not None:
                self.draw_tool.text((cx + 5, cy + 5), str(self.text_func(h)), fill=(200, 200, 200), font=self.font)
