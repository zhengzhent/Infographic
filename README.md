# Infographic

## 具体文件解释

- csv 中存放 data，title
- Variation 中存放一些信息图的布局模板

- text2image_prompt.py: 用于生成文生图模型的输入 prompt，目前所用的模型是
  "Qwen/Qwen3-235B-A22B-Instruct-2507"，输出的结果会被保存在 /output 目录下。

- img_gen.py: 用于生成图片。输入是"text2image_prompt.py"所生成的 prompt 文件，输出是 image，结果保存在 output/image/ 下。

- merge_textVariation.py: 用于生成最后的信息图。可手动替换 Size & Position，以及对 Variation 的描述。（关于对 position 的确定，代码里也写了通过 VLM 来确定的 code，但是效果不好我注释掉了）

- merge.py 是用 VLM 进行最后合成的，效果不好，可以不用管。

- totrans.py 处理图片使之背景透明，首先进行像素判断，判断像素是否接近白色（容差 20），如果高于阈值则设置为透明，然后图像二值化，标记连通区域，降噪。

- trim 实现对 text image 的裁剪，使得上下边没有白色的多余的边。

- layout_optim.py 是进行了布局优化的做法，布局优化的 js 脚本再 layoutjs 文件夹下。

# 运行

如果自动化运行整个流程，可以直接运行 main.py. 不过不建议。建议分模块调试。

# 模型选择：

国内：https://cloud.siliconflow.cn/me/models

国外：https://aihubmix.com/models

# github 拉取

建议及时拉取 GitHub 仓库中的代码，我可能会随时更新。
