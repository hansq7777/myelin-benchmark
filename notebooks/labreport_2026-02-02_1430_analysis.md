# Lab Report

- 时间（开始）：2026-02-02 14:05
- 时间（结束）：2026-02-02 14:30
- 任务类型（analysis / training / inference）：analysis

## 工作内容
- 部署 Bio-Formats bftools 与 CZI 元信息读取工具
- 使用 showinf 读取 series 数与 OME-XML 元数据
- 关闭 zeissczi.autostitch 自动拼接，按 series 拆分 OME-TIFF

## 数据与方法
- 数据来源/版本：`data/00_raw/20241206_pig_hippocampus/pig hippocampus 2x2.czi`
- 方法名：Bio-Formats bftools（showinf / bfconvert）
- 配置文件：`-option zeissczi.autostitch false`

## 结果
- Series 数：4（每个 series 为一个完整 Z-stack）
- 像素类型：uint8（8-bit）
- 分辨率：dx=dy=0.439294 µm；dz=0.396329 µm（dz≈0.90*dx）
- 输出：
  - `data/00_raw/20241206_pig_hippocampus/pig_hippocampus_2x2_ometiff/pig_hippocampus_2x2_S00.ome.tif`
  - `data/00_raw/20241206_pig_hippocampus/pig_hippocampus_2x2_ometiff/pig_hippocampus_2x2_S01.ome.tif`
  - `data/00_raw/20241206_pig_hippocampus/pig_hippocampus_2x2_ometiff/pig_hippocampus_2x2_S02.ome.tif`
  - `data/00_raw/20241206_pig_hippocampus/pig_hippocampus_2x2_ometiff/pig_hippocampus_2x2_S03.ome.tif`

## 备注
- 已验证输出 OME-TIFF 含 StageLabel 坐标与 PhysicalSize 信息
- 如需批量处理其他 CZI，可复用同一拆分策略与脚本
