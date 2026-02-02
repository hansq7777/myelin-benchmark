# Lab Report

- 时间：2026-02-02 17:30
- 任务类型：analysis / data-split

## 工作内容
- 重新生成按 stack 分组的 8/2 训练/验证划分，明确排除 `PIG_INTERFACE_S00` 作为验证集。
- 固定 seed=42 并保存划分文件，作为后续 nnUNet 训练的统一 split。

## 数据与方法
- 数据集：`Dataset001_20241206_MyelinConfData`
- 分组键：case_id 去掉 `_z###`
- 脚本：`tools/nnunet_prep/make_splits_grouped.py`
- 训练/验证比例：8/2
- 随机种子：42
- 约束：`PIG_INTERFACE_S00` 不进入验证集

## 划分结果
- Train stacks：`PIG_INTERFACE_S00`, `S1BF_S19`, `S1BF_S26`
- Val stacks：`S1BF_S24`
- Train cases：159
- Val cases：51

## 输出位置
- `data/00_raw/nnUNet_raw/Dataset001_20241206_MyelinConfData/splits_final.json`
- `data/04_processed/nnUNet_preprocessed/Dataset001_20241206_MyelinConfData/splits_final.json`
- `data/05_splits/nnunet_Dataset001_20241206_MyelinConfData_splits.json`
- `data/05_splits/nnunet_Dataset001_20241206_MyelinConfData_splits_stacks.json`

## 备注
- 后续对比实验必须使用同一 split；如需变更需提前说明并记录。
