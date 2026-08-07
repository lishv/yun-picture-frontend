# 绘灵云正式品牌 Logo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用正式的“协作画框”视觉系统完整替换旧云图库品牌资源，并同步更新页头 Logo、SVG favicon 和包含 16×16、32×32、48×48 子图的真实 ICO。

**Architecture:** 三个正式品牌 SVG、页头入口 Logo 和 favicon 共享海军蓝、湖蓝及交叠图片卡片几何，但 favicon 使用更粗、更少细节的专用图形。Pillow 脚本以高分辨率抗锯齿方式重复生成多尺寸 ICO；Python 契约测试验证资源内容、旧文件清理、ICO 目录、HTML 接入和品牌文案。

**Tech Stack:** SVG、HTML5、Python 3、Pillow 12.3.0、`unittest`、`xml.etree.ElementTree`、`struct`

---

## 文件结构

- Create: `src/assets/branding/hualing-cloud-icon.svg`：正式彩色图标。
- Create: `src/assets/branding/hualing-cloud-icon-mono.svg`：使用 `currentColor` 的单色图标。
- Create: `src/assets/branding/hualing-cloud-logo-horizontal.svg`：包含“绘灵云／图片协作平台”的横版字标。
- Modify: `src/assets/logo.svg`：当前 `GlobalHeader.vue` 直接使用的新版图标副本。
- Modify: `public/favicon.svg`：浏览器标签页专用简化图标。
- Modify: `public/favicon.ico`：包含 16×16、32×32、48×48 子图的真实 ICO。
- Modify: `scripts/generate_favicon.py`：可重复生成新版 ICO。
- Modify: `tests/branding/test_logo_assets.py`：新版品牌契约测试。
- Verify: `index.html`：继续优先引用 SVG favicon 并保留 ICO fallback。
- Delete after verification: `src/assets/branding/cloud-gallery-icon.svg`。
- Delete after verification: `src/assets/branding/cloud-gallery-icon-mono.svg`。
- Delete after verification: `src/assets/branding/cloud-gallery-logo-horizontal.svg`。

### Task 1: 将资源测试切换为“绘灵云”契约

**Files:**
- Modify: `tests/branding/test_logo_assets.py`

- [ ] **Step 1: 用新版测试完整替换旧测试内容**

