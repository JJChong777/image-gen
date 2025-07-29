# image-gen

# Run test client on its own (not connected to API)
- `cd client_streamlit`
- `pip install -r requirements.txt`
- `python -m streamlit run app.py`

# Setup before running server (Important)
Important: You need at least 48 GB of RAM to run this because Stable Diffusion eats 20GB already

- Download WSL 2 Ubuntu 22.04 from Windows Store https://apps.microsoft.com/detail/9pn20msr04dw?hl=en-US&gl=US
- Download docker desktop https://www.docker.com/products/docker-desktop/
- Create a file in C:/Users/YourUsername/.wslconfig (the file is called .wslconfig in the directory and write

`[wsl2]`    
`memory=20GB  # Max RAM WSL2/Docker can use`    
`processors=4  # Number of CPUs`    
`swap=8GB  # Swap file size`    
`localhostForwarding=true`    

to allow stable diffusion to eat all your system memory  

add .env file in the folder and add your HF token (ask me or Teppei for a HF token) if you don't have and write HF_TOKEN = your token here  
or you can apply for one following the instructions here https://huggingface.co/docs/hub/en/security-tokens and apply for a Read token (fine grained is a mistake)  

# Run server on docker
- `docker compose up --build fast-api`

(for stable diffusion image generation model)  
- Wait for stable diffusion image generation model to load after `Loading image generation model...` logged in your terminal  (takes very long (approx 5min), you can go grab a coffee first)  
- Open task manager and watch all your memory get eaten by stable diffusion (20GB of RAM gone)  
This is the ideal output you should get  
etching 18 files: 100%|██████████| 18/18 [04:21<00:00, 14.50s/it]  
Loading pipeline components...: 100%|██████████| 7/7 [00:02<00:00,  3.35it/s]  
fast-api       | INFO:     Application startup complete.  
fast-api       | Image generation model loaded successfully.  
fast-api       | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)

(experimental image editing model)
- Wait for FLUX.1-Kontext-dev to load after `Loading image editing model...` logged in your terminal  (takes extremely long (approx 30+min), you can go eat lunch first)
- Open task manager and watch all your memory get eaten by the Flux Kontext model (30+GB of RAM gone)
This is the ideal output you should get
Fetching 23 files: 100%|██████████| 23/23 [31:33<00:00, 82.31s/it]
Loading pipeline components...:  29%|██▊       | 2/7 [00:02<00:05,  1.06s/it]You set `add_prefix_space`. The tokenizer needs to be converted from the slow tokenizers
Loading checkpoint shards: 100%|██████████| 3/3 [00:00<00:00, 13.27it/s]it/s]  
Loading checkpoint shards: 100%|██████████| 2/2 [00:00<00:00, 18.59it/s]it/s]  
Loading pipeline components...: 100%|██████████| 7/7 [00:02<00:00,  2.50it/s]  
fast-api       | Image generation model loading failed: 'FluxKontextPipeline' object has no attribute 'unet'  
I have no idea why pipe.to('cuda') is giving issues, this needs to be patched  

- Test if the server is up using these commands  

Check if server is healthy: `curl http://localhost:8000/`    
Expected output:  
{"message": "ok"}  

Send prompt (for image generation): `curl -X POST -F "user_input=cat in a hat" http://localhost:8000/input`    
Expected output:  
{"message":"Input received: cat in a hat"}  

Get image generated: `curl -o output.png http://localhost:8000/image`     
Expected output:
% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed  
100 1612k  100 1612k    0     0  15545      0  0:01:46  0:01:46 --:--:--  406k 

Send prompt (for image editing): `curl -X POST "http://localhost:8000/input_image" -F "user_input=make this cat robotic" -F "image=@\"server_api/generated_images/cat in a hat.png\""`  
Expected output:
Not sure yet because error occured: image input received should be a URL linking to an image, a local path, or a PIL image, not bytes. 

Get image edited (in theory): `curl -o output.png http://localhost:8000/edit`     
Expected output:
probably the same as image generated in theory, but not tested because of above error  

# Run both using docker (works but not tested)
make sure you are in the main directory
- `docker compose up --build`

