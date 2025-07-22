# image-gen

# Run test client on its own (not connected to API)
- `cd client_streamlit`
- `pip install -r requirements.txt`
- `python -m streamlit run app.py`

# Run server on its own (run API, not sure if it works)
- `cd server_api`
- `pip install -r requirements.txt`
- `fastapi dev main.py`

if fastapi can install onto PATH, otherwise use the same python -m in front trick

# Run both using docker (exprimental, most likely will not work)
make sure you are in the main directory
- `docker compose up --build`

