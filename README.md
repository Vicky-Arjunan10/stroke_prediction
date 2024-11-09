# **Heart Stroke Risk Prediction**

An end-to-end stroke prediction application using machine learning to assess patient risk based on health metrics.

## **Project Overview**

This project predicts heart stroke risks for men and women by analyzing key health metrics. The system includes a web interface, machine learning API, database storage, scheduled jobs, data validation, and monitoring.

**Project Components**
FastAPI
Version: 0.104.0

The API, built with FastAPI, handles requests for predictions based on user data, integrating with the machine learning model and a PostgreSQL database.

**Endpoints:**
predict: POST request for predictions and storing results.
get-predict: GET request to retrieve stored predictions.

**Streamlit**
Version: 1.27.2

The user interface, developed with Streamlit, provides an interactive web application for users to:

Make single predictions: Enter health data directly.
Upload CSV for batch predictions: Analyze multiple patient records at once.
View history: Filter past predictions by date, source (web app or scheduled jobs).


**Model Training**
Using a Logistic Regression model, this project predicts the probability of a heart stroke based on features like age, BMI, glucose level, and history of hypertension and other diseases.

**File Descriptions**
Here’s a breakdown of the project files and folders:

graphql
Copy code
├── airflow            # Airflow DAGs validated by Great Expectations
│   ├── dags
│   ├── logs
│   └── gx
├── api-db             # FastAPI and PostgreSQL integration
│   ├── main.py        # Main FastAPI script
│   └── functions.py   # Functions for database interactions
├── app                # Streamlit web app
│   ├── Predict.py     # Single and batch prediction pages
│   ├── History.py     # History viewing page
│   └── utils.py       # Helper functions for the app
├── model              # Stored trained model
│   ├── DSP_NLP_Review.ipynb   # Notebook for model training
│   ├── dsp_project_model.pkl  # Trained logistic regression model
│   └── dsp_project_tfidf_model.pkl # TF-IDF model for text preprocessing
├── images             # README images and other visuals
├── README.md
├── requirements.txt   # Project dependencies
└── .gitignore

## **Main Components**
Web App
The app has two primary pages:

Predict: Generate predictions in three ways:
Enter your own review: Input custom text.
Generate a random review: Use a preset example.
Upload a CSV: Batch predictions from uploaded files.
History: View and filter prediction history, with options to filter by date and type (app or scheduled job).
API
Implemented two main endpoints using FastAPI:

predict: Handles prediction inference and stores results in the database.
get-predict: Retrieves stored predictions for review.

**Database**
Using PostgreSQL to store predictions, with a table schema that includes:

id: Unique identifier for each prediction
review: User-submitted review text
rating: Predicted score from the model
time: Timestamp for each prediction
type: Source of prediction (App or Scheduled Job)
Job Scheduling
Two DAGs are implemented in Airflow for scheduled tasks:

Ingest Data: Collects new data and validates with Great Expectations every minute.
Predict Data: Processes a batch of new data for predictions every two minutes.

**Data Validation**
Using Great Expectations to enforce data quality standards:

Review text must not be null.
Length: Text cannot exceed specified character limits.
Spam: Detected spam entries are rejected.
No URLs: Links are not allowed in text.

**Data Monitoring**
A Grafana dashboard provides real-time monitoring of prediction and ingestion jobs, pulling data from PostgreSQL.

Installation & Setup
Initial Installation
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Install Docker and Docker Compose (Docker Desktop can be used).

Build Docker image and start services:

bash
Copy code
cd airflow
docker build -f Dockerfile -t {name_of_the_image}:latest .
docker-compose -f "docker-compose.yml" up -d --build
Running Steps
Run FastAPI server:

bash
Copy code
cd api-db
uvicorn main:app --reload
Access: localhost:8000
Run Streamlit web app:

bash
Copy code
cd app
streamlit run Predict.py
Access: localhost:8501
Run Airflow webserver:

Access: localhost:8080

**Usage Guide
Web Application**

• Single Prediction: Fill in the health metrics form for an instant stroke risk prediction.
• Multiple Prediction: Upload a CSV file to process multiple entries simultaneously.
• Past Predictions: Explore historical data and filter results based on various criteria. API Service
• Make Predictions:
bash
curl -X POST 'http://127.0.0.1:8000/predict' \
-H 'Content-Type: application/json' \
-d '{"age": 45, "bmi": 28.5, "hypertension": 1, "glucose_level": 150, ...}'
• Retrieve Past Predictions:
bash
curl -X GET 'http://127.0.0.1:8000/past-predictions'
Monitoring & Alerts
• Data Integrity: Continuous checks via Airflow ensure data quality.
• Model Performance: Periodically review and update the model using new data insights.
• Alerts: The system raises alerts in case of data validation failures or unexpected model behavior. Future Enhancements
• Model Improvement: Experiment with more complex algorithms like Random Forest or Neural Networks.
• Enhanced Monitoring: Use tools like Grafana to visualize system health and model performance metrics.
• Deployment: Package the entire system using Docker for streamlined deployment.
has context menu.

# **Thank you**
