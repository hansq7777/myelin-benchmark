# Myelin Benchmark

本项目用于横向对比不同方法在髓鞘/髓鞘相关任务上的预测效能，提供统一的数据组织、实验运行与评估流程，确保可复现与公平比较。

## 关键文档
- 工作流：`docs/WORKFLOW.md`
- 目录结构：`docs/STRUCTURE.md`
- 操作规范：`docs/OPERATION_RULES.md`
- 运行防误跑与阻断机制：`docs/NNUNET_GUARDRAILS.md`
- 项目背景：`docs/PROJECT_CONTEXT_v0.2.md`
- Lab Report 模板：`notebooks/labreport_template.md`

## Dependencies & Tools（含版本）
> 说明：方法级依赖应在 `env/` 或 `methods/<method_name>/` 内单独记录并锁定版本。

| 类别 | 工具/依赖 | 版本 | 说明 |
|---|---|---|---|
| 版本控制 | Git | 2.34.1 | 项目版本管理 |
| 运行环境 | Python | 3.10.12 | 脚本与评估工具 |
| 包管理 | pip | 24.0 | Python 依赖安装 |

## 数据与输出约定（简述）
- 原始数据：`data/00_raw/`
- 导入/格式转换：`data/01_import/`
- 元数据：`data/02_metadata/`
- 标签/真值：`data/03_labels/`
- 处理后数据：`data/04_processed/`
- 划分文件：`data/05_splits/`
- 预测输出：`data/06_inference/`

## 使用说明（简版）
1. 准备数据并按目录规范放置。
2. 在 `methods/` 下接入方法并配置运行脚本。
3. 运行训练/推理与评估脚本，输出到 `results/`。
4. 每次分析/训练/预测后，在 `notebooks/` 写一份 Lab Report。

## 统一阻断机制（Contract + Guarded Runner）
- 统一入口：`scripts/nnunet_guarded_run.sh`
- 已接入：nnUNet 与 DeepBranchTracer（DBT）
- 关键校验阻断：`dx/dy/dz`、通道构造、split 一致性、输入非空、DBT 数据结构完整性
- 日志输出：`preflight_report.json` + `status.tsv`（含退出码、信号、心跳）
- 目标：减少错跑、空跑、覆盖跑；问题可追溯且可复用到新模型

## DBT 后处理工具（单根无分叉追踪统计）
- 脚本：`methods/deepbranchtracer/tools/postprocess_tracks.py`
- 用途：对 DBT 输出的 `pro.lab/pro.skl` 做分叉消解与端点桥接，导出 `track_id` 级 SWC 与定量表。
- 主要输出：
  - `tracks_merged.swc`：桥接与分叉消解后的合并 SWC
  - `tracks_summary.csv`：每根轨迹长度/方向/分叉数/桥接数
  - `tracks_nodes.csv`：每个节点坐标、半径、父子关系
  - `bridges.csv`：端点桥接明细（距离、方向一致性、概率路径评分）
  - `postprocess_meta.json`：阈值、spacing、总长度与密度摘要

示例命令：

```bash
python methods/deepbranchtracer/tools/postprocess_tracks.py \
  --prob-lab data/06_inference/case001.pro.lab.tif \
  --prob-skl data/06_inference/case001.pro.skl.tif \
  --output-dir data/06_inference/postprocess_case001 \
  --dx 0.439294 --dy 0.439294 --dz 0.396329 \
  --lab-thr 0.5 --skl-thr 0.5 \
  --bridge-max-gap-um 3.0 --bridge-min-cos 0.6 \
  --bridge-use-prob-path --bridge-min-path-prob 0.3 \
  --save-track-swcs
```

定量定义（工具内置）：
- 长度：按节点链累积欧氏距离并乘 `dx/dy/dz`（um）
- 方向：同时导出端点向量方向与 PCA 主方向
- 密度：`total_length_um / ROI_area_um2` 与 `total_length_um / ROI_volume_um3`
