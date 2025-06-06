import streamlit as st
import requests


# 
if "user" not in st.session_state:
    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password",type="password")

    if st.button("Login"):
        res = requests.get(
            "http://localhost:8000/login",
            auth =(username,password)
        )
        if res.status_code == 200:
            st.session_state.user = res.json()
            st.success(f"Logged in as {st.session_state.user['role']}")
        else:
            st.error("Invalid login")
        