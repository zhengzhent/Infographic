# --------------------------------------------------GPT image
import os
from openai import OpenAI
import base64

# 配置API
client = OpenAI(api_key="sk-4edwdp7EOKT3WC0Y333b022202084f8e91B0Fa67461cE9B8", base_url="https://aihubmix.com/v1")

# 确保output目录存在
output_dir = 'output/image'
os.makedirs(output_dir, exist_ok=True)

# 读取txt文件中的prompt
def read_prompt_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read()

# 从txt文件中读取prompt
illus_prompt = read_prompt_from_file('output/illus_prompt_Qwen3-235B.txt')
text_prompt = read_prompt_from_file('output/text_prompt_Qwen3-235B.txt')

# 生成illus图片
response_illus = client.images.generate(
    model="gpt-image-1-mini", 
    prompt=illus_prompt, 
    size="1024x1024", 
    # quality="high",
    n=1,
)

# 生成text图片
response_text = client.images.generate(
    model="gpt-image-1-mini", 
    prompt=text_prompt, 
    size="1024x1024", 
    # quality="high",
    n=1,
)

#保存图片 
illus_image_bytes = base64.b64decode(response_illus.data[0].b64_json)
with open("output/image/illus_GPTimage_DSV3_nospace_1024.png", "wb") as f:
    f.write(illus_image_bytes)

text_image_bytes = base64.b64decode(response_text.data[0].b64_json)
with open("output/image/text_GPTimage_DSV3_nospace_1024.png", "wb") as f:
    f.write(text_image_bytes)

print("succuss generate image")