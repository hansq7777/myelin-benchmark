# Bio-Formats bftools

本目录用于本地转换 CZI/OME-TIFF（bfconvert/showinf）。为避免仓库膨胀，二进制与 jar 不纳入版本控制。

获取方式（示例）：
```
mkdir -p tools/bftools
curl -L -o /tmp/bftools.zip https://downloads.openmicroscopy.org/bio-formats/8.3.0/artifacts/bftools.zip
unzip -q /tmp/bftools.zip -d tools/bftools
```

使用示例：
```
./tools/bftools/bftools/showinf -nopix -option zeissczi.autostitch false your.czi
./tools/bftools/bftools/bfconvert -option zeissczi.autostitch false -series 0 your.czi out.ome.tif
```
