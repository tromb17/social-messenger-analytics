import pandahouse as ph
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import pytz

import seaborn as sns

from io import StringIO
import io
import requests
import telegram
import matplotlib.pyplot as plt

from airflow.decorators import dag, task
from airflow.operators.python import get_current_context

# Подключение к базе
connection = {
    'host': 'https://clickhouse.lab.karpov.courses',
    'password': 'dpo_python_2020',
    'user': 'student',
    'database': 'simulator_20250620'
}

# параметры dag
default_args = {
    'owner': 'troshin_vs',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2025, 8, 3),
}

# интервал запуска
schedule_interval = '*/15 * * * *'

now_time = datetime.now(tz=pytz.timezone("Europe/Moscow"))
time_to_check = now_time.strftime('%Y-%m-%d %H:%M:%S')
time_to_compare = (now_time - timedelta(1)).strftime('%Y-%m-%d %H:%M:%S')

def ch_get_df(query='Select 1', host='https://clickhouse.lab.karpov.courses', user='student', password='dpo_python_2020'):
    r = requests.post(host, data=query.encode("utf-8"), auth=(user, password), verify=False)
    result = pd.read_csv(StringIO(r.text), sep='\t')
    return result


@dag(default_args=default_args, schedule_interval=schedule_interval, catchup=False)
def dag_alert_troshin():
    
    @task
    def extract_feed_df(end_time):
        query = f"""
                SELECT
                    toStartOfFifteenMinutes(time) AS event_date,
                    count(DISTINCT user_id) AS feed_users,
                    countIf(action = 'like') AS likes,
                    countIf(action = 'view') AS views,
                    ROUND(countIf(action = 'like') / countIf(action = 'view'), 2) AS ctr
                  FROM
                    simulator_20250620.feed_actions
                  WHERE
                    toStartOfFifteenMinutes(time) < toStartOfFifteenMinutes(toDateTime('{end_time}'))
                  GROUP BY
                    event_date
                  ORDER BY
                    event_date DESC
                  LIMIT 10
                FORMAT TSVWithNames
                """
        df = ch_get_df(query=query)
        return df
    
    @task
    def extract_msg_df(end_time):
        query = f"""
                  SELECT
                   toStartOfFifteenMinutes(time) as event_date,
                   count() as sent_messages,
                   count(distinct user_id) as message_users
                  FROM
                    simulator_20250620.message_actions
                WHERE
                    toStartOfFifteenMinutes(time) < toStartOfFifteenMinutes(toDateTime('{end_time}')) 
                  GROUP BY
                    event_date
                  ORDER BY
                    event_date DESC
                  LIMIT 10
                FORMAT TSVWithNames"""
        df = ch_get_df(query=query)
        return df

    @task
    def send_alert(df_current, df_previous, metric, threshold_pct):
        my_token = '***' #токен вашего бота
        bot = telegram.Bot(token=my_token)
        chat_id = -969316925
        
        current_value = df_current.iloc[0][metric]
        yesterday_value = df_previous.iloc[0][metric]
        difference_pct = current_value/yesterday_value*100
        if abs(100-difference_pct) > threshold_pct:
            if difference_pct>100:
                alrt_mssg = f'Метрика {metric} значительно повысилась \nТекущее значение: {current_value}\
                 \nЗначение за предыдущий день: {yesterday_value} \nРазница: {round(abs(100-difference_pct),2)}%'

            if difference_pct<100:
                alrt_mssg = f'Метрика {metric} значительно понизилась \nТекущее значение: {current_value}\
                 \nЗначение за предыдущий день: {yesterday_value} \nРазница: {round(abs(100-difference_pct),2)}%'

            #Отправка сообщения в чат
            bot.sendMessage(chat_id=chat_id, text=alrt_mssg)
            
            # Подготовка данных для графика
            df_current['day_type'] = 'current'
            df_previous['day_type'] = 'previous'

            df_combined = pd.concat([df_current, df_previous])

            df_combined['event_date'] = pd.to_datetime(df_combined['event_date']).dt.strftime('%H:%M:%S')
            df_combined = df_combined.sort_values(by='event_date')
            
            # Построение графика
            plt.figure(figsize=(12, 6))
            sns.lineplot(data=df_combined, x='event_date', y=metric, hue='day_type', marker='o')
            plt.xticks(rotation=45)
            plt.title(f'Значения {metric} по дням (текущий и предыдущий)')
            plt.tight_layout()
            
            # Отправка графика в чат
            plot_object = io.BytesIO()
            plt.tight_layout()
            plt.savefig(plot_object)
            plot_object.seek(0)
            plot_object.name = 'alert_metrics.png'
            plt.close()
            bot.sendPhoto(chat_id=chat_id, photo=plot_object)

                
    df_feed_current = extract_feed_df(time_to_check)
    df_yesterday = extract_feed_df(time_to_compare)
    df_msg_current = extract_msg_df(time_to_check)
    df_msg_yesterday = extract_msg_df(time_to_compare)
    
    for i in ['feed_users', 'likes', 'views', 'ctr']:
        send_alert(df_feed_current, df_yesterday, i, 50)

    for i in ['sent_messages', 'message_users']:
        send_alert(df_msg_current, df_msg_yesterday, i, 50)

dag_alert_troshin = dag_alert_troshin()
    
