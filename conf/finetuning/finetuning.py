"""
conf/finetuning/finetuning.py

In here we have the functions that are used to fine-tune the model using the OpenAI API with generated data.
Firstly we upload the training data file, then we create a fine-tuning job and wait for it to finish.
Then we save the fine-tuned model and update the AI_MODEL environment variable to the new model.

This is optional and meant for experimentation purposes. So this is not done in the interface and UI.

Pre-requisites:

0. Have the databases, clients and the backend running,otherwise it won't work.

1. You need at least 10 recommendations from the Spotify API (depending on one your request it can vary
from 10 songs to 200 songs) , the important thing is 10 request with different characteristics and weights
that will construct the necessary minimum '10' prompts for the training data file.
-> In my case i had around 400 request (therefore around 400 example prompts for the training data and in the end i had
 around 6000 songs in the recommendations collection in the MongoDB database.

 1.1 You can use this endpoint to get the recommendations from the Spotify API:

 make a get request to the endpoint: /generate_random_recommendations/<number of recommendations you want>

 this will generate random recommendations and insert them into the recommendations collection in the MongoDB database.

 1.2 Then you can use the prompts.py file to generate the prompts for the training data file.
 You will have a file called prompts.jsonl in the data/training_data folder.

 1.3 Use this file to fine-tune the model.

2. If you want to understand the training data, take a look at example_training_prompts.jsonl file in the
data/training_data folder.

In this code we have used prompts.jsonl if not found we use the example_training_prompts.jsonl file.

3. You can do this also easily in the OpenAI interface.

"""
import logging
import time
from openai import OpenAI
import os
from backend import OPENAI_API_KEY, AI_MODEL, OPENAI_CLIENT

# Construct the absolute path to the training data file
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
training_data_path = os.path.join(base_dir, 'data', 'training_data', 'prompts.jsonl')

# Check if the prompts.jsonl file exists, if not use the example_training_prompts.jsonl file
if not os.path.exists(training_data_path):
    training_data_path = os.path.join(base_dir, 'data', 'training_data', 'example_training_prompts.jsonl')

client = OPENAI_CLIENT


def upload_data():
    """
    Upload the training data file to the OpenAI API.
    :return:  The ID of the uploaded training file.
    """
    # Upload a training data file - example_training_prompts.jsonl
    logging.info("Uploading training data file from path: %s", training_data_path)
    response = client.files.create(
        file=open(training_data_path, "rb"),
        purpose="fine-tune"
    )
    return response.id


# Create a fine-tuning event
def fine_tune(training_file_id):
    """
    Create a fine-tuning job with the uploaded training file and the AI model.
    :param training_file_id: the ID of the uploaded training file from upload_data()
    :return: the ID of the fine-tuning job.
    """
    logging.info("Creating fine-tuning job with training file: %s and model: %s", training_file_id, AI_MODEL)
    response = client.fine_tuning.jobs.create(
        training_file=training_file_id,
        model=AI_MODEL
    )
    return response.id


def job_status(job_id):
    """
    Retrieve the status of a fine-tuning job.
    :param job_id: the ID of the fine-tuning job.
    :return: the status of the fine-tuning job.
    """
    return client.fine_tuning.jobs.retrieve(job_id)


def cancel_job(job_id):
    """
    Cancel a fine-tuning job.
    :param job_id: the ID of the fine-tuning job to cancel.
    :return: the response from the API.
    """
    logging.info("Cancelling fine-tuning job: %s", job_id)
    return client.fine_tuning.jobs.cancel(job_id)


if __name__ == '__main__':
    training_file_id = upload_data()
    fine_tune_job_id = fine_tune(training_file_id)
    status = job_status(fine_tune_job_id)
    # if the job is ongoing, wait for it to finish
    while status.finished_at is None:
        status = job_status(fine_tune_job_id)
        if status.status == "failed":
            logging.error("Fine-tuning job %s failed.", fine_tune_job_id)
            cancel_job(fine_tune_job_id)
            break
        logging.info("Fine-tuning job status: %s", status.status)
        time.sleep(10)
    logging.info("Fine-tuning job %s finished.", fine_tune_job_id)
    # save the fine-tuned model and change the environment variable AI_MODEL to the new model
    fine_tuned_model = status.model
    logging.info("Fine-tuned model: %s", fine_tuned_model)
    # update the AI_MODEL environment variable
    os.environ["AI_MODEL"] = fine_tuned_model
    logging.info("AI_MODEL environment variable updated to: %s", fine_tuned_model)
    logging.info("Fine-tuning process completed. Make sure to update the AI_MODEL environment variable in .env file "
                 "as well.")
