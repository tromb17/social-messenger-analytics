import telegram
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import pandas as pd
import pandahouse as ph
from datetime import datetime, timedelta
from airflow.decorators import dag, task
from airflow.operators.python import get_current_context

#%matplotlib inline

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
    'start_date': datetime(2025, 6, 26),
}

# интервал запуска
schedule_interval = '0 11 * * *'

@dag(default_args=default_args, schedule_interval=schedule_interval, catchup=False)
def dag_report_troshin():
    
    @task
    def extract_dfs():
        q = """
            SELECT 
                toDate(time) AS date,
                uniqExact(user_id) AS DAU,
                sum(action = 'like') as likes,
                sum(action = 'view') as views,
                likes/views as CTR
            FROM simulator_20250620.feed_actions
            WHERE toDate(time) BETWEEN today()-7 AND today()-1
            GROUP BY date
            ORDER BY date
            """
        df = ph.read_clickhouse(q, connection=connection)
        return df
    
    @task
    def send_report(df, chat_id=None):
        
        df_yesterday = df[-1:]
        my_token = '***' # тут нужно заменить на токен вашего бота
        bot = telegram.Bot(token=my_token) # получаем доступ
        chat_id = chat_id or -1002614297220

        #формирование сообщения в бот
        message = (f"Значения ключевых метрик за {df_yesterday['date'].dt.strftime('%d-%m-%Y').values[0]}\n"
           f"- DAU: {df_yesterday['DAU'].values[0]}\n"
           f"- Просмотры: {df_yesterday['views'].values[0]}\n"
           f"- Лайки: {df_yesterday['likes'].values[0]}\n"
           f"- CTR: {round(df_yesterday['CTR'].values[0], 3)}\n")

        #print(message)
        bot.sendMessage(chat_id=chat_id, text=message, parse_mode="Markdown")

        sns.set(rc = {'figure.figsize':(21,9)})

        # DAU
        plt.subplot(2, 2, 1)
        sns.barplot(x=df['date'].dt.date, y=df['DAU'], color = 'b')
        plt.title('DAU', fontsize = 25, pad = 20)
        plt.ylim(bottom = min(df['DAU']) - min(df['DAU']) * .05, top = max(df['DAU']) * 1.01)
        plt.xlabel(''), plt.ylabel('')

        # VIEWS
        plt.subplot(2, 2, 2)
        sns.lineplot(x=df['date'].dt.date, y=df['views'], color = 'b', label = 'views')
        plt.figtext(0.3, 0.03, 'Просмотры', ha = "center", fontsize = 25)
        plt.ylim(bottom = 500000)
        plt.xlabel(''), plt.ylabel('')

        # LIKES
        plt.subplot(2, 2, 3)
        sns.lineplot(x=df['date'].dt.date, y=df['likes'], color = 'b')
        plt.figtext(0.72, 0.9, 'Лайки', ha = "center", fontsize = 25)
        plt.ylim(bottom = 100000)
        plt.xlabel(''), plt.ylabel('')

        # CTR
        plt.subplot(2, 2, 4)
        sns.barplot(x=df['date'].dt.date, y=df['CTR'], color = 'b')
        plt.figtext(0.72, 0.03, 'CTR', ha = "center", fontsize = 25)
        plt.ylim(bottom = min(df['CTR']) - min(df['CTR']) * .05, top = max(df['CTR']) * 1.05)
        plt.xlabel(''), plt.ylabel('')

        plot_object = io.BytesIO()
        plt.savefig(plot_object)
        plot_object.seek(0)
        plot_object.name = 'plot.png'
        plt.close()
        bot.sendPhoto(chat_id=chat_id, photo=plot_object)
    
    df = extract_dfs()
    send_report(df)
    
dag_report_troshin = dag_report_troshin()
