"""
main.py
Runs the entire application.
"""

import threading
import time
from flask import render_template_string
from conf import *
from conf.spotifyapi import spotifyauth
from backend.application import app
from backend.chat import chat, interface
from frontend.app import run_chainlit

if __name__ == "__main__":
    app.run(port=5000, debug=False)
