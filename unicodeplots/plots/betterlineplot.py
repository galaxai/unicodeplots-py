from typing import Optional, Sequence

from unicodeplots.canvas.ncanvas import Canvas, LineStyle, MarkerStyle
from unicodeplots.utils import ColorType


class Lineplot:
    def __init__(
        self,
        x=None,  # What is x
        y=None,  # What is y
    ):
        self.points = self._validate_input(x, y)
        self._compute_bounds()

    def plot(
        self,
        scatter=False,
        marker: list[str] = ["•"],
        colors: list[str] = ["BLUE", "GREEN", "RED"],
        canvas: Optional[Canvas] = None,
    ):
        print("Plotting lineplot")

        if isinstance(colors, str):
            colors = [colors]
        colors_codes: list[int] = [ColorType.from_string(color).value for color in colors]

        style = MarkerStyle(marker=marker[0]) if scatter else LineStyle()

        canvas = Canvas(
            width=80,  # can make this configurable later
            height=24,
            x_min=self.min_x,
            x_max=self.max_x,
            y_min=self.min_y,
            y_max=self.max_y,
            style=style,
        )

        for idx, line in enumerate(self.points):
            # Line
            if scatter:
                for i in range(len(line)):
                    x, y = line[i]
                    canvas.set_pixel(x, y, color=colors_codes[idx % len(colors_codes)])
            else:
                for i in range(1, len(line)):
                    x1, y1 = line[i - 1]
                    x2, y2 = line[i]
                    canvas.line(x1, y1, x2, y2, color=colors_codes[idx % len(colors_codes)])

        print(canvas.render())

    def _compute_bounds(self):
        x_values = [point[0] for line in self.points for point in line]
        y_values = [point[1] for line in self.points for point in line]
        self.min_x, self.max_x = min(x_values), max(x_values)
        self.min_y, self.max_y = min(y_values), max(y_values)

    def _validate_input(self, x, y) -> list[Sequence[tuple[int | float, int | float]]]:
        if x is None or y is None:
            raise ValueError("Both x and y are required")

        points: list[Sequence[tuple[int | float, int | float]]] = []

        # Checks if x = [x,x1] where x1 is a list[int] and y = [y,y1] where y1 is a list[int]
        if isinstance(x, (list, tuple)) and x and isinstance(x[0], (list, tuple)):
            if not isinstance(y, (list, tuple)) or len(x) != len(y):
                raise ValueError("When x is a list of lists, y must also be a list of same length")

            for x_arr, y_arr in zip(x, y):
                points.append(list(zip(x_arr, y_arr)))

        elif callable(y):  # x=list[int] y = math.sin
            points.append([(x_point, y(x_point)) for x_point in x])

        elif isinstance(y, (list, tuple)):
            if all(callable(item) for item in y):
                for y_fn in y:
                    points.append([(x_point, round(y_fn(x_point), 3)) for x_point in x])
            elif any(callable(item) for item in y):
                raise ValueError("Cannot mix callable and non-callable items in y")
            else:
                points.append(list(zip(x, y)))

        elif isinstance(y, (float, int)):
            points.append(list(zip(x, [y] * len(x))))
        else:
            raise ValueError("y must be callable, list, tuple, or number")
        if not points or all(len(line) == 0 for line in points):
            raise ValueError("Cannot create plot with no data points")
        return points


# Lineplot(data=[(0, 0), (1, 1), (2, 4)])

# Lineplot(x=[0, 1, 2], y=[0, 1, 4])

# Lineplot(x=[0, 1, 2], y=lambda x: x**2)

# Lineplot(x=list(range(10)), y=[math.sin, math.cos])

# Lineplot(x=list(range(10)), y=5)

# Lineplot(x=range(3), y=[lambda x: x, lambda x: x**2])

# try:
#     Lineplot(data=[])  # or
# except ValueError as e:
#     print(e)

# try:
#     Lineplot(x=[], y=[])
# except ValueError as e:
#     print(e)
if __name__ == "__main__":
    Lineplot(x=[-1, 2, 3, 7], y=[-1, 2, 9, 4]).plot()

    x_vals = [x / 100 for x in range(-310, 620)]
    import math
    from random import seed, uniform

    a = Lineplot(x=x_vals, y=[math.sin, math.cos]).plot()

    seed(42)
    x = [uniform(-5, 5) for _ in range(100)]
    y = [uniform(-5, 5) for _ in range(100)]
    # Lineplot(x=x, y=y).plot(scatter=True)
    x1 = [uniform(-5, 5) for _ in range(100)]
    y1 = [uniform(-5, 5) for _ in range(100)]
    line1 = list(zip(x, y))
    line2 = list(zip(x1, y1))
    # Lineplot(x=[x, x1], y=[y, y1]).plot(scatter=True)
