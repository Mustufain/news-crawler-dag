from datetime import date, datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.operators.ecs import ECSOperator
from airflow.models import Variable


start_date = date(2014, 1, 1)  # 1st Jan 2014
end_date = date(2021, 5, 31)  # 31st May 2021
start_datetime = datetime.combine(start_date,
                                      datetime.min.time())
end_datetime = datetime.combine(end_date,
                                datetime.min.time())

default_args = {
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
    'start_date': start_datetime,
    'end_date': end_datetime
}

NEWS_CRAWLER_DAG = DAG(dag_id='news_crawler_historical',
                       schedule_interval='@daily',  # every day at midnight
                       default_args=default_args,
                       concurrency=2,
                       catchup=True)


SCRAPER = ECSOperator(task_id='news_scraper_historical',
                      dag=NEWS_CRAWLER_DAG,
                      # set this connection id in airflow web UI
                      aws_conn_id="aws_default",
                      cluster="news-crawler-ecs",
                      task_definition="ecs-task-definition",
                      launch_type="FARGATE",
                      overrides={"containerOverrides": [
                          {
                              "name": "news-crawler-container",
                              "command": ['{{ds}}']
                          },
                      ],
                      },
                      network_configuration={
                          "awsvpcConfiguration": {
                              # set these variables in airflow web UI
                              "securityGroups": [Variable.get("SECURITY_GROUP_ID")],
                              "subnets": [Variable.get("SUBNET_ID")],
                              "assignPublicIp": "ENABLED",
                          },
                      },
                      awslogs_group="/ecs/ecs-task-definition")

# pylint: disable=pointless-statement
SCRAPER
