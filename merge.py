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
    final_prompt = prompt_template.format(data=formatted_data, position=position, title=title)

    return final_prompt

# 生成d3
def image_gen(api_key, variation_path, illus,text_image,prompt_text, base_url="https://api.example.com/v1"):
    """
    OpenAI的API
    """
    client = OpenAI(
        api_key=api_key,
        base_url=base_url
    )
    
    with open(variation_path, "rb") as image_file:
        response = client.chat.completions.create(
            model="Qwen/Qwen3-VL-32B-Thinking",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt_text},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64.b64encode(image_file.read()).decode('utf-8')}"}},
                        {
                            "type": "image_url", 
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{illus}",
                                "detail": "high"
                            }
                        },
                        {
                            "type": "image_url", 
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{text_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
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
position = get_position(api_key, image_path, get_position_prompt, base_url).choices[0].message.content
print(position)
# 生成最后结果的prompt

gen_prompt = """
#Role
You are a professional chart drawing expert, skilled in using D3 code to create various charts and combine PNG elements to form HTML infographics.

#Task Requirements
##Input
- Receive a set of titled data provided by the user, along with a reference chart image, an illustration, and a text image.
- Data: {data}
- Title：{title}
- The path of the illustration is in "image/illus_image_Qwen_image.png"，the path of the Text image is in "image/text_image_Qwen_image.png"

## Specific Requirements
First, draw the chart in the given chart area using D3 format. Then, reserve space for the Text image and illustration by using placeholders. Afterward, insert the corresponding illustration and Text image PNGs in their respective positions. Finally, generate the infographic in HTML format.

##Chart Drawing
- The chart style (such as colors) should adapt to the content of the title but must not the same as reference chart exactly.
- Ensure that the numerical values in the chart are correctly rendered while maintaining consistency with the visual style of the reference image.
- Guarantee the clarity of the chart.
- Do not draw the chart title.
- Label colors should be black, of appropriate size to avoid overlap. Do not draw tick marks, but tick labels must be displayed.

## Infographic Composition Requirements
- Layout information: Canvas size is 1080 × 1920. Element sizes and positions: {position}.
- The chart should be drawn in the chart area. For the illustration and Text image, use placeholders to reserve space initially. Then, adjust the image sizes and insert them into the corresponding areas of the SVG. Ensure that all three elements fill their respective regions completely.
- Choose a suitable background color (not white) for the canvas（Background of 1080·1920） according to the title content, ensuring visual storytelling and readability.

## Output Requirements
Output the D3 code used to draw the chart. The result must be a fully functional .html file.

##Notes
- Strictly follow the style of the reference image when drawing; do not arbitrarily change the style.
- Ensure that the generated D3 code can accurately render the required chart using the user-provided data.
"""

#融合data和position的prompt 
prompt_final = build_prompt_with_csv(csv_path, gen_prompt)
# print(prompt_final)

illustration_base64 = encode_image_to_base64(illustration_path)
text_image_base64 = encode_image_to_base64(text_image_path)

# 生成D3
result = image_gen(api_key, variation_path, illustration_base64,text_image_base64,prompt_final, base_url).choices[0].message.content
output_path = os.path.join("output", "result2.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(result)

print(f"✅ HTML 文件已保存到: {output_path}")
