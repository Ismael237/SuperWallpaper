import requests
import json
import zipfile
import telebot # type: ignore
from os import getenv
from random import choice
from dotenv import load_dotenv

load_dotenv()

UNSPLASH_CLIENT_ID = getenv('UNSPLASH_CLIENT_ID')
TELEGRAM_BOT_TOKEN = getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = getenv('TELEGRAM_CHAT_ID')

BASE_UNSPLASH_API_URL =f'https://api.unsplash.com/photos/random?client_id={UNSPLASH_CLIENT_ID}&query='
BASE_TELEGRAM_API_URL='https://api.telegram.org/bot'


bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN, parse_mode='MarkdownV2')

def send_photo_with_message(image_url, message):
    res = bot.send_photo(TELEGRAM_CHAT_ID, image_url, message)
    message_id = res.message_id
    reaction = [
        { 
         'type': 'emoji',
         'emoji': '❤' ,
        }
    ]
    data = {
        'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
        'message_id': message_id,
        'reaction': json.dumps(reaction)
    }
    response = requests.post(f'{BASE_TELEGRAM_API_URL}{TELEGRAM_BOT_TOKEN}/setMessageReaction', data=data)
    if response.status_code != 200:
        print(response.text)
    
def send_document_with_message(filename, image_url, message, image_name):
    response = requests.get(image_url)
    
    if response.status_code == 200:
        image_data = response.content
        
        with zipfile.ZipFile(filename+'.zip', 'w') as zip_file:
            zip_file.writestr(image_name+'.jpg', image_data)
            
        bot.send_document(TELEGRAM_CHAT_ID, open(filename+'.zip', 'rb'), caption=message)
        
        
def send_doc(name, image_description, image_url):
    send_document_with_message(f'image_{name}', image_url[name], f'Quality: *{name.title()}*', f'{image_description}_{name}')
        
def get_random_theme_keyword():
    theme_keywords = getenv('WALLPAPER_THEME_KEYWORDS')
    theme_keywords_list = theme_keywords.split(',')
    return choice(theme_keywords_list)

def transform_to_camel_case(phrase):
    words = phrase.split()
    capitalized_words = [word.capitalize() for word in words]
    camel_case_phrase = ''.join(capitalized_words)
    return camel_case_phrase

theme_keyword = get_random_theme_keyword()
camel_theme_keyword = transform_to_camel_case(theme_keyword)

response = requests.get(f'{BASE_UNSPLASH_API_URL}{theme_keyword}')

if response.status_code == 200:
    image = json.loads(response.text)
    image_url = image['urls']
    image_description = image['alt_description']
    image_location = image['location']['name']
    image_author = image['user']['name']
    
    msg = f'''Name: *{image_description.title()}*
            \n\nLocation: *{image_location}*
            \n\nAuthor: *{image_author}*
            \n\n{'#'+camel_theme_keyword} {'#'+camel_theme_keyword+'Wallpaper'} #Wallpaper #DailyWallpaper
            #HDWallpaper #WallpaperOfTheDay #FollowForMore #LikeAndShare
            '''
    
    send_photo_with_message(image_url['small'], msg)
    send_doc('regular', image_description, image_url)
    send_doc('full', image_description, image_url)
    send_doc('raw', image_description, image_url)
else:
    print('Request failed:', response.status_code)
    print('Request failed:', response.text)
