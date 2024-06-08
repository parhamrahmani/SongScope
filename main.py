import subprocess
import sys

from flask import Flask, request, redirect, session
from flask import redirect, session, render_template
from conf import *
from backend.application import app
import conf.spotifyapi.spotifyauth
import conf.spotifyapi.spotfiyapi_functions
import openai
from pydantic import BaseModel

# run the app
if __name__ == "__main__":
    app.run(host="localhost", port=5000)
    script_path = os.path.abspath('frontend/testing_streamlit.py')
    subprocess.Popen([sys.executable, '-m', 'streamlit', 'run', script_path])
