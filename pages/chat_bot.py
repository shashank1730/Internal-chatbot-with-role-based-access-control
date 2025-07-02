import streamlit as st
import requests
#from streamlit_chat import message as chat_message  # Optional: use this or custom markdown styling


# --- Page config ---
st.set_page_config(page_title="Secure File Chat", layout="wide", page_icon="💬")

# --- CSS Styling ---
def inject_custom_css():
    st.markdown("""
        <style>
        body {
            background-color: #f4f4f8;
        }
        .stChatMessage {
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            border-radius: 12px;
            max-width: 90%;
        }
        .user-msg {
            background-color: #e0f7fa;
            align-self: flex-end;
        }
        .assistant-msg {
            background-color: #f1f8e9;
        }
        .chat-box {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            max-width: 900px;
            margin: auto;
        }
        </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# --- Backend Response Function ---
def response(input_text):
    try:
        res = requests.post(
            "http://localhost:8000/chat",
            json={"message": input_text, "role": st.session_state.user["role"]},
            auth=(st.session_state.user["user"], st.session_state.user["password"])
        )
        print("DEBUG:", res.status_code, res.text)
        res.raise_for_status()
        return res.json()
    except requests.exceptions.RequestException as e:
        print("❌ Request failed:", str(e))
        return {"response": f"❌ Server error: {str(e)}", "sources": []}
    except Exception as e:
        print("❌ Unexpected error:", str(e))
        return {"response": f"❌ Unknown error: {str(e)}", "sources": []}


# --- Session Setup ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- Authenticated View ---
if "user" in st.session_state:
    st.sidebar.title("🔐 User Info")
    st.sidebar.markdown(f"**Logged in as:** `{st.session_state.user['user']}`")
    st.sidebar.markdown(f"**Role:** `{st.session_state.user['role']}`")

    # 🚪 Logout button
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()

    st.title("📁 Role-based File Chat Assistant")
    st.markdown("Ask anything about your files. The assistant will fetch the relevant information based on your role access.")

    user_question = st.chat_input("🔍 Type your query here...")
    if user_question:
        with st.spinner("🤖 Thinking..."):
            answer = response(user_question)
            st.session_state.chat_history.append(("user", user_question))
            st.session_state.chat_history.append(("assistant", answer["response"], answer.get("sources", [])))

    st.divider()
    with st.container():
        st.markdown('<div class="chat-box">', unsafe_allow_html=True)
        for entry in st.session_state.chat_history:
            if entry[0] == "user":
                st.markdown(f'<div class="stChatMessage user-msg"><b>🧑‍💻 You:</b><br>{entry[1]}</div>', unsafe_allow_html=True)
            elif entry[0] == "assistant":
                response_text, sources = entry[1], entry[2]
                st.markdown(f'<div class="stChatMessage assistant-msg"><b>🤖 Assistant:</b><br>{response_text}</div>', unsafe_allow_html=True)
                if sources:
                    st.markdown("#### 📎 Files Referenced:")
                    shown = set()
                    for doc in sources:
                        key = (doc["file_name"], doc["link"])
                        if key not in shown:
                            shown.add(key)
                            st.markdown(f"📄 [{doc['file_name']}]({doc['link']})", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- Login Page ---
else:
    st.title("🔐 Secure ChatBot Portal")
    st.subheader("Please log in to access your files and use the assistant.")
    st.write("Your role determines what files you can access.")
    if st.button("🔑 Go to Login"):
        st.switch_page("streamlit_app.py")
