from PIL import Image
import numpy as np
import os
import cv2

def make_transparent(input_image_path, output_image_path, tolerance=20, min_area=20):
    # 打开图像文件
    img = Image.open(input_image_path)
    
    # 确保图像是RGBA格式（带有alpha通道）
    img = img.convert("RGBA")

    # 获取图像的像素数据
    datas = img.getdata()

    # 创建新的数据列表
    new_data = []
    for item in datas:
        # 判断当前像素是否接近白色，使用容差
        if item[0] > 255 - tolerance and item[1] > 255 - tolerance and item[2] > 255 - tolerance:
            new_data.append((255, 255, 255, 0))  # 设置透明
        else:
            new_data.append(item)  # 保留原始像素
    
    # 更新图像的数据
    img.putdata(new_data)

    # 将图片转换为 numpy 数组，便于后续处理
    img_array = np.array(img)

    # 创建二值掩码，非透明的像素为 1，透明的像素为 0
    mask = (img_array[:,:,3] > 0).astype(np.uint8)

    # 使用 OpenCV 的连通组件标记
    num_labels, labels = cv2.connectedComponents(mask)

    # 遍历所有连通区域，计算其面积，去除小区域
    for label in range(1, num_labels):  # 从 1 开始，0 是背景
        area = np.sum(labels == label)
        if area < min_area:
            img_array[labels == label] = [255, 255, 255, 0]  # 设置透明

    # 将处理后的图像数据转换回 PIL 图像
    img = Image.fromarray(img_array)

    # 创建输出目录（如果不存在）
    out_dir = os.path.dirname(output_image_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    # 保存处理后的图像
    img.save(output_image_path)
    print(f"Image saved: {output_image_path}")

# 调用函数
make_transparent("output/image/illus_image_high_GPTimage.png", "output/transparent_image/high_GPT_illus.png")
make_transparent("output/image/text_image_high_GPTimage.png", "output/transparent_image/high_GPT_text.png")
