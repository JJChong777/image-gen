import streamlit as st
from modules import display_img_with_download, RequestType, make_safe_request, API_URL, generate_file_name
import time
from io import BytesIO

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
    
def main():
    st.title("Edit a image with AI")

    if "messages_edit" not in st.session_state:
        st.session_state.messages_edit = [{"role": "assistant", "content": "Hi, I'm the Image Editing Chatbot! Type in a prompt to get started", "ok":True, "img_name": None}]
    if "image_cache_edit" not in st.session_state:
        st.session_state.image_cache_edit = {}
    if "chat_disabled_edit" not in st.session_state:
        st.session_state.chat_disabled_edit = False
    if "last_prompt_text_edit" not in st.session_state:
        st.session_state.last_prompt_text_edit = False
    if "last_prompt_img_edit" not in st.session_state:
        st.session_state.last_prompt_img_edit = False

    suggested_questions = [
        "Add a hat to the cat",
        "Add contrails behind the plane",
        "Add birthday candles to the cake"
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
                st.session_state.chat_input_edit = selected_question
    
    prompt = st.chat_input(placeholder="Type your image generation prompt here...",
        accept_file=True,
        file_type=["jpg", "jpeg", "png"],
        disabled=st.session_state.chat_disabled_edit,
        key='chat_input_edit'
        )

    for msg in st.session_state.messages_edit:
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
                        img_bytes = st.session_state.image_cache_edit.get(img_name)
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

    if prompt:
        st.session_state.chat_disabled_edit = True
        st.session_state.last_prompt_text_edit = prompt.text
        if prompt.files:
            st.session_state.last_prompt_img_edit = prompt.files[0]
        # Add user message to session state
        st.session_state.messages_edit.append({
            "role": "user", 
            "content": f"edit prompt: {prompt.text if prompt.text else None}, image attached: {prompt.files[0].name if prompt.files else None}"
        })
        st.rerun()
    
    if st.session_state.last_prompt_img_edit and st.session_state.last_prompt_text_edit:
        last_prompt_text_edit = st.session_state.last_prompt_text_edit
        last_prompt_img_edit = st.session_state.last_prompt_img_edit
        
        with st.chat_message("assistant"):
            with st.spinner("Sending prompt and image file to server..."):
                success, prompt_response = send_edit_image_prompt(last_prompt_text_edit, last_prompt_img_edit)
                
                if success:
                    message = prompt_response.json().get("message")
                    st.success(message)
                else:
                    error_msg = f"Failed to send prompt and image: {prompt_response}"
        
                    st.session_state.messages_edit.append({"role": "assistant", "content": error_msg, "ok": False})
                    st.session_state.chat_disabled_edit = False
                    st.session_state.last_prompt_text_edit = None
                    st.session_state.last_prompt_img_edit = None
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
                        st.session_state.messages_edit.append({"role": "assistant", "content": error_msg, "ok": False})
                        st.session_state.chat_disabled_edit = False
                        st.session_state.last_prompt_text_edit = None
                        st.session_state.last_prompt_img_edit = None
                        st.rerun()
                        
                    img_name = generate_file_name()
                    img_bytes = img_response.content
                    st.session_state.image_cache_edit[img_name] = img_bytes
                    st.session_state.messages_edit.append({"role": "assistant", "content": None, "ok": True, "img_name": img_name})
                    st.session_state.chat_disabled_edit = False
                    st.session_state.last_prompt_text_edit = None
                    st.session_state.last_prompt_img_edit = None
                    st.rerun()
                else:
                    error_msg = f"Failed to fetch edited image: {img_response}"
                    st.session_state.messages_edit.append({"role": "assistant", "content": error_msg, "ok": False})
                    st.session_state.chat_disabled_edit = False
                    st.session_state.last_prompt_text_edit = None
                    st.session_state.last_prompt_img_edit = None
                    st.rerun()
    
    elif st.session_state.last_prompt_text_edit:
        error_msg = f"Please attach a image to edit with AI"
        st.session_state.messages_edit.append({"role": "assistant", "content": error_msg, "ok": False})
        st.session_state.chat_disabled_edit = False
        st.session_state.last_prompt_text_edit = None
        st.session_state.last_prompt_img_edit = None
        st.rerun()

    elif st.session_state.last_prompt_img_edit:
        error_msg = f"Please write a prompt to specify how image should be edited with AI"
        st.session_state.messages_edit.append({"role": "assistant", "content": error_msg, "ok": False})
        st.session_state.chat_disabled_edit = False
        st.session_state.last_prompt_text_edit = None
        st.session_state.last_prompt_img_edit = None
        st.rerun()

if __name__ == "__main__":
    main()