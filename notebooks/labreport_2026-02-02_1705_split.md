# Lab Report

- 时间：2026-02-02 17:05
- 任务类型：analysis / data-split

## 工作内容
- 按 stack 分组进行 8/2 训练/验证划分，并固定为后续 nnUNet 训练基准。
- 使用固定 seed=42 生成划分；划分文件写入 raw 与 preprocessed 数据目录，并在 `data/05_splits/` 归档。

## 数据与方法
- 数据集：`Dataset001_20241206_MyelinConfData`
- 分组键：case_id 去掉 `_z###`（即 stack 级分组）
- 脚本：`tools/nnunet_prep/make_splits_grouped.py`
- 训练/验证比例：8/2
- 随机种子：42

## 划分结果
- Train stacks：`S1BF_S19`, `S1BF_S24`, `S1BF_S26`
- Val stacks：`PIG_INTERFACE_S00`
- Train cases：153
- Val cases：57

## 输出位置
- `data/00_raw/nnUNet_raw/Dataset001_20241206_MyelinConfData/splits_final.json`
- `data/04_processed/nnUNet_preprocessed/Dataset001_20241206_MyelinConfData/splits_final.json`
- `data/05_splits/nnunet_Dataset001_20241206_MyelinConfData_splits.json`
- `data/05_splits/nnunet_Dataset001_20241206_MyelinConfData_splits_stacks.json`

## 备注
- 后续对比实验必须使用同一 split；如需变更需提前说明并记录。
- 若需严格可复现，请在训练脚本中固定随机种子并关闭 cudnn benchmark（见操作规范）。
