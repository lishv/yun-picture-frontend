# 蓝紫云境 Logo 优化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有云图库 Logo 重绘为适合 16×16 favicon 的蓝紫圆角底板与白色云图融合符号，并完成 SVG、真实多尺寸 ICO 和网页接入。

**Architecture:** 四个彩色 SVG 共享同一视觉语言，但 favicon 使用针对小尺寸简化的几何；每个 SVG 使用独立渐变 ID。`public/favicon.ico` 由确定可用的 Pillow 12.3.0 从高分辨率矢量等价绘制结果生成，并包含 16、32、48 三个 PNG 编码子图。Python 契约测试检查 SVG、ICO 目录结构、HTML favicon 顺序和页面标题。

**Tech Stack:** SVG、HTML5、Python 3、Pillow 12.3.0、`unittest`、`xml.etree.ElementTree`、`struct`

---

## 文件结构

- Modify: `src/assets/branding/cloud-gallery-icon.svg`：64×64 新版蓝紫品牌图标。
- Modify: `src/assets/branding/cloud-gallery-icon-mono.svg`：新版 `currentColor` 单色图标。
- Modify: `src/assets/branding/cloud-gallery-logo-horizontal.svg`：新版图标和文字组合。
- Create: `public/favicon.svg`：针对 16×16 优化的浏览器 SVG 图标。
- Modify: `public/favicon.ico`：包含 16、32、48 三个 PNG 子图的真实 ICO。
- Create: `scripts/generate_favicon.py`：可重复生成 ICO 的 Pillow 脚本。
- Modify: `index.html`：优先声明 SVG favicon，再声明 ICO。
- Modify: `tests/branding/test_logo_assets.py`：覆盖新视觉契约、ICO 和 HTML 接入。

### Task 1: 扩展失败的资源契约测试

**Files:**
- Modify: `tests/branding/test_logo_assets.py`

- [ ] **Step 1: 将测试更新为新版完整契约**

测试应保留现有 XML、可访问性、自包含、文案和 `currentColor` 检查，并新增以下常量与测试：

```python
import struct

FAVICON_SVG = ROOT / "public" / "favicon.svg"
FAVICON_ICO = ROOT / "public" / "favicon.ico"
INDEX_HTML = ROOT / "index.html"
BRAND_COLORS = ["#397BFF", "#7C4DFF"]


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
```

彩色资源映射扩展为：

```python
COLORED_ASSETS = {
    "icon": ASSETS["icon"],
    "horizontal": ASSETS["horizontal"],
    "favicon": FAVICON_SVG,
}
```

将 viewBox 期望扩展为 favicon 的 `0 0 32 32`，并让彩色渐变测试断言三个不同渐变 ID 及颜色 `BRAND_COLORS`。新增：

```python
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
    self.assertEqual(root.attrib.get("viewBox"), "0 0 32 32")
    symbol = root.find(f".//{{{SVG_NS}}}path[@data-part='cloud-picture-symbol']")
    self.assertIsNotNone(symbol)
    self.assertEqual(symbol.attrib.get("fill"), "#FFFFFF")
    self.assertEqual(root.findall(f".//{{{SVG_NS}}}circle"), [])


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
```

- [ ] **Step 2: 运行测试确认新版契约失败**

Run:

```bash
"/d/Dell/code/anaconda/python.exe" tests/branding/test_logo_assets.py -v
```

Expected: 因旧颜色、缺少 `public/favicon.svg`、旧 ICO 尺寸或 HTML 声明不符合要求而失败。

### Task 2: 重绘彩色品牌图标与 favicon SVG

**Files:**
- Modify: `src/assets/branding/cloud-gallery-icon.svg`
- Create: `public/favicon.svg`
- Test: `tests/branding/test_logo_assets.py`

- [ ] **Step 1: 将彩色图标改为蓝紫圆角底板**

使用 `viewBox="0 0 64 64"`、唯一渐变 `cloud-gallery-icon-violet-gradient`，底板为 `x="2" y="2" width="60" height="60" rx="14"`。白色融合符号使用单个带 `fill-rule="evenodd"` 的 path，云形主体中切出山峰负形；不包含 `circle`、白色画框或细线。

- [ ] **Step 2: 创建 32×32 简化 favicon.svg**

```svg
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" role="img" aria-labelledby="cloud-gallery-favicon-title">
  <title id="cloud-gallery-favicon-title">智能协同云图库</title>
  <defs>
    <linearGradient id="cloud-gallery-favicon-violet-gradient" x1="3" y1="3" x2="29" y2="29" gradientUnits="userSpaceOnUse">
      <stop stop-color="#397BFF" />
      <stop offset="1" stop-color="#7C4DFF" />
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="30" height="30" rx="7" fill="url(#cloud-gallery-favicon-violet-gradient)" />
  <path data-part="cloud-picture-symbol" fill="#FFFFFF" fill-rule="evenodd" d="M9.25 23.5A6.25 6.25 0 0 1 8.3 11.08 8.25 8.25 0 0 1 23.98 13.6a5.1 5.1 0 0 1-1.08 9.9H9.25Zm2.05-3.1h10.1l-3.15-4-2.18 2.45-1.72-1.75-3.05 3.3Z" />
</svg>
```

