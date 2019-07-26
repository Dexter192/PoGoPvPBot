# -*- coding: utf-8 -*-
import logging
logging.basicConfig(filename='log.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('Info')
import pandas as pd
import database
import language_support

#The json file of currently supported language responses
jsonresponse = language_support.responses
    
"""
Performs a query to the csv file of iv distributions and returns 
some information about the pokemon with the optimal IVs
@param pokemon_name: The name of the pokemon that we are insterested in
@param responses: The json responses of the current language
@return: A formatted response for the optimal IV distribution
"""
def optimal_iv(pokemon_name, responses):
    try:
        eng_name = get_english_name(pokemon_name)
        df = pd.read_csv('ranking/'+eng_name+'.csv')
        index_worst = df.shape[0]-1
        percent_worst = round((100/df.iloc[0]['stat-product'])*df.iloc[index_worst]['stat-product'], 2)
        response = responses['iv_optimal']
        response += responses['iv_stats']
        response = response.format(pokemon_name.capitalize(), df.iloc[0]['ivs'], df.iloc[0]['cp'], df.iloc[0]['stat-product'], '100', percent_worst)
        return response
    #We cannot find this pokemon
    except:
        response = responses['iv_no_pokemon']
        return response.format(pokemon_name)

"""
If the user has given IVs additional to the pokemon we want to see where this IV distribution ranks
@param pokemon_name: The name of the pokemon that we are interested in 
@param att: The attack stat of the pokemon
@param de: The defense stat of the pokemon (def is predefined)
@param sta: The stamina stat of the pokemon 
@param responses: The json responses of the current language
@return: A formatted response for the IV distribution of this pokemon
"""
def iv_given(pokemon_name, att, de, sta, responses):
    try:
        eng_name = get_english_name(pokemon_name)
        df = pd.read_csv('ranking/'+eng_name+'.csv')
        iv = att + ' ' + de + ' ' + sta
        row = df.loc[df['ivs'] == iv]
        optimal_stat_product = df.iloc[0]['stat-product']
        percent = round((100/optimal_stat_product)*row.iloc[0]['stat-product'], 2)
        index_worst = df.shape[0]-1
        percent_worst = round((100/optimal_stat_product)*df.iloc[index_worst]['stat-product'], 2)
        response = responses['iv_given']
        response = response.format(pokemon_name.capitalize(), row.iloc[0]['rank'])
        response += responses['iv_stats']
        response = response.format(row.iloc[0]['ivs'], row.iloc[0]['cp'], row.iloc[0]['stat-product'], percent, percent_worst)
        return response
    #We cannot find this pokemon
    except:
        response = responses['iv_no_pokemon']
        return response.format(pokemon_name)


def get_english_name(local_name):
    name = local_name.lower().capitalize()
    df = pd.read_csv('pokemon_info/translations.csv')
    idx = df.where(df == name).dropna(how='all').index
    try:
        return df.iloc[idx[0], 0]
    except:
        logger.info("Cannot find english name for (%s)", local_name)
        
        
"""
This method is called when the user types /iv
- It retrieves the language
- checks, if we want to enable or disable iv checks in groups
- checks, if IV queries are allowed in this group 
- Performs an IV request
"""    
def iv_rank(update, context):
    #Retrieve the current language
    language = database.get_language(update.message.chat_id)
    responses = jsonresponse[language]
    logger.info('IV request by %s with query %s', update._effective_user.username, context.args)
    #Check, if IV queries should be en-/disabled in this group
    if len(context.args) == 1 and (context.args[0] == 'enable' or context.args[0] == 'disable'):
        logger.info("/IV %s by %s", context.args[0] , update._effective_user.username)
        #En-/disable IV queries for this group
        database.toggle_groups(update, context, 'IV')
        return
    #If we are in a group and dont want ivs queries are disabled we just delete the request and return
    if update.message.chat_id < 0 and not database.group_enabled(update.message.chat_id, 'IV'):
        logger.info("Disabled /iv request attempted by (%s)", update._effective_user.username)
        context.bot.delete_message(chat_id=update.message.chat_id,message_id=update.message.message_id)
        return
    
    #The user didn't specify a pokemon
    if(len(context.args) == 0):
        logger.info("Invalid pokemon")
        response = responses['iv_no_argument']
    #If the user just specified a Pokemon - Return the optimal distribution
    elif(len(context.args) == 1):
        response = optimal_iv(context.args[0].lower(), responses)
    #If the user gave IVs with the pokemon - Return where this one ranks
    elif(len(context.args) == 4):
        response = iv_given(context.args[0].lower(), context.args[1], context.args[2], context.args[3], responses)
    #We got some weird input which we cannot perform
    else:
        logger.info("Could not perform /iv request")
        response = responses['iv_error']
    logger.info('Return %s', response.encode("utf-8"))
    #Send the response to the user
    context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=response)