```python
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
OLD_ASSETS = [
    BRANDING / "cloud-gallery-icon.svg",
    BRANDING / "cloud-gallery-icon-mono.svg",
    BRANDING / "cloud-gallery-logo-horizontal.svg",
]
FAVICON_ICO = ROOT / "public" / "favicon.ico"
INDEX_HTML = ROOT / "index.html"
NAVY = "#173B67"
TEAL = "#2B8EBF"


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
                for token in ("<image", "<script", "@import", "linearGradient"):
                    self.assertNotIn(token, source)
                for element in root.iter():
                    for attribute in ("href", f"{{{XLINK_NS}}}href"):
                        reference = element.attrib.get(attribute)
                        if reference is not None:
                            self.assertTrue(reference.startswith("#"), reference)

    def test_colored_assets_use_formal_brand_palette(self):
        for name in ("icon", "horizontal", "header", "favicon"):
            with self.subTest(asset=name):
                source = ASSETS[name].read_text(encoding="utf-8")
                self.assertIn(NAVY, source)
                self.assertIn(TEAL, source)
                self.assertNotIn("#397BFF", source)
                self.assertNotIn("#7C4DFF", source)

    def test_assets_use_overlapping_frame_symbol_without_ai_motifs(self):
        for name in ("icon", "horizontal", "header", "favicon"):
            with self.subTest(asset=name):
                root = parse_svg(ASSETS[name])
                frames = root.findall(f".//{{{SVG_NS}}}rect[@data-part='picture-frame']")
                self.assertEqual(len(frames), 2)
                source = ASSETS[name].read_text(encoding="utf-8").lower()
                for forbidden in ("spark", "star", "circuit", "robot", "magic"):
                    self.assertNotIn(forbidden, source)

    def test_mono_asset_uses_only_current_color_and_white(self):
        source = ASSETS["mono"].read_text(encoding="utf-8")
        self.assertIn("currentColor", source)
        self.assertNotRegex(source, re.compile(r"#[0-9a-fA-F]{3,8}"))

    def test_horizontal_logo_contains_brand_hierarchy(self):
        root = parse_svg(ASSETS["horizontal"])
        copy = ["".join(node.itertext()).strip() for node in root.findall(f".//{{{SVG_NS}}}text")]
        self.assertEqual(copy, ["绘灵云", "图片协作平台"])

    def test_favicon_uses_compact_canvas_without_text(self):
        root = parse_svg(ASSETS["favicon"])
        self.assertEqual(root.attrib.get("viewBox"), "0 0 32 32")
        self.assertEqual(root.findall(f".//{{{SVG_NS}}}text"), [])
        self.assertEqual(len(root.findall(f".//{{{SVG_NS}}}rect[@data-part='picture-frame']")), 2)

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

    def test_old_brand_assets_are_removed(self):
        self.assertEqual([path for path in OLD_ASSETS if path.exists()], [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试并确认新资源缺失、旧资源未删除等预期失败**

Run:

```bash
cd "D:/Dell/code/IntelliJ IDEA 2026.1.1/mycode/yun-picture/yun-picture-frontend" && "/d/Dell/code/anaconda/python.exe" tests/branding/test_logo_assets.py -v
```

Expected: FAIL，至少报告缺少 `hualing-cloud-icon.svg`，且 `test_old_brand_assets_are_removed` 失败。

### Task 2: 创建正式彩色图标并替换页头 Logo

**Files:**
- Create: `src/assets/branding/hualing-cloud-icon.svg`
- Modify: `src/assets/logo.svg`
- Test: `tests/branding/test_logo_assets.py`

- [ ] **Step 1: 创建 64×64 正式彩色图标**

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-labelledby="hualing-cloud-icon-title">
  <title id="hualing-cloud-icon-title">绘灵云图片协作平台</title>
  <rect x="2" y="2" width="60" height="60" rx="13" fill="#173B67" />
  <rect data-part="picture-frame" x="20" y="14" width="31" height="27" rx="5" fill="none" stroke="#FFFFFF" stroke-width="4" />
  <rect data-part="picture-frame" x="12" y="23" width="34" height="27" rx="5" fill="#FFFFFF" />
  <path d="M17 45 25.5 34l6 6.1 4.4-4.8L42 45H17Z" fill="#2B8EBF" />
</svg>
```

- [ ] **Step 2: 用相同内容替换页头入口 `src/assets/logo.svg`，仅更换可访问 ID 以避免内联冲突**

将 `title` ID 改为 `hualing-header-logo-title`，并同步修改根元素的 `aria-labelledby`；其他几何与颜色保持一致。

- [ ] **Step 3: 解析两个 SVG**

Run:

```bash
cd "D:/Dell/code/IntelliJ IDEA 2026.1.1/mycode/yun-picture/yun-picture-frontend" && "/d/Dell/code/anaconda/python.exe" -c "import xml.etree.ElementTree as ET; ET.parse('src/assets/branding/hualing-cloud-icon.svg'); ET.parse('src/assets/logo.svg'); print('brand and header icons: valid')"
```

Expected: `brand and header icons: valid`。

### Task 3: 创建单色与横版品牌 Logo

**Files:**
- Create: `src/assets/branding/hualing-cloud-icon-mono.svg`
- Create: `src/assets/branding/hualing-cloud-logo-horizontal.svg`
- Test: `tests/branding/test_logo_assets.py`

- [ ] **Step 1: 创建单色图标**

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-labelledby="hualing-cloud-mono-title">
  <title id="hualing-cloud-mono-title">绘灵云单色图标</title>
  <rect x="2" y="2" width="60" height="60" rx="13" fill="currentColor" />
  <rect x="20" y="14" width="31" height="27" rx="5" fill="none" stroke="white" stroke-width="4" />
  <rect x="12" y="23" width="34" height="27" rx="5" fill="white" />
  <path d="M17 45 25.5 34l6 6.1 4.4-4.8L42 45H17Z" fill="currentColor" />
