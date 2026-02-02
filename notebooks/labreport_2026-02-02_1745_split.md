# Lab Report

- 时间：2026-02-02 17:45
- 任务类型：analysis / data-split

## 工作内容
- 按 stack 分组生成 4-fold（leave-one-stack-out）划分，用于后续 nnUNet 训练。
- 固定 seed=42 并保存划分文件。

## 数据与方法
- 数据集：`Dataset001_20241206_MyelinConfData`
- 分组键：case_id 去掉 `_z###`
- 脚本：`tools/nnunet_prep/make_splits_grouped.py`
- 随机种子：42
- 规则：4-fold，按 stack 轮流作为验证集

## 划分结果（val stack by fold）
- Fold 0：`S1BF_S24`
- Fold 1：`S1BF_S19`
- Fold 2：`S1BF_S26`
- Fold 3：`PIG_INTERFACE_S00`

## 输出位置
- `data/00_raw/nnUNet_raw/Dataset001_20241206_MyelinConfData/splits_final.json`
- `data/04_processed/nnUNet_preprocessed/Dataset001_20241206_MyelinConfData/splits_final.json`
- `data/05_splits/nnunet_Dataset001_20241206_MyelinConfData_splits.json`
- `data/05_splits/nnunet_Dataset001_20241206_MyelinConfData_splits_stacks.json`

## 备注
- 后续对比实验必须使用同一 split；如需变更需提前说明并记录。
