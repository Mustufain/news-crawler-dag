Airflow dag to orchestrate news crawler
--
Dag runs daily at midnight and crawls all the news articles posted on the day. 

# Usage
1. Run database migrations and create first user account: ``docker-compose up airflow-init``
2. Start all services: ```docker-compose up```
3. The webserver available at: ```http://localhost:8080```. The default account has the login ```airflow``` and the password ```airflow```.

For detailed info: https://airflow.apache.org/docs/apache-airflow/stable/start/docker.html

Currently it is integrated with news-crawler and runs a docker container in AWS ECS.

There are two dags in ```/dags``` folder:
1. ```news_crawler_dag``` is scheduled to run daily starting from ```June 1st 2021```
2. ```news_crawler_historical_dag``` processes historical data from 
   ```Jan 1st 2014``` to ```May 31st 2021```.
   