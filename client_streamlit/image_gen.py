import streamlit as st
from modules import display_img_with_download, RequestType, make_safe_request, API_URL, generate_file_name
import time
import base64


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
        st.session_state.messages = [{"role": "assistant", "content": "Hi, I'm the Image Generation Chatbot! Type in a prompt to get started", "ok":True, "image": None}]
    if "chat_disabled" not in st.session_state:
        st.session_state.chat_disabled = False
    if "disable_next_input" not in st.session_state:
        st.session_state.disable_next_input = False

    st.session_state.chat_disabled = st.session_state.disable_next_input
    st.session_state.disable_next_input = False

    prompt = st.chat_input(placeholder="Type your image generation prompt here...",
        accept_file=True,
        file_type=["jpg", "jpeg", "png"],
        disabled=st.session_state.chat_disabled
        )

    suggested_questions = [
        "Generate an image of a F16 plane in the clear blue sky flying over mountains"
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
                    if msg["image"]:
                        payload = msg["image"]
                        name = payload["name"]
                        base64_str = payload["base64_str"]
                        with st.chat_message("assistant"):
                            display_img_with_download(name, base64.b64decode(base64_str))
                    if msg["content"]:
                        with st.chat_message("assistant"):
                            st.markdown(msg["content"])

        else:
            st.error("Message with invalid role") 

    if prompt:
        st.session_state.disable_next_input = True
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("assistant"):
            with st.spinner("Sending prompt to server..."):
                time.sleep(2.5)
                success, prompt_response = send_prompt(prompt)
                if success:
                    message = prompt_response.json().get("message")
                    st.success(message)
                else:
                    st.error(prompt_response)
                    st.session_state.messages.append({"role": "assistant", "content": img_response, "ok": False})
                    return
            with st.spinner("Fetching image from server..."):
                time.sleep(2.5)
                success, img_response = fetch_image()
                if not success: 
                    st.error(img_response)
                    st.session_state.messages.append({"role": "assistant", "content": img_response, "ok": False})
                    return
                img_name = generate_file_name()
                img_bytes = img_response.content
                display_img_with_download(img_bytes, img_name)
                st.session_state.messages.append({"role": "assistant", "content": None, "ok": True, "image": {"name": img_name, "base64_str": base64.b64encode(img_bytes)}})



        
        # display_img_with_download(name, image_url)
            
        # if image_url:
        #     name = generate_file_name()
        #     st.session_state.messages.append({"role": "assistant", "content": None, "ok": True, "image": {"name": name, "url": image_url}})

if __name__ == "__main__":
    main()