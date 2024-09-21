import os
import requests
import pandas as pd
import logging
from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from datetime import datetime, timedelta

# Define paths
GOOD_DATA_PATH = '/opt/airflow/good_data/'
PROCESSED_FILES_DIR = '/opt/airflow/processed_files_list/'  # Folder to track processed files

# Ensure the processed files folder exists
if not os.path.exists(PROCESSED_FILES_DIR):
    os.makedirs(PROCESSED_FILES_DIR)

# Define the file to track processed files
PROCESSED_FILES_PATH = os.path.join(PROCESSED_FILES_DIR, 'processed_files.txt')

# Define the function for checking new data
def check_for_new_data(**kwargs):
    # List all files in the good_data directory
    files = [f for f in os.listdir(GOOD_DATA_PATH) if f.endswith('.csv')]

    # Read the processed files
    processed_files = {}
    if os.path.exists(PROCESSED_FILES_PATH):
        with open(PROCESSED_FILES_PATH, 'r') as f:
            for line in f.readlines():
                parts = line.strip().split('|')
                processed_files[parts[0]] = parts[1:]  # Store file name and details

    # Identify new files
    new_files = [f for f in files if f not in processed_files]

    if not new_files:
        # If no new files are found, mark the DAG as skipped
        logging.info("No new files found. Skipping DAG run.")
        return False  # ShortCircuitOperator will skip the downstream tasks

    # If new files are found, pass the list to the next task
    kwargs['ti'].xcom_push(key='files', value=new_files)
    return True

# Define the function for making predictions
def make_predictions(**kwargs):
    # Fetch the list of files from XCom
    ti = kwargs['ti']
    files = ti.xcom_pull(task_ids='check_for_new_data', key='files')

    if not files:
        logging.info("No new files to process.")
        return

    # Define the API endpoint for making predictions
    api_url = os.getenv('API_URL', 'http://host.docker.internal:8000/predict')

    for file in files:
        file_path = os.path.join(GOOD_DATA_PATH, file)
        data = pd.read_csv(file_path)

        # Handle NaN values: replace with None
        data = data.where(pd.notnull(data), None)
        data_json = {'data': data.to_dict(orient='records')}
        process_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Make the API call
        try:
            response = requests.post(api_url, json=data_json)
            response.raise_for_status()

            logging.info(f"Predictions for {file} successfully made.")

            # Log the processed file details
            with open(PROCESSED_FILES_PATH, 'a') as f:
                f.write(f"{file}|{process_time}|Success|No\n")

        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to make predictions for {file}. Error: {e}")

            # Log the failed attempt
            with open(PROCESSED_FILES_PATH, 'a') as f:
                f.write(f"{file}|{process_time}|Failed|Yes\n")

# Define default arguments
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
        dag_id='prediction_job_dag',
        default_args=default_args,
        start_date=datetime(2024, 9, 15),
        schedule_interval='*/2 * * * *',  # Runs every 2 minutes
        catchup=False,
        max_active_runs=1  # Prevent overlapping runs
) as dag:

    # Task 1: Check for new data
    check_for_new_data_task = ShortCircuitOperator(
        task_id='check_for_new_data',
        python_callable=check_for_new_data,
        provide_context=True
    )

    # Task 2: Make predictions
    make_predictions_task = PythonOperator(
        task_id='make_predictions',
        python_callable=make_predictions,
        provide_context=True,
        depends_on_past=True  # Ensure it only runs after the previous task has completed
    )

    # Set task dependencies
    check_for_new_data_task >> make_predictions_task
