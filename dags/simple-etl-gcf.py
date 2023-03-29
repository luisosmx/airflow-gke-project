from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
import requests

# Make the request to GCF
def run_gcf():
    # The API endpoint
  url = "https://etl-ine-fn3dsc324a-uc.a.run.app"

  # A GET request to the API
  response = requests.get(url)

  # Print the response
  response_text = response.text
  print(response_text)

dag = DAG('simple-etl-gcf', description='Simple ETL GCF',
          schedule_interval=None,
          start_date=datetime(2023, 3, 29), catchup=False)

request_operator = PythonOperator(task_id='run_simple_gcf', python_callable=run_gcf, dag=dag)

request_operator