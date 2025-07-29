import torch
from diffusers import FluxKontextPipeline
from diffusers.utils import load_image
from PIL import Image

edit_pipe = FluxKontextPipeline.from_pretrained("black-forest-labs/FLUX.1-Kontext-dev", torch_dtype=torch.bfloat16)
edit_pipe.to("cuda")

input_image = load_image("https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/diffusers/cat.png")

image = edit_pipe(
  image=input_image,
  prompt="Add a hat to the cat",
  guidance_scale=2.5
).images[0]

# Save the edited image locally
output_path = "cat_with_hat.png"
image.save(output_path)

print(f"Image saved to {output_path}")