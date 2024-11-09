import os
import random
import shutil
import logging
import json
from datetime import datetime, timedelta
import requests
from airflow.models import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.exceptions import AirflowSkipException
import pytz
import great_expectations as ge
from great_expectations.data_context import DataContext
import pandas as pd
from sqlalchemy import create_engine, text
from random import choice

# Paths
RAW_DATA_PATH = '/opt/airflow/raw_data/'
GOOD_DATA_PATH = '/opt/airflow/good_data/'
BAD_DATA_PATH = '/opt/airflow/bad_data/'
GX_CONFIG_PATH = '/opt/airflow/gx'  # Update this path if different

# Microsoft Teams Webhook URL
MS_TEAMS_WEBHOOK_URL = "https://epitafr.webhook.office.com/webhookb2/f08f8c45-b8c8-4a15-8c96-4e3fddad43cf@3534b3d7-316c-4bc9-9ede-605c860f49d2/IncomingWebhook/3e5936ce314d4d70bf7f815346d706e4/e9cf1a09-1814-4e9e-ba41-2bbb67ac9a9e/V2boFS04O5oeMNOa9VmA6jAQISzac2uGWRNrqWlXO-J6Q1"

# Database connection details
DATABASE_URL = 'postgresql+psycopg2://user:password@localhost:5432/dbname'  # Update this with your actual database URL

# Step 1: Read one random file from the raw_data folder
def read_data(**kwargs):
    raw_data_folder = '/opt/airflow/raw_data'
    tot_dir_files = os.listdir(raw_data_folder)
    if not tot_dir_files:
        raise AirflowSkipException("No files in the raw_data folder!")
    file_name = choice(tot_dir_files)
    file_path = os.path.join(raw_data_folder, file_name)
    df = pd.read_csv(file_path)
    ti = kwargs['ti']
    ti.xcom_push(key='file_path', value=file_path)
    ti.xcom_push(key='file_name', value=file_name)
    ti.xcom_push(key='nb_rows', value=len(df))
    ti.xcom_push(key='data', value=df.to_json(orient='records'))
    return file_path

# Step 2: Validate data with Great Expectations

def validate_data(**kwargs):
    ti = kwargs['ti']
    raw_data_folder = '/opt/airflow/raw_data'
    context = DataContext("/opt/airflow/gx")
    datasource = context.get_datasource("my_datasource")
    expectation_suite_path = os.path.join(context.root_directory, "expectations", "adv.json")

    with open(expectation_suite_path, 'r') as f:
        suite = json.load(f)

    selected_file = random.choice(os.listdir(raw_data_folder))
    file_path = os.path.join(raw_data_folder, selected_file)
    df = pd.read_csv(file_path)
    df_ge = ge.from_pandas(df)
    results = df_ge.validate(expectation_suite=suite)

    total_records = len(df)
    invalid_records, valid_records, invalid_columns, validation_success = 0, total_records, [], True

    for column_validation in results["results"]:
        if "result" in column_validation:
            column_result = column_validation["result"]
            unexpected_count = column_result.get("unexpected_count", 0)
            element_count = column_result.get("element_count", total_records)
            invalid_records += unexpected_count
            valid_records = element_count - invalid_records
            column_name = column_validation["expectation_config"]["kwargs"].get("column", "Unknown")
            if unexpected_count > 0 and column_name not in invalid_columns:
                invalid_columns.append(column_name)
                validation_success = False

    invalid_rows_percentage = (invalid_records / total_records) * 100 if total_records > 0 else 0

    validation_summary = {
        "file_name": selected_file,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "nb_rows": total_records,
        "total_records": total_records,
        "valid_records": valid_records,
        "invalid_records": invalid_records,
        "invalid_percentage": invalid_rows_percentage,
        "validation_success": validation_success,
        "invalid_columns": invalid_columns
    }

    ti.xcom_push(key='validation_results', value=validation_summary)
    return validation_summary


# Step 3: Send alerts to MS Teams
def send_alerts(**kwargs):
    validation_results = kwargs['ti'].xcom_pull(task_ids='validate_data', key='validation_results')

    if not validation_results:
        raise ValueError("No validation results received from validate_data task!")

    # Use "validation_success" to match the key in validate_data function
    validation_passed = validation_results.get("validation_success")
    if validation_passed is None:
        raise KeyError("'validation_success' key not found in validation results!")

    # Generate a report link (for simplicity, assume it exists)
    report_link = "http://example.com/report"  # Replace with actual report generation logic

    # Determine the criticality and errors
    criticality = "low" if validation_passed else "high"
    errors_summary = f"Summary of errors: {validation_results.get('invalid_columns', 'N/A')} issues detected."

    # Send Teams alert
    message = f"Data Validation Alert\n\nCriticality: {criticality}\nErrors: {errors_summary}\nReport: {report_link}"
    send_teams_alert(message)

# Send alert to MS Teams
def send_teams_alert(message):
    headers = {"Content-Type": "application/json"}
    payload = {"text": message}
    response = requests.post(MS_TEAMS_WEBHOOK_URL, json=payload, headers=headers)
    if response.status_code != 200:
        logging.error(f"Failed to send alert to MS Teams: {response.text}")
    else:
        logging.info("Alert sent to MS Teams successfully.")

