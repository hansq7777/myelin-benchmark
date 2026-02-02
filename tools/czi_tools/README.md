# CZI Metadata Tool

本工具用于读取 Zeiss CZI 文件的元数据（包含尺度、场景/Stage 坐标等）。

## 安装位置
- 目录：`tools/czi_tools/`
- Python 环境：`tools/czi_tools/.venv/`

## 使用方法
```
/home/dilgerlab/Siqi/myelin-benchmark/tools/czi_tools/.venv/bin/python \
  /home/dilgerlab/Siqi/myelin-benchmark/tools/czi_tools/read_czi_meta.py \
  /path/to/file.czi
```

## 输出信息
- 轴与维度（Axes/Shape）
- 场景数量（S 维度）与 Z slices（Z 维度）
- XY 分辨率、Z 方向间距（若元数据包含）
- 每个 Scene 的 Stage 坐标（若元数据包含）
