"""
backend/application.py

handles the first page and authorization pages


"""
from urllib.parse import urljoin

from flask import Flask, render_template, redirect, session, request, jsonify, Response
import os
from dotenv import load_dotenv
import openai
import subprocess
import traceback
from conf import *
from conf.mongodb.query import collection_query_by_fields, collection_query_all
from backend import app
import requests


@app.route('/')
def index():
    return render_template('welcome.html')


@app.route("/home")
def home():
    timestamp = session.get('expires_at')
    if not timestamp:
        return redirect('/login')
    return render_template('home.html')
