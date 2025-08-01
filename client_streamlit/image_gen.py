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
    
def main():
    st.title("Generate a image with AI")

    if "messages_gen" not in st.session_state:
        st.session_state.messages_gen = [{"role": "assistant", "content": "Hi, I'm the Image Generation Chatbot! Type in a prompt to get started", "ok":True, "img_name": None}]
    if "image_cache_gen" not in st.session_state:
        st.session_state.image_cache_gen = {}
    if "chat_disabled_gen" not in st.session_state:
        st.session_state.chat_disabled_gen = False
    if "last_prompt_text_gen" not in st.session_state:
        st.session_state.last_prompt_text_gen = False

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
                st.session_state.chat_input_gen = selected_question

    prompt = st.chat_input(placeholder="Type your image generation prompt here...",
        accept_file=False,
        disabled=st.session_state.chat_disabled_gen,
        key='chat_input_gen'
    )

    for msg in st.session_state.messages_gen:
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
                        img_bytes = st.session_state.image_cache_gen.get(img_name)
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
        st.session_state.chat_disabled_gen = True
        st.session_state.last_prompt_text_gen = prompt
        st.rerun()


    if st.session_state.last_prompt_text_gen:
        last_prompt_text_gen = st.session_state.last_prompt_text_gen
        with st.chat_message("user"):
            st.markdown(last_prompt_text_gen)
        st.session_state.messages_gen.append({"role": "user", "content": last_prompt_text_gen})
        with st.chat_message("assistant"):
            with st.spinner("Sending prompt to server..."):
                time.sleep(5) # uncomment if testing spinner or delay
                success, prompt_response = send_prompt(last_prompt_text_gen)
                if success:
                    message = prompt_response.json().get("message")
                    st.success(message)
                else:
                    error_msg = f"Failed to send prompt: {prompt_response}"
                    st.session_state.messages_gen.append({"role": "assistant", "content": error_msg, "ok": False})
                    st.session_state.chat_disabled_gen = False
                    st.session_state.last_prompt_text_gen = None
                    st.rerun()
            with st.spinner("Fetching image from server..."):
                time.sleep(5) # uncomment if testing spinner or delay
                success, img_response = fetch_image()
                if success: 
                    img_name = generate_file_name()
                    img_bytes = img_response.content
                    st.session_state.image_cache_gen[img_name] = img_bytes
                    st.session_state.messages_gen.append({"role": "assistant", "content": None, "ok": True, "img_name": img_name})
                    st.session_state.chat_disabled_gen = False
                    st.session_state.last_prompt_text_gen = None
                    st.rerun()
                else:
                    error_msg = f"Failed to fetch generated image: {prompt_response}"
                    st.session_state.messages_gen.append({"role": "assistant", "content": error_msg, "ok": False})
                    st.session_state.chat_disabled_gen = False
                    st.session_state.last_prompt_text_gen = None
                    st.rerun()

if __name__ == "__main__":
    main()