from pathlib import Path
import re
import struct
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
BRANDING = ROOT / "src" / "assets" / "branding"
SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"

ASSETS = {
    "icon": BRANDING / "cloud-gallery-icon.svg",
    "horizontal": BRANDING / "cloud-gallery-logo-horizontal.svg",
    "mono": BRANDING / "cloud-gallery-icon-mono.svg",
}
FAVICON_SVG = ROOT / "public" / "favicon.svg"
FAVICON_ICO = ROOT / "public" / "favicon.ico"
INDEX_HTML = ROOT / "index.html"
BRAND_COLORS = ["#397BFF", "#7C4DFF"]
COLORED_ASSETS = {
    "icon": ASSETS["icon"],
    "horizontal": ASSETS["horizontal"],
    "favicon": FAVICON_SVG,
}


def parse_svg(path: Path) -> ET.Element:
    return ET.parse(path).getroot()


def ico_sizes(path: Path) -> list[tuple[int, int]]:
    data = path.read_bytes()
    reserved, image_type, count = struct.unpack_from("<HHH", data, 0)
    if (reserved, image_type) != (0, 1):
        raise AssertionError("not a valid icon directory")
    sizes = []
    for index in range(count):
        width, height = struct.unpack_from("<BB", data, 6 + index * 16)
        sizes.append((width or 256, height or 256))
    return sizes


class LogoAssetsTest(unittest.TestCase):
    def test_all_expected_svg_assets_exist_and_are_valid_xml(self):
        paths = {**ASSETS, "favicon": FAVICON_SVG}
        for name, path in paths.items():
            with self.subTest(asset=name):
                self.assertTrue(path.is_file(), f"missing {path}")
                self.assertEqual(parse_svg(path).tag, f"{{{SVG_NS}}}svg")

    def test_each_svg_has_accessible_title(self):
        paths = {**ASSETS, "favicon": FAVICON_SVG}
        for name, path in paths.items():
            with self.subTest(asset=name):
                root = parse_svg(path)
                title = root.find(f"{{{SVG_NS}}}title")
                self.assertIsNotNone(title)
                self.assertTrue((title.text or "").strip())
                self.assertEqual(root.attrib.get("role"), "img")
                self.assertEqual(root.attrib.get("aria-labelledby"), title.attrib.get("id"))

    def test_assets_have_explicit_viewboxes_and_no_page_background(self):
        expected = {
            "icon": "0 0 64 64",
            "horizontal": "0 0 360 88",
            "mono": "0 0 64 64",
            "favicon": "0 0 32 32",
        }
        paths = {**ASSETS, "favicon": FAVICON_SVG}
        for name, path in paths.items():
            with self.subTest(asset=name):
                root = parse_svg(path)
                self.assertEqual(root.attrib.get("viewBox"), expected[name])
                self.assertNotIn("style", root.attrib)
                for rect in root.findall(f".//{{{SVG_NS}}}rect"):
                    self.assertNotEqual(rect.attrib.get("width"), "100%")

    def test_svg_files_are_self_contained(self):
        paths = {**ASSETS, "favicon": FAVICON_SVG}
        forbidden = ("<image", "<script", "@import")
        for name, path in paths.items():
            with self.subTest(asset=name):
                source = path.read_text(encoding="utf-8")
                for token in forbidden:
                    self.assertNotIn(token, source)
                root = parse_svg(path)
                for element in root.iter():
                    for attribute in ("href", f"{{{XLINK_NS}}}href"):
                        reference = element.attrib.get(attribute)
                        if reference is not None:
                            self.assertTrue(reference.startswith("#"), f"external reference: {reference}")

    def test_colored_assets_use_new_blue_violet_palette(self):
        ids = set()
        for name, path in COLORED_ASSETS.items():
            with self.subTest(asset=name):
                root = parse_svg(path)
                gradients = root.findall(f".//{{{SVG_NS}}}linearGradient")
                self.assertEqual(len(gradients), 1)
                gradient_id = gradients[0].attrib["id"]
                self.assertNotIn(gradient_id, ids)
                ids.add(gradient_id)
                stops = gradients[0].findall(f"{{{SVG_NS}}}stop")
                self.assertEqual([stop.attrib["stop-color"] for stop in stops], BRAND_COLORS)

    def test_favicon_svg_uses_simplified_white_symbol(self):
        root = parse_svg(FAVICON_SVG)
        symbol = root.find(f".//{{{SVG_NS}}}path[@data-part='cloud-picture-symbol']")
        self.assertIsNotNone(symbol)
        self.assertEqual(symbol.attrib.get("fill"), "#FFFFFF")
        self.assertEqual(root.findall(f".//{{{SVG_NS}}}circle"), [])

    def test_mono_asset_uses_current_color_without_brand_colors(self):
        source = ASSETS["mono"].read_text(encoding="utf-8")
        root = parse_svg(ASSETS["mono"])
        self.assertIn("currentColor", source)
        self.assertEqual(root.findall(f".//{{{SVG_NS}}}linearGradient"), [])
        self.assertNotRegex(source, re.compile(r"#[0-9a-fA-F]{3,8}"))

    def test_horizontal_logo_contains_approved_copy(self):
        root = parse_svg(ASSETS["horizontal"])
        copy = ["".join(node.itertext()).strip() for node in root.findall(f".//{{{SVG_NS}}}text")]
        self.assertEqual(copy, ["智能协同云图库", "海量免费图片获取平台"])

    def test_ico_contains_required_sizes(self):
        self.assertEqual(ico_sizes(FAVICON_ICO), [(16, 16), (32, 32), (48, 48)])

    def test_index_prefers_svg_and_keeps_ico_fallback(self):
        source = INDEX_HTML.read_text(encoding="utf-8")
        svg_link = '<link rel="icon" type="image/svg+xml" href="/favicon.svg">'
        ico_link = '<link rel="icon" href="/favicon.ico" sizes="any">'
        self.assertIn(svg_link, source)
        self.assertIn(ico_link, source)
        self.assertLess(source.index(svg_link), source.index(ico_link))
        self.assertIn("<title>智能协同云图库</title>", source)


if __name__ == "__main__":
    unittest.main()
