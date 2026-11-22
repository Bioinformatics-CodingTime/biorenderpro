# biorenderpro · 科研 SVG 图标库

公开科研绘图素材合集。本机快捷入口仍为 `biorender`。当前版本：2026-11-22。

**[下载完整 SVG 图标库](https://github.com/Bioinformatics-CodingTime/biorenderpro/releases/latest/download/biorenderpro-svg.zip)** · [校验文件](https://github.com/Bioinformatics-CodingTime/biorenderpro/releases/latest/download/biorenderpro-svg.zip.sha256) · [版本与附件](https://github.com/Bioinformatics-CodingTime/biorenderpro/releases)

完整图标在 Release 附件中；GitHub 的 Code → Download ZIP 只包含检索工具和元数据，不含 SVG 素材。下载完整包并解压后，再打开其中的 `index.html`。

**47,200 个文件内容不同的 SVG**：科研与技术 37,822，通用符号 8,276，来源标记的 AI 素材 1,102。这是 SHA-256 字节去重结果，不是唯一生物学对象数量；改色、重新导出及适配版本仍可能画的是同一对象。

## 打开和使用

- 已配置快捷入口的本机可继续输入 `biorender` 或使用同名 Mac 应用；其他电脑直接解压完整素材包使用。
- 双击 `index.html` 或 `打开图标库.command`，即可离线检索和预览。优先使用英文关键词，如 `monocyte`、`heart`、`pipette`。
- 可按来源、类别、素材类型和许可证筛选。每个图标提供来源链接和署名记录。
- 离线页面的“打开 SVG”会在新标签页打开本地图，再用浏览器“另存为”；也可从 `icons/` 直接复制或拖入绘图软件。
- 将整个解压后的文件夹一起移动。不要只搬走 `index.html` 或 `catalog.js`。

## 文件与备份

- `catalog.json`：逐图文件路径、作者、来源、许可、SHA-256，以及合并的重复来源记录。
- `notices/`：原始许可、署名、适配说明和排除清单。
- `COVERAGE.md`：来源覆盖数量和未收录范围。
- `sources.json` 与 `sources/*-manifest.json`：快照、下载地址及汇总数据。
- `SHA256SUMS`：便携包内各文件校验值；解压后可运行 `shasum -a 256 -c SHA256SUMS`。

完整素材包名为 `biorenderpro-svg.zip`，旁附 `.sha256` 校验文件。包内含索引中全部 SVG 路径（含重复来源对应文件）、网页、许可证和元数据。原始下载 ZIP、站点响应和未通过校验的原件保留在本机工作目录，不打进便携包。

## GitHub 下载

仓库：[Bioinformatics-CodingTime/biorenderpro](https://github.com/Bioinformatics-CodingTime/biorenderpro)。完整 SVG、离线检索页和来源记录随 Release 素材包一起提供。

上游入口：[Bioicons](https://github.com/duerrsimon/bioicons)、[SiliCoDraw 图标扩展包](https://github.com/Alex-D-C/SiliCoDraw/tree/main/icon-expansions)、[Colony Care](https://github.com/Colony-Care/lab-icons)。其余来源及收录范围见 [COVERAGE.md](COVERAGE.md)。

## 许可与素材边界

每张图沿用自己的许可，不能将全库统一标成 MIT、CC0 或“无版权”。部分图有 NC（非商业）或 SA（相同方式共享）条件；某些上游记录只给出 `CC BY` 等未注明版本的简称。使用前以对应来源的完整许可为准，保留署名与修改说明。来源未提供作者时保留为空，不推测补写。

共 1,204 个去重后 SVG 含 `<image>` 元素，页面已标注；它们可能含嵌入位图或引用图像，不能据 `.svg` 后缀视为纯矢量。其余 45,996 个未检测到 `<image>` 元素。AI 标记仅沿用来源公开元数据，未逐图鉴定。

这不是 BioRender 官方素材库，没有导出其付费库；也不承诺收尽全网素材。

## 验证与复建

索引中的 SVG 已逐文件检查 XML、文件存在性、脚本/事件属性与 SHA-256。浏览器验证覆盖首屏 60 张图、按来源抽样 115 张图、搜索、翻页、筛选、真实本地 SVG 打开及手机宽度布局；未逐张人工审校科学准确性。

保留完整本机 `sources/` 和已下载的 `icons/expanded/` 后，Python 3.11+ 可运行：

```sh
python3 expand_sources.py validate
python3 build_library.py
node test_gallery.cjs
python3 package_library.py
```

构建会更新生成文件，自制图标应另存。便携包供使用和分享，不含复建所需的全部原始下载包。当前采集器依赖本次记录的上游目录结构，不是永久稳定的全网自动更新服务。
