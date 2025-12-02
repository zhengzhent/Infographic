# 图片填充
import cv2
import numpy as np
from PIL import Image


# -------------------------
# 1. 加载已有 chart.png 生成 mask
# -------------------------
def load_chart_and_make_mask(chart_path, mask_path):
    chart = Image.open(chart_path).convert("RGBA")
    arr = np.array(chart)

    # 使用 alpha 判断前景
    alpha = arr[:, :, 3]
    mask = (alpha > 10).astype(np.uint8) * 255

    Image.fromarray(mask).save(mask_path)
    print("初始 mask 保存:", mask_path)
    return mask_path


# -------------------------
# 2. 把新的 PNG（如含标题的图）加入 mask
# -------------------------
def update_mask_with_new_png(base_mask_path, new_png_path, out_mask_path):
    base_mask = cv2.imread(base_mask_path, cv2.IMREAD_GRAYSCALE)
    new_img = Image.open(new_png_path).convert("RGBA")
    new_arr = np.array(new_img)
    new_alpha = new_arr[:, :, 3]

    # 合并 mask：前景 OR 合并
    combined = np.maximum(base_mask, (new_alpha > 10).astype(np.uint8) * 255)
    cv2.imwrite(out_mask_path, combined)
    print("更新后的 mask 保存:", out_mask_path)
    return out_mask_path


# -------------------------
# 3. 在 mask 中找最大空白矩形（用于放 illustration）
# -------------------------
def find_empty_rect(mask_path):
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)

    # 反转：空白=255，前景=0
    inv = cv2.threshold(mask, 1, 255, cv2.THRESH_BINARY_INV)[1]

    # 查找外轮廓
    contours, _ = cv2.findContours(inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    best_rect = None
    max_area = 0

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        area = w * h
        if area > max_area:
            max_area = area
            best_rect = (x, y, w, h)

    print("找到可插入 illustration 的矩形区域:", best_rect)
    return best_rect


# -------------------------
# 4. 将 illustration.png 自动插入空白区域
# -------------------------
def insert_illustration(base_png_path, illustration_path, rect, save_path):
    base = Image.open(base_png_path).convert("RGBA")
    illus = Image.open(illustration_path).convert("RGBA")

    x, y, w, h = rect
    illus_resized = illus.resize((w, h))

    base.paste(illus_resized, (x, y), illus_resized)
    base.save(save_path)
    print("最终合成图已输出:", save_path)


# -------------------------
# 执行流程
# -------------------------
# if __name__ == "__main__":
# 你的 PNG 文件
chart_png = "chart.png"                # 已有 chart
new_title_png = "output/transparent_image/text_deepseekV3.png" # 含标题的 PNG（你 PPT 第二步）
illustration_png = "output/transparent_image/illus_deepseekV3.png"  # 用于插入的 PNG

# 1. chart → 初始 mask
m1 = load_chart_and_make_mask(chart_png)

# 2. 新 PNG → 更新 mask
m2 = update_mask_with_new_png(m1, new_title_png)

# 3. 找出 mask 中最大空白矩形
rect = find_empty_rect(m2)

# 4. illustration 自动插入空白区域
insert_illustration(new_title_png, illustration_png, rect, "final_output.png")
