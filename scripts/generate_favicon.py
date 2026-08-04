from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public" / "favicon.ico"
SCALE = 8
CANVAS = 48 * SCALE
BLUE = (57, 123, 255, 255)
VIOLET = (124, 77, 255, 255)


def interpolate(start: int, end: int, ratio: float) -> int:
    return round(start + (end - start) * ratio)


def draw_master_icon() -> Image.Image:
    gradient = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    pixels = gradient.load()
    denominator = 2 * (CANVAS - 1)
    for y in range(CANVAS):
        for x in range(CANVAS):
            ratio = (x + y) / denominator
            pixels[x, y] = tuple(
                interpolate(BLUE[channel], VIOLET[channel], ratio) for channel in range(4)
            )

    background_mask = Image.new("L", (CANVAS, CANVAS), 0)
    mask_draw = ImageDraw.Draw(background_mask)
    margin = SCALE
    mask_draw.rounded_rectangle(
        (margin, margin, CANVAS - margin - 1, CANVAS - margin - 1),
        radius=11 * SCALE,
        fill=255,
    )

    image = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    image.alpha_composite(Image.composite(gradient, Image.new("RGBA", gradient.size), background_mask))

    symbol_mask = Image.new("L", (CANVAS, CANVAS), 0)
    symbol = ImageDraw.Draw(symbol_mask)
    symbol.ellipse((8 * SCALE, 20 * SCALE, 28 * SCALE, 39 * SCALE), fill=255)
    symbol.ellipse((14 * SCALE, 12 * SCALE, 38 * SCALE, 39 * SCALE), fill=255)
    symbol.ellipse((27 * SCALE, 18 * SCALE, 43 * SCALE, 39 * SCALE), fill=255)
    symbol.rectangle((13 * SCALE, 27 * SCALE, 39 * SCALE, 39 * SCALE), fill=255)
    symbol.polygon(
        [
            (15 * SCALE, 36 * SCALE),
            (22 * SCALE, 29 * SCALE),
            (27 * SCALE, 34 * SCALE),
            (31 * SCALE, 30 * SCALE),
            (39 * SCALE, 38 * SCALE),
            (15 * SCALE, 38 * SCALE),
        ],
        fill=0,
    )

    white = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 255))
    image.alpha_composite(Image.composite(white, Image.new("RGBA", white.size), symbol_mask))
    return image


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    master = draw_master_icon()
    master.save(
        OUTPUT,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
    )
    print("generated public/favicon.ico: 16x16, 32x32, 48x48")


if __name__ == "__main__":
    main()
