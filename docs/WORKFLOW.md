# 工作流与对比方案

## 1) 目标与范围
- 目标：在统一数据、统一评估指标与统一资源约束下，横向比较不同方法的预测效能。
- 任务类型示例：
  - 分割（myelin mask）
  - 分类（有/无髓鞘、损伤等级）
  - 回归（密度、厚度、面积比例）

## 2) 基础数据与最低要求
### 必需数据
- 原始影像：显微镜扫描、切片图像或体数据。
- 真值标注：mask/ROI/评分表。
- 元数据：样本ID、成像条件、批次信息、动物/病例信息（去标识化）。

### 可选数据
- 额外通道（荧光/染色通道）
- 质量控制信息（模糊、曝光、切片损伤）

## 3) 统一文件结构
- `data/00_raw/`：原始数据（保持不变）
- `data/01_import/`：导入/格式转换后的数据
- `data/02_metadata/`：样本清单、元数据（去标识化）
- `data/03_labels/`：对应标签
- `data/04_processed/`：统一格式（如 TIFF/PNG、标准化分辨率/切块）
- `data/05_splits/`：固定分割文件（CSV/JSON）
- `data/06_inference/`：预测输出结果

示例：
```
data/04_processed/
  sample_001/
    image.tif
  sample_002/
    image.tif

data/03_labels/
  sample_001_mask.tif
  sample_002_mask.tif

data/05_splits/
  train.csv
  val.csv
  test.csv
```

## 4) 方法接入（统一接口）
每种方法在 `methods/<method_name>/` 下保留：
- `run_train.sh` / `run_infer.sh`：统一入口
- `config.yaml`：方法参数
- 输出约定：预测结果写入 `data/06_inference/<method_name>/`，必要时镜像到 `results/<method_name>/preds/`

## 5) 评估与比较工具
### 指标（按任务类型）
- 分割：Dice、IoU、Precision/Recall、Boundary F1
- 分类：Accuracy、F1、AUC
- 回归：MAE、RMSE、R2

### 工具建议
- 评估脚本：`tools/` 或 `scripts/eval_*.py`
- 统计比较：成对检验、方差分析、置信区间
- 可视化：箱线图、PR曲线、ROC曲线、样本可视对比

## 6) 部署与运行
### 环境
- 在 `env/` 记录：
  - Python 版本
  - 依赖库（requirements.txt / environment.yml）
  - CUDA / cuDNN 版本

### 计算资源建议
- GPU：视方法复杂度（>= 8GB 显存建议；大模型需 12–24GB）
- CPU：预处理与评估可用多核
- 存储：原始与中间数据需大空间

## 7) 实验记录
- 每次实验在 `experiments/<date>_<method>/` 下保存：
  - 配置快照
  - 训练日志
  - 评估结果
- 结果汇总在 `results/summary.csv` 或 `results/summary.json`

## 8) 比较流程（建议）
1. 数据整理：`scripts/prepare_data.py`
2. 生成固定分割：`scripts/make_splits.py`
3. 逐方法训练与推理：`methods/<method>/run_train.sh` + `run_infer.sh`
4. **推理前一致性检查（强制）**：
   - 核对 dz/分辨率是否与训练一致（必要时先重采样）。
   - 核对通道数与命名（_0000…）是否符合模型输入。
   - 核对文件后缀与 dataset.json 一致。
   - 统计 case 数量与来源，记录到 manifest。
   - **如发现不一致，必须先询问确认再继续推理。**
5. **推理后重建 zstack**：将逐 slice 预测重组为 zstack OME‑TIFF，并写入：
   - 原始 OME‑XML 元信息（影像尺寸/分辨率/物镜/采集信息）
   - 预测元信息（模型名、trainer/plans、推理设置、dz 重采样参数、commit/seed）
   - 运行摘要（日期、输入来源、样本数、异常与跳过清单）
6. 统一评估：`scripts/eval_all.py`
7. 汇总与统计：`analysis/compare_methods.py`
