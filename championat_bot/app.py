import telebot
from bs4 import BeautifulSoup
from resourses import tags, TOKEN, main_url, headers
import re
import requests as req
from telebot import types


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    text = f'Здравствуй, {message.from_user.first_name}!'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('/help', )
    item2 = types.KeyboardButton('/tags')
    markup.add(item1, item2)
    bot.send_message(message.chat.id, text.format(message.from_user), reply_markup=markup)


@bot.message_handler(commands=['help'])
def help(message: telebot.types.Message):
    text = '\nЭто бот, который выдает 3 последних новости для выбранного футбольного клуба из сайта "https://www.championat.com".\n\
Чтобы начать работу, введите команду боту из списка команд.\nУвидеть список всех доступных футбольных команд: /tags'
    bot.reply_to(message, text)


@bot.message_handler(commands=['tags'])
def get_tags(message: telebot.types.Message):
    text = 'Доступные команды:'
    for key in tags.keys():
        text = '\n'.join((text, key, ))
    bot.reply_to(message, text)


@bot.message_handler(content_types=["text"])
def get_news(message: telebot.types.Message):
    result = ""
    val = message.text
    try:
        if val not in tags.keys():
            raise ValueError
        else:
            input_url = f"{main_url}/tags/{tags[val]}/news/"

            def get_link():  # достает ссылки последних 10 новостей и добавляет в список
                link_list = []
                pattern = re.compile(r'href="(.*)" target=')
                resp = req.get(input_url, headers=headers)
                soup = BeautifulSoup(resp.text, 'html.parser')
                tags = soup.find_all(['div'], class_="news-item__content")[:3]
                for tag in tags:
                    link = f'{main_url}{re.findall(pattern, str(tag))[0]}'
                    link_list.append(link)
                # print(link_list)
                return link_list

            def get_news_text():  # вытаскивает текст новости по ссылке
                news = []
                for url in get_link():
                    resp = req.get(url, headers=headers)
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    tags = soup.find(['div'], id="articleBody").find_all('p')
                    for tag in tags:
                        text = " ".join(tag.text.split())
                        news.append(text)
                    news.append('\n\n\n')
                # print(news)
                return news

            for i in get_news_text():
                result += i

            bot.reply_to(message, result)
    except ValueError:
        bot.send_message(message.chat.id, 'Введите правильную команду из списка'.format(message.from_user))


bot.polling(non_stop=True)







