# -*- coding: utf-8 -*-
import logging
logging.basicConfig(filename='log.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('Info')
import requests
import pandas as pd
import database
import language_support

jsonresponse = language_support.responses

    
def optimal_iv(pokemon_name, responses):
    try:
        df = pd.read_csv('ranking/'+pokemon_name+'.csv')
        response = responses['iv_optimal']
        response += responses['iv_stats']
        response = response.format(pokemon_name.capitalize(), df.iloc[0]['ivs'], df.iloc[0]['cp'], df.iloc[0]['stat-product'], '100%')
        return response
    except:
        response = responses['iv_no_pokemon']
        return response.format(pokemon_name)

def iv_given(pokemon_name, att, de, sta, responses):
    df = pd.read_csv('ranking/'+pokemon_name+'.csv')
    iv = att + ' ' + de + ' ' + sta
    row = df.loc[df['ivs'] == iv]
    optimal_stat_product = df.iloc[0]['stat-product']
    percent = round((100/optimal_stat_product)*row.iloc[0]['stat-product'], 2)
    response = responses['iv_given']
    response = response.format(pokemon_name.capitalize(), row.iloc[0]['rank'])
    response += responses['iv_stats']
    response = response.format(row.iloc[0]['ivs'], row.iloc[0]['cp'], row.iloc[0]['stat-product'], percent)
    return response

    
def iv_string(df, percent, response, responses):
    response += responses['iv_stats']
    response = response.format(df.iloc[0]['ivs'], df.iloc[0]['cp'], df.iloc[0]['stat-product'], percent)
    return response

def iv_rank(update, context):
    language = database.get_language(update.message.chat_id)
    responses = jsonresponse[language]
    logger.info('IV request by %s with query %s', update._effective_user.username, context.args)
    #Check, if the setting should be updated
    if len(context.args) == 1 and (context.args[0] == 'enable' or context.args[0] == 'disable'):
        logger.info("/IV %s by %s", context.args[0] , update._effective_user.username)
        database.toggle_groups(update, context, 'IV')
        return
    #If we are in a group and dont want ivs to be searchable, return
    if update.message.chat_id < 0 and not database.group_enabled(update.message.chat_id, 'IV'):
        logger.info("Disabled /iv request attempted by (%s)", update._effective_user.username)
        context.bot.delete_message(chat_id=update.message.chat_id,message_id=update.message.message_id)
        return
    
    if(len(context.args) == 0):
        logger.info("Invalid pokemon")
        response = responses['iv_no_argument']
    elif(len(context.args) == 1):
        response = optimal_iv(context.args[0].lower(), responses)
    elif(len(context.args) == 4):
        response = iv_given(context.args[0].lower(), context.args[1], context.args[2], context.args[3], responses)
    else:
        logger.info("Could not perform /iv request")
        response = responses['iv_error']
        #contents = requests.get('https://gostadium.club/pvp/iv?pokemon=pidgey&max_cp=1500')
    logger.info('Return %s', response)
    context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=response)
