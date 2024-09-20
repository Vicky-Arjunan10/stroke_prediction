import streamlit as st
import pandas as pd
import requests

# Streamlit page configuration
st.set_page_config(layout='wide')

# Page title
st.title("Heart Stroke Risk Prediction")
selection = st.selectbox("Select Prediction Type", ('Single Prediction', 'Multiple Prediction'),
                         index=0)  # Default to Single Prediction

# Single Prediction Form
if selection == 'Single Prediction':
    with st.form('Heart Stroke Prediction Form'):
        # Set default values
        default_gender = 'Male'
        default_hypertension = 'No'
        default_heart_diseases = 'No'
        default_age = 30
        default_glucose_level = 100.0
        default_bmi = 25.0

        # Gender selectbox with a default value
        gender = st.selectbox("Select Gender", ('Male', 'Female'), index=0 if default_gender == 'Male' else 1)

        # Hypertension selectbox with a default value
        hypertension = st.selectbox("Do you have Hypertension?", ('Yes', 'No'),
                                    index=0 if default_hypertension == 'Yes' else 1)

        # Heart diseases selectbox with a default value
        heart_diseases = st.selectbox("Do you have Heart Diseases?", ('Yes', 'No'),
                                      index=0 if default_heart_diseases == 'Yes' else 1)

        # Convert 'Yes'/'No' responses to 1/0
        hypertension = 1 if hypertension == 'Yes' else 0
        heart_diseases = 1 if heart_diseases == 'Yes' else 0

        # Age number input with a default value
        age = st.number_input("Age", step=1, min_value=0, max_value=100, value=default_age)

        # Glucose level number input with a default value
        glucose_level = st.number_input("Glucose Level", step=0.1, min_value=0.0, max_value=500.0,
                                        value=default_glucose_level)

        # BMI number input with a default value
        bmi = st.number_input("BMI", step=0.1, min_value=0.0, max_value=100.0, value=default_bmi)

        # Predict button
        button = st.form_submit_button('Predict')

    if button:
        # Prepare data for single prediction
        data = {
            'data': {
                'gender': gender,
                'age': age,
                'hypertension': hypertension,
                'diseases': heart_diseases,
                'glucose': glucose_level,
                'bmi': bmi
            }
        }

        # API call to the FastAPI `/predict` endpoint
        url = 'http://127.0.0.1:8000/predict'
        response = requests.post(url, json=data)

        if response.status_code == 200:
            st.write(f'Your risk of getting a heart stroke is **{response.json()}**')
        else:
            st.write(f"Error in calling API. Status code: {response.status_code}")

# Multiple Prediction Form
if selection == 'Multiple Prediction':
    file = st.file_uploader('Upload CSV or Excel file', type=['csv',])
    if file is not None:
        # Read the uploaded file
        df = pd.read_csv(file)
        data = df.to_dict(orient='records')
        json_data = {'data': data}

        csv_button = st.button('Predict')

        if csv_button:
            # API call to the FastAPI `/predict` endpoint for multiple predictions
            url = 'http://127.0.0.1:8000/predict'
            response = requests.post(url, json=json_data)

            if response.status_code == 200:
                result = response.json()
                result_df = pd.DataFrame(result, columns=['Risk'])
                output_df = pd.concat([df, result_df], axis=1)
                st.dataframe(output_df, hide_index=True)
            else:
                st.write(f"Error in calling API. Status code: {response.status_code}")
