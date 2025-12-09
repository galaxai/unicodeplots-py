import math
import os
from random import seed, uniform

import pytest

from unicodeplots.plots import Imageplot, Lineplot
from unicodeplots.plots.imageplot import SUPPORTED_TERMS

# The first time you run this, pytest-snapshot will save 'output'
# Subsequent runs will compare 'output' to the saved version.


def test_lineplot_example_01(snapshot):
    """
    Tests the README example of a simple line plot.
    """
    x = [-1, 2, 3, 7]
    y = [-1, 2, 9, 4]
    plot = Lineplot(x, y)
    output = plot.plot()

    snapshot.assert_match(output, "Lineplot_Example_01.txt")


def test_lineplot_example_02(snapshot):
    x_vals = [x / 100 for x in range(-310, 620)]
    plot = Lineplot(x=x_vals, y=[math.sin, math.cos])
    output = plot.plot()
    snapshot.assert_match(output, "Lineplot_Example_02.txt")


def test_lineplot_example_03(snapshot):
    seed(42)
    x = [uniform(-5, 5) for _ in range(100)]
    y = [uniform(-5, 5) for _ in range(100)]

    plot = Lineplot(x, y)
    output = plot.plot(scatter=True)
    snapshot.assert_match(output, "Lineplot_Example_03.txt")


def test_lineplot_example_04(snapshot):
    seed(42)
    x = [uniform(-5, 5) for _ in range(100)]
    y = [uniform(-5, 5) for _ in range(100)]
    x1 = [uniform(-5, 5) for _ in range(100)]
    y1 = [uniform(-5, 5) for _ in range(100)]

    plot = Lineplot(
        x=[x, x1],
        y=[y, y1],
    )
    output = plot.plot(
        scatter=True,
        marker=["*", "x"],
    )
    snapshot.assert_match(output, "Lineplot_Example_04.txt")


def test_imageplot_example_01(snapshot, capsys):
    if os.environ.get("CI"):
        pytest.skip("Skipping Kitty protocol test in CI environment")

    term = os.environ.get("TERM", "")
    if term.lower() not in SUPPORTED_TERMS:
        pytest.skip("Terminal doesn't support Kitty protocol")

    # With kitty protocol
    Imageplot("media/monarch.png").render()
    captured = capsys.readouterr()
    snapshot.assert_match(captured.out, "Imageplot_Example_01.txt")


def test_imageplot_example_02(snapshot, capsys):
    # Without kitty protocol
    Imageplot("media/monarch.png", force_ascii=True).render()
    captured = capsys.readouterr()
    snapshot.assert_match(captured.out, "Imageplot_Example_02.txt")
