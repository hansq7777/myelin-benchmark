# Lab Report

- 时间（开始）：2026-02-02 15:00
- 时间（结束）：2026-02-02 15:20
- 任务类型（analysis / training / inference）：analysis

## 工作内容
- 按重叠滑窗（z-1,z,z+1）生成 2D 3 通道伪 3D 训练样本
- 以中心切片作为标签
- 生成 nnUNet v2 数据集结构与 dataset.json

## 数据与方法
- 数据来源/版本：
  - `data/00_raw/20241206_s1bf/slice_144_left_hemisphere_S1BF_ometiff/`
  - `data/03_labels/20241206_s1bf/`
  - `data/00_raw/20241206_pig_hippocampus/pig_hippocampus_interface_ometiff/`
  - `data/03_labels/20241206_pig_hippocampus/`
- 方法名：nnUNet v2 2D 3-channel pseudo-3D
- 配置：滑动窗口重叠，标签取中间切片

## 结果
- 数据集：`Dataset001_20241206_MyelinConfData`
- 输出目录：`data/00_raw/nnUNet_raw/Dataset001_20241206_MyelinConfData/`
- 训练样本数：191（S19:32, S24:51, S26:51, Pig:57）
- 备注：S19 annotation 仅 34 slices，已按 min(Zraw,Zann) 生成样本

## 备注
- 已停止在训练开始前
