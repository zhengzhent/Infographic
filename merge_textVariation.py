from openai import OpenAI
import base64
import os
import csv

api_key = "sk-pvumtcpseclngzrccpwqyzyzmqmnunwhwjgdqdseerfkckcm"
image_path = "image/template.png"
base_url = "https://api.siliconflow.cn/v1"
output_dir = "image/output"
csv_path = "csv/1.csv"
variation_path = "image/Variation2.png"
illustration_path = "image/output/illus_image.png"
text_image_path = "image/output/text_image.png"


os.makedirs(output_dir, exist_ok=True)
with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    first_row = next(reader)  # 读取第一行
    second_column = first_row[1]  # 索引从0开始，[1]表示第二列
    print("标题：", second_column)
    title = second_column

# 获取坐标
def get_position(api_key, image_path, prompt_text, base_url="https://api.example.com/v1"):
    """
    调用OpenAI兼容的API
    """
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    with open(image_path, "rb") as image_file:
        response = client.chat.completions.create(
            model="Qwen/Qwen3-VL-32B-Instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode('utf-8')}"}}
                    ]
                }
            ],
            # max_tokens=1000
        )
    
    return response

# 图片编码 
def encode_image_to_base64(image_path):
    """将图片转换为base64编码"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

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

# 获取坐标prompt
get_position_prompt = """
You are a professional infographic design expert, skilled in using D3.js for visual layout planning and spatial composition.
Your task is to analyze the provided infographic template image, identify the three key visual elements (Text image, illustration, and chart), and then plan their sizes and positions on a new 1080 (width) × 1920 (height) infographic canvas. The goal is to ensure the overall layout is balanced and fills the entire space proportionally.

Input:
Infographic template image.

Steps:
- Element Identification
    Analyze the template image and accurately identify the following regions:
    Gray background: Text image
    Green background: illustration
    Blue background: chart
    Record each element’s approximate location (e.g., top/middle/bottom, left/center/right) and their relative proportions (aspect ratio, area ratio, etc.).
- New Infographic Layout Planning
    With a 1080×1920 canvas as the target, map the relative layout proportions and hierarchical relationships derived from the template image to the new canvas. Recalculate the following for each element:
    Size (width × height)
    Coordinates (x, y), where (0, 0) is the top-left corner of the canvas
    Ensure all three elements maintain proportional relationships similar to the template and collectively fill the new layout area harmoniously.

Output Format Requirements:
only output the size and coordinates for each element.Format as follows:
 <result>
 Text image: size (width × height), position (x, y)
 Illustration: size (width × height), position (x, y)
 Chart: size (width × height), position (x, y)
 </result>

Please strictly follow the above process and format requirements.

"""

# 获取结果中的位置信息
# position = get_position(api_key, image_path, get_position_prompt, base_url).choices[0].message.content
# print(position)
# # 生成最后结果的prompt

gen_prompt = """
# Role
You are a professional chart-drawing expert, skilled in using D3 code to create various charts and in composing PNG elements into an HTML infographic.
# Task Requirements
## Input Reception
- Receive from the user a dataset with a title and a chart description, as well as the illustration and Text image.
- Title: {title}
- Data: {data}
- The path to the illustration is "transparent_image/Qwen_illus_test.png", and the path to the Text image is "transparent_image/Qwen_text_test.png".
#Specific Requirements
First, draw a chart in the given chart area using D3 format. Then, reserve space for the Text image and illustration with placeholders, and afterwards insert the illustration and Text image PNGs into their respective positions. Finally, generate an infographic in HTML format.
#Chart Drawing
Generate a minimalist vertical bar chart: the input is a set of (category, value) pairs; before drawing the chart, first sort the data by value in ascending order so that the bar heights strictly follow an increasing trend from left to right, consistent with the reference chart; then create one vertical bar for each data item, placing the bars from left to right in this sorted order with equal spacing and equal width, with all bar bottoms aligned on the same horizontal baseline and heights proportional to their values. Each bar should be a pill-shaped vertical rectangle with rounded top and bottom, using a consistent style and no gradients, textures, or shadow effects. The chart should keep only a single baseline at the bottom and should not draw a y-axis, tick marks, grid lines, title, or legend. For each bar, place the category label text centered horizontally below the bar, using the category from the data, and place the value label text centered horizontally above the top of the bar, using the corresponding value from the data. Leave sufficient padding around the edges of the canvas so there is enough space for the value labels at the top and the category labels at the bottom, and do not add any other decorative elements. The color of the chart is determined by the title, and the chart background is transparent so that only the chart elements themselves and the underlying canvas background are visible.
#Infographic Overall Drawing Requirements
Layout information: canvas size is 1024 · 1024, element sizes and positions:
 The position refers to the offset of the element’s top-left corner from the canvas origin (the top-left corner)
 <RESULT>    
 Text image: Size (800x540), Position (-80,-80)    
 illustration: Size (350x350), Position (60,350)    
 chart: Size (1024x1024), Position (0,0)  
 </RESULT>
 - The chart is drawn in the chart area, with a margin of 60px from the edges of the chart area, and should occupy as much of the area as possible. Placeholders are first reserved for the illustration and the text image, then the provided image paths are inserted. The images are embedded into their corresponding regions within the SVG, and all three elements fully occupy their respective areas. 
- Based on visual storytelling and readability requirements, choose a suitable canvas background (not white) according to the title—specifically the 1024×1024 canvas background, not the entire webpage background.
## Output Requirements
The returned result must be a complete, runnable .html file, and within the .html file there must be no additional explanatory or reasoning text outside the <!DOCTYPE html> <html lang="en"> ... </html> tags.
# Notes
- Strictly follow the reference template’s style; do not change the design on your own.
- Ensure the D3 code accurately uses the user-provided data to render a chart that meets all requirements.
"""

#融合data和position的prompt 
prompt_final = build_prompt_with_csv(csv_path, gen_prompt)
# print(prompt_final)

# illustration_base64 = encode_image_to_base64(illustration_path)
# text_image_base64 = encode_image_to_base64(text_image_path)

# 生成D3
result = image_gen(api_key, prompt_final, base_url).choices[0].message.content
# output_path = os.path.join("output", "result_square_DSV3_csv4.html")
output_path = os.path.join("output", "test.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(result)

print(f"✅ HTML 文件已保存到: {output_path}")
