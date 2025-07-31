import streamlit as st
from modules import display_img_with_download, RequestType, make_safe_request, API_URL, generate_file_name
import time
from io import BytesIO

def send_prompt(prompt: str):
    input_url = f"{API_URL}/input"
    payload = {'user_input': f'{prompt}'}
    return make_safe_request(RequestType.POST, input_url, payload)

def fetch_image():
    image_url = f"{API_URL}/image"
    return make_safe_request(RequestType.GET, image_url)

def send_edit_image_prompt(prompt: str, image_file):
    input_url = f"{API_URL}/input_image"
    
    # Debug: Check what type of object we're dealing with
    print(f"Image file type: {type(image_file)}")
    print(f"Image file name: {getattr(image_file, 'name', 'No name attribute')}")
    
    try:
        # If it's a Streamlit UploadedFile, we need to handle it properly
        if hasattr(image_file, 'read'):
            # Reset file pointer to beginning
            image_file.seek(0)
            files = {
                'image': (image_file.name, image_file, image_file.type)
            }
        else:
            # If it's already bytes or another format
            files = {
                'image': ('uploaded_image.png', image_file, 'image/png')
            }
        
        payload = {'user_input': prompt}
        
        # Use requests to send multipart form data
        import requests
        response = requests.post(input_url, data=payload, files=files)
        
        if response.status_code == 200:
            return True, response
        else:
            print(f"Error response: {response.status_code} - {response.text}")
            return False, f"HTTP {response.status_code}: {response.text}"
            
    except Exception as e:
        print(f"Exception in send_edit_image_prompt: {str(e)}")
        return False, f"Exception: {str(e)}"

def fetch_edited_image():
    image_url = f"{API_URL}/edit"
    return make_safe_request(RequestType.GET, image_url)

# reset everything back to the way it was (emergency button)
def clear_session_state():
    for key in st.session_state.keys():
        del st.session_state[key]
    
