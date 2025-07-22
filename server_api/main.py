from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from PIL import Image, ImageDraw, ImageFont
import os
import torch
from diffusers import StableDiffusion3Pipeline
import time

start_time = time.time()

pipe = StableDiffusion3Pipeline.from_pretrained("stabilityai/stable-diffusion-3.5-medium", 
                                                torch_dtype=torch.bfloat16, 
                                                text_encoder_3=None, #Drop T5 text encoder to decrease memory requirements
                                                tokenizer_3=None, #Drop T5 text encoder to decrease memory requirements
                                                # token=
                                                )
pipe = pipe.to("cuda")


app = FastAPI()

# Health Check 
@app.get("/")
def root():
    return {"message": "ok"}

# Save the last user input (in-memory for simplicity)
last_input = ""

@app.post("/input") # curl -X POST -F "user_input=prompt here" http://127.0.0.1:8000/input
def receive_input(user_input: str = Form(...)):
    global last_input
    last_input = user_input
    return {"message": f"Input received: {user_input}"}

@app.get("/image") # http://127.0.0.1:8000/image
def get_image():
    image = pipe(
        prompt=last_input,
        num_inference_steps=28,
        guidance_scale=3.5,
    ).images[0]

    image_path = f"{last_input}.png"
    image.save(image_path)
    return FileResponse(image_path, media_type="image/png")
