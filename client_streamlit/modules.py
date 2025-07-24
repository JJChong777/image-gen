import streamlit as st
import requests
from io import BytesIO

from datetime import datetime
import pytz
import random
import string
from enum import Enum

API_URL = "http://fast-api:8000"

class RequestType(str, Enum):
    GET = "GET"
    POST = "POST"

def make_safe_request(req_type: RequestType, url: str, payload: dict = None):
    try:
        if req_type == RequestType.GET:
            # For GET, payload goes into params
            response = requests.get(url, params=payload)
        elif req_type == RequestType.POST:
            # For POST, payload goes into json body
            response = requests.post(url, data=payload)
        return True, response
    except requests.exceptions.HTTPError as http_err:
        error_msg = f"HTTP error occurred: {http_err}"
        # Check if a response object exists before accessing its attributes
        if http_err.response is not None:
            if http_err.response.status_code is not None: # status_code itself can be None in some edge cases
                error_msg += f", Status Code: {http_err.response.status_code}"
            # Use http_err.response.text to get the body content, not just http_err.response itself
            if http_err.response.text: # Check if response_text is not empty
                error_msg += f", Response Text: {http_err.response.text}"
        return False, error_msg
    except requests.exceptions.ConnectionError:
        return False, "Connection error. Is the server running or URL correct?"
        
    except requests.exceptions.Timeout:
        return False, "Timeout error: The request took too long."
    except requests.exceptions.RequestException as err:
        return False, f"An unexpected request error occurred: {err}"
    except Exception as e:
        return False, f"An unexpected error occurred: {e}"



def generate_file_name():
    # Singapore time
    sg_tz = pytz.timezone("Asia/Singapore")
    now = datetime.now(sg_tz)

    # Format: YYYYMMDD_HHMMSS
    timestamp = now.strftime("%Y%m%d_%H%M%S")

    # 4-char random hash
    random_hash = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

    # Final filename
    filename = f"{timestamp}_{random_hash}"
    return filename

def display_img_with_download(img_bytes, name):
    if img_bytes:
        st.image(BytesIO(img_bytes), caption=name, width=500)
        st.download_button(
            label="Download Image",
            data=img_bytes,
            file_name=f"{name.replace(' ', '_')}.jpg",
            mime="image/jpeg",
            on_click="ignore"
        )
    else:
        st.error("Passed bad data into display image")

def display_img_with_download_thumbnail(image_data, name):
    if image_data:
        # Create a thumbnail-style card layout
        with st.container():
            with st.columns([1, 4, 1])[1]:  # Center column
                st.image(image_data, caption=name, use_container_width=True)  # Thumbnail size
                st.download_button(
                    label=f"Download {name}",
                    data=image_data,
                    file_name=f"{name.replace(' ', '_')}.jpg",
                    mime="image/jpeg",
                    key=f"download_{name}",
                    on_click="ignore"
                )








