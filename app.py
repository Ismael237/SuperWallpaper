import requests
import json
import zipfile
import telebot

YOUR_ACCESS_KEY='XJeBnKhqxqgf3j-Xy-2AIm4LuIVgO8x4NWnMHXxKv9o'
BASE_UNSPLASH_API_URL=f'https://api.unsplash.com/photos/random?client_id={YOUR_ACCESS_KEY}&query=landscape'
BASE_TELEGRAM_API_URL='https://api.telegram.org/bot'
BOT_TOKEN='7140173014:AAEVqSi5-PWotzVV1JpSzCfjFOVGQgyzBEU'
METHOD_NAME='sendPhoto'
CHAT_ID='-1001862829347'

bot = telebot.TeleBot(BOT_TOKEN, parse_mode='MarkdownV2')

def send_photo_with_message(image_url, message):
    res = bot.send_photo(CHAT_ID, image_url, message)
    message_id = res.message_id
    reaction = [
        { 
         'type': 'emoji',
         'emoji': '❤' 
        }
    ]
    data = {
        'chat_id': CHAT_ID,
        'message_id': message_id,
        'reaction': json.dumps(reaction)
    }
    response = requests.post(f'{BASE_TELEGRAM_API_URL}{BOT_TOKEN}/setMessageReaction', data=data)
    if response.status_code != 200:
        print(response.text)
    
def send_document_with_message(filename, image_url, message, image_name):
    response = requests.get(image_url)
    
    if response.status_code == 200:
        image_data = response.content
        
        with zipfile.ZipFile(filename+'.zip', 'w') as zip_file:
            zip_file.writestr(image_name+'.jpg', image_data)
            
        bot.send_document(CHAT_ID, open(filename+'.zip', 'rb'), caption=message)
        
        
def send_doc(name, image_description, image_url):
    send_document_with_message(f'image_{name}', image_url[name], f'quality: *{name.title()}*', f'{image_description}_{name}')
        

response = requests.get(f'{BASE_UNSPLASH_API_URL}')

if response.status_code == 200:
    image = json.loads(response.text)
    image_url = image['urls']
    image_description = image['alt_description']
    image_location = image['location']['name']
    image_author = image['user']['name']
    msg = f'''Name: *{image_description.title()}*\n\nLocation: *{image_location}*\n\nAuthor: *{image_author}*\n\n'''
    send_photo_with_message(image_url['small'], msg)
    send_doc('regular', image_description, image_url)
    send_doc('full', image_description, image_url)
else:
    print('Request failed:', response.status_code)
    print('Request failed:', response.text)
