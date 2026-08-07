from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "public" / "favicon.ico"
SCALE = 16
CANVAS = 32 * SCALE
DEEP_BLUE = (18, 59, 93, 255)
INSPIRATION_TEAL = (52, 182, 168, 255)


def polygon(draw: ImageDraw.ImageDraw, points: list[tuple[float, float]], fill) -> None:
    draw.polygon(
        [(round(x * SCALE), round(y * SCALE)) for x, y in points],
        fill=fill,
    )


def draw_master_icon() -> Image.Image:
    image = Image.new("RGBA", (CANVAS, CANVAS), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)

    polygon(draw, [(4, 8.5), (8.5, 4.5), (11.5, 7.5), (6.5, 12), (3, 12)], INSPIRATION_TEAL)
    polygon(draw, [(4.5, 14.5), (9.5, 10.5), (12.5, 13.5), (7, 18), (3.5, 18)], INSPIRATION_TEAL)
    polygon(draw, [(4, 21), (10.5, 16.5), (14, 19.5), (6.5, 25), (3, 25)], INSPIRATION_TEAL)

    polygon(draw, [(14.5, 10), (21, 4), (28, 10), (23.5, 10), (21, 7.5), (18.5, 10)], DEEP_BLUE)
    polygon(draw, [(13.5, 11), (28.5, 11), (27, 14.5), (15, 14.5)], DEEP_BLUE)
    polygon(draw, [(12.5, 16), (28, 16), (26.5, 19.5), (14, 19.5)], DEEP_BLUE)
    polygon(draw, [(15, 21), (19.5, 22.5), (22, 20.5), (28.5, 27.5), (24, 27.5), (21.5, 24.5), (18.5, 27.5), (12.5, 27.5)], DEEP_BLUE)
    return image


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    draw_master_icon().save(
        OUTPUT,
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48)],
    )
    print("generated Hualing geometric mark favicon.ico: 16x16, 32x32, 48x48")


if __name__ == "__main__":
    main()
