import streamlit as st
from client_streamlit.modules import display_img_with_download, generate_file_name

def image_edit_with_prompt(image_file, prompt):
    """Generate a edited image with the original image file and a prompt"""
    # Simulated image edit with prompt
    return "https://upload.wikimedia.org/wikipedia/commons/1/1a/YF-16_and_YF-17_in_flight.jpg"

    

def main():
    st.title("Edit an image with a prompt")
    image_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if image_file is not None:
        st.image(image_file, caption="Preview", width=300)
    # with st.form("image_edit_prompt_form"):
    prompt = st.text_area("Enter a prompt", value="Enhance this image of an F-16 fighter jet soaring through a clear blue sky above rugged mountains. Emphasize the sense of speed and power by adding subtle motion blur to the jet's wings or exhaust, while keeping the mountains sharp. Adjust lighting to create dynamic shadows and highlights on the aircraft, making it pop against the background. Consider a slightly desaturated, cinematic color grade to enhance the dramatic atmosphere, perhaps with a subtle vignette to draw the eye.")
        # submitted = st.form_submit_button("Edit Image")
    submitted = st.button("Edit Image")

    if submitted:
        if image_file is not None and prompt:
            image_url = image_edit_with_prompt(image_file, prompt)
            name = generate_file_name()
            st.success("Form submitted successfully!")
            display_img_with_download(name, image_url)

        else:
            st.warning("Please upload an image and enter a prompt.")

if __name__ == "__main__":
    main()