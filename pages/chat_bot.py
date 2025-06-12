import streamlit as st

import requests



def response(input_text):
    res = requests.post(
        "http://localhost:8000/chat",
        json={
            "message": input_text,
            "role": st.session_state.user["role"]
        },
        auth=(
            st.session_state.user["user"],
            st.session_state.user["password"]
        )
    )

    print("DEBUG:", res.status_code, res.text)

    if res.status_code == 200:
        return res.json()["response"]
    else:
        return "❌ Error: " + res.text



    


if "user" in st.session_state:
    st.title(f"Welcome now you have access to all {st.session_state.user['role']} releated files")
    user_question = st.chat_input("Search for your files")
    if user_question:
        with st.spinner("Thinking..."):
            answer = response(user_question)
            st.chat_message("assistant").write(answer)
# ...existing code...
else:
    st.title("Welcome to the Chat Bot Page")
    st.write("Please log in to access your files.")
    if st.button("Go to Login"):
        st.switch_page("streamlit_app.py")
# ...existing code...
