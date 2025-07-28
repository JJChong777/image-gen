# image-gen

# Run test client on its own (not connected to API)
- `cd client_streamlit`
- `pip install -r requirements.txt`
- `python -m streamlit run app.py`

# Setup before running server (Important)
- Download WSL 2 Ubuntu 22.04 from Windows Store https://apps.microsoft.com/detail/9pn20msr04dw?hl=en-US&gl=US
- Download docker desktop https://www.docker.com/products/docker-desktop/
- Create a file in C:\Users\YourUsername\.wslconfig and write

[wsl2]
memory=20GB  # Max RAM WSL2/Docker can use  
processors=4  # Number of CPUs  
swap=8GB  # Swap file size  
localhostForwarding=true  

to allow stable diffusion to eat all your system memory

# Run server on docker
- `docker compose up --build fast-api`
- Wait for Model to load after `Loading Model...` logged in your terminal
This is the ideal output you should get
etching 18 files: 100%|██████████| 18/18 [04:21<00:00, 14.50s/it]
Loading pipeline components...: 100%|██████████| 7/7 [00:02<00:00,  3.35it/s]
fast-api       | INFO:     Application startup complete.
fast-api       | Model loaded successfully.
fast-api       | INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)

- Test if the server is up using these commands

Check if server is healthy: curl http://localhost:8000/
Expected output:
{"message": "ok"}

Send prompt: curl -X POST -F "user_input=cat in a hat" http://localhost:8000/input 
Expected output:
{"message":"Input received: cat in a hat"}

Get image: curl -o output.png http://localhost:8000/image   
Expected output:
% Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed  
100 1612k  100 1612k    0     0  15545      0  0:01:46  0:01:46 --:--:--  406k 

# Run both using docker (works but not tested)
make sure you are in the main directory
- `docker compose up --build`

