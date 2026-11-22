# 来源与收录范围

快照日期：2026-11-22。数量单位为 SVG 文件记录；变体、原始版与适配版不是独立生物学对象。

有效索引来源记录共 52,997 条，合并 5,797 条字节完全相同的记录后，显示 47,200 个文件。共有 42 个来源/版本标签；同一机构可能经多个渠道出现，标签数不是独立网站数。

## 获取范围

- [Bioicons GitHub](https://github.com/duerrsimon/bioicons)：读取本次 ZIP 中 2,830 个 SVG 原件；其中 4 个格式损坏/空文件、2 个含脚本，均保留原件并从索引排除。另有上游目录索引 3 个名称未匹配文件，见 notices/Bioicons/catalog-missing-files.json。
- [SiliCoDraw](https://github.com/Alex-D-C/SiliCoDraw/tree/main/icon-expansions)：15 个扩展包的 10,687 条 SVG 片段，封装为独立 SVG。固定使用上游 100×100 viewBox，保留默认配色；适配修改说明随包保存。
- [BioCartoon](https://biocartoon.com/)：公共 assets.sqlite 快照的 21,996 条可用 SVG 下载记录全部获取，21,992 条通过索引校验。NIH BioArt、Reactome、SciDraw 等在此处为镜像获取；original 标签指镜像提供的完整 SVG，与 SiliCoDraw 片段适配版区分，未宣称已逐一同原站比对。
- [PhyloPic](https://www.phylopic.org/)：固定 API build 564，279 页、13,370 条记录全部下载。13,369 条 XML 合格；1 条有重复属性。优先用 source SVG，否则使用站点提供的 vectorized SVG。
- [Sciicons](https://www.sciicons.com/)：本次公开目录中 is_pro=false 的 3,635 条记录全部为可获取 SVG，保留公开作者、出处及许可字段；不读取 Pro 素材。
- [SwissBioPics](https://www.swissbiopics.org/)：本次画廊列出的 32 个细胞图；[官方许可说明](https://www.swissbiopics.org/help)。
- [Colony Care](https://github.com/Colony-Care/lab-icons)：本次仓库 icons/ 下的 314 个 SVG；示例/其他目录的 SVG 不计入图标目录。
- [Arcadia Science Zenodo v1.2](https://doi.org/10.5281/zenodo.18395998)：官方存档内 144 个 SVG，下载包 MD5 与记录一致。

## 按来源标签统计

“索引前记录”包括同图在多个来源出现的记录；“去重主条目”按首次保留的来源归属。来源筛选仍能找到合并记录，不能把主条目为 0 理解为未下载。

| 来源/版本 | 索引前有效记录 | 去重主条目 |
|---|---:|---:|
| Bioicons original | 2824 | 2821 |
| Bioicons · original | 2790 | 0 |
| SciDraw · original | 611 | 594 |
| PhyloPic · original | 13369 | 13352 |
| Wikimedia Commons · via Sciicons | 206 | 204 |
| SwissBioPics · via Sciicons | 30 | 27 |
| SwissBioPics · original | 32 | 30 |
| Expression Atlas anatomograms | 28 | 28 |
| Arcadia Science | 144 | 144 |
| BioDraws | 160 | 160 |
| Bioicons | 454 | 454 |
| Inkscape Electric Symbols | 204 | 204 |
| Health Icons | 640 | 640 |
| NIH BioArt Source | 752 | 752 |
| OCHA Humanitarian Icons | 283 | 283 |
| Open Crop Icons | 221 | 221 |
| PhyloPic | 3178 | 3178 |
| Reactome Icon Library | 645 | 645 |
| SBOL Visual | 63 | 63 |
| SciDraw | 367 | 367 |
| Servier Medical Art | 3193 | 3193 |
| WMO WorldWeatherSymbols | 355 | 355 |
| NIAID NIH BioArt Source · original | 4810 | 4502 |
| NIH BioArt · via Sciicons | 548 | 53 |
| Health Icons · original | 1616 | 1531 |
| Health Icons · via Sciicons | 1483 | 0 |
| Noto Emoji · original | 3998 | 3973 |
| OpenMoji · original | 4495 | 4300 |
| OpenMoji · via Sciicons | 106 | 4 |
| Reactome Icon Library · original | 2571 | 2571 |
| Arcadia Science · via Sciicons | 144 | 75 |
| Arcadia Science · original | 144 | 0 |
| User-generated · original | 1 | 1 |
| BioCartoon · original | 1100 | 1100 |
| PhyloPic · via Sciicons | 104 | 94 |
| Servier Medical Art · via Sciicons | 322 | 309 |
| Open Crop Icons · via Sciicons | 253 | 253 |
| Janosh Diagrams · via Sciicons | 157 | 157 |
| Electrical Symbol Library · via Sciicons | 74 | 59 |
| Microscopy Components · via Sciicons | 65 | 65 |
| Sciicons · via Sciicons | 143 | 143 |
| Colony Care · original | 314 | 295 |

## 完整性和排除项

- 扩展下载的 SVG 共 39,491 条，下载缺失 0 条；其中 3 条 XML 损坏、2 条含脚本，未进入扩展索引。详情：diagnostics/expanded-validation-failures.json。
- 加上 Bioicons 原始包的排除项，共排除 11 个来源文件记录（包含同一问题图的不同来源记录）。原件保留在本机；整理包只收录通过校验的条目。
- Mac 上 3 组仅文件名大小写不同的 BioCartoon 图标已用上游 ID 改为不同本地文件名，并重新下载各原件。未删除原来的下载文件。
- BioCartoon 有 3,185 条目录记录未提供 SVG（含 Servier 3,020 条、SciDraw 160 条和 BioArt 5 条），不把它们包装为 SVG；Servier 的 SVG 另由 SiliCoDraw/Sciicons 收录。
- 通用符号和 AI 素材另设类型筛选。去重只比较文件字节，没有合并相似轮廓、不同颜色或重新导出的同一图案。
- Togo/DBCLS 在 Bioicons 内的内容已随库收录；独立全量 SVG 存档入口未成功获取，因此未声称完整覆盖。OpenScienceArt 当前检查入口未得到可用图库；BioRender 官方付费素材未收录。
- 镜像记录的许可和作者信息按原样保留，未对所有原作者网页逐条复核；未逐张人工审校图形准确性或外部图像引用的离线可用性。
- 分发仓库：[biorenderpro](https://github.com/Bioinformatics-CodingTime/biorenderpro)，完整 SVG 通过 Release 素材包提供；Code 源码包不含素材。
