# Lab Report

- 时间（开始）：2026-02-02 14:30
- 时间（结束）：2026-02-02 14:45
- 任务类型（analysis / training / inference）：analysis

## 工作内容
- 使用 Bio-Formats（showinf/bfconvert）在 autostitch=false 条件下拆分 CZI
- 解析 OME-XML 获取 series 数与物理分辨率
- 建立 OME-TIFF 输出目录并导出完整 Z-stack

## 数据与方法
- 数据来源/版本：
  - `data/00_raw/20241206_pig_hippocampus/pig hippocampus interface.czi`
  - `data/00_raw/20241206_s1bf/slice 144 left hemisphere S1BF.czi`
- 方法名：Bio-Formats bftools
- 配置：`-option zeissczi.autostitch false`

## 结果
- interface：series=1，输出 `pig_hippocampus_interface_S00.ome.tif`
- s1bf：series=28，输出 `slice_144_left_hemisphere_S1BF_S00..S27.ome.tif`
- 像素类型：uint8（8-bit）
- 分辨率：dx=dy=0.439294 µm；dz=0.396329 µm

## 备注
- 输出均保留 OME-XML（含 StageLabel/PhysicalSize）
- 服务器版本检查返回 503，但不影响转换结果
