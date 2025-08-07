import telegram
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io
import pandas as pd
import pandahouse as ph
from datetime import datetime, timedelta
import math
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
    'start_date': datetime(2025, 7, 27),
}

# интервал запуска
schedule_interval = '0 11 * * *'

@dag(default_args=default_args, schedule_interval=schedule_interval, catchup=False)
def dag_final_report_troshin():
    
    @task
    def extract_feed_df():
        q = """
            SELECT 
                toDate(time) AS date,
                uniqExact(user_id) AS DAU_feed,
                uniqExact(post_id) AS post_viewed,
                sum(action = 'like') AS likes,
                sum(action = 'view') AS views,
                likes/DAU_feed AS avg_likes_per_user,
                views/DAU_feed AS avg_views_per_user,
                likes/views as CTR
            FROM simulator_20250620.feed_actions
            WHERE toDate(time) BETWEEN today()-31 AND today()-1
            GROUP BY date
            ORDER BY date
            """
        df = ph.read_clickhouse(q, connection=connection)
        return df
    
    @task
    def extract_message_df():
        q = """
            SELECT 
                toDate(time) AS date,
                uniqExact(user_id) AS DAU_message,
                count(*) AS count_messages,
                count_messages/DAU_message AS avg_messages_per_user
            FROM simulator_20250620.message_actions
            WHERE toDate(time) BETWEEN today()-31 AND today()-1
            GROUP BY date
            ORDER BY date
            """
        df = ph.read_clickhouse(q, connection=connection)
        return df
    
    @task
    def send_report(feed_df, message_df, chat_id=None):
        
        def percentage_change(old, new):
            new = float(new)
            old = float(old)

            if math.isclose(old, 0.0):
                return 0.0 
            return (new - old) / old * 100
    
        def get_users_by_status():
            query='''
            SELECT this_week as week, -uniq(user_id) as users_number, status FROM

                (SELECT user_id, 
                groupUniqArray(toMonday(toDate(time))) as weeks_visited, 
                addWeeks(arrayJoin(weeks_visited), +1) this_week, 
                if(has(weeks_visited, this_week) = 1, 'retained', 'gone') as status, 
                addWeeks(this_week, -1) as previous_week
                FROM simulator_20250620.feed_actions
                group by user_id)

                where status = 'gone'

                group by this_week, previous_week, status

                HAVING this_week != addWeeks(toMonday(today()), +1)

                union all


                SELECT this_week as week, toInt64(uniq(user_id)) as users_number, status FROM

                (SELECT user_id, 
                groupUniqArray(toMonday(toDate(time))) as weeks_visited, 
                arrayJoin(weeks_visited) this_week, 
                if(has(weeks_visited, addWeeks(this_week, -1)) = 1, 'retained', 'new') as status, 
                addWeeks(this_week, -1) as previous_week
                FROM simulator_20250620.feed_actions
                group by user_id)

                group by this_week, previous_week, status
            '''
            users_by_status = ph.read_clickhouse(query=query, connection=connection)
            return users_by_status

        my_token = '***' # токен бота
        bot = telegram.Bot(token=my_token) # получаем доступ
        chat_id = chat_id or -1002614297220 #477555112

        max_date = feed_df['date'].dt.date.max()
        min_date = max_date -  pd.to_timedelta(30, unit='d')

        min_date = min_date.strftime('%Y-%m-%d')
        max_date = max_date.strftime('%Y-%m-%d')

        # Подготовка переменных
        dau_feed_now = feed_df[feed_df['date'] == max_date]['DAU_feed'].values[0]
        dau_feed_month_ago = feed_df[feed_df['date'] == min_date]['DAU_feed'].values[0]
        dau_feed_change = percentage_change(dau_feed_month_ago, dau_feed_now)

        posts_viewed_now = feed_df[feed_df['date'] == max_date]['post_viewed'].values[0]
        posts_viewed_month_ago = feed_df[feed_df['date'] == min_date]['post_viewed'].values[0]
        posts_viewed_change = percentage_change(posts_viewed_month_ago, posts_viewed_now)

        likes_now = feed_df[feed_df['date'] == max_date]['likes'].values[0]
        likes_month_ago = feed_df[feed_df['date'] == min_date]['likes'].values[0]
        likes_change = percentage_change(likes_month_ago, likes_now)

        views_now = feed_df[feed_df['date'] == max_date]['views'].values[0]
        views_month_ago = feed_df[feed_df['date'] == min_date]['views'].values[0]
        views_change = percentage_change(views_month_ago, views_now)

        avg_views_now = feed_df[feed_df['date'] == max_date]['avg_views_per_user'].values[0]
        avg_views_month_ago = feed_df[feed_df['date'] == min_date]['avg_views_per_user'].values[0]
        avg_views_change = percentage_change(avg_views_month_ago, avg_views_now)


        avg_likes_now = feed_df[feed_df['date'] == max_date]['avg_likes_per_user'].values[0]
        avg_likes_month_ago = feed_df[feed_df['date'] == min_date]['avg_likes_per_user'].values[0]
        avg_likes_change = percentage_change(avg_likes_month_ago, avg_likes_now)

        ctr_now = feed_df[feed_df['date'] == max_date]['CTR'].values[0]
        ctr_month_ago = feed_df[feed_df['date'] == min_date]['CTR'].values[0]
        ctr_change = percentage_change(ctr_month_ago, ctr_now)

        dau_message_now = message_df[message_df['date'] == max_date]['DAU_message'].values[0]
        dau_message_month_ago = message_df[message_df['date'] == min_date]['DAU_message'].values[0]
        dau_message_change = percentage_change(dau_message_month_ago, dau_message_now)

        messages_sent_now = message_df[message_df['date'] == max_date]['count_messages'].values[0]
        messages_sent_month_ago = message_df[message_df['date'] == min_date]['count_messages'].values[0]
        messages_sent_change = percentage_change(messages_sent_month_ago, messages_sent_now)

        avg_messages_sent_now = message_df[message_df['date'] == max_date]['avg_messages_per_user'].values[0]
        avg_messages_sent_month_ago = message_df[message_df['date'] == min_date]['avg_messages_per_user'].values[0]
        avg_messages_sent_change = percentage_change(avg_messages_sent_month_ago, avg_messages_sent_now)

        # Формирование сообщения
        message = (
            f"📮 *Отчёт по приложению с {min_date} по {max_date}:*\n\n"
            f"Динамика метрик за месяц:\n\n"
            f"📰 *Лента*\n"
            f"• DAU: {dau_feed_now} ➡️ {dau_feed_change:.2f}%\n"
            f"• Просмотрено постов: {posts_viewed_now} ➡️ {posts_viewed_change:.2f}%\n"
            f"• Просмотры: {views_now} ➡️ {views_change:.2f}%\n"
            f"• Лайки: {likes_now} ➡️ {likes_change:.2f}%\n"
            f"• Среднее число просмотров на пользователя в день: {avg_views_now:.2f} ➡️ {avg_views_change:.2f}%\n"
            f"• Среднее число лайков на пользователя в день: {avg_likes_now:.2f} ➡️ {avg_likes_change:.2f}%\n"
            f"• CTR: {ctr_now:.2f} ➡️ {ctr_change:.2f}%\n\n"
            f"💬 *Мессенджер*\n"
            f"• DAU: {dau_message_now} ➡️ {dau_message_change:.2f}%\n"
            f"• Отправлено сообщений: {messages_sent_now} ➡️ {messages_sent_change:.2f}%\n"
            f"• Среднее количество отправленных сообщений на пользователя в день: {avg_messages_sent_now:.2f} ➡️ {avg_messages_sent_change:.2f}%\n\n"

        )
        bot.sendMessage(chat_id=chat_id, text=message, parse_mode="Markdown")

        formatted_dates = feed_df['date'].dt.strftime('%d-%m')
        #Графики метрик по Ленте новостей
        sns.set(rc = {'figure.figsize':(21,13)})
        plt.suptitle('Ключевые метрики за последний месяц', fontsize=25)

        step=3
        # DAU
        plt.subplot(2, 2, 1)
        ax = sns.barplot(
            x=formatted_dates, 
            y=feed_df['DAU_feed'], 
            color='b', 
            label='DAU ленты'
        )
        ax = sns.barplot(
            x=formatted_dates, 
            y=message_df['DAU_message'], 
            color='orange',
            linewidth=2, 
            label='DAU мессенджера'
        )
        plt.xlabel(''), plt.ylabel('')
        plt.title('DAU', fontsize=20)
        plt.legend()
        ax.set_xticks(range(0, len(formatted_dates), step))
        ax.set_xticklabels(formatted_dates[::step], rotation=45)

        # VIEWS/LIKES
        plt.subplot(2, 2, 3)
        ax = sns.lineplot(x=formatted_dates, y=feed_df['views'], color = 'b', label = 'views', marker='o', linewidth=3)
        ax = sns.lineplot(x=formatted_dates, y=feed_df['likes'], color = 'orange', label='likes', marker='o', linewidth=3)
        plt.xlabel(''), plt.ylabel('')
        plt.title('Просмотры и лайки', fontsize=20)
        plt.legend()
        ax.set_xticks(range(0, len(formatted_dates), step))
        ax.set_xticklabels(formatted_dates[::step], rotation=45)

        # LIKES
        plt.subplot(2, 2, 4)
        ax = sns.lineplot(x=formatted_dates, y=feed_df['post_viewed'], color = 'b', marker='o', linewidth=3)
        plt.xlabel(''), plt.ylabel('')
        plt.title('Количество постов', fontsize=20)
        ax.set_xticks(range(0, len(formatted_dates), step))
        ax.set_xticklabels(formatted_dates[::step], rotation=45)

        # CTR
        plt.subplot(2, 2, 2)
        ax = sns.barplot(x=formatted_dates, y=feed_df['CTR'], color = 'b')
        plt.ylim(bottom = min(feed_df['CTR']) - min(feed_df['CTR']) * .05, top = max(feed_df['CTR']) * 1.05)
        plt.xlabel(''), plt.ylabel('')
        plt.title('CTR', fontsize=20)
        ax.set_xticks(range(0, len(formatted_dates), step))
        ax.set_xticklabels(formatted_dates[::step], rotation=45)

        plot_object = io.BytesIO()
        plt.savefig(plot_object)
        plot_object.seek(0)
        plot_object.name = 'plot.png'
        plt.close()
        bot.sendPhoto(chat_id=chat_id, photo=plot_object)

        #Графики дополнительных метрик
        sns.set(rc = {'figure.figsize':(18,7)})
        plt.suptitle('Дополнительные метрики за последний месяц', fontsize=20)

        plt.subplot(1, 3, 1)
        ax = sns.lineplot(x=formatted_dates, y=feed_df['avg_likes_per_user'], color = 'orange', marker='o', label='Лайки')
        ax = sns.lineplot(x=formatted_dates, y=feed_df['avg_views_per_user'], color = 'b', marker='o', label='Просмотры')
        plt.xlabel(''), plt.ylabel('')
        plt.title('Просмотры и лайки на пользователя', fontsize=15)
        plt.legend()
        ax.set_xticks(range(0, len(formatted_dates), step))
        ax.set_xticklabels(formatted_dates[::step], rotation=45)

        plt.subplot(1, 3, 2)
        ax = sns.lineplot(x=formatted_dates, y=message_df['avg_messages_per_user'], color = 'b')
        plt.xlabel(''), plt.ylabel('')
        plt.title('Сообщений на пользователя', fontsize=15)
        ax.set_xticks(range(0, len(formatted_dates), step))
        ax.set_xticklabels(formatted_dates[::step], rotation=45)

        plt.subplot(1, 3, 3)
        users_by_status = get_users_by_status()
        users_by_status = users_by_status.sort_values('week')
        users_by_status['week_str'] = users_by_status['week'].dt.strftime('%Y-%m-%d')

        ax = sns.barplot(data=users_by_status, x='week_str', y='users_number', hue = 'status', palette={'new': '#1f77b4', 'retained': '#2ca02c', 'gone': '#d62728'})
        plt.grid()
        plt.xlabel(''), plt.ylabel('')
        plt.title('Retention аудитории', fontsize=15)
        plt.xticks(rotation=45)

        plot_object = io.BytesIO()
        plt.savefig(plot_object)
        plot_object.seek(0)
        plot_object.name = 'plot.png'
        plt.close()
        bot.sendPhoto(chat_id=chat_id, photo=plot_object)
    
    feed_df = extract_feed_df()
    message_df = extract_message_df()
    send_report(feed_df, message_df)
    
dag_final_report_troshin = dag_final_report_troshin()
