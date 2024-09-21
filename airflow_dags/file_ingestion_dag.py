import os
import random
import shutil
from datetime import datetime, timedelta
import logging

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.exceptions import AirflowSkipException
import pytz

# Define paths for raw_data and good_data directories
RAW_DATA_PATH = '/opt/airflow/raw_data/'
GOOD_DATA_PATH = '/opt/airflow/good_data/'

# Task 1: Read one random file from the raw_data folder
def read_data(**kwargs):
    # Get a list of all files in the raw_data folder
    files = os.listdir(RAW_DATA_PATH)

    if not files:
        raise AirflowSkipException("No files in the raw_data folder!")

    # Randomly choose one file
    selected_file = random.choice(files)
    file_path = os.path.join(RAW_DATA_PATH, selected_file)

    # Pass the selected file path to the next task via XCom
    return file_path

# Task 2: Move the selected file to the good_data folder
def save_file(**kwargs):
    # Fetch the file path returned by the read_data task
    ti = kwargs['ti']
    file_path = ti.xcom_pull(task_ids='read_data')

    if not file_path:
        raise FileNotFoundError("No file path received from the read_data task!")

    # Move the file from raw_data to good_data
    file_name = os.path.basename(file_path)

    # Get the current timestamp in Paris timezone
    paris_tz = pytz.timezone('Europe/Paris')
    timestamp = datetime.now(paris_tz).strftime("%Y%m%d_%H%M%S")

    # Create a new file name with timestamp
    new_file_name = f"{timestamp}_{file_name}"
    destination_path = os.path.join(GOOD_DATA_PATH, new_file_name)

    shutil.move(file_path, destination_path)
    logging.info(f"File {file_name} moved to good_data folder as {new_file_name}.")

# Define the DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='file_ingestion_dag',
    default_args=default_args,
    start_date=datetime(2023, 9, 1),
    schedule_interval='* * * * *',  # Change this to the interval you want
    catchup=False
) as dag:

    # Task 1: Read one file randomly from raw_data
    read_data_task = PythonOperator(
        task_id='read_data',
        python_callable=read_data,
    )

    # Task 2: Move the file to good_data
    save_file_task = PythonOperator(
        task_id='save_file',
        python_callable=save_file,
    )

    # Set the task dependencies
    read_data_task >> save_file_task
