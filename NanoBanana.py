import os
from openai import OpenAI
from PIL import Image
from io import BytesIO
import base64

client = OpenAI(
    api_key="sk-4edwdp7EOKT3WC0Y333b022202084f8e91B0Fa67461cE9B8", # 换成你在 AiHubMix 生成的密钥
    base_url="https://aihubmix.com/v1",
)

prompt = """
I am currently working on generating an infographic. I will provide the data and the title, and you need to first generate the images for each corresponding part, and then compose them into a complete infographic.
# Data:
Year, Lumina Grain, GeoNuts, Skyberry Pulp, AquaBeans, Zephyr Cotton, Terran Spice Mix
 1993, 279.43, 299.86, 297.59, 303.76, 302.91, 329.13
 1994, 272.91, 352.95, 296.64, 324.96, 261.76, 320.84
 1995, 252.7, 344.68, 278.16, 334.5, 234.22, 349.42
 1996, 233.4, 252.22, 285.67, 354.64, 219.88, 345.33
 1997, 217.83, 214.29, 267.62, 363.94, 197.27, 350.75
 1998, 214.34, 296.64, 246.76, 386.43, 156.67, 428.21
 1999, 166.77, 359.06, 237.01, 394.55, 154.05, 443.34
 2000, 153.4, 352.12, 231.72, 405.16, 138.62, 490.33
 2001, 169.06, 252.49, 222.04, 428.25, 132.93, 508.68
 2002, 122.82, 225.7, 216.8, 430.84, 117.8, 477.11
 2003, 128.51, 296.27, 212.8, 445.62, 117.64, 532.65
 2004, 104.76, 375.92, 207.58, 471.95, 88.1, 566.74
 2005, 109.04, 360.85, 185.01, 473.7, 86.79, 604.19
 2006, 64.6, 239.69, 179.38, 492.35, 74.4, 597.16
 2007, 54.91, 222.98, 175.01, 509.49, 66.57, 626.36
 2008, 20.59, 294.45, 162.81, 528.1, 63.81, 663.84
 2009, 22.03, 378.38, 142.58, 541.95, 45.96, 675.31
 2010, 6.87, 347.04, 142.13, 549.55, 45.95, 685.47
 2011, 3.0, 263.99, 136.32, 568.81, 40.98, 716.74
 2012, 3.0, 229.78, 126.56, 590.67, 34.89, 768.13
 2013, 3.0, 302.64, 114.43, 602.72, 34.45, 784.3
 2014, 3.0, 359.22, 99.11, 611.11, 36.48, 817.81
 2015, 3.0, 340.64, 116.89, 629.95, 27.15, 835.93
 2016, 3.0, 255.59, 101.11, 645.92, 19.16, 825.83
 2017, 3.0, 227.14, 81.23, 663.1, 18.89, 874.59
 2018, 3.0, 288.8, 72.74, 675.07, 33.89, 927.17
 2019, 3.0, 377.21, 68.41, 687.93, 25.38, 904.79
# Title:
Fertilizer Price
# Illustration Rendering:
In this part, you need to draw the visual illustration that best matches the title. First analyze the title and decide what type of visual elements best complement the infographic design. Choose an appropriate illustration style and specific visual elements that can effectively convey and enhance the main idea. The illustration must not contain any text.
# Title Image Rendering:
In this part, you need to render the title as an image, and you may also choose to add some subtitle text. You should first determine how many lines the title text should be split into, and you can use some icons to decorate the text, for example by replacing a letter with an element whose style matches the title. The font style and artistic effects for the text should be determined based on the title.
# Chart Drawing:
In this part, you need to draw a stacked area chart. Based on the provided CSV-format data, each row represents the incremental values of different categories for that year. The stacking order of the data series in the stacked area chart must strictly follow the series order given in the first row and must not be changed. Make sure the chart is drawn accurately, with the data correctly mapped to the horizontal and vertical axes. The chart must include all the provided data and labels, but do not display numeric values directly on the chart. Use a consistent visual style throughout, with the specific style decided by you. The color of the chart is determined by the title, and the chart background should be the same as the underlying canvas background, with an appropriate color chosen according to the title. The entire graphic should use only a single background color.
# Layout Information:
In this part, you need to define the positions of the title, illustration, and chart yourself, and you must ensure that the elements do not overlap or obscure one another.
"""
response = client.chat.completions.create(
    model="gemini-3-pro-image-preview",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt,
                }
            ],
        },
    ],
    modalities=["text", "image"],
    temperature=0.7,
)
try:
    # 查看返回的图像内容
    if (
        hasattr(response.choices[0].message, "multi_mod_content")
        and response.choices[0].message.multi_mod_content is not None
    ):
        for part in response.choices[0].message.multi_mod_content:
            if "inline_data" in part and part["inline_data"] is not None:
                print("\n🖼️ [Image content received]")
                image_data = base64.b64decode(part["inline_data"]["data"])
                image = Image.open(BytesIO(image_data))
                # image.show() # 取消注释以显示图片
                image.save("stacked_area_without3.png")
                print("✅ Image saved to: generated_image.png")
            
    else:
        print("No valid multimodal response received.")
except Exception as e:
    print(f"Error processing response: {str(e)}")