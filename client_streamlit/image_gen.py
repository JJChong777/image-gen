import streamlit as st
from modules import display_img_with_download, generate_file_name
API_URL = "http://fast-api:8000"

def generate_image(prompt):
    url = f"{API_URL}/input"
    payload = {'user_input': f'{prompt}'}
    
    return "https://upload.wikimedia.org/wikipedia/commons/1/1a/YF-16_and_YF-17_in_flight.jpg"

def main():
    st.title("Generate a image")


    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hi, I'm the Image Generation Chatbot! Type in a prompt to get started", "ok":True, "image": None}]

    prompt = st.chat_input(placeholder="Type your image generation prompt here...",
        accept_file=True,
        file_type=["jpg", "jpeg", "png"],)

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
                        image_url = payload["url"]
                        with st.chat_message("assistant"):
                            display_img_with_download(name, image_url)
                    if msg["content"]:
                        with st.chat_message("assistant"):
                            st.markdown(msg["content"])

        else:
            st.error("Message with invalid role") 

    if prompt:
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.spinner():
            image_url = generate_image(prompt)
        if image_url:
            name = generate_file_name()
            with st.chat_message("assistant"):
                display_img_with_download(name, image_url)
            st.session_state.messages.append({"role": "assistant", "content": None, "ok": True, "image": {"name": name, "url": image_url}})

if __name__ == "__main__":
    main()