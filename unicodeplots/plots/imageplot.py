import base64
import os
import sys
from io import BytesIO
from pathlib import Path
from random import random
from typing import Sequence, TypeAlias

# NOTE: note all SUPPORTED_TERMS were tested
SUPPORTED_TERMS = [
    "xterm-kitty",
    "xterm-ghostty",
    "WezTerm",
    "iTerm.app",
    "foot",
    "alacritty",
    "konsole",
    "contour",
    "Terminal.app",
    "rxvt-unicode-256color",
    "tmux-256color",
]

from PIL import Image
from PIL.Image import Image as PILImage

from unicodeplots.utils import time_execution
from unicodeplots.utils.tensor import TensorAdapter

Image2D: TypeAlias = list[list[int]]
Image3D: TypeAlias = list[list[list[int]]]
strImage: TypeAlias = str | Path | PILImage


def tensor_to_pil(data: TensorAdapter) -> Image:
    shape = data.shape
    mode = "RGB" if len(shape) == 3 and shape[2] == 3 else "L"
    height, width = shape[0], shape[1]
    flat_pixels = []
    for row in data:
        for pixel in row:
            pixel = tuple(map(int, pixel)) if mode == "RGB" else (int(pixel),) * 3  # Ensure RGB format
            flat_pixels.append(pixel)

    img = Image.new("RGB", size=(width, height))
    img.putdata(data=flat_pixels)
    return img


def create_kitty_sequence(img: PILImage) -> str:
    width, height = img.size
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_bytes = buffer.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")
    kitty_sequence = f"\033_Gf=100,a=T,t=d,X=0,Y=0,C=1,s={width},v={height};{img_base64}\033\\  "
    return kitty_sequence


class Imageplot:
    """
    Takes only one image
    Only available with PIL installed
    """

    def __init__(self, X: Image2D | Image3D | strImage, force_ascii=False, img_h: int = 24):
        self.X = X
        self.ascii = force_ascii
        self.img_h = img_h

    def render(self):
        tensor = self.parse_input()
        self.render_unicode(tensor) if self.ascii else self.render_kitty(tensor)

    def render_unicode(self, data: PILImage) -> None:
        resized_data = self.resize(data)
        img = self.unicode_encode(resized_data)
        for row in img:
            print(row)

    def resize(self, img: PILImage) -> PILImage:
        original_width, original_height = img.size
        aspect_ratio = original_height / original_width
        scale = 2 if self.ascii else 1  # Compensate for block aspect ratio
        new_width = int(self.img_h / aspect_ratio * scale)

        return img.resize((new_width, self.img_h))

    def render_kitty(self, data: PILImage):
        kitty_sequence = create_kitty_sequence(data)
        sys.stdout.write(kitty_sequence)

    def unicode_encode(self, image: PILImage) -> list[str]:
        rows = []
        width, height = image.size
        pixels = image.load()

        for y in range(height):
            row = ""
            for x in range(width):
                r, g, b = pixels[x, y]
                row += f"\033[48;2;{r};{g};{b}m \033[0m"
            rows.append(row)
        return rows

    def parse_input(self) -> TensorAdapter | PILImage:
        if isinstance(self.X, (str, PILImage, Path)):
            try:
                return load_image(self.X)
            except Exception as e:
                print(f"Error loading image: {e}")
                # Load error image bc i think its funny
                raise ValueError("Error loading image")
        else:
            tensor = TensorAdapter(self.X)
            return tensor_to_pil(tensor)


def load_image(path: str | Path) -> PILImage:
    img = Image.open(path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img


class ImageplotGrid:
    def __init__(
        self,
        images: Sequence[Image2D | Image3D | strImage],
        *,
        cols: int = 5,
        padding: int = 16,
    ):
        if not images:
            raise ValueError("ImageplotGrid requires at least one image.")
        self.images = list(images)
        self.cols = cols
        self.padding = max(0, padding)

    def render(self) -> None:
        pil_images = []
        for img in self.images:
            if isinstance(img, PILImage):
                pil_images.append(img)
            elif isinstance(img, (str, Path)):
                pil_images.append(load_image(img))
            else:  # Note this is really slow
                tensor = TensorAdapter(img)
                pil_images.append(tensor_to_pil(tensor))
        self.render_kittens(pil_images)

    def render_kittens(self, images: Sequence[PILImage]) -> None:
        x_offset = 0
        term_width = os.get_terminal_size().columns * 7
        rows, row = [], []
        for idx, img in enumerate(images):
            row.append(img)
            if x_offset + img.width >= term_width or len(row) >= self.cols:
                x_offset = 0
                rows.append(row)
                row = []
            else:
                x_offset += img.width + self.padding
        if row:
            rows.append(row)

        for row in rows:
            x_offset = 0
            for idx, img in enumerate(row):
                kitten = create_kitty_sequence(img).replace("C=0", "C=1")
                if idx == len(row) - 1:
                    kitten = kitten.replace("C=1", "C=0") + "\n"
                kitten = kitten.replace("X=0", f"X={x_offset}")
                x_offset += img.width + self.padding
                sys.stdout.write(kitten)
            sys.stdout.flush()


@time_execution
def test_grid_strimages():
    img = "media/monarch.png"
    ImageplotGrid([img] * 9, cols=3, padding=2).render()


@time_execution
def test_grid_mixed():
    img = "media/monarch.png"
    size = 256
    rgb = [[[random() * 255 for _ in range(3)] for _ in range(size)] for _ in range(size)]
    ImageplotGrid([img, rgb, img, rgb, rgb], cols=3, padding=2).render()


@time_execution
def test_imageplot_str():
    img = "media/monarch.png"
    Imageplot(img).render()


@time_execution
def test_imageplot_numeric():
    rgb = [[[random() * 255 for _ in range(3)] for _ in range(28)] for _ in range(28)]
    grayscale = [[random() * 255 for _ in range(28)] for _ in range(28)]

    Imageplot(rgb).render()
    Imageplot(grayscale).render()


if __name__ == "__main__":
    print(f"test_grid_strimages: {test_grid_strimages()}")
    print(f"test_grid_mixed: {test_grid_mixed()}")
    print(f"test_imageplot_str: {test_imageplot_str()}")
    print(f"test_imageplot_numeric: {test_imageplot_numeric()}")
