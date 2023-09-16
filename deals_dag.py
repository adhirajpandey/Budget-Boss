from datetime import timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from fetch_images import getImages
from extract_deals import getDeals


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'bb_deals_dag',
    default_args=default_args,
    description='DAG for fetching deals and images for BudgetBoss',
    schedule_interval='*/15 * * * *',
    catchup=False
)

fetch_deals_task = PythonOperator(
    task_id='fetch_new_deals',
    python_callable=getDeals,
    dag=dag,
)

fetch_images_task = PythonOperator(
    task_id='fetch_new_images',
    python_callable=getImages,
    dag=dag,
)

fetch_deals_task >> fetch_images_task
