# nnUNet v2 Deployment (Local)

此部署固定在项目目录内，避免文件外溢。

## 位置与约定
- 代码与环境：`methods/nnunet/`
- 模型与训练结果：`methods/nnunet/nnUNet_results/`
- 原始数据：`data/00_raw/nnUNet_raw/`
- 预处理数据：`data/04_processed/nnUNet_preprocessed/`
- 推理输出：`data/06_inference/nnunet/`

## 环境激活
```
source methods/nnunet/nnunet_env.sh
```

## 版本锁定
- 依赖锁定：`methods/nnunet/requirements.lock.txt`
- PyTorch（GPU, CUDA 12.1 wheels）：torch 2.5.1+cu121
- nnUNet v2：2.6.3

## 源码与可编辑安装
- 本地源码：`methods/nnunet/nnunetv2_src/`
- 环境使用可编辑安装（`pip install -e`），确保自定义改动立即生效。

## Early Stop（默认策略）
- 启用：是（默认）
- 监控指标：`val_losses`（越小越好）
- `min_delta=0.001`
- `patience=20`
- `min_epochs=30`
- `cooldown=5`
- 说明：若自定义 Trainer 覆盖 `on_epoch_end`，需调用 `super().on_epoch_end()` 以保留早停逻辑。

## 常用命令示例
> 以下命令需先 `source methods/nnunet/nnunet_env.sh`

- 验证安装：
```
python -c "import torch, nnunetv2; print(torch.__version__, nnunetv2.__version__)"
```

- 查看 nnUNet 变量：
```
echo $nnUNet_raw
```

## 说明
- nnUNet 的训练与推理默认会使用 `nnUNet_raw/`, `nnUNet_preprocessed/`, `nnUNet_results/`。
- 本项目强制将上述路径限定在项目内部。
