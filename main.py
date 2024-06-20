import subprocess
import sys
import threading
import time
import os
from flask import Flask, request, redirect, session
from flask import redirect, session, render_template
from conf import *
import conf.spotifyapi.spotifyauth
import conf.spotifyapi.spotfiyapi_functions
import openai
from pydantic import BaseModel


def run_flask():
    from backend.application import app
    app.run(host="localhost", port=5000, debug=False)  # Disable reloader


def run_streamlit():
    time.sleep(5)  # Give Flask a few seconds to start
    script_path = os.path.abspath('frontend/testing_streamlit.py')
    subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', script_path])


if __name__ == "__main__":
    # Create threads for running Flask and Streamlit
    flask_thread = threading.Thread(target=run_flask)
    streamlit_thread = threading.Thread(target=run_streamlit)

    # Start the threads
    flask_thread.start()
    streamlit_thread.start()

    # Wait for both threads to complete
    flask_thread.join()
    streamlit_thread.join()