# Step 4: Save statistics to the database
def save_statistics(**kwargs):
    ti = kwargs['ti']

    # Retrieve data from XCom
    file_name = ti.xcom_pull(key='file_name')
    nb_rows = ti.xcom_pull(key='nb_rows')
    validation_results = ti.xcom_pull(key='validation_results')

    # Check if validation_results is None
    if validation_results is None:
        raise ValueError("Validation results are missing or not available.")

    # Prepare data to save, with default values if keys are missing
    invalid_percentage = validation_results.get("invalid_percentage", 0)
    invalid_columns = ', '.join(validation_results.get("invalid_columns", []))
    validation_success = validation_results.get("validation_success", False)
    total_records = validation_results.get("total_records", 0)
    valid_records = validation_results.get("valid_records", 0)
    invalid_records = validation_results.get("invalid_records", 0)

    # Get current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Database connection string
    DATABASE_URL = 'postgresql://postgres:oneplusx@host.docker.internal:5432/airflowsql'

    # Create engine and connect to PostgreSQL
    engine = create_engine(DATABASE_URL)

    # Prepare the SQL query to insert data into the table
    query = text(""" 
        INSERT INTO data_statistics (
            file_name, timestamp, nb_rows, total_records, valid_records, 
            invalid_records, invalid_percentage, validation_success, invalid_columns
        ) 
        VALUES (:file_name, :timestamp, :nb_rows, :total_records, :valid_records, 
                :invalid_records, :invalid_percentage, :validation_success, :invalid_columns)
    """)

    # Execute the query
    with engine.connect() as connection:
        connection.execute(query, {
            'file_name': file_name,
            'timestamp': timestamp,
            'nb_rows': nb_rows,
            'total_records': total_records,
            'valid_records': valid_records,
            'invalid_records': invalid_records,
            'invalid_percentage': invalid_percentage,
            'validation_success': validation_success,
            'invalid_columns': invalid_columns
        })
    logging.info(f"Saved statistics for {file_name} to the database.")


def save_file(**kwargs):
    ti = kwargs['ti']

    # Pull validation results and validated data
    validation_results = ti.xcom_pull(key='validation_results', task_ids='validate_data')
    validated_data_df = ti.xcom_pull(key='validated_data', task_ids='validate_data')

    # Log the pulled values to see what's being received
    logging.info(f"Validation Results: {validation_results}")
    logging.info(f"Validated Data DataFrame: {validated_data_df}")

    # Ensure validated_data_df is not None and contains 'is_valid' column
    if validated_data_df is None:
        raise ValueError("Validated data is None, possibly due to an issue in the validate_data task.")
    if 'is_valid' not in validated_data_df.columns:
        raise ValueError("'is_valid' column is missing in the validated data")

    # Define paths for good and bad data folders
    good_data_folder = '/opt/airflow/good_data'
    bad_data_folder = '/opt/airflow/bad_data'

    # Separate good and bad data based on 'is_valid' column
    good_data = validated_data_df[validated_data_df['is_valid'] == 'yes'].drop(columns=['is_valid'])
    bad_data = validated_data_df[validated_data_df['is_valid'] == 'no'].drop(columns=['is_valid'])

    # Define file paths for saving good and bad data
    base_filename = os.path.splitext(validation_results['file_name'])[0]
    good_data_path = os.path.join(good_data_folder, f"{base_filename}_good.csv")
    bad_data_path = os.path.join(bad_data_folder, f"{base_filename}_bad.csv")

    # Save the DataFrames to the respective folders
    good_data.to_csv(good_data_path, index=False)
    bad_data.to_csv(bad_data_path, index=False)

    # Push paths to XCom for any further processing
    ti.xcom_push(key='good_data_path', value=good_data_path)
    ti.xcom_push(key='bad_data_path', value=bad_data_path)

    # Log the saved file paths for good and bad data
    logging.info(f"Good data saved to: {good_data_path}")
    logging.info(f"Bad data saved to: {bad_data_path}")

    return {"good_data_path": good_data_path, "bad_data_path": bad_data_path}


# Define the DAG
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='data_ingestion_dag_with_validation',
    default_args=default_args,
    start_date=datetime(2023, 9, 1),
    schedule_interval='* * * * *',  # Every minute
    catchup=False
) as dag:

    # Task 1: Read data
    read_data_task = PythonOperator(
        task_id='read_data',
        python_callable=read_data,
    )

    # Task 2: Validate data
    validate_data_task = PythonOperator(
        task_id='validate_data',
        python_callable=validate_data,
    )

    # Task 3: Send alerts
    send_alerts_task = PythonOperator(
        task_id='send_alerts',
        python_callable=send_alerts,
    )

    # Task 4: Save statistics
    save_statistics_task = PythonOperator(
        task_id='save_statistics',
        python_callable=save_statistics,
    )

    # Task 5: Save file based on validation result
    save_file_task = PythonOperator(
        task_id='save_file',
        python_callable=save_file,
    )

    # Task dependencies to match the desired DAG structure
    read_data_task >> validate_data_task
    validate_data_task >> [send_alerts_task, save_statistics_task, save_file_task]
