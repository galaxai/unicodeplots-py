import math

import pytest

from unicodeplots import Lineplot

# --- Test Cases ---
# (test_id, x_input, y_input, expected_output, expected_exception)
validate_input_cases = [
    ("missing_xy", None, None, None, ValueError),
    ("xy", [1, 2, 3], [1, 2, 3], [([1, 2, 3], [1, 2, 3])], None),
    ("y_callable", [1, 2, 3], lambda x: x * x, [([1, 2, 3], [1, 4, 9])], None),
    (
        "multiple_xy_sequences",
        [[1, 2], [3, 4, 5]],
        [[10, 20], [30, 40, 50]],
        [([1, 2], [10, 20]), ([3, 4, 5], [30, 40, 50])],
        None,
    ),
    (
        "list_of_callables",
        [1, 2, 3],
        [lambda x: x * 10, lambda x: x * 5],
        [([1, 2, 3], [10, 20, 30]), ([1, 2, 3], [5, 10, 15])],
        None,
    ),
    ("constant_y", [1, 2, 3], 7, [([1, 2, 3], [7, 7, 7])], None),
    ("mixed_callable_error", [1, 2], [lambda x: x, 2], None, ValueError),
]

# Structure:
# (description, x_range_params, y_generator_func, yscale_func)
# x_range_params could be (start, stop) for range()
# y_generator_func takes x and returns y
lineplot_data_and_scale_cases = [
    ("Linear scale, Y=2^X, X=[1..10]", (1, 11), lambda x: 2**x, None),
    ("Log2 scale, Y=2^X, X=[1..10]", (1, 11), lambda x: 2**x, math.log2),
    ("Linear scale, Y=3*X, X=[0..5]", (0, 6), lambda x: 3 * x, None),
    ("Log10 scale, Y=10^X, X=[1..4]", (1, 5), lambda x: 10**x, math.log10),
    ("Linear scale, Y=X^2, X=[-3..3]", (-3, 4), lambda x: x**2, None),
    (
        "Log scale (base e), Y=e^X, X=[1..5]",
        (1, 6),
        lambda x: math.exp(x),
        math.log,
    ),
]


@pytest.mark.parametrize(
    "test_id, x_input, y_input, expected_output, expected_exception",
    validate_input_cases,
    ids=[c[0] for c in validate_input_cases],
)
def test_validate_input_cases(test_id, x_input, y_input, expected_output, expected_exception):
    """
    Tests the Lineplot._validate_input helper with various combinations of inputs.
    """
    # Create a minimal Lineplot instance to call the helper method.
    plot = Lineplot([0, 1], [0, 1])

    if expected_exception:
        with pytest.raises(expected_exception):
            plot._validate_input(x_input, y_input)
        return

    # pylint: disable=protected-access
    actual_output = plot._validate_input(x_input, y_input)

    assert len(actual_output) == len(expected_output)

    for i, (actual_line, expected_line) in enumerate(zip(actual_output, expected_output)):
        actual_x = [point[0] for point in actual_line]
        actual_y = [point[1] for point in actual_line]
        expected_x, expected_y = expected_line

        assert actual_x == pytest.approx(expected_x), f"X-coordinates mismatch for line {i}"
        assert actual_y == pytest.approx(expected_y), f"Y-coordinates mismatch for line {i}"


@pytest.mark.parametrize(
    "description, x_range_params, y_generator_func, yscale_func",
    lineplot_data_and_scale_cases,
    ids=[case[0] for case in lineplot_data_and_scale_cases],
)
def test_lineplot_data_and_scale(
    description,
    x_range_params,
    y_generator_func,
    yscale_func,
    monkeypatch,
):
    """
    Tests Lineplot with various data generation methods and verifies that y-scale
    is delegated to the Canvas when plotting instead of affecting the stored bounds.
    """
    # 1. Generate Data based on parameters
    x_start, x_stop = x_range_params
    X_gen = list(range(x_start, x_stop))

    if not X_gen:
        pytest.skip(f"Skipping test '{description}' due to empty X data generation.")
        return  # For clarity

    Y_gen = [y_generator_func(x) for x in X_gen]

    # 2. Calculate Expected X/Y Min/Max from generated data
    expected_min_x = min(X_gen)
    expected_max_x = max(X_gen)
    expected_min_y = min(Y_gen)
    expected_max_y = max(Y_gen)

    # 3. Instantiate Lineplot with raw data
    plot = Lineplot(X_gen, Y_gen)

    # 4. Assertions on stored bounds (raw values)
    assert plot.min_x == expected_min_x, f"Failed min_x check for {description}"
    assert plot.max_x == expected_max_x, f"Failed max_x check for {description}"
    assert plot.min_y == pytest.approx(expected_min_y), f"Failed min_y check for {description}"
    assert plot.max_y == pytest.approx(expected_max_y), f"Failed max_y check for {description}"

    # 5. Ensure the provided y_scale function is passed through to Canvas when plotting
    captured_canvas_kwargs = {}

    class DummyCanvas:  # pragma: no cover - simple test double
        def __init__(self, *args, **kwargs):
            captured_canvas_kwargs.update(kwargs)

        def line(self, *args, **kwargs):
            return None

        def set_pixel(self, *args, **kwargs):
            return None

        def render(self):
            return "rendered"

    monkeypatch.setattr("unicodeplots.plots.lineplot.Canvas", DummyCanvas)

    y_scale_callable = yscale_func or (lambda value: value)
    render_output = plot.plot(y_scale=y_scale_callable)

    assert render_output == "rendered"
    assert captured_canvas_kwargs["y_scale"] is y_scale_callable
    assert captured_canvas_kwargs["y_min"] == pytest.approx(plot.min_y)
    assert captured_canvas_kwargs["y_max"] == pytest.approx(plot.max_y)
