# -*- coding: utf-8 -*-
import logging
logging.basicConfig(filename='log.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('Info')
from datetime import datetime
import requests
import re
import urllib
import json 
import database

"""
Not too interesting - This scrapes the silph website and returns the players rank. This will change once there is an API
"""
def silph_rank(update, context):
    if len(context.args) != 1:
        logger.info("Invalid rank request by %s (%s)", update._effective_user.username, context.args)
        context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text="Ich brauche einen Spieler. Beispiel /rank ValorAsh")    
        return
    if context.args[0] == 'enable' or context.args[0] == 'disable':
        logger.info("/rank %s by %s", context.args[0] , update._effective_user.username)
        database.toggle_groups(update, context, 'Rank')
        return
    #If we are in a group and dont want ranks to be searchable, return
    if update.message.chat_id < 0 and not database.group_enabled(update.message.chat_id, 'Rank'):
        logger.info("Disabled /rank request attempted by (%s)", update._effective_user.username)
        context.bot.delete_message(chat_id=update.message.chat_id,message_id=update.message.message_id)
        return
    name = context.args[0]
    logger.info('Silph rank request by %s for user %s', update._effective_user.username, name)
    user_id = database.get_silph_id(name)
    if user_id is None:
        url = 'https://sil.ph/'+name
        html = requests.get(url).content
        html = str(html)
        user = re.search('user_id: (\d+)', html)
        if user is None:
            logger.info('User %s does not have a silph card', name)
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text="Ich konnte den Nutzer " + name + " nicht finden")
            return
        else:
            logger.info('Adding userid to the database for user %s', name)
        user_id = user[0].split()[1]
        database.add_silph_id(name, user_id)
    url = 'https://sil.ph/card/cardData.json?user_id=' + str(user_id)
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
