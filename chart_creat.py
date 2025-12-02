import pandas as pd
import base64
from dashscope import ImageSynthesis

API_KEY = "sk-pvumtcpseclngzrccpwqyzyzmqmnunwhwjgdqdseerfkckcm"
MODEL = "Qwen/Qwen-Image"
CSV_FILE = "csv/bar/1.csv"
OUT_PNG = "chart.png"

# -------------------------
# 读取 CSV
# -------------------------
df = pd.read_csv(CSV_FILE)
table_text = df.to_csv(index=False)

# -------------------------
# 英文 prompt（避免 header 编码错误）
# -------------------------
prompt = "Draw a professional bar chart based on the provided CSV data."

# -------------------------
# 中文内容作为 extra（进入 body，不进入 header）
# -------------------------
extra_cn = f"""
请根据下方 CSV 数据绘制一张专业的柱状图：

要求：
- 使用清爽的配色
- 标题为 "Production of Crops"
- 横轴为 {df.columns[0]}
- 纵轴为 {df.columns[1]}
- 图表背景浅绿色
- 数值显示在柱子上方

CSV 数据如下：
{table_text}
"""

# -------------------------
# 调用 API（兼容旧版 SDK）
# -------------------------
result = ImageSynthesis.call(
    prompt,              # ← 第一个位置参数（必须）
    model=MODEL,
    api_key=API_KEY,
    input={
        "extra": extra_cn
    },
    parameters={
        "size": "1024*1024"
    }
)



# -------------------------
# 保存图片
# -------------------------
image_base64 = result["output"]["results"][0]["base64"]
image_bytes = base64.b64decode(image_base64)

with open(OUT_PNG, "wb") as f:
    f.write(image_bytes)

print("图表已生成：", OUT_PNG)
