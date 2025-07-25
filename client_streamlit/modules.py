import streamlit as st
import requests
from io import BytesIO

from datetime import datetime
import pytz
import random
import string



def fetch_image_from_url(name, url):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"}
    try:
        response = requests.get(url, headers=headers, )  # Add timeout for safety
        response.raise_for_status()  # Raise an exception for HTTP errors
    except requests.exceptions.HTTPError as http_err:
        st.error(f"HTTP error occurred while downloading image '{name}': {http_err}")
        return None
    except requests.exceptions.ConnectionError:
        st.error(f"Connection error occurred while accessing '{url}'. Please check your internet connection or the URL.")
        return None
    except requests.exceptions.Timeout:
        st.error(f"Request timed out while accessing '{url}'.")
        return None
    except requests.exceptions.RequestException as err:
        st.error(f"An unexpected error occurred while downloading image '{name}': {err}")
        return None
    else:
        image_data = BytesIO(response.content)
        return image_data


def display_img_with_download(name, url):
    image_data = fetch_image_from_url(name, url)
    if image_data:
        st.image(image_data, caption=name, width=500)
        st.download_button(
            label="Download Image",
            data=image_data,
            file_name=f"{name.replace(' ', '_')}.jpg",
            mime="image/jpeg",
            on_click="ignore"
        )

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

def display_img_with_download_thumbnail(name, url):
    image_data = fetch_image_from_url(name,url)

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
