import streamlit as st
import requests

if "user" not in st.session_state:
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        res = requests.get(
            "http://localhost:8000/login",
            auth=(username, password)
        )
        if res.status_code == 200:
            st.session_state.user = {
            "user": username,
            "password": password,  # ✅ storing password for later API use
            "role": res.json()["role"]
        }
            st.success("Login successful!")
            st.switch_page("pages/chat_bot.py")  # ✅ This works if pages/chat_bot.py exists
        else:
            st.error("Invalid credentials")

else:
    # user_info = st.session_state.user
    st.title(f"You are already logged in as {st.session_state.user['user']}")
    if st.button("Switch to chat bot and access your files here"):
        st.switch_page("pages/chat_bot.py")
