import streamlit as st
import requests
from datetime import datetime

# Initialize the session state for the chat history
if 'sessions' not in st.session_state:
    st.session_state['sessions'] = {}

st.title("SongScope Chat")

user_input = st.text_input("Enter your question:", "")

if st.button("Send"):
    if user_input:
        with st.spinner("Waiting for response..."):
            try:
                response = requests.post("http://localhost:5000/private_chat", json={"text": user_input})
                response.raise_for_status()
                response_text = response.json()["response"]
                session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
                if session_id not in st.session_state['sessions']:
                    st.session_state['sessions'][session_id] = []
                st.session_state['sessions'][session_id].append(("user", user_input))
                st.session_state['sessions'][session_id].append(("bot", response_text))
                st.success("Response received")
            except requests.exceptions.RequestException as e:
                st.error(f"Error: {e}")

# Display the current chat in the main area
st.subheader("Current Chat")
for role, msg in reversed(st.session_state['sessions'][session_id]):
    if role == "user":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**Bot:** {msg}")

# Display the session titles in the sidebar
st.sidebar.subheader("Chat History")
for session_id in st.session_state['sessions']:
    if st.sidebar.button(session_id):
        for role, msg in st.session_state['sessions'][session_id]:
            if role == "user":
                st.sidebar.markdown(f"**You:** {msg}")
            else:
                st.sidebar.markdown(f"**Bot:** {msg}")