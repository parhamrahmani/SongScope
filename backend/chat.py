"""
# backend/chat.py

This file handles the requests to the chat endpoint and enables chatting with the AI assistant.
It also serves and renders the interface for the chat application.


"""
import logging
import threading
import time
import traceback
import json
from backend import app, TAVILY_CLIENT, SYSTEM_PROMPT, AI_MODEL, OPENAI_API_KEY, OPENAI_CLIENT, OPEN_AI_ASSISTANT_ID
from flask import request, jsonify, redirect, render_template_string, render_template, session, make_response, url_for
from conf.jsontools.chat_history_to_jsonl import chat_history_to_jsonl
from conf.spotifyapi.spotfiyapi_functions import search_track_on_spotify
from frontend.app import run_chainlit
from backend.webscraping import tavily_search, pitchfork_review
import inspect

function_lookup = {
    "search_track_on_spotify": search_track_on_spotify,
    "tavily_search": tavily_search,
    "pitchfork_review": pitchfork_review
}


def submit_tool_outputs(thread_id, run_id, tools_to_call):
    """
    This function submits the outputs of the tools called in a thread to the OpenAI API.

    Parameters:
    thread_id (str): The ID of the thread where the tools are called.
    run_id (str): The ID of the run where the tools are called.
    tools_to_call (list): A list of tools to be called.

    Returns:
    response: The response from the OpenAI API after submitting the tool outputs.
    """

    # Initialize an empty list to store the tool outputs
    tool_outputs_array = []

    # Loop over each tool in the list of tools to call
    for tool in tools_to_call:
        # Initialize the output of the tool to None
        output = None

        # Retrieve the ID, function name, and arguments of the tool
        tool_call_id = tool.id
        function_name = tool.function.name
        function_args = json.loads(tool.function.arguments)

        # Retrieve the actual function to call from the function lookup dictionary
        function_to_call = function_lookup[function_name]

        # Get the parameters of the function to call
        params = inspect.signature(function_to_call).parameters

        # Filter out any arguments that are not expected by the function
        valid_args = {k: v for k, v in function_args.items() if k in params}

        # Call the function with the valid arguments and store the output
        output = function_to_call(**valid_args)

        # If there is an output, convert it to a JSON string and append it to the tool outputs array
        if output:
            output_str = json.dumps(output)
            tool_outputs_array.append({"tool_call_id": tool_call_id, "output": output_str})

    # Submit the tool outputs to the OpenAI API and return the response
    return OPENAI_CLIENT.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_outputs_array
    )


@app.route('/interface', methods=['GET'])
def interface():
    """
    This function handles the GET requests to the '/interface' endpoint. It starts the Chainlit server if it's not
    already running and redirects the user to the chat interface. If the user is not authenticated, it redirects
    them to the login page.

    Returns:
    A redirect response to the chat interface or the login page.
    """

    # Check if the user is authenticated
    if 'access_token' not in session:
        logging.info("User not authenticated -- redirecting to login")
        # If not, redirect them to the login page
        return redirect('/login')

    # Check if the Chainlit server is running
    if not any(thread.name == 'chainlit' for thread in threading.enumerate()):
        # If not, start the Chainlit server
        logging.info("Starting Chainlit thread")
        chainlit_thread = threading.Thread(target=run_chainlit, name='chainlit', daemon=True)
        chainlit_thread.start()
        time.sleep(3)
        logging.info("Chainlit thread started -- redirecting to chat interface")

    # Redirect the user to the chat interface
    return redirect(f'http://localhost:8000/?session_id={session.sid}')


@app.route('/chat', methods=['POST'])
def chat():
    """
    This function handles the POST requests to the '/chat' endpoint. It processes the user's message, interacts with
    the OpenAI API to generate a response, and returns the response.

    The function retrieves the thread ID and the user's message from the request. It then cancels any active runs in
    the thread, adds the user's message to the thread, and creates a new run with the OpenAI assistant.

    The function waits for the run to complete, and if the run requires action (i.e., if a tool needs to be called),
    it submits the tool outputs. Once the run is completed, it retrieves the assistant's messages and returns the
    assistant's response.

    If there are any errors during this process, the function returns an error message.

    Returns:
    A JSON response containing the status and the assistant's message or an error message.
    """
    thread_id = request.json.get("thread_id")
    message = request.json.get("message")
    logging.info(f"Chat started: thread_id={thread_id}")
    logging.info(f"User Message: {message}")

    try:
        # Cancel any active runs
        runs = OPENAI_CLIENT.beta.threads.runs.list(thread_id=thread_id)
        for run in runs.data:
            if run.status in ['queued', 'in_progress']:
                logging.info(f"Cancelling active run: {run.id}")
                OPENAI_CLIENT.beta.threads.runs.cancel(thread_id=thread_id, run_id=run.id)

        # Add the user's message to the thread
        OPENAI_CLIENT.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )

        # Create a run
        run = OPENAI_CLIENT.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=OPEN_AI_ASSISTANT_ID)

        # Wait for the run to complete
        while run.status not in ["completed", "failed"]:
            logging.info(f"Run status: {run.status}")
            time.sleep(1)
            run = OPENAI_CLIENT.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run.status == 'requires_action':
                run = submit_tool_outputs(thread_id, run.id, run.required_action.submit_tool_outputs.tool_calls)

        # Retrieve the assistant's messages
        messages = OPENAI_CLIENT.beta.threads.messages.list(thread_id=thread_id)

        if messages.data:
            assistant_message = messages.data[0]
            if assistant_message.content:
                text_content = assistant_message.content[0].text.value

                # Add the verified content as a new assistant message
                OPENAI_CLIENT.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="assistant",
                    content=text_content
                )

                # Store the conversation
                chat_history_to_jsonl(thread_id, message, text_content)

                logging.info(f"Assistant Response: {text_content}")
                return jsonify({"status": "success", "message": text_content})
            else:
                return jsonify({"status": "error", "message": "No content in assistant's message"}), 500
        else:
            return jsonify({"status": "error", "message": "No messages found"}), 500

    except Exception as e:
        logging.error("Error: ", e)
        traceback.print_exc()
        return jsonify({"status": "error", "message": "An error occurred"}), 500
