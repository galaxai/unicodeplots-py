# UnicodePlots-py

Unicode plotting library designed for use in python.

> [!WARNING]
> Library is not in development.

# Supported backends

- [x] python
> Support for other backends will come very late
- [ ] numpy
- [ ] pytorch
- [ ] tinygrad

# Inference

## Lineplot examples

### Example 1 – basic line plot
```python
Lineplot([-1, 2, 3, 7], [-1, 2, 9, 4]).plot()
```
![Lineplot](media/img1.png)

### Example 2 – sine and cosine series
```python
x_vals = [x / 100 for x in range(-310, 620)]
Lineplot(x=x_vals, y=[math.sin, math.cos]).plot()
```
![SinCos](media/img2.png)

### Example 3 – scatter cloud
```python
seed(42)
x = [uniform(-5, 5) for _ in range(100)]
y = [uniform(-5, 5) for _ in range(100)]

Lineplot(x, y).plot()
```
![Scatter](media/img3.png)

### Example 4 – multi-series scatter with markers
```python
seed(42)
x = [uniform(-5, 5) for _ in range(100)]
y = [uniform(-5, 5) for _ in range(100)]
x1 = [uniform(-5, 5) for _ in range(100)]
y1 = [uniform(-5, 5) for _ in range(100)]

plot = Lineplot(
    x=[x, x1],
    y=[y, y1],
)

plot.plot(scatter=True,marker=["*", "x"])
```
![Scatter2](media/img4.png)

## imageplot (Imageplot)
>If your terminal supports the kitty graphics protocol, you may need to set the environment variable ASCII=1
```python
Imageplot("media/monarch.png").render()
```
![Imageplot](media/imageplot.png)
## It also support kitty image protocol
![ImageKitty](media/imagekitty.png)
### To come
> stairs (Staircase Plot) \
> barplot (Bar Plot - horizontal) \
> histogram (Histogram - horizontal / vertical) \
> boxplot (Box Plot - horizontal) \
> densityplot (Density Plot) \
> contourplot (Contour Plot) \
> heatmap (Heatmap Plot) \


# Documentation
> TODO

## Installation

```bash
uv pip install git+https://github.com/GalaxAI/unicodeplot-py.git
```

Inspired by [UnicodePlots.jl](https://github.com/Evizero/UnicodePlots.jl)

# License
This code is free to use under the terms of the MIT license.
