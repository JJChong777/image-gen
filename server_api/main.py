from fastapi import FastAPI, Form, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from PIL import Image
import os
import torch
# from diffusers import StableDiffusion3Pipeline
from diffusers import FluxKontextPipeline
from diffusers.utils import load_image
import time
import gc
from io import BytesIO

start_time = time.time()
hf_token = os.environ.get("HF_TOKEN")
if not hf_token:
    raise ValueError("HF_TOKEN environment variable is not set. Please set it to your Hugging Face API token.")

# Save the last user input, image and initialize the pipes (in-memory for simplicity)
last_input = ""
last_input_image = None
# gen_pipe = None  
edit_pipe = None 

# ignore all the slow HF models loading first for frontend testing
# @asynccontextmanager
# async def lifespan(app: FastAPI):
    # global gen_pipe
    # try:
    #     print("Loading image generation model (stable-diffusion-3.5-medium)...")
    #     gen_pipe = StableDiffusion3Pipeline.from_pretrained( 
    #         "stabilityai/stable-diffusion-3.5-medium",
    #         torch_dtype=torch.bfloat16,
    #         text_encoder_3=None,
    #         tokenizer_3=None,
    #         token=hf_token
    #     )
    #     gen_pipe = gen_pipe.to("cuda")
    #     print("Image generation model (stable-diffusion-3.5-medium) loaded successfully.")
    # except Exception as e:
    #     print(f"Image generation model (stable-diffusion-3.5-medium) loading failed: {e}")
    
    # global edit_pipe
    # try:
    #     print("Loading image editing model (FLUX.1-Kontext-dev)...")
    #     edit_pipe = FluxKontextPipeline.from_pretrained(
    #         "black-forest-labs/FLUX.1-Kontext-dev", 
    #         torch_dtype=torch.bfloat16, 
    #         token=hf_token
    #     )
    #     edit_pipe.to("cuda")
    #     print(f"Edit pipe dtype: {edit_pipe.unet.dtype}")
    #     print("Image editing model (FLUX.1-Kontext-dev) loaded successfully.")
    # except Exception as e:
    #     print(f"Image generation model (FLUX.1-Kontext-dev) loading failed: {e}")

    # yield  # App is running

    # # Cleanup here
    # try:
    #     # if 'gen_pipe' in globals() and gen_pipe:
    #     #     del gen_pipe
    #     if 'edit_pipe' in globals() and edit_pipe:
    #         del edit_pipe
    # except Exception as e:
    #     print(f"Error during cleanup: {e}")

    # gc.collect()

    # torch.cuda.empty_cache()
    # torch.cuda.ipc_collect()
    # print("Memory fully cleared.")

# app = FastAPI(lifespan=lifespan)
app = FastAPI()


# Health Check 
@app.get("/")
def root():
    return {"message": "ok"}


# @app.post("/input") # curl -X POST -F "user_input=prompt here" http://127.0.0.1:8000/input
# def receive_input(user_input: str = Form(...)):
#     global last_input
#     last_input = user_input
    # print(f"Received prompt: {last_input}")
#     return {"message": f"Prompt received: {user_input}"}

# @app.get("/image")  # http://127.0.0.1:8000/image
# def get_gen_image():
#     global last_input
#     # Raise an HTTPException if no input or image has been provided yet
#     if not last_input:
#         raise HTTPException(status_code=400, detail="No prompt has been provided yet. Please use the /input endpoint first.")

#     try:
#         image = gen_pipe(
#             prompt=last_input,
#             num_inference_steps=28,
#             guidance_scale=3.5,
#         ).images[0]

#         # Sanitize the filename to prevent issues with invalid characters
#         sanitized_filename = "".join(c if c.isalnum() or c in (' ', '.', '_', '-') else '_' for c in last_input)
#         image_path = f"generated_images/{sanitized_filename}.png" # It's good practice to save to a specific directory

#         # Ensure the directory exists
#         os.makedirs("generated_images", exist_ok=True)

#         image.save(image_path)
#         last_input = ""
#         return FileResponse(image_path, media_type="image/png")
#     except Exception as e:
#         # Catch any errors during image generation (e.g., CUDA out of memory, model issues)
#         print(f"Error during image generation: {e}")
#         last_input = ""
#         raise HTTPException(status_code=500, detail=f"Error generating image: {e}")

