# 智能协同云图库 Logo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 生成一套能直接用于“智能协同云图库”前端项目的彩色图标、横版品牌标志和单色图标 SVG。

**Architecture:** 三个 SVG 均为独立、无外部依赖的静态资源。彩色图标和横版标志复用相同的 64×64 图形几何，但各自使用唯一渐变 ID；单色版本复用相同几何并以 `currentColor` 着色。使用 Python 标准库测试 SVG 的 XML 合法性、语义标签、画布、渐变唯一性、外部依赖和关键图形约束。

**Tech Stack:** SVG 1.1/HTML5 SVG、XML、Python 3 标准库 `unittest` 和 `xml.etree.ElementTree`

---

## 文件结构

- 创建 `src/assets/branding/cloud-gallery-icon.svg`：透明背景彩色纯图标，适合导航栏、头像及 favicon 源文件。
- 创建 `src/assets/branding/cloud-gallery-logo-horizontal.svg`：图标、主标题和副标题组成的横版品牌标志。
- 创建 `src/assets/branding/cloud-gallery-icon-mono.svg`：使用 `currentColor` 的透明背景单色图标。
- 创建 `tests/branding/test_logo_assets.py`：验证三个 SVG 的结构、可访问性、自包含性与品牌约束。

### Task 1: 建立 Logo 静态资源契约测试

**Files:**
- Create: `tests/branding/test_logo_assets.py`

- [ ] **Step 1: 创建验证测试**

```python
from pathlib import Path
import re
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


def parse_svg(path: Path) -> ET.Element:
    return ET.parse(path).getroot()


class LogoAssetsTest(unittest.TestCase):
    def test_all_expected_assets_exist_and_are_valid_xml(self):
        for name, path in ASSETS.items():
            with self.subTest(asset=name):
                self.assertTrue(path.is_file(), f"missing {path}")
                root = parse_svg(path)
                self.assertEqual(root.tag, f"{{{SVG_NS}}}svg")

    def test_each_asset_has_accessible_title(self):
        for name, path in ASSETS.items():
            with self.subTest(asset=name):
                root = parse_svg(path)
                title = root.find(f"{{{SVG_NS}}}title")
                self.assertIsNotNone(title)
                self.assertTrue((title.text or "").strip())
                self.assertEqual(root.attrib.get("role"), "img")
                self.assertEqual(root.attrib.get("aria-labelledby"), title.attrib.get("id"))

    def test_assets_have_explicit_viewboxes_and_no_fixed_background(self):
        expected = {
            "icon": "0 0 64 64",
            "horizontal": "0 0 360 88",
            "mono": "0 0 64 64",
        }
        for name, path in ASSETS.items():
            with self.subTest(asset=name):
                root = parse_svg(path)
                self.assertEqual(root.attrib.get("viewBox"), expected[name])
                self.assertNotIn("style", root.attrib)
                for rect in root.findall(f".//{{{SVG_NS}}}rect"):
                    self.assertNotEqual(rect.attrib.get("width"), "100%")

    def test_svg_files_are_self_contained(self):
        forbidden = ("<image", "<script", "@import", "http://", "https://")
        for name, path in ASSETS.items():
            with self.subTest(asset=name):
                source = path.read_text(encoding="utf-8")
                for token in forbidden:
                    self.assertNotIn(token, source)
                root = parse_svg(path)
                for element in root.iter():
                    self.assertNotIn(f"{{{XLINK_NS}}}href", element.attrib)

    def test_colored_assets_use_unique_blue_green_gradients(self):
        ids = set()
        for name in ("icon", "horizontal"):
            root = parse_svg(ASSETS[name])
            gradients = root.findall(f".//{{{SVG_NS}}}linearGradient")
            self.assertEqual(len(gradients), 1)
            gradient = gradients[0]
            gradient_id = gradient.attrib["id"]
            self.assertNotIn(gradient_id, ids)
            ids.add(gradient_id)
            stops = gradient.findall(f"{{{SVG_NS}}}stop")
            self.assertEqual([stop.attrib["stop-color"] for stop in stops], ["#1677FF", "#42D392"])

    def test_mono_asset_uses_current_color_without_gradient(self):
        source = ASSETS["mono"].read_text(encoding="utf-8")
        root = parse_svg(ASSETS["mono"])
        self.assertIn("currentColor", source)
        self.assertEqual(root.findall(f".//{{{SVG_NS}}}linearGradient"), [])
        self.assertNotRegex(source, re.compile(r"#[0-9a-fA-F]{3,8}"))

    def test_horizontal_logo_contains_approved_copy(self):
        root = parse_svg(ASSETS["horizontal"])
        copy = ["".join(node.itertext()).strip() for node in root.findall(f".//{{{SVG_NS}}}text")]
        self.assertEqual(copy, ["智能协同云图库", "海量免费图片获取平台"])

    def test_icons_keep_safe_padding_for_small_sizes(self):
        for name in ("icon", "mono"):
            root = parse_svg(ASSETS[name])
            artwork = root.find(f".//{{{SVG_NS}}}g[@data-part='artwork']")
            self.assertIsNotNone(artwork)
            self.assertEqual(artwork.attrib.get("transform"), "translate(6 8)")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 运行测试并确认因资源尚不存在而失败**

Run:

```bash
python -m unittest tests/branding/test_logo_assets.py -v
```

Expected: `test_all_expected_assets_exist_and_are_valid_xml` 等测试失败，并显示缺少 `src/assets/branding/cloud-gallery-icon.svg`。

### Task 2: 创建透明背景彩色纯图标

**Files:**
- Create: `src/assets/branding/cloud-gallery-icon.svg`
- Test: `tests/branding/test_logo_assets.py`

- [ ] **Step 1: 创建 64×64 彩色图标**

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-labelledby="cloud-gallery-icon-title">
  <title id="cloud-gallery-icon-title">智能协同云图库</title>
  <defs>
    <linearGradient id="cloud-gallery-icon-gradient" x1="8" y1="8" x2="56" y2="56" gradientUnits="userSpaceOnUse">
      <stop stop-color="#1677FF" />
      <stop offset="1" stop-color="#42D392" />
    </linearGradient>
  </defs>
  <g data-part="artwork" transform="translate(6 8)">
    <path d="M15 42C8.37 42 3 36.63 3 30c0-6.08 4.53-11.1 10.4-11.88C15.62 11.58 21.8 7 29 7c8.35 0 15.25 6.17 16.41 14.2A10.5 10.5 0 0 1 49 41.88V42H15Z" fill="url(#cloud-gallery-icon-gradient)" />
    <rect x="13" y="20" width="34" height="25" rx="6" fill="#FFFFFF" fill-opacity="0.96" />
    <circle cx="38.5" cy="27.5" r="3.5" fill="#1677FF" />
    <path d="M17.5 40 26 31.5l6.2 6.2 4.1-4.1L43 40H17.5Z" fill="url(#cloud-gallery-icon-gradient)" />
  </g>
</svg>
```

