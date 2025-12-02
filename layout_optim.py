from openai import OpenAI
import base64
import os
import csv

api_key = "sk-pvumtcpseclngzrccpwqyzyzmqmnunwhwjgdqdseerfkckcm"
image_path = "image/template.png"
base_url = "https://api.siliconflow.cn/v1"
output_dir = "image/output"
csv_path = "csv/bar/4.csv"
# variation_path = "image/Variation2.png"
# illustration_path = "image/output/illus_image.png"
# text_image_path = "image/output/text_image.png"


os.makedirs(output_dir, exist_ok=True)
with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    first_row = next(reader)  # 读取第一行
    second_column = first_row[1]  # 索引从0开始，[1]表示第二列
    print("标题：", second_column)
    title = second_column

def build_prompt_with_csv(csv_path, prompt_template):
    """
    prompt_template中应包含 {data} 占位符。
    """
    data_rows = []

    # 读取 CSV
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)  # 转为列表方便切片

    # 跳过前两行，只取第三行到最后一行
    if len(rows) > 2:
        data_rows = rows[2:]
    else:
        raise ValueError("CSV 文件少于3行，无法提取数据。")

    # 将数据格式化为字符串（例如用逗号分隔每列）
    formatted_data = "\n".join([", ".join(row) for row in data_rows])

    # 嵌入到 prompt 模板中
    # final_prompt = prompt_template.format(data=formatted_data, position=position, title=title)
    final_prompt = prompt_template.format(data=formatted_data, title=title)
    return final_prompt

# 生成d3
def image_gen(api_key,prompt_text, base_url="https://api.example.com/v1"):
    """
    OpenAI的API
    """
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",
        messages=[
            {
                "role": "user",
                "content": prompt_text
            }
        ]
        # max_tokens=1000
    )
    
    return response

gen_prompt_en = """
# Role
You are a professional chart drawing expert proficient in using D3 code to create various types of charts.
# Input Reception
Receive a dataset with a title and chart description from the user.
Title: {title}
Data: {data}
# Overall requirements for the infographic
- The page must contain a `<div id="chart-container"></div>` as the only container for the infographic. The SVG’s `width` and `height` must both be `1024`.
- Inside this container, create exactly one `<svg>` element, which serves as the canvas for the entire infographic.
- All chart elements (axes, gridlines, bars/lines/scatter points, text, decorative graphics, etc.) must be drawn inside this single `<svg>`.
- Chart size and position (top-left corner of the chart relative to the top-left corner of the canvas):
  - `chart: Size (1000x570), Position (16, 400)`
- Based on the title and the needs of visual storytelling and readability, choose an appropriate background color for the 1024×1024 canvas (it must not be white). This background refers to the SVG canvas background, not the background color of the entire webpage.
# Chart Drawing
- In this section, you need to generate a minimalist-style vertical bar chart. The input is a set of (category, value) data pairs.
- Then, draw a vertical bar for each data point, arranged from left to right in sorted order, with equal spacing between bars, consistent bar width, and all bars aligned at the same horizontal baseline at the bottom. The height of each bar should be proportional to its corresponding value. Each bar should be a "pill-shaped" vertical rectangle (with rounded top and bottom ends), with a unified overall style, and no gradients, textures, or shadow effects.
- The chart should retain only a single baseline at the bottom, without drawing a y-axis, tick marks, grid lines, title, or legend.
- For each bar, place the category label text (using the "category" from the data) horizontally centered below the bottom of the bar, and place the value label text (using the "value" from the data) horizontally centered above the top of the bar.
- The chart should fill the entire chart area as much as possible, but ensure there is enough space to place the labels. Do not add any other decorations.
- The color scheme of the chart is determined by the given title. The chart background should remain transparent, displaying only the chart elements themselves and the canvas background below.
- Use a <div> with an id of chart-container as the container, and create an <svg> inside it as the root node of the chart.
# Output Requirements
- The returned result must be a complete and runnable .html file.
- The answer must start with <!DOCTYPE html> and end with </html>, with standard HTML structure in between. There must not be any explanatory text, and there must be no English comments or descriptions before or after it.
# Notes
- Strictly adhere to the style of the reference template and do not make design changes on your own.
- Ensure the D3 code strictly uses the data provided by the user to render a chart that meets all the above requirements.
- A <script src="./layoutjs/layout2.js"></script> tag must be added at the end to import the script.
"""

# gen_prompt_cn = """
# # 角色（Role）
# 你是一名专业的图表绘制专家，精通使用 D3 代码创建各类图表。
# # 输入接收（Input Reception）
# 从用户处接收一组带有标题和图表描述的数据集。
# 标题（Title）：{title}
# 数据（Data）：{data}
# # 信息图整体要求
# - 页面中必须包含一个 `<div id="chart-container"></div>` 作为信息图的唯一容器。svg的width和height均为1024.
# - 在这个容器内部，只创建一个 `<svg>` 元素，作为整张信息图的总画布。
# - 所有图表元素（坐标轴、网格线、柱子/折线/散点等）、文字、装饰图形都必须画在这一张 `<svg>` 里。
# - 图表的尺寸与位置（指元素左上角相对于画布左上角的偏移量）：
#    chart: Size (1000x570), Position (16,420)
# - 根据视觉叙事与可读性需求，依据标题选择合适的背景颜色（不得为白色），这里的背景指 1024×1024 的画布背景，而不是将整个网页背景改变颜色。
# # 图表绘制（Chart Drawing）
# - 在这个部分你需要生成一张极简风格的竖直柱状图，输入是一组 (category, value) 的数据对。
# 随后为每条数据绘制一根竖直柱形，从左到右按照排序后的顺序依次排列，柱形之间间距相等，柱宽一致，所有柱形的底部对齐在同一水平基线，高度与对应的数值成正比。每根柱形应为“药丸形”竖直矩形（上下端为圆角），整体风格统一，不使用渐变、纹理或阴影效果。
# - 图表仅保留底部的一条基线，不绘制 y 轴、刻度线、网格线、标题或图例。
# - 对于每根柱形，在其底部下方水平居中放置类别标签文本（使用数据中的 category），在其顶部上方水平居中放置数值标签文本（使用数据中的 value）。
# - 图表尽可能占满整个chart区域，但是需要保证有足够的空间以放置标签，不添加其他的任何装饰。
# - 图表的配色由给定的标题决定，图表背景需保持透明，使得只显示图表元素本身以及其下方的画布背景。
# # 输出要求
# - 返回结果必须是一个完整且可运行的 .html 文件
# - 回答以'<!DOCTYPE html>'开头，以'</html>' 结尾，中间是标准HTML结构不要有任何解释性的文字，前后不要英文的注释和说明
# # 注意事项（Notes）
# - 必须严格遵循参考模板的风格，不要自行更改设计。
# - 确保 D3 代码严格使用用户提供的数据，渲染出满足以上所有要求的图表。
# - 在最后必须添加 `<script src="../../layoutjs/layout2.js"></script>` 引入脚本
# """

#融合data和position的prompt 
prompt_final = build_prompt_with_csv(csv_path, gen_prompt_en)
# print(prompt_final)

# illustration_base64 = encode_image_to_base64(illustration_path)
# text_image_base64 = encode_image_to_base64(text_image_path)

# 生成D3
result = image_gen(api_key, prompt_final, base_url).choices[0].message.content
# output_path = os.path.join("output", "result_square_DSV3_csv4.html")
output_path = os.path.join("output", "layoutoptim/test4-en.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(result)

print(f"✅ HTML 文件已保存到: {output_path}")
