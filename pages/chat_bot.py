import streamlit as st

import requests



def response(input_text):
    try:
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
        res.raise_for_status()  # This will raise if status != 200

        return res.json()  # ✅ This is what your backend returns: a dict
    except requests.exceptions.RequestException as e:
        print("❌ Request failed:", str(e))
        return {
            "response": f"❌ Server error: {str(e)}",
            "sources": []
        }
    except Exception as e:
        print("❌ Unexpected error:", str(e))
        return {
            "response": f"❌ Unknown error: {str(e)}",
            "sources": []
        }



    
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


if "user" in st.session_state:
    st.title(f"Welcome now you have access to all {st.session_state.user['role']} releated files")
    user_question = st.chat_input("Search for your files")
    if user_question:
        with st.spinner("Thinking..."):
            answer = response(user_question)
            st.session_state.chat_history.append(("user", user_question))
            st.session_state.chat_history.append(("assistant", answer["response"], answer.get("sources", [])))
            for entry in st.session_state.chat_history:
                sender = entry[0]
                if sender == "user":
                    with st.chat_message("user"):
                        st.markdown(entry[1])
                elif sender == "assistant":
                    response_text, sources = entry[1], entry[2]
                    with st.chat_message("assistant"):
                        st.markdown(response_text)
                        if sources:
                            shown = set()
                            st.markdown("#### 🗂️ Files used:")
                            for doc in sources:
                                key = (doc["file_name"], doc["link"])
                                if key not in shown:
                                    shown.add(key)
                                    st.markdown(f"📄 [{doc['file_name']}]({doc['link']})", unsafe_allow_html=True)


# ...existing code...
else:
    st.title("Welcome to the Chat Bot Page")
    st.write("Please log in to access your files.")
    if st.button("Go to Login"):
        st.switch_page("streamlit_app.py")
# ...existing code...