- [ ] **Step 2: 运行契约测试**

Run:

```bash
python -m unittest tests/branding/test_logo_assets.py -v
```

Expected: 与 `icon` 有关的子测试通过；横版和单色资源仍因文件不存在而失败。

- [ ] **Step 3: 进行 SVG XML 快速解析验证**

Run:

```bash
python -c "import xml.etree.ElementTree as ET; ET.parse('src/assets/branding/cloud-gallery-icon.svg'); print('icon svg: valid')"
```

Expected: `icon svg: valid`。

### Task 3: 创建 currentColor 单色图标

**Files:**
- Create: `src/assets/branding/cloud-gallery-icon-mono.svg`
- Test: `tests/branding/test_logo_assets.py`

- [ ] **Step 1: 创建与彩色版几何一致的单色图标**

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-labelledby="cloud-gallery-mono-title">
  <title id="cloud-gallery-mono-title">智能协同云图库单色图标</title>
  <g data-part="artwork" transform="translate(6 8)" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M15 42C8.37 42 3 36.63 3 30c0-6.08 4.53-11.1 10.4-11.88C15.62 11.58 21.8 7 29 7c8.35 0 15.25 6.17 16.41 14.2A10.5 10.5 0 0 1 49 41.88V42H15Z" />
    <rect x="13" y="20" width="34" height="25" rx="6" />
    <circle cx="38.5" cy="27.5" r="3.5" fill="currentColor" stroke="none" />
    <path d="m17.5 40 8.5-8.5 6.2 6.2 4.1-4.1L43 40" />
  </g>
