import subprocess

subprocess.run(["python", "text_image_prompt.py"], check=True)
subprocess.run(["python", "img_gen.py"], check=True)
subprocess.run(["python", "merge_textVariation.py"], check=True)
