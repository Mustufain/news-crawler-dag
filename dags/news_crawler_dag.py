from datetime import date, datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.operators.ecs import ECSOperator
from airflow.models import Variable
from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator


def alert_slack_channel(context):
    """
    Send alerts to slack channel on airflow failure
    :param context:
    :return:
    """
    # url on slack incoming web hook
    webhook = Variable.get("SLACK_WEBHOOK")

    last_task = context.get('task_instance')
    task_name = last_task.task_id
    log_link = f"<{last_task.log_url}|{task_name}>"
    error_message = context.get('exception') or context.get('reason')

    execution_date = context.get('execution_date')
    title = f':red_circle: {task_name} has failed!'
    msg_parts = {
        'Execution date': execution_date,
        'Log': log_link,
        'Error': error_message
    }
    msg = "\\n".join([title,
                      *[f"*{key}*: {value}" for key, value in msg_parts.items()]
                      ]).strip()

    SlackWebhookOperator(
        task_id='notify_slack_channel',
        http_conn_id=webhook,
        message=msg,
    ).execute(context=None)


start_date = date(2021, 6, 1)  # 1 June 2021
start_datetime = datetime.combine(start_date,
                                  datetime.min.time())
default_args = {
    'retries': 2,
    'retry_delay': timedelta(minutes=2),
    'start_date': start_datetime,
    'on_failure_callback': alert_slack_channel
}

NEWS_CRAWLER_DAG = DAG(dag_id='news_crawler',
                       schedule_interval='@daily',  # every day at midnight
                       default_args=default_args,
                       concurrency=3,
                       catchup=True)


SCRAPER = ECSOperator(task_id='news_scraper',
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