def main():
    st.title("Generate a image")

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hi, I'm the Image Generation Chatbot! Type in a prompt to get started", "ok":True, "img_name": None}]
    if "image_cache" not in st.session_state:
        st.session_state.image_cache = {}
    if "chat_disabled" not in st.session_state:
        st.session_state.chat_disabled = False
    if "last_prompt_text" not in st.session_state:
        st.session_state.last_prompt_text = False
    if "last_prompt_img" not in st.session_state:
        st.session_state.last_prompt_img = False



    suggested_questions = [
        "Cat with a hat",
        "F16 plane in blue sky",
        "Happy birthday strawberry shortcake"
    ]

    with st.chat_message("assistant"):
        st.markdown("Try asking:")
        with st.form("suggested_question_form"):
            selected_question = st.selectbox(
                "What suggested question would you like to ask?",
                suggested_questions,
                index=None,
                placeholder="Select suggested question...",
            )
            submitted = st.form_submit_button('Submit Question')
            if submitted:
                st.session_state.chat_input = selected_question

    prompt = st.chat_input(placeholder="Type your image generation prompt here...",
        accept_file=True,
        file_type=["jpg", "jpeg", "png"],
        disabled=st.session_state.chat_disabled,
        key="chat_input"
        )

    for msg in st.session_state.messages:
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
        elif msg["role"] == "assistant":
                if not msg["ok"]:
                    with st.chat_message("assistant"):
                        st.error(msg["content"])
                else:
                    if msg["img_name"]:
                        img_name = msg["img_name"]
                        img_bytes = st.session_state.image_cache.get(img_name)
                        if img_bytes:
                            with st.chat_message("assistant"):
                                display_img_with_download(img_bytes, img_name)
                        else:
                            st.error(f"Image with name: {img_name} not found in image cache")
                    if msg["content"]:
                        with st.chat_message("assistant"):
                            st.markdown(msg["content"])
        else:
            st.error("Message with invalid role") 

    # clear session state button
    if (len(st.session_state.messages) > 1):
        st.button("Clear Session State", key="clear_chat_button", on_click=clear_session_state)

    if prompt:
        st.session_state.chat_disabled = True
        st.session_state.last_prompt_text = prompt.text
        if prompt.files:
            st.session_state.last_prompt_img = prompt.files[0]
        st.rerun()
    
    if st.session_state.last_prompt_img and st.session_state.last_prompt_text:
        last_prompt_text = st.session_state.last_prompt_text
        last_prompt_img = st.session_state.last_prompt_img
        
        with st.chat_message("user"):
            st.markdown(f"{last_prompt_text}, image attached: {last_prompt_img.name}")
        
        # Add user message to session state
        st.session_state.messages.append({
            "role": "user", 
            "content": f"{last_prompt_text}, image attached: {last_prompt_img.name}"
        })
        
        with st.chat_message("assistant"):
            with st.spinner("Sending prompt and image file to server..."):
                success, prompt_response = send_edit_image_prompt(last_prompt_text, last_prompt_img)
                
                if success:
                    message = prompt_response.json().get("message")
                    st.success(message)
                else:
                    error_msg = f"Failed to send prompt and image: {prompt_response}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg, "ok": False})
                    st.session_state.chat_disabled = False
                    st.session_state.last_prompt_text = None
                    st.session_state.last_prompt_img = None
                    st.rerun()
                    
            with st.spinner("Fetching edited image from server..."):
                success, img_response = fetch_edited_image()
                if success: 
                    # Check if response is actually an image
                    content_type = img_response.headers.get('content-type', '')
                    if not content_type.startswith('image/'):
                        error_msg = f"Server returned non-image content: {content_type}"
                        if hasattr(img_response, 'text'):
                            error_msg += f" ,Response text: {img_response.text[:500]}"
                        st.session_state.messages.append({"role": "assistant", "content": error_msg, "ok": False})
                        st.session_state.chat_disabled = False
                        st.session_state.last_prompt_text = None
                        st.session_state.last_prompt_img = None
                        st.rerun()
                        
                    img_name = generate_file_name()
                    img_bytes = img_response.content
                    st.session_state.image_cache[img_name] = img_bytes
                    st.session_state.messages.append({"role": "assistant", "content": None, "ok": True, "img_name": img_name})
                    st.session_state.chat_disabled = False
                    st.session_state.last_prompt_text = None
                    st.session_state.last_prompt_img = None
                    st.rerun()
                else:
                    error_msg = f"Failed to fetch edited image: {img_response}"
                    st.error(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg, "ok": False})
                    st.session_state.chat_disabled = False
                    st.session_state.last_prompt_text = None
                    st.session_state.last_prompt_img = None
                    st.rerun()



    elif st.session_state.last_prompt_text:
        last_prompt_text = st.session_state.last_prompt_text
        with st.chat_message("user"):
            st.markdown(last_prompt_text)
        st.session_state.messages.append({"role": "user", "content": last_prompt_text})
        with st.chat_message("assistant"):
            with st.spinner("Sending prompt to server..."):
                time.sleep(5) # uncomment if testing spinner or delay
                success, prompt_response = send_prompt(last_prompt_text)
                if success:
                    message = prompt_response.json().get("message")
                    st.success(message)
                else:
                    error_msg = f"Failed to send prompt: {prompt_response}"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg, "ok": False})
                    st.session_state.chat_disabled = False
                    st.session_state.last_prompt_text = None
                    st.session_state.last_prompt_img = None
                    st.rerun()
            with st.spinner("Fetching image from server..."):
                time.sleep(5) # uncomment if testing spinner or delay
                success, img_response = fetch_image()
                if success: 
                    # SUCCESS
                    img_name = generate_file_name()
                    img_bytes = img_response.content
                    st.session_state.image_cache[img_name] = img_bytes
                    st.session_state.messages.append({"role": "assistant", "content": None, "ok": True, "img_name": img_name})
                    st.session_state.chat_disabled = False
                    st.session_state.last_prompt_text = None
                    st.rerun()
                    # SUCCESS
                else:
                    error_msg = f"Failed to fetch generated image: {prompt_response}"
                    st.session_state.messages.append({"role": "assistant", "content": error_msg, "ok": False})
                    st.session_state.chat_disabled = False
                    st.session_state.last_prompt_text = None
                    st.session_state.last_prompt_img = None
                    st.rerun()

if __name__ == "__main__":
    main()