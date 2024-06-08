import streamlit as st
import requests

# Initialize the session state for the chat history
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

st.title("SongScope Chat")

user_input = st.text_input("Enter your question:", "")

if st.button("Send"):
    if user_input:
        with st.spinner("Waiting for response..."):
            try:
                response = requests.post("http://localhost:5000/private_chat", json={"text": user_input})
                response.raise_for_status()
                response_text = response.json()["response"]
                st.session_state['messages'].append(("user", user_input))
                st.session_state['messages'].append(("bot", response_text))
                st.success("Response received")
            except requests.exceptions.RequestException as e:
                st.error(f"Error: {e}")

st.subheader("Chat History")
for role, msg in st.session_state['messages']:
    if role == "user":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**Bot:** {msg}")

if st.button("Save Session History"):
    from datetime import datetime
    with open(f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", "w") as f:
        for role, msg in st.session_state['messages']:
            if role == "user":
                f.write(f"You: {msg}\n")
            else:
                f.write(f"Bot: {msg}\n")
    st.success("Session history saved successfully.")