</svg>
```

- [ ] **Step 2: 创建 360×88 横版 Logo**

横版 SVG 使用海军蓝底板、两个 `data-part="picture-frame"` 画框、湖蓝山形，并加入两段文字：

```svg
<text x="92" y="36" fill="#182433" font-family="Inter, 'PingFang SC', 'Microsoft YaHei', sans-serif" font-size="28" font-weight="700">绘灵云</text>
<text x="93" y="60" fill="#667789" font-family="Inter, 'PingFang SC', 'Microsoft YaHei', sans-serif" font-size="14" font-weight="400" letter-spacing="2">图片协作平台</text>
```

根 `viewBox` 为 `0 0 360 88`，图标放置于 `translate(10 12)`，使用唯一可访问 ID `hualing-cloud-horizontal-title`。

- [ ] **Step 3: 运行测试观察剩余失败仅来自 favicon、ICO 和旧资源**

Run:

```bash
cd "D:/Dell/code/IntelliJ IDEA 2026.1.1/mycode/yun-picture/yun-picture-frontend" && "/d/Dell/code/anaconda/python.exe" tests/branding/test_logo_assets.py -v
```

Expected: 正式品牌 SVG、颜色、横版文案通过；favicon、ICO 或旧资源清理测试仍失败。

### Task 4: 完整替换 `public` 浏览器品牌资源

**Files:**
- Modify: `public/favicon.svg`
- Modify: `scripts/generate_favicon.py`
- Modify: `public/favicon.ico`
- Test: `tests/branding/test_logo_assets.py`

- [ ] **Step 1: 用专用 32×32 图形覆盖 `public/favicon.svg`**

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" role="img" aria-labelledby="hualing-favicon-title">
  <title id="hualing-favicon-title">绘灵云图片协作平台</title>
  <rect x="1" y="1" width="30" height="30" rx="7" fill="#173B67" />
  <rect data-part="picture-frame" x="11" y="7" width="15" height="13" rx="2.5" fill="none" stroke="#FFFFFF" stroke-width="2.2" />
  <rect data-part="picture-frame" x="6" y="12" width="17" height="14" rx="2.5" fill="#FFFFFF" />
  <path d="m8.5 23 4.3-5.4 3.1 3.1 2.3-2.5 3.1 4.8H8.5Z" fill="#2B8EBF" />
</svg>
```

- [ ] **Step 2: 重写 `scripts/generate_favicon.py`**

脚本使用 Pillow 创建 384×384 母版：透明画布、海军蓝圆角底板、白色后景描边画框、白色前景画框和湖蓝山形。用 `Image.Resampling.LANCZOS` 的 Pillow ICO 保存能力写出：

```python
master.save(
    output,
    format="ICO",
    sizes=[(16, 16), (32, 32), (48, 48)],
)
```

脚本必须通过 `Path(__file__).resolve().parents[1] / "public" / "favicon.ico"` 定位输出，并打印：

```text
generated 绘灵云 favicon.ico: 16x16, 32x32, 48x48
```

绘制坐标按 32 单位设计后乘以 12：底板 `(1,1,31,31)`、后框 `(11,7,26,20)`、前框 `(6,12,23,26)`、山形点 `(8.5,23),(12.8,17.6),(15.9,20.7),(18.2,18.2),(21.3,23)`。

- [ ] **Step 3: 生成并覆盖 ICO**

Run:

```bash
cd "D:/Dell/code/IntelliJ IDEA 2026.1.1/mycode/yun-picture/yun-picture-frontend" && "/d/Dell/code/anaconda/python.exe" scripts/generate_favicon.py
```

Expected: `generated 绘灵云 favicon.ico: 16x16, 32x32, 48x48`。

- [ ] **Step 4: 检查真实 ICO 子图**

Run:

```bash
cd "D:/Dell/code/IntelliJ IDEA 2026.1.1/mycode/yun-picture/yun-picture-frontend" && "/d/Dell/code/anaconda/python.exe" -c "from PIL import Image; im=Image.open('public/favicon.ico'); print(sorted(im.info['sizes']))"
```

Expected: `[(16, 16), (32, 32), (48, 48)]`。

### Task 5: 验证 HTML 接入并安全移除旧资源

**Files:**
- Verify: `index.html:4-9`
- Delete: `src/assets/branding/cloud-gallery-icon.svg`
- Delete: `src/assets/branding/cloud-gallery-icon-mono.svg`
- Delete: `src/assets/branding/cloud-gallery-logo-horizontal.svg`
- Test: `tests/branding/test_logo_assets.py`

- [ ] **Step 1: 检查 `index.html` 已包含且按顺序声明以下内容**

```html
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="icon" href="/favicon.ico" sizes="any">
```

并确认：

```html
<title>绘灵云图片协作平台</title>
```

