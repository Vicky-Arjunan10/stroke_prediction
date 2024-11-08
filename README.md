**Heart Stroke Risk Prediction**

An end-to-end heart stroke risk prediction system designed to evaluate patients' risk levels based on key health metrics like BMI, Glucose level, hypertension, heart disease history, using a robust machine learning model and offering a full-featured web interface. The project encompasses automated data processing, scheduled predictions, data validation, and monitoring features to maintain data integrity and model performance.

**Overview**

The Heart Stroke Risk Prediction project is an advanced system integrating various technologies to deliver reliable stroke risk assessments for patients. It features a web-based application for user interaction, an API for serving machine learning predictions, a database to store historical data, and scheduled jobs managed by Apache Airflow to automate data processing and monitoring.

**Project Structure**

The system is divided into multiple interconnected components:

**Web Application & API**

**Frameworks Used:**

Streamlit (v1.38.0) for the web interface

FastAPI (v0.112.2) for the backend API

**Key Features:**

**Interactive Form:** Users can enter individual health metrics and instantly get a prediction.

**Batch Predictions:** Users can upload CSV files for multiple predictions at once.

**History Access:** Users can view previously made predictions filtered by date or type.

**Machine Learning Model**

**Model Choice:** Logistic Regression, chosen for its interpretability and effectiveness in binary classification problems like stroke risk prediction.

**Data Preprocessing:**

Scaling:Numerical features such as age and BMI are scaled using StandardScaler.

Encoding:Categorical variables, like gender, are processed using LabelEncoder.

**Performance Metrics:**

Accuracy Score: Evaluates the overall effectiveness of the model.

Confusion Matrix: Assesses the model's true positive and negative predictions.

Classification Report: Provides precision, recall, and F1-score metrics.

Model Storage:The trained model is serialized using joblib for efficient deployment.

**Key Technologies & Libraries**

•	scikit-learn: For model development and evaluation.

•	pandas: For data manipulation and preprocessing.

•	joblib: For saving and loading the machine learning model.

•	PostgreSQL (v16): A robust database to store prediction records, ensuring data persistence and easy access.

**Database Management**

**PostgreSQL**

•	The database serves as a central hub for storing all prediction data.

•	Data Stored:

  Input features submitted for predictions.

  Output predictions (stroke risk results).

  Metadata such as timestamp and source (manual input or batch).

  Historical Predictions Interface

•	Users can query the database through the web app to view past predictions.

•	Advanced filtering options allow sorting by date and input method, enhancing the user experience.
Automated Data Processing with Apache Airflow

•	Apache Airflow (v2.6.3): Manages automated data ingestion and prediction workflows.

**Airflow DAGs:**

**Data Ingestion DAG:**

Runs every 5 minutes to process new data.

Validates incoming data (checking for missing values, outliers, etc.).

Segregates valid data for prediction and flags invalid entries.

**Prediction Job DAG:**

Detects newly validated data.

Sends data to the prediction API and stores the results in the database.

**Data Validation Steps**

**1.	Raw Data Ingestion:** Captures and processes data files from various sources.

**2.	Data Quality Checks:**

Missing Value Detection: Identifies incomplete records.

Outlier Identification: Flags abnormally high or low values in metrics.

Type Verification: Ensures data matches the expected formats.

**3.	Data Segregation:**

Good Data: Valid records ready for prediction.

Bad Data: Erroneous records flagged for review.

**Installation Guide**

**Prerequisites**

•	Python 3.9+

•	PostgreSQL v16

•	Docker 

•	Apache Airflow v2.6.3

**Setup Instructions**

1.	Clone the Repository:
   
2.	bash

git clone https://github.com/stroke_prediction.git

cd heart_stroke_prediction

3.	Create a Virtual Environment:
   
bash

python -m venv venv

source venv/bin/activate  # On Windows: venv\Scripts\activate

4.	Install Dependencies:
   
bash

pip install -r requirements.txt

5.	Initialize PostgreSQL Database:
   
Set up a new PostgreSQL database for storing prediction records.

6.	Start the API (FastAPI):
    
bash

uvicorn app.main:app --reload

7.	Launch the Web Application (Streamlit):
   
bash

streamlit run app/webapp.py

8.	Setup and Initialize Airflow:
    
bash

pip install apache-airflow

airflow db init

9.	Run Airflow Webserver and Scheduler:
    
bash

airflow webserver --port 8080

airflow scheduler


**Running the Application**

Web App (Streamlit): Accessible at http://localhost:8501

API Service (FastAPI): Running on http://localhost:8000

Airflow UI: Manage DAGs at http://localhost:8080

Grafana: http://localhost:3000



**Usage Guide**

**Web Application**

•	Single Prediction: Fill in the health metrics form for an instant stroke risk prediction.

•	Multiple Prediction: Upload a CSV file to process multiple entries simultaneously.

•	Past Predictions: Explore historical data and filter results based on various criteria.
API Service

•	Make Predictions:

bash

curl -X POST 'http://127.0.0.1:8000/predict' \

-H 'Content-Type: application/json' \

-d '{"age": 45, "bmi": 28.5, "hypertension": 1, "glucose_level": 150, ...}'

•	Retrieve Past Predictions:

bash

curl -X GET 'http://127.0.0.1:8000/past-predictions'

**Monitoring & Alerts**

•	Data Integrity: Continuous checks via Airflow ensure data quality.

•	Model Performance: Periodically review and update the model using new data insights.

•	Alerts: The system raises alerts in case of data validation failures or unexpected model behavior.
Future Enhancements

•	Model Improvement: Experiment with more complex algorithms like Random Forest or Neural Networks.

•	Enhanced Monitoring: Use tools like **Grafana** to visualize system health and model performance metrics.

•	Deployment: Package the entire system using Docker for streamlined deployment.

