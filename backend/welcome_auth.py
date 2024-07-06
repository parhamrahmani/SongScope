"""
backend/welcome_auth.py

handles the first page and authorization pages


"""

from flask import Flask, render_template, redirect, session, request, jsonify, Response
import traceback
from backend import app
import logging


@app.route('/')
def index():
    return render_template('welcome.html')


@app.route("/home")
def home():
    try:
        timestamp = session.get('expires_at')
        logging.info(f"Timestamp: {timestamp}")
        if not timestamp:
            logging.info("No timestamp - redirecting to login")
            return redirect('/login')
        logging.info("Rendering home page")
        return render_template('home.html')
    except Exception as e:
        logging.error(e)
        traceback.print_exc()
        return render_template('welcome.html')
