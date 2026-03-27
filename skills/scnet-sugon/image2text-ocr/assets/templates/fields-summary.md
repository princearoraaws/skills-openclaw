# 各识别类型的字段说明（elements 内容）

根据 ocrType 不同，返回的 `elements` 对象包含以下字段：

## GENERAL (通用文字)
- `width`: 图像宽度（像素）
- `height`: 图像高度（像素）
- `angle`: 图像旋转角度（度）
- `text`: 文字块数组，每个块包含：
  - `text`: 文字内容
  - `pos`: 四边形坐标 [[左上], [右上], [右下], [左下]]
  - `x`, `y`, `width`, `height`: 文本块位置和尺寸
  - `text_class`: 文本类别（1竖向，2横向）
  - `confidences`, `chars` 等
