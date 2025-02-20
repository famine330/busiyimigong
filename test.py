from paddleocr import PaddleOCR

# 初始化 PaddleOCR
ocr = PaddleOCR(
    use_angle_cls=True, lang="ch", det_db_thresh=0.1, det_db_box_thresh=0.3
)  # 使用中文模型

# 图片路径
image_path = "test.png"

# 进行 OCR 识别
result = ocr.ocr(image_path, cls=True)

# 打印识别结果
for line in result:
    for word in line:
        print(word[1][0])  # 打印识别到的文本