</svg>
```

- [ ] **Step 2: 运行契约测试**

Run:

```bash
python -m unittest tests/branding/test_logo_assets.py -v
```

Expected: 与 `icon`、`mono` 有关的子测试通过；只有横版资源相关测试仍失败。

- [ ] **Step 3: 验证单色文件没有硬编码十六进制颜色**

Run:

```bash
python -c "from pathlib import Path; import re; s=Path('src/assets/branding/cloud-gallery-icon-mono.svg').read_text(); assert 'currentColor' in s and not re.search(r'#[0-9a-fA-F]{3,8}', s); print('mono color: valid')"
```

Expected: `mono color: valid`。

### Task 4: 创建横版品牌标志

**Files:**
- Create: `src/assets/branding/cloud-gallery-logo-horizontal.svg`
- Test: `tests/branding/test_logo_assets.py`

- [ ] **Step 1: 创建 360×88 横版 SVG**

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 88" role="img" aria-labelledby="cloud-gallery-horizontal-title">
  <title id="cloud-gallery-horizontal-title">智能协同云图库，海量免费图片获取平台</title>
  <defs>
    <linearGradient id="cloud-gallery-horizontal-gradient" x1="8" y1="8" x2="56" y2="56" gradientUnits="userSpaceOnUse">
      <stop stop-color="#1677FF" />
      <stop offset="1" stop-color="#42D392" />
    </linearGradient>
  </defs>
  <g transform="translate(6 8)">
    <g data-part="artwork" transform="translate(6 8)">
      <path d="M15 42C8.37 42 3 36.63 3 30c0-6.08 4.53-11.1 10.4-11.88C15.62 11.58 21.8 7 29 7c8.35 0 15.25 6.17 16.41 14.2A10.5 10.5 0 0 1 49 41.88V42H15Z" fill="url(#cloud-gallery-horizontal-gradient)" />
      <rect x="13" y="20" width="34" height="25" rx="6" fill="#FFFFFF" fill-opacity="0.96" />
      <circle cx="38.5" cy="27.5" r="3.5" fill="#1677FF" />
      <path d="M17.5 40 26 31.5l6.2 6.2 4.1-4.1L43 40H17.5Z" fill="url(#cloud-gallery-horizontal-gradient)" />
    </g>
    <text x="76" y="35" fill="#172033" font-family="Inter, 'PingFang SC', 'Microsoft YaHei', sans-serif" font-size="24" font-weight="700" letter-spacing="0.5">智能协同云图库</text>
    <text x="77" y="58" fill="#667085" font-family="Inter, 'PingFang SC', 'Microsoft YaHei', sans-serif" font-size="13" font-weight="400" letter-spacing="1.2">海量免费图片获取平台</text>
  </g>
</svg>
```

- [ ] **Step 2: 运行完整契约测试**

Run:

```bash
python -m unittest tests/branding/test_logo_assets.py -v
```

Expected: 8 个测试全部显示 `ok`，最终输出 `OK`。

### Task 5: 完成视觉和工程验证

**Files:**
- Verify: `src/assets/branding/cloud-gallery-icon.svg`
- Verify: `src/assets/branding/cloud-gallery-icon-mono.svg`
- Verify: `src/assets/branding/cloud-gallery-logo-horizontal.svg`

- [ ] **Step 1: 检查三个文件均能被 XML 解析器读取**

Run:

```bash
python -c "from pathlib import Path; import xml.etree.ElementTree as ET; files=sorted(Path('src/assets/branding').glob('*.svg')); assert len(files)==3; [ET.parse(f) for f in files]; print('\n'.join(str(f) for f in files))"
```

Expected: 输出三个 SVG 路径且进程以状态码 0 结束。

- [ ] **Step 2: 在支持 SVG 预览的编辑器中检查彩色纯图标**

打开 `src/assets/branding/cloud-gallery-icon.svg`，分别以约 16×16、32×32 和 128×128 的显示尺寸查看。确认：

- 云朵外轮廓连续；
- 白色图片框清晰；
- 太阳和山峰在 16×16 下没有形成明显脏点；
- 画布四周存在安全边距；
- 背景透明。

Expected: 五项均满足；若 16×16 下细节无法辨认，只允许调整 `circle` 半径、山峰路径或白色画框尺寸，不改变 64×64 `viewBox`、主色和核心构图。

- [ ] **Step 3: 检查横版品牌标志**

打开 `src/assets/branding/cloud-gallery-logo-horizontal.svg`，确认：

- 图标没有被裁切；
- 主标题完整显示为“智能协同云图库”；
- 副标题完整显示为“海量免费图片获取平台”；
- 图标、主标题、副标题层级明确；
- 在浅色背景下文字对比清晰。

Expected: 五项均满足，且整体适合高度约 44px 的网站导航栏等比缩放使用。

- [ ] **Step 4: 检查单色图标的 CSS 可着色能力**

创建一次性浏览器预览或 IDE SVG 预览，以不同 `color` 值展示 `cloud-gallery-icon-mono.svg`。确认所有轮廓、太阳和山峰均随 `currentColor` 改变，且背景保持透明。

Expected: 图标可以统一显示为任意 CSS 颜色，没有残留蓝色、绿色或白色硬编码填充。

- [ ] **Step 5: 运行最终回归验证**

Run:

```bash
python -m unittest tests/branding/test_logo_assets.py -v
```

Expected: 所有测试通过并输出 `OK`。

## 实施边界

- 本计划只生成 Logo 资源及其验证测试，不替换现有 `src/assets/logo.svg`，也不修改 `App.vue`、布局或 favicon 引用。
- 不生成 PNG，因为 SVG 已满足无损缩放要求；如后续平台必须使用 PNG，应从最终 SVG 单独导出，而不是维护另一套图形源。
- 当前项目不是 Git 仓库，因此不包含 commit 步骤。
