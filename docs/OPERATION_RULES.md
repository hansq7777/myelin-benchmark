# 操作规范与实验记录要求

本文件用于约束后续所有操作，确保工作流一致、可复现、可比较。

## 必须遵守的工作流
1. **数据组织**
   - 原始数据只放入 `data/00_raw/`，保持只读、不做改动。
   - 导入/格式转换后的数据放入 `data/01_import/`。
   - 元数据放入 `data/02_metadata/`。
   - 标注/真值放入 `data/03_labels/`。
   - 处理后的统一格式数据放入 `data/04_processed/`。
   - 训练/验证/测试划分固定存放于 `data/05_splits/`。
   - 预测输出结果统一写入 `data/06_inference/`。

2. **方法接入**
   - 每个方法必须放在 `methods/<method_name>/`。
   - 模型代码部署、模型训练、checkpoints 等全部放在该方法目录下。
   - 统一入口脚本：`run_train.sh`、`run_infer.sh`。
   - 预测输出统一写入 `data/06_inference/<method_name>/`。

3. **实验配置**
   - 所有实验配置必须保存在 `configs/`。
   - 每次实验必须在 `experiments/<date>_<method>/` 保存配置快照和日志。

4. **评估与比较**
   - 通用工具与共享脚本放在 `tools/`（优先）。
   - 评估结果统一写入 `results/`（如 `summary.csv`）。

## Lab Report 要求（强制）
**每次完成以下任意操作后，必须写一份 Lab Report：**
- 分析（analysis）
- 训练（training）
- 预测/推理（inference）

### 位置与命名
- 统一存放在 `notebooks/` 目录下。
- 文件名建议：`labreport_YYYY-MM-DD_HHMM_<task>.md`
  - 例如：`labreport_2026-02-02_1530_training.md`

### Lab Report 必填内容
- **时间**：开始与结束时间（含日期与时间）
- **任务类型**：analysis / training / inference
- **工作内容**：简要步骤与关键设置
- **数据与方法**：数据来源/版本、方法名、配置文件名
- **结果**：关键指标、图表文件名、输出路径
- **备注**：异常/问题/下一步

## 违反处理
- 任何不符合上述规则的操作，视为无效实验；需补齐记录后方可继续。
