# Myelin Benchmark

本项目用于横向对比不同方法在髓鞘/髓鞘相关任务上的预测效能，提供统一的数据组织、实验运行与评估流程，确保可复现与公平比较。

## 关键文档
- 工作流：`docs/WORKFLOW.md`
- 目录结构：`docs/STRUCTURE.md`
- 操作规范：`docs/OPERATION_RULES.md`
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
