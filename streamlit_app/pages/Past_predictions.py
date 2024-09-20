import streamlit as st
import requests
import pandas as pd

st.title("Past Predictions Page")

with st.form('Past Predictions Form'):
    start_date = st.date_input("Enter Start Date")
    end_date = st.date_input("Enter End Date")
    source = st.selectbox("Select Source", ("webapp", "Scheduled", "All"), index=2)
    submit = st.form_submit_button("Retrieve Data")

if submit:
    url = "http://localhost:8000/past_predictions"
    data= {"start": start_date, "end": end_date, "source": source}
    response = requests.get(url, params=data)

    if response.status_code == 200:
        prediction = response.json()
        df = pd.DataFrame(prediction)
        column_order = ['id','created_date', 'created_time', 'source',
                        'gender', 'age', 'heart_diseases', 'hypertension',
                        'glucose', 'bmi', 'result']
        df = df.reindex(columns=column_order)
        st.dataframe(df, hide_index=True)
    else:
        st.error("Error in data Retrieval")
