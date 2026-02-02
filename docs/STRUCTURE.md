# 目录结构

```
myelin-benchmark/
  data/
    00_raw/           # 原始影像或扫描数据（只读）
    01_import/        # 导入/格式转换后的数据
    02_metadata/      # 样本清单、元数据、病例信息（去标识化）
    03_labels/        # 标注/真值（mask、ROI、CSV等）
    04_processed/     # 预处理后的统一格式数据
    05_splits/        # 训练/验证/测试划分（固定以保证公平）
    06_inference/     # 预测输出结果
  methods/            # 各方法的代码或适配脚本
  tools/              # 通用工具与共享脚本
  configs/            # 统一的实验配置（YAML/JSON）
  experiments/        # 每次实验的运行记录（含配置快照）
  results/            # 指标与可视化输出
  analysis/           # 统计比较与汇总脚本
  notebooks/          # 探索性分析（可选）
  scripts/            # 数据准备、评估、报告生成脚本
  env/                # 环境与部署说明（requirements/conda/docker等）
  docs/               # 工作流与说明文档
  logs/               # 训练/推理日志
```

建议将大体量数据放在独立磁盘/挂载点，并在 `data/` 下建立符号链接。
