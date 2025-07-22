import streamlit as st

st.set_page_config(layout="wide")

def main():
    pages = [
        st.Page("search.py", title="Search Images", icon="🔍"),
        st.Page("image_gen.py", title="Generate Image", icon="🤖"),
        st.Page("edit_image.py", title="Edit Image", icon="🖌️")
    ]

    selected_page = st.navigation(pages)
    selected_page.run()

if __name__ == "__main__":
    main()