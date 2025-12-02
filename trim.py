from PIL import Image
import numpy as np

def trim_vertical_white(in_path: str, out_path: str,
                        bg_color=(255, 255, 255),
                        tolerance: int = 10,
                        extra_pad: int = 0):
    """
    尽可能裁剪图片上下的白边（只裁剪垂直方向）。

    :param in_path: 输入图片路径
    :param out_path: 输出图片路径
    :param bg_color: 背景颜色，默认纯白
    :param tolerance: 容差，越大越容易被认为是背景（0 表示必须完全等于 bg_color）
    :param extra_pad: 裁剪后在上下各保留的额外像素，用于留一点安全边距
    """
    img = Image.open(in_path).convert("RGB")
    arr = np.asarray(img).astype(np.int16)   # (H, W, 3)

    # 与背景色的差异（简单 L1 距离）
    bg = np.array(bg_color, dtype=np.int16).reshape(1, 1, 3)
    diff = np.abs(arr - bg).sum(axis=-1)    # (H, W)

    # mask: True 表示这一像素不是背景
    mask = diff > tolerance

    # 如果整张图都是白的，就直接保存
    if not mask.any():
        img.save(out_path)
        return

    # 找到“有内容”的所有行索引
    rows_with_content = np.where(mask.any(axis=1))[0]
    y_min = int(rows_with_content[0])
    y_max = int(rows_with_content[-1]) + 1  # 注意下边界要 +1

    # 根据 extra_pad 再稍微扩一点，防止切到文字
    y_min = max(0, y_min - extra_pad)
    y_max = min(arr.shape[0], y_max + extra_pad)

    width = img.width
    # 只裁剪上下：left=0, right=width
    cropped = img.crop((0, y_min, width, y_max))
    cropped.save(out_path)


if __name__ == "__main__":
    # 调整 tolerance 和 extra_pad 试试效果
    trim_vertical_white(
        "output/image/text_GPTimage_DSV3_nospace.png",
        "output/image/text_GPTimage_DSV3_trimed.png",
        bg_color=(255, 255, 255),
        tolerance=15,   # 文字有抗锯齿时可以稍微大一点
        extra_pad=4     # 上下各留 4 像素安全边
    )
    trim_vertical_white(
        "output/image/illus_GPTimage_DSV3_nospace.png",
        "output/image/illus_GPTimage_DSV3_trimed.png",
        bg_color=(255, 255, 255),
        tolerance=15,   # 文字有抗锯齿时可以稍微大一点
        extra_pad=4     # 上下各留 4 像素安全边
    )
    print("success trim!")
