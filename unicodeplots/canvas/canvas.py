from typing import Callable, Optional, Protocol, runtime_checkable

from unicodeplots.utils import ColorType


@runtime_checkable
class PlotStyle(Protocol):
    def adjust_grid(self, canvas: "Canvas") -> None:
        """Let style configure canvas pixel dimensions."""
        ...

    def set_pixel(self, canvas: "Canvas", px: int, py: int, color: int) -> None:
        """Draw a pixel at the given pixel coordinates."""
        ...


class LineStyle(PlotStyle):
    def __init__(self):
        self.x_pixels_per_char = 2
        self.y_pixels_per_char = 4
        self.bit_table = [
            [0x01, 0x02, 0x04, 0x40],  # x=0
            [0x08, 0x10, 0x20, 0x80],  # x=1
        ]

    def adjust_grid(self, canvas: "Canvas") -> None:
        canvas.x_pixels_per_char = self.x_pixels_per_char
        canvas.y_pixels_per_char = self.y_pixels_per_char

    def set_pixel(
        self,
        canvas: "Canvas",
        px: int,
        py: int,
        color: int,
    ) -> None:
        """Set a Braille pixel using bit manipulation."""
        # Convert pixel coords to character coords
        cx = px // canvas.x_pixels_per_char
        cy = py // canvas.y_pixels_per_char

        if not (0 <= cx < canvas.width and 0 <= cy < canvas.height):
            return

        # Find position within the character (0-1 for x, 0-3 for y)
        x_in = px % canvas.x_pixels_per_char
        y_in = py % canvas.y_pixels_per_char

        bit = self.bit_table[x_in][y_in]
        canvas.grid[cy][cx] |= bit
        canvas.colors[cy][cx] = color


class MarkerStyle(PlotStyle):
    def __init__(self, marker: str = "•"):
        self.x_pixels_per_char = 1
        self.y_pixels_per_char = 1
        self.marker = marker

    def adjust_grid(self, canvas: "Canvas") -> None:
        """Set canvas pixel dimensions for markers."""
        canvas.x_pixels_per_char = self.x_pixels_per_char
        canvas.y_pixels_per_char = self.y_pixels_per_char

    def set_pixel(self, canvas: "Canvas", px: int, py: int, color: int) -> None:
        """Set a marker character at the given position."""
        # Convert pixel coords to character coords
        cx = px // self.x_pixels_per_char
        cy = py // self.y_pixels_per_char

        if not (0 <= cx < canvas.width and 0 <= cy < canvas.height):
            return

        canvas.grid[cy][cx] = ord(self.marker)
        canvas.colors[cy][cx] = color


class Canvas:
    _SUPERSAMPLE: int = 8

    def __init__(
        self,
        width: int = 80,
        height: int = 24,
        x_min: float = 0.0,
        x_max: float = 1.0,
        y_min: float = 0.0,
        y_max: float = 1.0,
        style: Optional[PlotStyle] = None,
        x_flip: bool = False,
        y_flip: bool = False,
        x_scale: Callable[[float], float] = lambda x: x,
        y_scale: Callable[[float], float] = lambda y: y,
    ):
        # Display dimensions
        self.width = width
        self.height = height
        self.x_pixels_per_char: int = 1
        self.y_pixels_per_char: int = 1
        self.x_scale = x_scale
        self.y_scale = y_scale

        # Data bounds (respect scaling)
        self.x_min = self.x_scale(x_min)
        self.x_max = self.x_scale(x_max)
        if self.x_min > self.x_max:
            self.x_min, self.x_max = self.x_max, self.x_min

        self.y_min = self.y_scale(y_min)
        self.y_max = self.y_scale(y_max)
        if self.y_min > self.y_max:
            self.y_min, self.y_max = self.y_max, self.y_min

        self.x_range = self.x_max - self.x_min or 1e-9
        self.y_range = self.y_max - self.y_min or 1e-9

        # Flips
        self.x_flip = x_flip
        self.y_flip = y_flip

        # Style determines pixel dimensions and how to draw
        self.style = style or LineStyle()
        self.style.adjust_grid(self)

        # Calculate pixel dimensions based on style
        self.pixel_width = width * self.x_pixels_per_char
        self.pixel_height = height * self.y_pixels_per_char

        # Create grids
        self.grid = [[0x2800] * width for _ in range(height)]
        self.colors = [[0] * width for _ in range(height)]

    def x_to_pixel(self, x: float) -> float:
        """Convert data x coordinate to pixel space"""
        x_scaled = self.x_scale(x)
        normalized = (x_scaled - self.x_min) / self.x_range  # 0 to 1
        if self.x_flip:
            normalized = 1 - normalized
        return normalized * self.pixel_width

    def y_to_pixel(self, y: float) -> float:
        """Convert data y coordinate to pixel space"""
        y_scaled = self.y_scale(y)
        normalized = (y_scaled - self.y_min) / self.y_range
        # Y grows down in screen space, so `1-` by default
        normalized = normalized if self.y_flip else 1 - normalized
        return normalized * self.pixel_height

    def set_pixel(self, x: float, y: float, color: int):
        """Set a pixel at data coordinates."""
        px = int(self.x_to_pixel(x))
        py = int(self.y_to_pixel(y))
        self.style.set_pixel(self, px, py, color)

    def _draw_bresenham_segment(self, px1: int, py1: int, px2: int, py2: int, color: int):
        """Draws a single line segment using Bresenham given INTEGER pixel coordinates."""

        dx = abs(px2 - px1)
        dy = abs(py2 - py1)
        sx = 1 if px1 < px2 else -1
        sy = 1 if py1 < py2 else -1
        err = dx - dy

        pixels = set()
        px_curr, py_curr = px1, py1

        while True:
            pixels.add((px_curr, py_curr))

            if px_curr == px2 and py_curr == py2:
                break

            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                px_curr += sx
            if e2 < dx:
                err += dx
                py_curr += sy

        # Set the actual pixels on the canvas
        for p_x, p_y in pixels:
            self.style.set_pixel(self, p_x, p_y, color)

    def line(self, x1: float, y1: float, x2: float, y2: float, color: int):
        """Draw a line between logical coordinates using Bresenham for smoother curves"""
        px1 = self.x_to_pixel(x1)
        py1 = self.y_to_pixel(y1)
        px2 = self.x_to_pixel(x2)
        py2 = self.y_to_pixel(y2)

        # Standard Bresenham at high resolution
        px1, py1 = int(round(px1)), int(round(py1))
        px2, py2 = int(round(px2)), int(round(py2))

        self._draw_bresenham_segment(px1, py1, px2, py2, color)

    def render(self) -> str:
        """Convert grid to string."""
        lines = []
        for row in range(self.height):
            line = ""
            for col in range(self.width):
                char = chr(self.grid[row][col])
                line += ColorType(self.colors[row][col]).apply(char)
            lines.append(line)
        return "\n".join(lines)
