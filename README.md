# SongScope 
In this project, i experimented with integrating a web app to Spotify API and OpenAI API for music recommendation. For more info and results click on [this](##final-and-personal-notes). 

## Table of Contents
1. [Introduction](#introduction)
2. [Pre-Installation Requirements](#pre-installation-requirements)
3. [Project Setup](#project-setup-debian-gnulinux-12)
4. [Running the Project](#running-the-project)
5. [Additional Information](#additional-information)
6. [Final and Personal Notes](#final-and-personal-notes)
7. [Support](#support)

## Introduction

SongScope is an AI-powered music recommendation system that leverages your Spotify data to suggest new songs you might enjoy. By analyzing your top tracks, liked songs, and favorite artists, SongScope provides personalized recommendations. The system can be further enhanced by incorporating your mood and emotional data for a more tailored experience.

Key features include:
- Personalized song recommendations based on your Spotify data
- Fine-tuning capabilities using your liked songs and Spotify's recommendation system
- Integration with music review websites for critical insights
- AI-powered chatbot for interactive music exploration

## Pre-Installation Requirements

- **Python 3.10**: Used as the interpreter for the project
- **Pip**: Required to install dependencies
- **Spotify Account**: Create one at [Spotify](https://www.spotify.com/)
- **Spotify Developer Account**: Set up a new app and obtain Client ID and Client Secret
  - Add redirect URI: `http://localhost:5000/callback`
- **OpenAI API Key**: Sign up at [OpenAI](https://platform.openai.com/signup)
- **MongoDB**: Database for storing music data
- **Nginx**: Web server for routing requests
- **Tavily API Key**: Required for enhanced search capabilities



## Project Setup (Debian GNU/Linux 12)

1. **Clone the repository**
   ```
   git clone https://github.com/parhamrahmani/SongScope.git
   ```

2. **Install dependencies**
   ```
   pip install -r requirements.txt
   ```
   or
   
   ```pip
    pip install requests python-dotenv Flask jsonify openai chromadb pymongo chainlit beautifulsoup4
    ```

3. **Set up Nginx**
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

4. **Set up MongoDB**
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

5. **Populate MongoDB with Spotify data**
       - Make sure the backend is running and access `http://localhost:5000/liked_songs` after setup.
       - Run this endpoint to populate the mongodb collections with your spotify data.
            ```bash
            http://localhost:5000/liked_songs
            ```
       - The data will be automatically inserted into the collections.
       - experiment with the Spotify recommendation system using the `localhost:5000/home` after authorization to tweak and get new recommendations.
       - experiment with the Spotify recommendation system using the `localhost:5000/generate_random_recommendations/<int:num_recommendations>` to get random recommendations to populate the table for using it for fine-tuning.
       - pay attention to the `num_recommendations` parameter to get the desired number of recommendations. There are rate limits for the Spotify API.

6. **Fine-Tuning (Optional)**
   **Fine-tuning is an optional step**

    - You can fine-tune the recommendation system by using the recommendations table in the database.
    - The more data you have in the recommendations table, the better the fine-tuning will be.
    - Fine-tuning costs money and time and wouldn't necessarily improve the recommendation system. It's an experimental feature. That's why it's optional.
    - Firstly run prompt.py to generate prompts based on the recommendations table. each prompt will be each iteration of a recommendation (based on its id). 
    - Then run the `conf/finetuning/finetuning.py` to fine-tune the model based on the prompts generated.
       - this will upload `conf/finetuning/prompts.jsonl` to the OpenAI API and will fine-tune the model based on the prompts.
    - **You can do this in OPENAI API Dashboard in their website as well if you want to do this with a gui environment**

7. **Set up OpenAI Assistant**
    - Go to `setup/setup_openai_assistant.py` and run the script to create/update a new assistant.
    - Get the assistant ID and set it as the `OPEN_AI_ASSISTANT_ID` in the `.env` file.
    - Make sure to include the functions that you need in the assistant. Otherwise, the assistant won't work properly.
    - You have to get the assistant ID from the OpenAI API Dashboard regardless of how you create the assistant. The 
Assistant ID will be also printed in the terminal after creating the assistant.

8. Get a Tavily API Key
    - Go to the Tavily API website and get your own API key.
    - Set the API key as the `TAVILY_KEY` in the `.env` file.
9. **Configure .env file**
    - Create `.env` in the root directory with required credentials
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
- Please use this locally and don't deploy the project online without proper security measures. This project is not production-ready and is not secure

## Running the Project
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
## Final and Personal Notes
- Successful Results
    - Music Recommendation with fine-tuned model → successful verification, good 
    quality of results and expected behavior.
    - Fine-Tuning jobs and methods to make datasets.
    - Working with Spotify API for functionalities
- Issues and Failures
    - web-scraping for pitchfork reviews
    - using newer openai models didn't work and resulted in responses that repeated the prompt. 
- Fine-Tuning Importance and Improvements
- Observations
  - This project was done mainly to put AI into test with subjects that are not 
    commonly used with AI like music reviews and recommendations. The core 
    functionality of this application worked as expected but the relative quality 
    was lower than using a specifically trained system like Spotify API. The best 
    would be to use OpenAI as an assistant with access to Spotify API and let 
    Spotify API to do the recommendation process. However this can be done with a 
    web application without AI as well. So in the long run, using specifically 
    trained systems like Spotify API can have better results than an default AI 
    model.
## Support
This repository won't be updated or maintained for now, but feel free to fork this repository and make a pull request!

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.






