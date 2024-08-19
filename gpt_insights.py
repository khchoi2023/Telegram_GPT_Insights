# pip install openai requests python-telegram-bot feedparser
# pip install python-telegram-bot
# pip install asyncio
# pip install nest_asyncio

import re
import time
import asyncio
import telegram
import feedparser
import pandas as pd
from openai import OpenAI
from datetime import datetime, timedelta, timezone


# Telegram Token
token = '{telegram_token}'
chat_id = '{Chat_ID}'

# ChatGPT
OPENAI_API_KE = '{OpenAI_API_key}'
client = OpenAI(api_key = OPENAI_API_KE)


# RSS URL
RSS_FEED_URLS = ['https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml',          # Coindesk
                'https://cointelegraph.com/rss',                                            # Cointelegraph
                'https://cryptobriefing.com/feed/',                                         # Cryptobriefing
                'https://bitcoinist.com/feed/'                                              # Bitcoinist
                ]


# RSS 피드에서 뉴스 가져오기
def fetch_news():
    now = datetime.now(timezone.utc)
    last_24_hours = now - timedelta(hours = 1)

    recent_news = []

    for feed_url in RSS_FEED_URLS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            entry_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)

            if entry_date > last_24_hours:
                recent_news.append(entry)
                print(f"Entry within the last 1 hour: {entry_date}")

    return recent_news


# 뉴스 기사 제목, 링크, 미디어 내용을 출력
def print_news(news_entry):
    title = news_entry.title
    link = news_entry.link
    date = news_entry.published
    return title, link, date


def gpt_content(link):
    print("-" * 80)

    # ChatGPT-4o Prompt Engineering
    news_input = f"{link}"
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": news_input},
            {"role": "system", "content": "{Prompt Engineering}"},
            {"role": "system", "content": "{Prompt Engineering}"},
        ]
    )

    final_content = completion.choices[0].message.content

    print(date)
    print()
    print(final_content)
    print()
    print(link)
    
    return final_content


####################################################################################################
try:
    df = pd.read_csv('news_log_kr.csv', encoding='UTF-8')
    print("log file load complete!")
except:
    df = pd.DataFrame(columns=['date', 'news', 'final_content', 'url', 'check'])
    df.to_csv('news_log_kr.csv', index=False, encoding='UTF-8')
    print('log file make complete!')


if __name__ == '__main__':
    news_entries = fetch_news()
    
    for entry in news_entries:
        url_check = 0
        aa = []
        title, link, date = print_news(entry)

        for i in range(len(df['url'])):
            if df['url'][i] == link:
                url_check = url_check + 1
            else:
                pass

        if url_check > 0:
            pass
        else:
            final_content = gpt_content(link)
            final_content = final_content.replace('*', '')
            final_content = final_content.replace('#', '')

            new_data = pd.DataFrame({'date': [date], 'news': [title], 'final_content' : [final_content], 'url': [link], 'check': 0})
            df = pd.concat([df, new_data], ignore_index=True)
            time.sleep(2)


df = df.sort_values(by='date', ascending=True)
df = df.reset_index(drop=True)
df.to_csv('news_log_kr.csv', index=False, encoding='UTF-8')


# Post Processing 1
df['final_content'] = df['final_content'].apply(
    lambda x: x.replace('제목:', '제목 :')
)

df['final_content'] = df['final_content'].apply(
    lambda x: x.replace('기사내용:', '기사내용 :')
)


df['final_content'] = df['final_content'].apply(
    lambda x: x.replace('영향:', '영향 :')
)

df['final_content'] = df['final_content'].apply(
    lambda x: x.replace('시장이 미치는 영향 :', '시장에 미치는 영향 :')
)

df['final_content'] = df['final_content'].apply(
    lambda x: x.replace('url:', 'url :')
)


##################################################
for j in range(len(df['check'])):
    if df['check'][j] == 0:

        print()
        print('Send Telegram message')
        print(df['date'][j])

        date_0 = df['date'][j]
        date_0 = re.split(r' \+\d{4}', date_0)[0]
        qq = date_0 + ' UTC' + '\n' + '\n' + df['final_content'][j]


        # Post Processing 2
        if '\n\n기사내용 :' in qq:
            pass
        else:
            qq = qq.replace('기사내용 :', '\n기사내용 :')

        if '\n\n시장에 미치는 영향 :' in qq:
            pass
        else:
            qq = qq.replace('시장에 미치는 영향 :', '\n시장에 미치는 영향 :')

        if '\n\nurl :' in qq:
            pass
        else:
            qq = qq.replace('url :', '\nurl :')

        if '기사내용 :\n' in qq:
            pass
        elif '기사내용 : \n' in qq:
            pass
        else:
            qq = qq.replace('기사내용 :', '기사내용 :\n')

        if '영향 :\n' in qq:
            pass
        elif '영향 : \n' in qq:
            pass
        else:
            qq = qq.replace('영향 :', '영향 :\n')


        ##################################################
        async def main():
            bot = telegram.Bot(token = token)
            await bot.send_message(chat_id, qq)

        asyncio.run(main())
        df.loc[j, 'check'] = 1
        df.to_csv('news_log_kr.csv', index=False, encoding='UTF-8')
        time.sleep(5)

    else:
        pass




