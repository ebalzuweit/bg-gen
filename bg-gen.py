import colorsys
import os

from argparse import ArgumentParser
from pathlib import Path
from PIL import Image
from rich import print


def bg_centered_crop(filepath: str, config):
    # process input image
    center = (config.width // 2, config.height // 2)
    input = Image.open(filepath)
    dominant_color = get_dominant_color(input)
    if input.width > input.height:
        ratio = (config.width * 0.45) / input.width
    else:
        ratio = (config.height * 0.7) / input.height
    crop_size = (int(input.width * ratio), int(input.height * ratio))
    crop_offset = (
        center[0] - crop_size[0] // 2,
        center[1] - crop_size[1] // 2,
    )
    crop_position = (
        crop_offset[0],
        crop_offset[1],
        crop_offset[0] + crop_size[0],
        crop_offset[1] + crop_size[1],
    )

    # build output image
    output = Image.new(
        mode="RGB", size=(config.width, config.height), color=dominant_color
    )
    if args.border > 0:
        border_position = (
            crop_position[0] - args.border,
            crop_position[1] - args.border,
            crop_position[2] + args.border,
            crop_position[3] + args.border,
        )
        border_size = (
            border_position[2] - border_position[0],
            border_position[3] - border_position[1],
        )
        output.paste(
            Image.new(mode="RGB", size=border_size, color=(255, 255, 255)),
            border_position,
        )
    output.paste(input.resize(crop_size), crop_position)

    # save to file
    filename = Path(filepath).stem
    savepath = os.path.join(config.output, f"{filename}.png")
    output.save(savepath)
    print(f"Wrote {savepath}")


def clamp(x, minimum, maximum):
    return max(minimum, min(maximum, x))


def get_dominant_color(image: Image):
    img = image.copy()
    img = img.convert("RGB")
    img = img.resize((1, 1), resample=0)
    dominant_color = img.getpixel((0, 0))
    hsv = colorsys.rgb_to_hsv(
        dominant_color[0] / 255, dominant_color[1] / 255, dominant_color[2] / 255
    )
    rgb = colorsys.hsv_to_rgb(hsv[0], clamp(hsv[1], 0.25, 0.45), clamp(hsv[2], 0.65, 0.85))
    dominant_color = (int(rgb[0] * 255), int(rgb[1] * 255), int(rgb[2] * 255))
    return dominant_color


def is_image(filepath: str) -> bool:
    try:
        with Image.open(filepath):
            return True
    except OSError:
        return False


def get_args():
    parser = ArgumentParser(
        prog="bg-gen", description="simple image generator for backgrounds"
    )
    parser.add_argument("input", help="Directory with source images")
    parser.add_argument("output", help="Directory for output images")
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--height", type=int, default=1080)
    parser.add_argument("--border", type=int, default=8)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = get_args()
    files = list(map(lambda f: os.path.join(args.input, f), os.listdir(args.input)))
    image_files = list(filter(is_image, files))
    print(f"Found {len(image_files)} images in directory.")
    for f in image_files:
        bg_centered_crop(f, args)
