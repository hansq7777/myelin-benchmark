# TODO List (Recommendations)

## 高优先级（数据与增强）
- 加入 Z 向衰减/深度归一化模拟（衰减曲线 + 分层对比度抖动）。
- ~~注入伪影增强（按成像机理建模）：~~
  - ~~点状噪声：背景高亮细颗粒，不附着髓鞘，通常几个到几十像素一团。~~
  - ~~片状噪声：靠近组织 surface 的高密度颗粒近似连片（并非每层都有）。~~
  - ~~散射噪声：远离组织时出现同心环式随机纹理。~~
  - ~~2.5D 一致性：点状/片状在相邻 2–3 层保持相关；散射纹理跨层共享但有轻微扰动。~~
- 加入深度位置编码通道（0–1 归一化 Z index）。

## 中优先级（结构约束与训练策略）
- 自定义 Trainer：加入 clDice / soft-skeleton 结构损失。
- 深层 slice 加权采样，提高深层 Recall。
- ~~引入早停策略（已模板化）：monitor=val_loss, patience=20, min_delta=0.001, min_epochs=30。~~

## 中优先级（后处理与评估）
- 2D 预测后做 3D skeleton/graph 重建，独立评估拓扑。
- 并行两套 gap 协议：允许短 gap / 不桥接，固定阈值与版本。
- 构建小型 3D 审计集（少量 ROI 人工 tracing）用于方向/连通性验证。

## 低优先级（模型探索）
- 2.5D k=2（5 通道）对照实验。
- 替代模型基线：HRNet / DeepLabv3+ / MONAI DynUNet。
- 3D 小 patch 试验（如 128×128×16）评估可行性与收益。

## 规模化推理建议
- 断点续跑 + 批处理流水线。
- OME-Zarr 作为训练/推理缓存格式（不改变归档格式）。

## 目录脚手架与横向对比
- ~~建立并行方法目录：`methods/nnunet_base`, `methods/nnunet_dice_cldice`, `methods/nnunet_trainer_v2`, `methods/nnunet_aug_zdecay`。~~
- ~~每个方法目录维护独立 `nnUNet_results` 与 `configs/`，共享同一 venv。~~
- 在 `results/compare_runs.csv` 记录每次训练指标，便于横向比较。
