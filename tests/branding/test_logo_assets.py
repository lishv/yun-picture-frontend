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
    "icon": BRANDING / "hualing-cloud-icon.svg",
    "horizontal": BRANDING / "hualing-cloud-logo-horizontal.svg",
    "mono": BRANDING / "hualing-cloud-icon-mono.svg",
    "header": ROOT / "src" / "assets" / "logo.svg",
    "favicon": ROOT / "public" / "favicon.svg",
}
FAVICON_ICO = ROOT / "public" / "favicon.ico"
INDEX_HTML = ROOT / "index.html"
DEEP_BLUE = "#123B5D"
INSPIRATION_TEAL = "#34B6A8"


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


class HualingLogoAssetsTest(unittest.TestCase):
    def test_expected_svg_assets_exist_and_are_valid_xml(self):
        for name, path in ASSETS.items():
            with self.subTest(asset=name):
                self.assertTrue(path.is_file(), f"missing {path}")
                self.assertEqual(parse_svg(path).tag, f"{{{SVG_NS}}}svg")

    def test_each_svg_is_accessible_and_self_contained(self):
        for name, path in ASSETS.items():
            with self.subTest(asset=name):
                root = parse_svg(path)
                title = root.find(f"{{{SVG_NS}}}title")
                self.assertIsNotNone(title)
                self.assertTrue((title.text or "").strip())
                self.assertEqual(root.attrib.get("role"), "img")
                self.assertEqual(root.attrib.get("aria-labelledby"), title.attrib.get("id"))
                source = path.read_text(encoding="utf-8")
                for token in ("<image", "<script", "@import", "linearGradient", "radialGradient"):
                    self.assertNotIn(token, source)
                for element in root.iter():
                    for attribute in ("href", f"{{{XLINK_NS}}}href"):
                        reference = element.attrib.get(attribute)
                        if reference is not None:
                            self.assertTrue(reference.startswith("#"), reference)

    def test_colored_marks_use_only_deep_blue_and_inspiration_teal(self):
        for name in ("icon", "header", "favicon"):
            with self.subTest(asset=name):
                source = ASSETS[name].read_text(encoding="utf-8")
                colors = set(re.findall(r"#[0-9A-Fa-f]{6}", source))
                self.assertEqual(colors, {DEEP_BLUE, INSPIRATION_TEAL})
        horizontal = ASSETS["horizontal"].read_text(encoding="utf-8")
        self.assertIn(DEEP_BLUE, horizontal)
        self.assertIn(INSPIRATION_TEAL, horizontal)
        for old_color in ("#173B67", "#2B8EBF", "#168AAD", "#397BFF", "#7C4DFF"):
            self.assertNotIn(old_color, horizontal)

    def test_colored_assets_encode_geometric_hui_mark(self):
        for name in ("icon", "horizontal", "header", "favicon"):
            with self.subTest(asset=name):
                root = parse_svg(ASSETS[name])
                self.assertEqual(len(root.findall(f".//*[@data-part='silk-ribbon']")), 3)
                self.assertEqual(len(root.findall(f".//*[@data-part='meeting-roof']")), 1)
                self.assertEqual(len(root.findall(f".//*[@data-part='picture-plane']")), 2)
                self.assertEqual(len(root.findall(f".//*[@data-part='convergence']")), 1)

    def test_marks_are_solid_and_have_no_background_tile(self):
        for name in ("icon", "header", "favicon"):
            with self.subTest(asset=name):
                root = parse_svg(ASSETS[name])
                self.assertEqual(root.findall(f".//{{{SVG_NS}}}rect"), [])
                source = ASSETS[name].read_text(encoding="utf-8")
                self.assertNotIn("stroke=", source)
                for obsolete in ("open-canvas", "collaboration-stroke", "forming-stroke", "picture-frame"):
                    self.assertNotIn(obsolete, source)

    def test_assets_avoid_generic_or_ai_motifs(self):
        for name, path in ASSETS.items():
            with self.subTest(asset=name):
                source = path.read_text(encoding="utf-8").lower()
                for forbidden in ("spark", "star", "circuit", "robot", "magic", "mountain", "cloud-shape"):
                    self.assertNotIn(forbidden, source)

    def test_mono_asset_uses_current_color_only(self):
        source = ASSETS["mono"].read_text(encoding="utf-8")
        self.assertIn("currentColor", source)
        self.assertNotRegex(source, re.compile(r"#[0-9a-fA-F]{3,8}"))
        self.assertNotIn("white", source.lower())

    def test_horizontal_logo_contains_brand_hierarchy(self):
        root = parse_svg(ASSETS["horizontal"])
        copy = ["".join(node.itertext()).strip() for node in root.findall(f".//{{{SVG_NS}}}text")]
        self.assertEqual(copy, ["绘灵云", "图片协作平台"])

    def test_favicon_uses_compact_canvas_without_text(self):
        root = parse_svg(ASSETS["favicon"])
        self.assertEqual(root.attrib.get("viewBox"), "0 0 32 32")
        self.assertEqual(root.findall(f".//{{{SVG_NS}}}text"), [])

    def test_ico_contains_required_sizes(self):
        self.assertEqual(ico_sizes(FAVICON_ICO), [(16, 16), (32, 32), (48, 48)])

    def test_index_uses_new_favicons_and_brand_title(self):
        source = INDEX_HTML.read_text(encoding="utf-8")
        svg_link = '<link rel="icon" type="image/svg+xml" href="/favicon.svg">'
        ico_link = '<link rel="icon" href="/favicon.ico" sizes="any">'
        self.assertIn(svg_link, source)
        self.assertIn(ico_link, source)
        self.assertLess(source.index(svg_link), source.index(ico_link))
        self.assertIn("<title>绘灵云图片协作平台</title>", source)


if __name__ == "__main__":
    unittest.main()
