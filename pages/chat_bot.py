import streamlit as st


if "user" in st.session_state:
    st.title(f"Welcome now you have access to all {st.session_state.user['role']} releated files")
    st.text_input("Search for your files")
# ...existing code...
else:
    st.title("Welcome to the Chat Bot Page")
    st.write("Please log in to access your files.")
    if st.button("Go to Login"):
        st.switch_page("streamlit_app.py")
# ...existing code...
