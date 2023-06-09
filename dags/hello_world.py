from datetime import datetime
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator

def print_hello():
    return 'Hello world! This worked!'

def print_sum():
    a = 5
    b = 7
    return f"{a} + {b} = {a+b}"

def print_division():
    a = 10
    b = 2
    return f"{a} / {b} = {a/b}"

def print_multiplication():
    a = 8
    b = 5
    return f"{a} * {b} = {a*b}"

dag = DAG('hello_world', description='Hello World DAG',
          schedule_interval='0 12 * * *',
          start_date=datetime(2017, 3, 20), catchup=False)

hello_operator = PythonOperator(task_id='hello_task', python_callable=print_hello, dag=dag)
sum_operator = PythonOperator(task_id='sum_task', python_callable=print_sum, dag=dag)
division_operator = PythonOperator(task_id='division_task', python_callable=print_division, dag=dag)
multiplication_operator = PythonOperator(task_id='multiplication_task', python_callable=print_multiplication, dag=dag)

hello_operator >> sum_operator >> division_operator >> multiplication_operator
