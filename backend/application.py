from flask import Flask, render_template, redirect, session, request, jsonify
import os
from dotenv import load_dotenv
import openai
import subprocess
import traceback
from conf import *
from conf.mongodb.query import collection_query_by_fields, collection_query_all

load_dotenv()

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = os.getenv('FLASK_SECRET_KEY')
app.debug = True

openai.api_key = os.getenv("OPENAI_API_KEY")


@app.route('/')
def index():
    return render_template('welcome.html')


@app.route("/home")
def home():
    timestamp = session.get('expires_at')
    if not timestamp:
        return redirect('/login')
    return render_template('home.html')


@app.route('/private_chat', methods=["POST"])
def chat():
    try:
        message_data = request.json
        user_input = message_data.get('text', '')

        if not user_input:
            return jsonify({"error": "No text provided"}), 400
        # input = {'artist_name': 'Sia'}
        prompt = user_input

        content = (f"You are a music critic and someone who gives music recommendations with a critical"
                   f" and professional viewpoint. "
                   f"Give your answers based on user's taste in music."
                   f"DO NOT ANSWER IMMEDIATELY. MAKE SURE TO GATHER ALL INFORMATION FIRST"
                   f"FROM THE USER.")

        client = openai.OpenAI(api_key=OPEN_AI_API_KEY)

        response = client.chat.completions.create(
            model=AI_MODEL,
            messages=[{"role": "system", "content": content},
                      {"role": "user", "content": prompt}]
        )
        return jsonify({"response": response.choices[0].message.content.strip()})
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