若已有且顺序正确，不修改该文件。

- [ ] **Step 2: 在删除前运行资源存在性和 XML 快速检查**

Run:

```bash
cd "D:/Dell/code/IntelliJ IDEA 2026.1.1/mycode/yun-picture/yun-picture-frontend" && "/d/Dell/code/anaconda/python.exe" -c "from pathlib import Path; import xml.etree.ElementTree as ET; required=[Path('src/assets/logo.svg'),Path('src/assets/branding/hualing-cloud-icon.svg'),Path('src/assets/branding/hualing-cloud-icon-mono.svg'),Path('src/assets/branding/hualing-cloud-logo-horizontal.svg'),Path('public/favicon.svg')]; assert all(p.is_file() for p in required); [ET.parse(p) for p in required]; print('new assets ready for cleanup')"
```

Expected: `new assets ready for cleanup`。只有该命令成功后才能执行下一步。

- [ ] **Step 3: 删除三个旧 cloud-gallery SVG**

删除：

```text
src/assets/branding/cloud-gallery-icon.svg
src/assets/branding/cloud-gallery-icon-mono.svg
src/assets/branding/cloud-gallery-logo-horizontal.svg
```

不得删除 `src/assets/logo.svg`、新版 `hualing-cloud-*` 或 `public` 目录资源。

- [ ] **Step 4: 运行完整契约测试**

Run:

```bash
cd "D:/Dell/code/IntelliJ IDEA 2026.1.1/mycode/yun-picture/yun-picture-frontend" && "/d/Dell/code/anaconda/python.exe" tests/branding/test_logo_assets.py -v
```

Expected: 10 项测试全部 `ok`，最终输出 `OK`。

### Task 6: 最终视觉与工程验收

**Files:**
- Verify: `src/assets/logo.svg`
- Verify: `src/assets/branding/hualing-cloud-icon.svg`
- Verify: `src/assets/branding/hualing-cloud-icon-mono.svg`
- Verify: `src/assets/branding/hualing-cloud-logo-horizontal.svg`
- Verify: `public/favicon.svg`
- Verify: `public/favicon.ico`

- [ ] **Step 1: 最终解析 SVG 并检查 ICO 尺寸**

Run:

```bash
cd "D:/Dell/code/IntelliJ IDEA 2026.1.1/mycode/yun-picture/yun-picture-frontend" && "/d/Dell/code/anaconda/python.exe" -c "from pathlib import Path; import xml.etree.ElementTree as ET; from PIL import Image; files=[Path('src/assets/logo.svg'),*Path('src/assets/branding').glob('hualing-cloud-*.svg'),Path('public/favicon.svg')]; assert len(files)==5; [ET.parse(f) for f in files]; im=Image.open('public/favicon.ico'); assert sorted(im.info['sizes'])==[(16,16),(32,32),(48,48)]; print('绘灵云 brand assets: valid')"
```

Expected: `绘灵云 brand assets: valid`。

- [ ] **Step 2: 检查页头视觉**

启动项目或在 IDE 中预览 `src/assets/logo.svg`，确认：

- 海军蓝底板正式、稳定；
- 两个画框的前后关系清楚；
- 湖蓝山形不过度抢眼；
- 在 `GlobalHeader.vue` 当前 Logo 尺寸下不拥挤；
- 没有星光、机器人、电路线、发光或渐变。

- [ ] **Step 3: 检查浏览器标签页**

清除该站点 favicon 缓存或强制刷新，确认 16×16 下能辨识两个交叠画框，底板没有触边，山形没有变成杂点，且 `public` 中的旧蓝紫图标不再显示。

- [ ] **Step 4: 检查横版和单色版本**

确认横版完整显示“绘灵云”和“图片协作平台”，文字不被裁切；单色版可通过 CSS `color` 改变底板及山形颜色，并维持白色画框层级。

## 实施边界

- 不修改 `GlobalHeader.vue` 的布局和引用路径，因为它已引用 `src/assets/logo.svg`。
- 不修改登录、注册、页脚、路由、接口或其他业务代码。
- 不引入 npm 依赖；ICO 使用现有 Pillow 12.3.0 生成。
- 只有在新资源通过存在性与 XML 检查后，才删除旧 `cloud-gallery` 文件。
- 当前项目不是 Git 仓库，因此不包含提交、分支、合并或 PR 步骤。
