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
   - 推理完成后必须将逐 slice 预测 **重建为 zstack OME‑TIFF**，与原始数据元信息对齐。
     - 写入原始 OME‑XML（尺寸、分辨率、物镜与采集参数）。
     - 写入预测元信息（模型名、trainer/plans、推理参数、dz 重采样、commit/seed）。
     - 若无法直接写入 OME‑XML，必须生成 sidecar JSON 并与输出 zstack 同名保存。

2. **方法接入**
   - 每个方法必须放在 `methods/<method_name>/`。
   - 模型代码部署、模型训练、checkpoints 等全部放在该方法目录下。
   - 统一入口脚本：`run_train.sh`、`run_infer.sh`。
   - 预测输出统一写入 `data/06_inference/<method_name>/`。

3. **推理前一致性检查（强制）**
   - 检查 **dz/分辨率** 是否与训练一致；若不一致，先重采样并记录参数。
   - 检查 **通道数与命名**（_0000…）是否与模型一致。
   - 检查 **文件后缀** 与 dataset.json 匹配。
   - 记录 **case 数量与来源**（manifest）。
   - 若发现不一致或异常，**必须先询问确认**，得到允许后再继续推理。

3. **实验配置**
   - 所有实验配置必须保存在 `configs/`。
   - 每次实验必须在 `experiments/<date>_<method>/` 保存配置快照和日志。

4. **评估与比较**
   - 通用工具与共享脚本放在 `tools/`（优先）。
   - 评估结果统一写入 `results/`（如 `summary.csv`）。

5. **划分与随机性（强制）**
   - 训练/验证划分必须按 **stack（或 animal/batch）分组**，禁止按 slice 随机打散。
   - 划分文件固定：`data/05_splits/nnunet_Dataset001_20241206_MyelinConfData_splits.json`。
   - 划分脚本固定 seed（当前：`42`），任何更改必须写入 Lab Report 并在变更说明中标注。
   - 当前固定规则：按 stack 分组 **4-fold（leave-one-stack-out）** 划分。
   - 训练若需保持可比性，必须保证 **同一 split、同一 seed、同一训练轮数/早停策略**。
   - 若计划同时改动多个因素（例如增强 + loss + trainer），必须先确认是否允许混合改动。

   **同一 seed 的建议做法（记录在 Lab Report）**
   - 运行前固定：`PYTHONHASHSEED=42`。
   - 训练脚本中固定：`random.seed(42)`, `np.random.seed(42)`, `torch.manual_seed(42)`,
     `torch.cuda.manual_seed_all(42)`。
   - 若需要严格可复现：设置 `torch.backends.cudnn.deterministic=True` 且 `benchmark=False`
     （可能显著减速）。默认 nnUNet 会启用 `cudnn.benchmark=True`，因此完全确定性并非默认保证。

6. **实验可比性（强制）**
   - 除非是对比不同策略本身（例如不同 trainer/增强），否则 **主要参数必须保持一致**：
     - 数据划分、训练轮数/早停、batch size、patch size、网络结构、预处理与推理设置。
   - 所有差异必须在 Lab Report 中显式记录。

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
