import logging
logging.basicConfig(filename='log.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('Info')
from datetime import datetime
import requests
import re
import urllib
import json 


pvprequests = {}
competitors = {}

def silph_rank(update, context):
    if len(context.args) != 1:
        context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text="Please specify a player. Example: /rank ValorAsh")    
    name = context.args[0]
    logger.info('Silph rank request by %s for user %s', update._effective_chat.username, name)
    url = 'https://sil.ph/'+name
    html = requests.get(url).content
    html = str(html)
   
    user = re.search('user_id: (\d+)', html)
    if user is None:
        context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text="I could not find the player " + name)
    user_id = user[0].split()[1]
    
    url = 'https://sil.ph/card/cardData.json?user_id=' + user_id
    f = urllib.request.urlopen(url)
    data = str(f.read())
    data = data[data.index('{'):]
    p = re.compile(r'\\')
    data = p.sub('', data)
    p = re.compile(r'<.*?>')
    data= p.sub('', data)
    p = re.compile(r'[\']')
    data= p.sub('', data)
    user_data = json.loads(data)
    name = user_data['data']['in_game_username']
    rank = user_data['data']['arenaGlobalRank']
    region = user_data['data']['home_region']
    response = "<b>Name: </b>" + name + "\n"
    response += "<b>Rank: </b>" + rank + "\n"
    response += "<b>Region: </b>" + region + "\n"
    logger.info('Return %s', response)
    context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=response)