from openai import OpenAI
import os
import csv

csv_path = "csv/1.csv"
  
# 确保输出目录存在
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

client = OpenAI(api_key="sk-pvumtcpseclngzrccpwqyzyzmqmnunwhwjgdqdseerfkckcm", 
                base_url="https://api.siliconflow.cn/v1")
SYSTEM_PROMPT = (
    "You are a senior prompt writer for text-to-image models. "
    "Always return ONLY the final prompt text segment with no extra commentary, "
    "no surrounding quotes, and no markdown code fences."
)

with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    first_row = next(reader)  # 读取第一行
    second_column = first_row[1]  # 索引从0开始，[1]表示第二列
    print("标题：", second_column)

title = second_column

def make_illus_prompt(title: str) -> str:
    return f"""
# Task Requirements
I want to generate **a visual illustration** for an infographic poster with the title **"{title}"**. Please help me generate a text segment as a **prompt for a text-to-image model** to create an appropriate visual element that complements and enhances the infographic content. The illustration should be **visually appealing, thematically relevant, and informative** with a **transparent  background** and **absolutely no text or words**. You need to design it from the following perspective (**Attention! The following content is provided only as a prompt for your consideration. No response or output is required!**):

## Visual Style and Theme Matching
In this aspect, you will decide the **overall style and thematic coherence** of the illustration. You need to analyze the title "{title}" and determine what type of visual element would best complement the infographic design. Consider whether the topic calls for specific visual metaphors, conceptual illustrations, data visualizations, or thematic imagery.
Please provide:
1. The main visual theme that best represents "{title}" (e.g., technology, nature, business, education, health, etc.).
2. The appropriate illustration style (e.g., minimalist flat design, geometric shapes, isometric illustration, modern vector art, conceptual imagery).
3. The core concept from "{title}" that should be visually represented through compelling imagery.
4. The specific visual elements that would effectively communicate and enhance the main ideas (e.g., abstract shapes, conceptual scenes, symbolic representations, data-inspired visuals).
5. The level of detail appropriate for the illustration (e.g., clean minimalist design, moderately detailed artwork, or rich conceptual illustration).
6. The background should remain **transparent**, and do not render the title.
7. **In the prompt, you need to stress that the illustration must contain no text, words, or letters whatsoever, focusing purely on visual communication.**

# Output
**Output Requirements**:
1. Directly output a text segment as a prompt for a text-to-image model, without any markdown code.
2. Describe the illustration design requirements as detailed as possible, focusing on visual appeal and thematic relevance.
3. Specify concrete visual elements, compositions, and styling details that would effectively complement the infographic content.
4. Avoid using vague artistic descriptions. Instead, focus on specific visual concepts and design approaches.
5. Ensure the prompt emphasizes that the illustration should be professionally designed, visually engaging, and suitable for modern infographic design.
6. **Explicitly state that the image must contain absolutely no text, words, letters, or any written content.**
7. **Focus on creating a cohesive visual element that enhances the infographic without competing with the data presentation.**
8. The background should remain **transparent**, and do not render the title.

Based on the above requirements, please output your design: 
"""
# ---------------------------------------------------------------------------------
# text prompt
def make_text_prompt(title: str) -> str:
     return f"""
# Task Requirements
I want to generate a **text image**, which will be used as the title of a poster in the future. Please help me generate a text segment as a **prompt for a text-to-image model** to create an appropriate text image. The content of the text is **"{title}"**, and the image background is **transparent**. You need to design it from the following three perspectives (**Attention! The following content is provided only as a prompt for your consideration. No response or output is required!**):

## Text Layout and Emphasis
In this aspect, you will decide the **overall layout of the text**. You need to appropriately break down the title "{title}" into lines according to its semantics. and consider whether certain key text should be emphasized. If "{title}" includes two or more sentences, the first sentence should be the main title, and the following sentences do not need to be emphasized.
Please provide:
1. How many lines the text should be split into (**each line must contain more than 5 words, and you must provide exactly 1 or 2 lines**). The extra space above and below the text should be kept blank.
2. The specific content of each line.
3. If there is key text, provide:
   - The key text that should be emphasized.
   - The method of emphasizing the key text, such as enlarging the font, changing the color, or using different colors for each letter.
4. **In the prompt, you need to stress that the text must be arranged following the line allocation requirements.**

## Decoration with Icons
In this aspect, you will decide whether to **decorate the text with icons**. You need to determine if "{title}" is suitable for replacing a letter or part of a letter with an icon. If so, please provide: 
1. The specific content of the icon.
2. Which letter (or part of the letter) in which word the icon will replace.

## Font Style and Artistic Effects
In this aspect, you will decide the **font style and artistic effects** for the text. You need to judge whether "{title}" is suitable for a specific font style (e.g., classical, futuristic, anime-style, etc.) and certain artistic text effects (e.g., cracks on the text surface, melting text, etc.). If applicable, please provide:
1. The font style, such as classical, futuristic, anime-style, etc.
2. The artistic effect, such as cracks on the text surface, melting text, burning text, etc.
3. The background should be **Transparent**.

# Output
**Output Requirements**:
1. Directly output a text segment as a prompt for a text-to-image model, without any markdown code.
2. Describe the design requirements as detailed as possible, but there is no need to elaborate on the purpose and significance of the design.
3. Do not answer each dimension one by one according to the task requirements. Instead, integrate the designs from all dimensions and output them together.
4. Avoid describing your design solely with stylistic adjectives. You should translate your design into specific presentation methods and scenarios.

Based on the three dimensions above, please output your design:"""

illus_prompt = make_illus_prompt(title)
text_prompt = make_text_prompt(title)

# ----  call ----
response_illus = client.chat.completions.create(
    model="Qwen/Qwen3-235B-A22B-Instruct-2507",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": illus_prompt},
    ],
    stream=True,
)

response_text = client.chat.completions.create(
    model="Qwen/Qwen3-235B-A22B-Instruct-2507",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": text_prompt},
    ],
    stream=True,
)

# 输出prompt查看
# for chunk in response_illus:
#     if not chunk.choices:
#         continue
#     if chunk.choices[0].delta.content:
#         print(chunk.choices[0].delta.content, end="", flush=True)
#     if chunk.choices[0].delta.reasoning_content:
#         print(chunk.choices[0].delta.reasoning_content, end="", flush=True)

# for chunk in response_text:
#     if not chunk.choices:
#         continue
#     if chunk.choices[0].delta.content:
#         print(chunk.choices[0].delta.content, end="", flush=True)
#     if chunk.choices[0].delta.reasoning_content:
#         print(chunk.choices[0].delta.reasoning_content, end="", flush=True)# 提取response_illus内容并保存为illus_prompt.txt
def save_response_to_file(response, filename):
    with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
        for chunk in response:
            if not chunk.choices:
                continue
            if chunk.choices[0].delta.content:
                f.write(chunk.choices[0].delta.content)
            if chunk.choices[0].delta.reasoning_content:
                f.write(chunk.choices[0].delta.reasoning_content)

# 保存illu_prompt
save_response_to_file(response_illus, 'illus_prompt_qwen3_235B.txt')
# 保存text_prompt
save_response_to_file(response_text, 'text_prompt_qwen3_235B.txt')
print("prompt已保存。")