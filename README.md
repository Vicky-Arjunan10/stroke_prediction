**Heart Stroke Risk Prediction**
An end-to-end stroke prediction application using machine learning to assess patient risk based on health metrics

Overview
This project involves predicting heart-stroke prediction for men and women. The system integrates a web interface, machine learning API, database for storing predictions, scheduled jobs, data validation, and monitoring tools.

Project Components
1. FastAPI (v0.95.2)**
The API service built using FastAPI handles requests for making predictions based on user input (single and multiple predictions). It communicates with the machine learning model and the database for storing predictions.

2. Streamlit (v1.19.0)
The user interface is developed using Streamlit, providing an interactive web application where users can:
- Make single predictions by filling in a form.
- Make multiple predictions by uploading a CSV file.
- View past predictions based on selected date ranges and sources (web app or scheduled).

3.Model Training

This project uses a Logistic Regression model to predict the risk of heart stroke based on various health factors such as age, BMI, hypertension, and glucose levels. The model is trained using a dataset containing relevant health records. We implemented scaling for numerical features using StandardScaler and handled categorical variables with a LabelEncoder. The final model is saved using joblib for deployment via FastAPI. Model accuracy and performance are evaluated using standard metrics like accuracy score, confusion matrix, and classification report.

Key Libraries:
scikit-learn: For model training and evaluation.
pandas: For data handling and preprocessing.
joblib: For model saving/loading.

4. PostgreSQL Database(v16)
A PostgreSQL database is used to store predictions and the corresponding input features. This allows easy retrieval of historical predictions and serves as the central storage for all prediction data.

5. Past Predictions
The web application allows users to view previously made predictions. Users can filter these by date range and source (web-based or scheduled predictions).

6. Airflow DAGs (v2.6.3)
An Airflow DAG (Directed Acyclic Graph) is scheduled to run every 5 minutes to:
- Ingest new data.
- Validate the data.
- Make predictions on clean data.
- Store predictions in the database.

7. Data Ingestion
- Raw Data: Data files are ingested as raw inputs and passed through a validation process.
- Good Data: Data that passes validation is used for making predictions. Invalid data is flagged and stored separately.


Installation Software Versions

- FastAPI: `v0.95.2`
- Streamlit: `v1.19.0`
- PostgreSQL: v16
- Airflow: `v2.6.3`
- Python: `v3.9+`





