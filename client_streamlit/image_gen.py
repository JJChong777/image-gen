import streamlit as st
from modules import display_img_with_download, RequestType, make_safe_request, API_URL, generate_file_name
import time


def send_prompt(prompt):
    input_url = f"{API_URL}/input"
    payload = {'user_input': f'{prompt}'}
    return make_safe_request(RequestType.POST, input_url, payload)

def fetch_image():
    image_url = f"{API_URL}/image"
    return make_safe_request(RequestType.GET, image_url)

    
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

    prompt = st.chat_input(placeholder="Type your image generation prompt here...",
        accept_file=True,
        file_type=["jpg", "jpeg", "png"],
        disabled=st.session_state.chat_disabled
        )

    suggested_questions = [
        "Generate an image of a cat with a hat"
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
                prompt = selected_question

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

    if prompt:
        st.session_state.chat_disabled = True
        st.session_state.last_prompt_text = prompt.text
        st.rerun()
    
    if st.session_state.last_prompt_text:
        last_prompt_text = st.session_state.last_prompt_text
        with st.chat_message("user"):
            st.markdown(last_prompt_text)
        st.session_state.messages.append({"role": "user", "content": last_prompt_text})
        with st.chat_message("assistant"):
            with st.spinner("Sending prompt to server..."):
                # time.sleep(2) # uncomment if testing spinner or delay
                success, prompt_response = send_prompt(last_prompt_text)
                if success:
                    message = prompt_response.json().get("message")
                    st.success(message)
                else:
                    st.session_state.messages.append({"role": "assistant", "content": prompt_response, "ok": False})
                    return
            with st.spinner("Fetching image from server..."):
                # time.sleep(2) # uncomment if testing spinner or delay
                success, img_response = fetch_image()
                if not success: 
                    st.session_state.messages.append({"role": "assistant", "content": img_response, "ok": False})
                    return
                img_name = generate_file_name()
                img_bytes = img_response.content
                st.session_state.image_cache[img_name] = img_bytes
                st.session_state.messages.append({"role": "assistant", "content": None, "ok": True, "img_name": img_name})
                st.session_state.chat_disabled = False
                st.session_state.last_prompt_text = None
                st.rerun()

if __name__ == "__main__":
    main()