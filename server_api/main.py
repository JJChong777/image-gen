from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
# from PIL import Image, ImageDraw, ImageFont
import os
import torch
from diffusers import StableDiffusion3Pipeline
import time

start_time = time.time()
hf_token = os.environ.get("HF_TOKEN")
if not hf_token:
    raise ValueError("HF_TOKEN environment variable is not set. Please set it to your Hugging Face API token.")

@asynccontextmanager
async def lifespan(app: FastAPI):
    global gen_pipe
    try:
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            raise ValueError("HF_TOKEN is not set.")

        print("Loading model...")
        gen_pipe = StableDiffusion3Pipeline.from_pretrained(
            
            "stabilityai/stable-diffusion-3.5-medium",
            torch_dtype=torch.bfloat16,
            text_encoder_3=None,
            tokenizer_3=None,
            token=hf_token
        )
        gen_pipe = gen_pipe.to("cuda")
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Model loading failed: {e}")

    yield  # App is running

    # Cleanup here
    print("Shutting down and cleaning up...")
    if gen_pipe:
        del gen_pipe  # remove reference
        torch.cuda.empty_cache()
        print("GPU memory cleared.")

app = FastAPI(lifespan=lifespan)
# Save the last user input (in-memory for simplicity)
last_input = ""
gen_pipe = None  # Global reference

# Health Check 
@app.get("/")
def root():
    return {"message": "ok"}


@app.post("/input") # curl -X POST -F "user_input=prompt here" http://127.0.0.1:8000/input
def receive_input(user_input: str = Form(...)):
    global last_input
    last_input = user_input
    return {"message": f"Input received: {user_input}"}

@app.get("/image")  # http://127.0.0.1:8000/image
def get_image():
    global last_input
    if not last_input:
        # Option 1: Raise an HTTPException if no input is provided yet
        raise HTTPException(status_code=400, detail="No prompt has been provided yet. Please use the /input endpoint first.")
        # Option 2: Fallback to a default image or message if no input is present
        # return FileResponse("static/default_image.png", media_type="image/png") # You'd need a default image
        # return {"message": "No prompt provided. Please submit a prompt via /input first."}

    try:
        image = gen_pipe(
            prompt=last_input,
            num_inference_steps=28,
            guidance_scale=3.5,
        ).images[0]

        # Sanitize the filename to prevent issues with invalid characters
        sanitized_filename = "".join(c if c.isalnum() or c in (' ', '.', '_', '-') else '_' for c in last_input)
        image_path = f"generated_images/{sanitized_filename}.png" # It's good practice to save to a specific directory

        # Ensure the directory exists
        os.makedirs("generated_images", exist_ok=True)

        image.save(image_path)
        return FileResponse(image_path, media_type="image/png")
    except Exception as e:
        # Catch any errors during image generation (e.g., CUDA out of memory, model issues)
        print(f"Error during image generation: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating image: {e}")

# gen_pipe = StableDiffusion3Pipeline.from_pretrained("stabilityai/stable-diffusion-3.5-medium", 
#                                                 torch_dtype=torch.bfloat16, 
#                                                 text_encoder_3=None, #Drop T5 text encoder to decrease memory requirements
#                                                 tokenizer_3=None, #Drop T5 text encoder to decrease memory requirements
#                                                 token = hf_token
#                                                 )
# gen_pipe = gen_pipe.to("cuda")

# test hard coded image
# @app.get("/image") # http://127.0.0.1:8000/image
# def get_image():
#     image_path = "static/cathat.jpg"
#     return FileResponse(image_path, media_type="image/jpeg")


# comment this out first 
# @app.get("/image") # http://127.0.0.1:8000/image
# def get_image():
#     image = gen_pipe(
#         prompt=last_input,
#         num_inference_steps=28,
#         guidance_scale=3.5,
#     ).images[0]

#     image_path = f"{last_input}.png"
#     image.save(image_path)
#     return FileResponse(image_path, media_type="image/png")