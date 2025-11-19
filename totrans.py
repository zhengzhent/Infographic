from PIL import Image
import os

def make_transparent(input_image_path, output_image_path):
    # 打开图像文件
    img = Image.open(input_image_path)
    
    # 确保图像是RGBA格式（带有alpha通道）
    img = img.convert("RGBA")

    # 获取图像的像素数据
    datas = img.getdata()

    # 创建新的数据列表
    new_data = []
    for item in datas:
        # 改变白色背景为透明
        if item[:3] == (255, 255, 255):  # 如果是白色背景
            new_data.append((255, 255, 255, 0))  # 设置透明
        else:
            new_data.append(item)  # 保留原始像素
    
    # 更新图像的数据
    img.putdata(new_data)

    out_dir = os.path.dirname(output_image_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    # 保存处理后的图片
    img.save(output_image_path)

# 调用函数
make_transparent("output/image/illus_image_high_GPTimage.png", "output/transparent_image/high_GPT_illus.png")
make_transparent("output/image/text_image_high_GPTimage.png", "output/transparent_image/high_GPT_text.png")