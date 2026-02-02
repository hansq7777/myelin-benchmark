# Environment Templates

本目录存放环境与依赖模板。请根据实际方法和硬件条件选用并锁定版本。

建议：
- 每个方法在 `methods/<method_name>/` 下保留自己的环境说明（如 `requirements.txt`）。
- 最终用于训练/推理的依赖必须锁定版本，以保证可复现。

可用模板：
- `requirements.txt`（pip）
- `environment.yml`（conda）

GPU 相关：
- CUDA / cuDNN 版本需与驱动及深度学习框架版本匹配。
- 建议在方法 README 里记录 GPU/driver/CUDA 信息。
