from PIL import Image
import numpy as np
import gradio as gr

def image_to_grayscale(image):
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    gray_image = image.convert("L")
    return np.array(gray_image)

demo = gr.Interface(
    fn=image_to_grayscale,
    inputs=gr.Image(type="pil"),
    outputs=gr.Image(type="numpy"),
    title="图像灰度化工具",
    description="上传彩色图像，转换为灰度图像"
)
demo.launch()