# @app.post("/input_image") # curl -X POST "http://localhost:8000/input_image" -F "user_input=make this cat robotic" -F "image=@\"server_api/generated_images/cat in a hat.png\""
# async def receive_input_image(user_input: str = Form(...), image: UploadFile = File(...)):
#     global last_input
#     global last_input_image
#     last_input = user_input
#     # image file name setting
#     image_filename = image.name or "uploaded_image.png"
#     # Read image bytes
#     # TODO: The image input received should be a URL linking to an image, a local path, or a PIL image, not bytes.
#     # Fix this line later 
#     image_bytes = await image.read()
#     # Convert bytes to PIL.Image
#     pil_image = Image.open(BytesIO(image_bytes)).convert("RGB")
#     user_image = load_image(pil_image)
#     last_input_image = user_image
#     # Ensure the directory exists
#     image_path = f"uploaded_images/{image_filename}"
#     os.makedirs("uploaded_images", exist_ok=True)
#     # Save it to disk
#     image.save(image_path)
#     # with open(f"uploaded_images/{image.name}", "wb") as f:
#     #     f.write(image_bytes)
    
#     print(f"Received prompt: {last_input}, Received image: {image.name}")
#     return {"message": f"Prompt received: {user_input}, File received: {image.name}"}

@app.post("/input_image")
async def receive_input_image(user_input: str = Form(...), image: UploadFile = File(...)):
    global last_input
    global last_input_image
    
    print(f"Received user_input: {user_input}")
    print(f"Received image filename: {image.filename}")
    print(f"Received image content_type: {image.content_type}")
    print(f"Received image size: {image.size}")
    
    try:
        last_input = user_input
        
        # Store the filename before reading
        image_filename = image.filename or "uploaded_image.png"
        
        # Read image bytes
        image_bytes = await image.read()
        print(f"Read {len(image_bytes)} bytes from uploaded file")
        
        # Check if we actually got image data
        if len(image_bytes) == 0:
            raise HTTPException(status_code=422, detail="Uploaded file is empty")
        
        # Convert bytes to PIL.Image
        try:
            pil_image = Image.open(BytesIO(image_bytes)).convert("RGB")
            print(f"Successfully created PIL image: {pil_image.size}")
        except Exception as pil_error:
            print(f"Error creating PIL image: {str(pil_error)}")
            raise HTTPException(status_code=422, detail=f"Invalid image format: {str(pil_error)}")
        
        # Use load_image function (modify based on what your function expects)
        try:
            user_image = load_image(pil_image)  # or load_image(image_bytes)
            last_input_image = user_image
            print("Successfully processed image with load_image function")
        except Exception as load_error:
            print(f"Error in load_image function: {str(load_error)}")
            # Continue anyway, just store the PIL image
            last_input_image = pil_image
        
        # Ensure the directory exists
        os.makedirs("uploaded_images", exist_ok=True)
        
        # Save PIL image to disk
        image_path = f"uploaded_images/{image_filename}"
        pil_image.save(image_path)
        print(f"Saved image to: {image_path}")
        
        print(f"Successfully processed: {last_input}, {image_filename}")
        return {"message": f"Prompt received: {user_input}, File received: {image_filename}"}
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Unexpected error processing image: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# hardcoded image editing API to test proper link with FastAPI (for frontend testing)
@app.get("/edit")  # http://127.0.0.1:8000/image
def get_edit_image():
    global last_input
    global last_input_image
    # Raise an HTTPException if no input or image has been provided yet
    if not last_input:
        raise HTTPException(status_code=400, detail="No prompt has been provided in the /input_image endpoint. Please try again")
    if not last_input_image:
        raise HTTPException(status_code=400, detail="No image has been provided in the /input_image endpoint. Please try again")
    # Return a hardcoded image file
    image_path = "server_api/generated_images/cat in a hat.png"  # Change as needed
    return FileResponse(image_path, media_type="image/png", filename="robot_cat.png")




# actual image editing API to test and load later, ditch first
# @app.get("/edit")  # http://127.0.0.1:8000/image
# def get_edit_image():
#     global last_input
#     global last_input_image
#     # Raise an HTTPException if no input or image has been provided yet
#     if not last_input:
#         raise HTTPException(status_code=400, detail="No prompt has been provided in the /input_image endpoint. Please try again")
#     if not last_input_image:
#         raise HTTPException(status_code=400, detail="No image has been provided in the /input_image endpoint. Please try again")

#     try:
#         image = edit_pipe(
#             image=last_input_image,
#             prompt=last_input,
#             guidance_scale=2.5
#         ).images[0]

#         # Sanitize the filename to prevent issues with invalid characters
#         sanitized_filename = "".join(c if c.isalnum() or c in (' ', '.', '_', '-') else '_' for c in last_input)
#         image_path = f"edited_images/{sanitized_filename}.png" # It's good practice to save to a specific directory

#         # Ensure the directory exists
#         os.makedirs("edited_images", exist_ok=True)

#         image.save(image_path)
#         last_input = ""
#         last_input_image = None
#         return FileResponse(image_path, media_type="image/png")
#     except Exception as e:
#         # Catch any errors during image generation (e.g., CUDA out of memory, model issues)
#         print(f"Error during image generation: {e}")
#         last_input = ""
#         last_input_image = None
#         raise HTTPException(status_code=500, detail=f"Error generating image: {e}")