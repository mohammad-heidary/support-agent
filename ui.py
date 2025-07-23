#ui.py
import streamlit as st
import requests
import uuid

API_URL = "http://localhost:8000"

# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = None
if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "history" not in st.session_state:
    st.session_state.history = []

st.title("💬 Smart Support Chatbot")

# Sign up / login form
with st.sidebar:
    st.subheader("🔐 Authentication")
    mode = st.radio("Choose mode", ["Login", "Sign Up"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    auth_button = st.button("Submit")

    if auth_button and username and password:
        form_data = {
            "username": username,
            "password": password
        }

        endpoint = "/auth/login" if mode == "Login" else "/auth/signup"
        response = requests.post(f"{API_URL}{endpoint}", data=form_data)

        if response.status_code == 200:
            if mode == "Login":
                st.session_state.access_token = response.json()["access_token"]
                st.success("🔓 Login successful!")
                st.session_state.session_id = str(uuid.uuid4())
                st.session_state.history = [{"role": "bot", "content": "hi! how can i help you? 😊"}]
            else:
                st.success("✅ Signup successful! You can now log in.")
        else:
            st.error(response.json().get("detail", "Error"))

# Check if user is authenticated
if st.session_state.access_token:
    st.markdown("### 🧠 Talk to the Chatbot")

    # Show history
    for msg in st.session_state.history:
        if msg["role"] == "user":
            st.chat_message("user").write(msg["content"])
        else:
            st.chat_message("assistant").write(msg["content"])

    # New user message input
    prompt = st.chat_input("Type your message...")

    if prompt:
        user_msg = {
            "session_id": st.session_state.session_id,
            "content": prompt
        }

        st.chat_message("user").write(prompt)
        st.session_state.history.append({"role": "user", "content": prompt})

        headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
        response = requests.post(f"{API_URL}/chat/send_message", json=user_msg, headers=headers)

        if response.status_code == 200:
            bot_reply = response.json()["response"]
        else:
            bot_reply = f"❌ Error: {response.text}"

        st.chat_message("assistant").write(bot_reply)
        st.session_state.history.append({"role": "bot", "content": bot_reply})

    # Start new session button
    if st.button("🔄 Start New Session"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.history = [{"role": "bot", "content": "hi! how can i help you? 😊"}]
        st.rerun()
else:
    st.info("Please log in to start chatting.")
