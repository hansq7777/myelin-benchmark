# Method Template

此模板用于统一方法接入流程，遵循可复现与可比较原则。

## 目录结构
```
methods/<method_name>/
  config.yaml
  run_train.sh
  run_infer.sh
  train.py
  infer.py
  checkpoints/
  outputs/
  README.md
```

## 约定
- 所有训练与推理输出（模型、日志、可视化）必须保存在本目录。
- 预测结果必须写入 `data/06_inference/<method_name>/`。
- 配置文件需完整记录数据路径、超参、随机种子、评估指标。

## 训练
```
./run_train.sh configs/your_config.yaml
```

## 推理
```
./run_infer.sh configs/your_config.yaml
```

## 评估建议（AI 专家实践）
- 固定数据划分（`data/05_splits/`）与随机种子。
- 报告多指标与统计置信区间（如 Dice/IoU/F1/AUC/MAE）。
- 报告运行资源（GPU、显存、耗时）。
- 保存可视化对比与失败样本分析。

## Early Stopping（标准配置）
默认建议（可在 `config.yaml` 中调整）：
- `monitor: val_loss`
- `mode: min`
- `patience: 20`
- `min_delta: 0.001`
- `min_epochs: 30`
- `cooldown: 5`
