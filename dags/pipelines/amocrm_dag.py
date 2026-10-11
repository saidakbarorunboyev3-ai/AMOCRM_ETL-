import pendulum

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
from datetime import datetime, timedelta

with DAG(
    dag_id="amoCRM_ETL",
    start_date=pendulum.datetime(2026, 10, 1, tz="Asia/Tashkent"),
    schedule="0 14 * * *",        
    catchup=False,
     default_args={"retries": 2, "retry_delay": timedelta(minutes=5)},
) as dag:

    
    run_Leads = BashOperator(
        task_id="run_Leads",
        bash_command="python amo_leads.py",
        cwd="/opt/airflow/dags/pipelines",
    )

    run_companies = BashOperator(
        task_id="run_companies",
        bash_command="python companies.py",
        cwd="/opt/airflow/dags/pipelines",
    )

    run_contacts = BashOperator(
        task_id="run_contacts",
        bash_command="python contacts.py",
        cwd="/opt/airflow/dags/pipelines",
    )

    run_tasks = BashOperator(
        task_id ="run_tasks",
        bash_command ="python tasks.py",
        cwd ="/opt/airflow/dags/pipelines",
    )

    run_users = BashOperator(
        task_id = "run_users",
        bash_command ="python users.py",
        cwd = "/opt/airflow/dags/pipelines"
    )

    run_users >> run_companies >> run_contacts >> run_Leads >> run_tasks

  
