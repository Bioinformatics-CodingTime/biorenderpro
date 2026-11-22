# biorenderpro · 有来源与许可依据的科研 SVG 图标库

**26,407 个通过本轮来源与许可核查的 SVG**。原有 47,200 个去重条目中，20,793 个证据不足的条目已移出检索页和公开下载包，原件归档保留，不作侵权判断。

[下载核查版完整图标库](https://github.com/Bioinformatics-CodingTime/biorenderpro/releases/latest/download/biorenderpro-svg.zip) · [校验文件](https://github.com/Bioinformatics-CodingTime/biorenderpro/releases/latest/download/biorenderpro-svg.zip.sha256)

解压后打开 `index.html`，或在已配置的本机输入 `biorender`。GitHub 的 Source code ZIP 不含 SVG，须下载 Release 附件。

## 这次核查做了什么

- 保留明确的原图出处、作者、适用许可和本地证据。部分镜像文件按 Git blob SHA-1 与官方仓库逐文件比对，匹配后改为官方出处。
- Bioicons 按固定版本原始文件和逐图许可目录核对；不把网站代码的 MIT 许可套给所有图片。
- PhyloPic 按官方逐图 API 记录核对作者、许可和图片下载地址；SwissBioPics 使用官方 API 文件与官方许可声明；Colony Care、Arcadia 按原始归档和许可核对。
- 对只有聚合站首页、原图对应关系不足、许可矛盾未解决的素材保守归档。归档不表示它们一定没有授权。
- 页面逐图提供“来源”和“署名与授权依据”，下载包含对应证据原文及 SHA256SUMS。

## 使用条件

每张图保留自己的许可证；全库不能统一宣称“无版权”或“不用署名”。CC BY 要求署名，SA / NC 素材另有共享或非商业条件，改图时应记录修改。请将页面中的署名随论文或作品保留。公开授权记录不等于对第三方权利的独立法律担保。

本库与 BioRender 官方无关联，也不含其付费素材导出。未逐张审核科学准确性；含 `<image>` 元素的 SVG 仍在页面单独标记。

## 归档与复建

本机旧版本、旧 ZIP、移出的 SVG 和逐文件 SHA-256 清单保存在 `biorender-library-archive/20261122-before-license-audit/`，不收入新下载包。旧 GitHub Release 转为草稿留存。

`build_library.py` 仅从 `notices/license-audit/approved-records.json` 重建并核对哈希；不会重新导入归档素材。需要扩充时，应先补齐出处和许可证据，再更新核查清单。

```sh
python3 build_library.py
node test_gallery.cjs
python3 package_library.py
```

详见 [收录范围](COVERAGE.md) 与 [核查报告](notices/license-audit/report.json)。
