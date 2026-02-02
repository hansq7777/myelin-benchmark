# Lab Report

- 时间（开始）：2026-02-02 15:48
- 时间（结束）：2026-02-02 15:55
- 任务类型（analysis / training / inference）：analysis

## 工作内容
- 按项目规范生成伪影增强样本：点状噪声、片状噪声、散射纹理背景
- 每类生成 5 份样本并输出为 JPG 供 review

## 数据与方法
- 数据来源：`data/00_raw/20241206_s1bf/.../slice_144_left_hemisphere_S1BF_S24.ome.tif`
- 增强类型：点状噪声 / 片状噪声 / 散射纹理

## 结果
- 输出目录：`/dfs/snout/Histology/RND2412/REVIEW/augment_noise_samples/`
- 文件：`point_noise_01..05.jpg`, `patch_noise_01..05.jpg`, `scatter_texture_01..05.jpg`

## 备注
- 使用同一基底 slice 生成，可用于对比不同噪声类型视觉效果
