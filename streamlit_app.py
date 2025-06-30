import streamlit as st
import requests

# -- Page Config --
st.set_page_config(page_title="FinSolve Access", page_icon="🔐", layout="centered")

# -- Custom CSS Style --
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Space Grotesk', sans-serif;
        background: radial-gradient(circle at top left, #0f2027, #203a43, #2c5364);
        color: #F2F2F2;
    }

    .login-box {
        background-color: #1e293b;
        padding: 2.5rem 2rem;
        border-radius: 18px;
        box-shadow: 0 0 30px rgba(0,0,0,0.5);
        text-align: center;
    }

    .login-box h1 {
        font-size: 2.2rem;
        margin-bottom: 0.5rem;
        color: #7dd3fc;
    }

    .login-box p {
        font-size: 0.95rem;
        color: #cbd5e1;
        margin-bottom: 2rem;
    }

    .stTextInput>div>input {
        background-color: #0f172a;
        color: white;
        border: 1px solid #334155;
        padding: 0.6rem;
        border-radius: 0.5rem;
    }

    .stButton>button {
        background: linear-gradient(135deg, #38bdf8, #0ea5e9);
        color: white;
        padding: 0.6rem 1.2rem;
        border: none;
        border-radius: 0.6rem;
        font-weight: bold;
        margin-top: 1rem;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #0ea5e9, #38bdf8);
        transform: scale(1.02);
    }
    </style>
""", unsafe_allow_html=True)

# -- Login Form --
with st.container():
    st.markdown("""<div class="login-box">
                <h1>FinSolve RAG Assistant</h1>
                <p>Secure login to access your internal AI chatbot.</p>""", unsafe_allow_html=True)
    st.markdown('<p>Secure login to access your internal AI chatbot.</p>', unsafe_allow_html=True)

    username = st.text_input("👤 Username", placeholder="e.g. tony_sharma")
    password = st.text_input("🔐 Password", type="password", placeholder="Your secret code")

    if st.button("🚀 Login"):
        with st.spinner("Validating your credentials..."):
            res = requests.get("http://localhost:8000/login", auth=(username, password))

        if res.status_code == 200:
            st.session_state.user = {
                "user": username,
                "password": password,
                "role": res.json()["role"]
            }
            st.success(f"✅ Logged in as {username} ({res.json()['role']})")
            st.balloons()
            st.switch_page("pages/chat_bot.py")
        else:
            st.error("❌ Invalid credentials. Try again.")

    st.markdown("</div>", unsafe_allow_html=True)

# -- Already Logged In --
if "user" in st.session_state:
    st.success(f"👋 Welcome back, {st.session_state.user['user']}")
    if st.button("🔁 Go to ChatBot"):
        st.switch_page("pages/chat_bot.py")
