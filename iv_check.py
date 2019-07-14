# -*- coding: utf-8 -*-
import logging
logging.basicConfig(filename='log.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('Info')
import requests
import pandas as pd

    
def optimal_iv(pokemon_name):
    url = 'https://gostadium.club/pvp/iv?pokemon=' + pokemon_name + '&max_cp=1500'
    html = requests.get(url).content
    df_list = pd.read_html(html)
    df = df_list[-1]
    df = df[1:2]
    response = "Optimale IVs for " + pokemon_name + "\n"
    return iv_string(df, response)

def iv_given(pokemon_name, att, de, sta):
    url = 'https://gostadium.club/pvp/iv?pokemon=' + pokemon_name + '&max_cp=1500&att_iv=' + att + '&def_iv=' + de + '&sta_iv=' + sta
    html = requests.get(url).content
    df_list = pd.read_html(html)
    df = df_list[-1]
    df = df[0:1]
    response = "Your " + pokemon_name + " is on rank <b>"  + str(df['Rank'].values[0]) + "</b>\n"
    return iv_string(df, response)

    
def iv_string(df, response):
    response += "<b>(A/D/S):</b> "  + str(df['IVs (A/D/S)'].values[0]) + "\n"
    response += "<b>CP:</b> "   + str(df['CP'].values[0]) + "\n"
    response += "<b>Stat Product:</b> " + str(df['Stat Product'].values[0]) + "\n"
    response += "<b>Percent:</b> " + str(df['% Max Stat'].values[0]) + "\n"
    return response

def iv_rank(update, context):
    logger.info('IV rank request by %s with query %s', update._effective_chat.username, context.args)
    if(len(context.args) == 0):
        response = "Please specify a Pokémon"
    elif(len(context.args) == 1):
        response = optimal_iv(context.args[0])
    elif(len(context.args) == 4):
        response = iv_given(context.args[0], context.args[1], context.args[2], context.args[3])
    else:
        response = "I could not perform the request"
        #contents = requests.get('https://gostadium.club/pvp/iv?pokemon=pidgey&max_cp=1500')
    logger.info('Return %s', response)
    context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=response)
