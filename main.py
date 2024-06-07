from flask import Flask, request, redirect, session
from flask import redirect, session, render_template
from conf import *
import conf.spotifyapi.spotifyauth
import conf.spotifyapi.spotfiyapi_functions
import openai
from pydantic import BaseModel


class Message(BaseModel):
    text: str


@app.route('/')
def index():
    return render_template('welcome.html')


# home page after login
@app.route("/home")
def home():
    timestamp = session.get('expires_at')
    if not timestamp:
        return redirect('/login')
    return render_template('home.html')


# run the app
if __name__ == '__main__':
    app.run(debug=True)