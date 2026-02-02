# Lab Report

- 时间（开始）：2026-02-02 15:20
- 时间（结束）：2026-02-02 15:45
- 任务类型（analysis / training / inference）：analysis

## 工作内容
- 对 S19 annotation 做 Z 维 padding，使其与 raw Z 维一致
- 重新生成 nnUNet 2D 3 通道伪 3D 训练样本（重叠滑窗）
- 生成 7:3 训练/验证划分
- 更新项目文档索引与 early stopping 配置模板

## 数据与方法
- 数据来源/版本：
  - `data/00_raw/20241206_s1bf/slice_144_left_hemisphere_S1BF_ometiff/`
  - `data/03_labels/20241206_s1bf/`
  - `data/00_raw/20241206_pig_hippocampus/pig_hippocampus_interface_ometiff/`
  - `data/03_labels/20241206_pig_hippocampus/`
- 方法名：nnUNet v2 2D 3-channel pseudo-3D
- 配置：滑动窗口重叠，标签取中心切片；7:3 划分

## 结果
- 数据集：`Dataset001_20241206_MyelinConfData`
- 输出目录：`data/00_raw/nnUNet_raw/Dataset001_20241206_MyelinConfData/`
- 训练样本数：210（S19:51, S24:51, S26:51, Pig:57）
- 划分：Train 147 / Val 63

## 备注
- S19 annotation 从 34 slices padding 到 53 slices（尾部补 0）
- 已停止在训练开始前
