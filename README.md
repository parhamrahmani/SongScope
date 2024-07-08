# SongScope 

## Introduction

SongScope is an AI powered music recommendation system that experiments with your spotify data such as your top tracks, liked songs
, artists , etc. to recommend you new songs that you might like. The system can add a personal touch to the recommendations
if you provide your mood and personal emotional data. The system can be also fine-tuned based on your liked songs and
spotify recommendation system to experiment with fine-tuned models too. Other features include a function to search
reviews from pitchfork or similar websites to get a better understanding of the song and artist and have a critical view.
The features combined with personalized fine-tuning can experiment with a newly personalized recommendation system.

## Pre-Installation Requirements
- **Python 3.10**

Python 3.10 is used as interpreter for the project.

- **Pip**

Needed to install the dependencies.

- **Spotify Account**

A Spotify account is needed to use the system. You can create one [here](https://www.spotify.com/).

- **Spotify Developer Account**

This project is built using locally, so you need to provide your own Spotify Client ID and Client Secret.
Please read this documentation to create your own Spotify Developer Account and get your own Client ID and Client Secret.
[Getting Started with Spotify Web API](https://developer.spotify.com/documentation/web-api/tutorials/getting-started)

- set up a new account and login to the Spotify Developer Dashboard.
    - Create a new app and get your Client ID and Client Secret.
    - Add the redirect URI as `http://localhost:5000/callback` in the app settings.


- **OPENAI API Key**

This project uses OpenAI API to generate song lyrics. You can get your own API key 
by signing up [here](https://platform.openai.com/signup).

We will also need OPENAI ASSISTANT ID which has functions available to it. We will do this
later in the project setup.

- **MongoDB and Nginx**

We will be using MongoDB as our database, Nginx for our web server configurations. 

The details will follow in the installation section. However, install these before starting with the project setup.

## Project Setup - Debian GNU/Linux 12 (Bookworm)
### 1. Clone the repository
```git
git clone https://github.com/parhamrahmani/SongScope.git
```
### 2. Install the dependencies
```pip
pip install -r requirements.txt
```
or 

```pip
pip install requests python-dotenv Flask jsonify openai chromadb pymongo chainlit beautifulsoup4
```
### 3. Set up Nginx configurations
- Install Nginx
```bash
sudo apt update
sudo apt install nginx
```
- Create a new configuration file for the project in the `/etc/nginx/sites-available` directory.
```bash
sudo nano /etc/nginx/sites-available/songscope
```
- Add the following configurations to the file.
```nginx
server {
    listen 80;

    server_name localhost;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /chat/ {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
- Create a symbolic link to the `sites-enabled` directory.
```bash
sudo ln -s /etc/nginx/sites-available/songscope /etc/nginx/sites-enabled
```
- Restart the Nginx service.
```bash
sudo systemctl restart nginx
```
- Check the status of the Nginx service.
```bash
sudo systemctl status nginx
```
### 4. Set up MongoDB
- Install MongoDB
```bash
sudo apt update
sudo apt install -y mongodb
```
- Start the MongoDB service
```bash
sudo systemctl start mongod
```
- Check the status of the MongoDB service
```bash
sudo systemctl status mongod
```
- Go to the `setup` directory and run the `mongodb_initial_setup.py` to set up the MongoDB databases.
- After running the script, the databases will be set up and the collections will be populated with *example data*.
- Delete the example data from the collections, since it will be populated with your own data later.
- list of collections in the spotifydb database:
    - albums
        - the albums that the user has at least listened one song from. It originates from the liked songs of the user.
    - artists
        - the artists that the user has at least listened one song from. It originates from the liked songs of the user.
    - liked_songs
        - the songs that the user has liked and saved in their library.
    - recommendations
        - the songs that the Spotify recommendation system has recommended to the user.
        - it originates from when the `/recommendations` and `/generate_random_recommendations/<int:num_recommendations> `are called, and it will be saved in the database.

### 5. Populate the MongoDB databases with your spotify data 
- Run this endpoint to populate the mongodb collections with your spotify data.
```bash
http://localhost:5000/liked_songs
```
- The data will be automatically inserted into the collections.
- experiment with the Spotify recommendation system using the `localhost:5000/home` after authorization to tweak and get new recommendations.
- experiment with the Spotify recommendation system using the `localhost:5000/generate_random_recommendations/<int:num_recommendations>` to get random recommendations to populate the table for using it for fine-tuning.
- pay attention to the `num_recommendations` parameter to get the desired number of recommendations. There are rate limits for the Spotify API.

### 6. Fine-Tuning (Optional)
**Fine-tuning is an optional step**

- You can fine-tune the recommendation system by using the recommendations table in the database.
- The more data you have in the recommendations table, the better the fine-tuning will be.
- Fine-tuning costs money and time and wouldn't necessarily improve the recommendation system. It's an experimental feature. That's why it's optional.
- Firstly run prompt.py to generate prompts based on the recommendations table. each prompt will be each iteration of a recommendation (based on its id). 
- Then run the `conf/finetuning/finetuning.py` to fine-tune the model based on the prompts generated.
   - this will upload `conf/finetuning/prompts.jsonl` to the OpenAI API and will fine-tune the model based on the prompts.
- **You can do this in OPENAI API Dashboard in their website as well if you want to do this with a gui environment**
### 7. Set up OpenAI Assistant 
- Go to `setup/setup_openai_assistant.py` and run the script to create/update a new assistant.
- Get the assistant ID and set it as the `OPEN_AI_ASSISTANT_ID` in the `.env` file.
- Make sure to include the functions that you need in the assistant. Otherwise, the assistant won't work properly.
- You have to get the assistant ID from the OpenAI API Dashboard regardless of how you create the assistant. The 
Assistant ID will be also printed in the terminal after creating the assistant.
### 8. Get Tavily API Key
- Go to the Tavily API website and get your own API key.
- Set the API key as the `TAVILY_KEY` in the `.env` file.
### 9. Set up the `.env` file
- Create a new `.env` file in the root directory of the project.
- Add the following environment variables to the `.env` file.
```env
SPOTIFY_CLIENT_ID=<YOUR_SPOTIFY_CLIENT_ID>
SPOTIFY_CLIENT_SECRET=<YOUR_SPOTIFY_CLIENT_SECRET>
REDIRECT_URI="http://localhost:5000/callback"
FLASK_SECRET_KEY=<YOUR_SECRET_KEY> # You can set a secret as anything you want
OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
CHROMADB_PATH=<PATH_TO_CHROMADB> # A path to store the chat history and reviews
MONGO_URI="mongodb://localhost:27017/spotifydb"
OPEN_AI_ASSISTANT_ID=<YOUR_OPENAI_ASSISTANT_ID>
AI_MODEL=<YOUR_OPENAI_MODEL> # The model that you want to use for the AI like gpt4o etc.
TAVILY_KEY=<YOUR_TAVILY_KEY>
```
### Additional Information
- This setup is done on a linux machine. You can set up the project on a Windows machine as well. For windows, you can use WSL or easily go to each requirement documentation and follow the instructions.
- Please use this locally and don't deploy the project online without proper security measures. This project is not production-ready and is not secure. 
## Running the project
### Start Nginx Service
- start
```bash
sudo systemctl start nginx
```
- check the status of nginx
```bash
sudo systemctl status nginx
```
### Start the MongoDB Service
- start
```bash
sudo systemctl start mongod
```
- check the status of mongodb
```bash
sudo systemctl status mongod
```
### Start the Application
- Go to the root directory of the project and run the following command.
```bash
python main.py
```
- you should see the following output
```bash
2024-07-01 02:27:48 - Loaded .env file
2024-07-01 02:27:48 - Anonymized telemetry enabled. See                     https://docs.trychroma.com/telemetry for more information.
 * Serving Flask app 'backend'
 * Debug mode: off
2024-07-01 02:27:48 - WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
2024-07-01 02:27:48 - Press CTRL+C to quit
```
- The application will be running on ´http://localhost:5000´
- After authorization, you should be redirected to `http://localhost:8000` to chat with the chatbot.
- At this point a new chainlit server will be started you should expect the following output
```bash
Starting Chainlit server
2024-07-01 02:29:13 - Loaded .env file
2024-07-01 02:29:14 - Your app is available at http://localhost:8000
Chainlit thread started.
2024-07-01 02:29:15 - 127.0.0.1 - - [01/Jul/2024 02:29:15] "GET /interface HTTP/1.1" 302 -
2024-07-01 02:29:16 - Translated markdown file for en-US not found. Defaulting to chainlit.md.
2024-07-01 02:29:18 - HTTP Request: POST https://api.openai.com/v1/threads "HTTP/1.1 200 OK"
```
This means that the chatbot is running.
- write something in the chatbot, and you should see the response from the chatbot. If the response is shown in the chatbot, the chatbot is working properly.
- expect the chatbot to be slow and have patience.
- You should expect this message in terminal when the chatbot is working properly. (This is a sample)
```bash
Entering chat function
Thread ID:  <the thread id of openai thread>
Message:  hi
2024-07-01 02:32:03 - HTTP Request: POST https://api.openai.com/v1/threads/<thread_id>/messages "HTTP/1.1 200 OK"
2024-07-01 02:32:04 - HTTP Request: POST https://api.openai.com/v1/threads/<thread_id>/runs "HTTP/1.1 200 OK"
Run status:  queued
2024-07-01 02:32:05 - HTTP Request: GET https://api.openai.com/v1/threads/<thread_id>/runs/run_9a7tEs4Wo5LSUuAjugVfNYrv "HTTP/1.1 200 OK"
Run status:  in_progress
2024-07-01 02:32:06 - HTTP Request: GET https://api.openai.com/v1/threads/<thread_id>/runs/run_9a7tEs4Wo5LSUuAjugVfNYrv "HTTP/1.1 200 OK"
2024-07-01 02:32:06 - HTTP Request: GET https://api.openai.com/v1/threads/<thread_id>/messages "HTTP/1.1 200 OK"
2024-07-01 02:32:07 - HTTP Request: POST https://api.openai.com/v1/threads/<thread_id>/messages "HTTP/1.1 200 OK"
2024-07-01 02:32:07 - Collection chat_history is not created.
Message in thread <thread_id> inserted successfully to chat history
Verified content:  Hello! How can I assist you today?
2024-07-01 02:32:07 - 127.0.0.1 - - [01/Jul/2024 02:32:07] "POST /chat HTTP/1.1" 200 -
```