- [ ] **Step 3: 运行测试验证 favicon 结构与新配色**

Run:

```bash
"/d/Dell/code/anaconda/python.exe" tests/branding/test_logo_assets.py -v
```

Expected: favicon SVG 和彩色图标相关检查通过；横版、ICO 和 HTML 接入仍可能失败。

### Task 3: 重绘横版与单色品牌资源

**Files:**
- Modify: `src/assets/branding/cloud-gallery-logo-horizontal.svg`
- Modify: `src/assets/branding/cloud-gallery-icon-mono.svg`
- Test: `tests/branding/test_logo_assets.py`

- [ ] **Step 1: 更新横版 Logo**

保留 `viewBox="0 0 360 88"` 与现有两行中文文案。将左侧图标替换为新版蓝紫圆角底板和白色融合符号，使用唯一 ID `cloud-gallery-horizontal-violet-gradient`。主标题颜色改为 `#29245C`，副标题使用 `#667085`。

- [ ] **Step 2: 更新单色 Logo**

保留 `viewBox="0 0 64 64"`、`role`、`title` 和 `aria-labelledby`。使用 `currentColor` 绘制圆角底板，并在底板内使用白色融合符号；为避免单色测试误判，不使用任何十六进制色值，白色通过 `fill="white"` 表示。

- [ ] **Step 3: 运行 SVG 契约测试**

Run:

```bash
"/d/Dell/code/anaconda/python.exe" tests/branding/test_logo_assets.py -v
```

Expected: 所有 SVG 和文案测试通过；ICO 与 HTML 测试尚未完成。

### Task 4: 生成真实多尺寸 ICO

**Files:**
- Create: `scripts/generate_favicon.py`
- Modify: `public/favicon.ico`
- Test: `tests/branding/test_logo_assets.py`

- [ ] **Step 1: 编写 Pillow 生成脚本**

脚本使用 `Image.new("RGBA")`、`ImageDraw.rounded_rectangle` 和高分辨率抗锯齿绘制。每个目标尺寸先以 8 倍分辨率绘制蓝紫逐行渐变和白色云图符号，再以 `Image.Resampling.LANCZOS` 缩放。通过：

```python
images[0].save(
    output,
    format="ICO",
    append_images=images[1:],
    sizes=[(16, 16), (32, 32), (48, 48)],
)
```

保存至 `public/favicon.ico`。脚本路径通过 `Path(__file__).resolve().parents[1]` 定位项目根目录，确保从任意工作目录执行。

- [ ] **Step 2: 运行生成脚本**

Run:

```bash
"/d/Dell/code/anaconda/python.exe" scripts/generate_favicon.py
```

Expected: 输出 `generated public/favicon.ico: 16x16, 32x32, 48x48`。

- [ ] **Step 3: 用 Pillow 与 ICO 目录双重检查尺寸**

Run:

```bash
"/d/Dell/code/anaconda/python.exe" -c "from PIL import Image; im=Image.open('public/favicon.ico'); print(sorted(im.info['sizes']))"
```

Expected: `[(16, 16), (32, 32), (48, 48)]`。

### Task 5: 接入 favicon 并完成回归验证

**Files:**
- Modify: `index.html:4-7`
- Test: `tests/branding/test_logo_assets.py`

- [ ] **Step 1: 更新 HTML favicon 声明**

将旧声明替换为：

```html
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="icon" href="/favicon.ico" sizes="any">
```

保留：

```html
<title>智能协同云图库</title>
```

并将 description 缩进与同级标签对齐，不修改描述文案。

- [ ] **Step 2: 运行完整资源测试**

Run:

```bash
"/d/Dell/code/anaconda/python.exe" tests/branding/test_logo_assets.py -v
```

Expected: 全部测试显示 `ok`，最终输出 `OK`。

- [ ] **Step 3: 解析全部 SVG 并检查 ICO 尺寸**

Run:

```bash
"/d/Dell/code/anaconda/python.exe" -c "from pathlib import Path; import xml.etree.ElementTree as ET; from PIL import Image; files=[*Path('src/assets/branding').glob('*.svg'), Path('public/favicon.svg')]; [ET.parse(f) for f in files]; im=Image.open('public/favicon.ico'); assert sorted(im.info['sizes'])==[(16,16),(32,32),(48,48)]; print('all logo assets: valid')"
```

Expected: `all logo assets: valid`。

- [ ] **Step 4: 浏览器视觉验收**

启动项目后清除该站点 favicon 缓存或使用强制刷新，检查标签页中的 16×16 图标。确认：蓝紫圆角底板完整、白色云朵可辨识、山峰切口不呈现为脏点、旧白色图片框不再出现。再分别预览三个品牌 SVG，确认横版文字未裁切、单色图标可用 CSS `color` 着色。

## 实施边界

- 不修改 Vue 页面、路由、业务组件或标题文案。
- 不删除 ICO fallback。
- 不引入 npm 包；ICO 生成使用环境中已确认的 Pillow 12.3.0。
- 当前目录不是 Git 仓库，因此没有提交、分支、合并或 PR 步骤。
