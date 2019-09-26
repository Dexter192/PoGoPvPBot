# -*- coding: utf-8 -*-
import logging
logging.basicConfig(filename='log.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('Info')
import pandas as pd
import database
import language_support
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


#The json file of currently supported language responses
jsonresponse = language_support.responses
    

"""
If the user has given IVs additional to the pokemon we want to see where this IV distribution ranks
When the user does not give IVs, return the optimal IVs for that pokemon
@param pokemon_name: The name of the pokemon that we are interested in 
@param att: The attack stat of the pokemon
@param de: The defense stat of the pokemon (def is predefined)
@param sta: The stamina stat of the pokemon 
@param responses: The json responses of the current language
@param league: The desired league CP cap ('1500' or '2500')
@return: A formatted response for the IV distribution of this pokemon
"""
def iv_given(pokemon_name, initial_language, responses, iv_config, att=None, de=None, sta=None, league='1500'):
    try:            
        df = pd.read_csv('ranking/'+league+'/'+pokemon_name+'.csv')
        #Check, if we want to get optimal IVs or given
        if att is None:
            row = df.loc[df['rank'] == 1]
            response = responses['iv_optimal']
        #Find the Pokemon with the give IV-Distribution
        else:
            iv = str(att) + ' ' + str(de) + ' ' + str(sta)
            row = df.loc[df['ivs'] == iv]
            response = responses['iv_given']

        #Compute the Stat product on the fly 
        optimal_stat_product = df.iloc[0]['stat-product']
        percent = round((100/optimal_stat_product)*row.iloc[0]['stat-product'], 2)
        index_worst = df.shape[0]-1
        percent_worst = round((100/optimal_stat_product)*df.iloc[index_worst]['stat-product'], 2)
        
        local_name = get_local_name(pokemon_name, initial_language)
        response = response.format(local_name.capitalize(), row.iloc[0]['rank'])
        #Print IV Distribution
        if iv_config[1]:
            response += responses['iv_stats_IV'].format(row.iloc[0]['ivs'])
            #Print IV percent
            if iv_config[7]:
                ivs = row.iloc[0]['ivs'].split(' ')
                percent = round(((int(ivs[0]) + int(ivs[1]) + int(ivs[2]))/45)*100,2)
                response += ' - ' + str(percent) + '%\n'
            else:
                response += '\n'
        #Print CP
        if iv_config[2]:
            response += responses['iv_stats_CP'].format(row.iloc[0]['cp'])
        #Print Level
        if iv_config[3]:
            response += responses['iv_stats_Level'].format(row.iloc[0]['maxlevel'])
        #Print Stat product
        if iv_config[4]:
            response += responses['iv_stats_StatProduct'].format(row.iloc[0]['stat-product'])
        #Print Stat percent
        if iv_config[5]:
            response += responses['iv_stats_Percent'].format(percent)
        #Print stat percent minimum
        if iv_config[6]:
            response += responses['iv_stats_PercentMinimum'].format(percent_worst)
               
        return response
    #We cannot find this pokemon
    except:
        response = responses['iv_no_pokemon']
        return response.format(pokemon_name)

def get_local_name(eng_name, col_index):
    name = eng_name.lower().capitalize()
    df = pd.read_csv('pokemon_info/translations.csv')
    idx = df.where(df == name).dropna(how='all').index
    try:
        return df.loc[idx[0], col_index]
    except:
        logger.info("Cannot find local name for (%s)", eng_name)


def get_english_name(local_name, group_language):
    name = local_name.lower().capitalize()
    df = pd.read_csv('pokemon_info/translations.csv')
    #Drop all entries which don't match the local name
    localized = df.where(df == name).dropna(how='all')
    #Return a tuple of the first appearance of the name
    index_tuple = list(df[localized.notnull()].stack().index)
    different_language = True
    for nationality in index_tuple:
        if nationality[1] == group_language or nationality[1] not in language_support.supported_languages:
            different_language = False
            break
    try:
        return df.iloc[localized.index[0], 0], index_tuple[0][1], different_language
    except:
        logger.info("Cannot find english name for (%s)", local_name)
    
"""
This message takes a single pokemon and returns the whole family as a list
"""        
def get_pokemon_family(pokemon_name, group_language):
    eng_name, initial_language, different_language = get_english_name(pokemon_name, group_language)
    eng_name = eng_name.capitalize()
    df = pd.read_csv('pokemon_info/evolutions.csv')
    index = df.where(df == eng_name).dropna(how='all').index
    return df.loc[index[0]].dropna(), initial_language, different_language

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
    
    league = '1500'
    if len(context.args) > 0 and context.args[0] == '2500':
        context.args.pop(0)
        league = '2500'
#    else:
#        league = '1500'
        
    #The user didn't specify a pokemon
    if(len(context.args) == 0):
        if update.message.chat_id < 0:
            admins = (admin.user.id for admin in context.bot.get_chat_administrators(update.message.chat.id))     
            if update._effective_user.id in admins:
                response = responses['iv_menu']
                context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=response, reply_markup=iv_keyboard(update.message.chat_id))
            else:
                response = responses['only_for_admins']
                bot_message = context.bot.send_message(parse_mode='Markdown', chat_id=update.message.chat_id, text=response)
                return 
        else:    
            logger.info("Invalid pokemon")
            response = responses['iv_menu']
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=response, reply_markup=iv_keyboard(update.message.chat_id))
            
    else:
        try:
            #Load the IV_Config for the current chat id (i.e. which attributes should be returned)
            iv_config = database.get_iv_config(update.message.chat_id)
            
            if context.args[0][0] is '+':
                evolutions, initial_language, different_language = get_pokemon_family(context.args[0][1:], language)
            else:
                evolutions, initial_language, different_language = get_english_name(context.args[0], language)
                evolutions = [evolutions]
            for evo in evolutions:
                #If the user just specified a Pokemon - Return the optimal distribution
                if(len(context.args) == 1):
                    response = iv_given(evo.lower(), initial_language, responses, iv_config, None, None, None, league)
                #If the user gave IVs with the pokemon - Return where this one ranks
                elif(len(context.args) == 4):
                    att = normalize_iv(context.args[1])
                    de = normalize_iv(context.args[2])
                    sta = normalize_iv(context.args[3])
                    response = iv_given(evo.lower(), initial_language, responses, iv_config, att, de, sta, league)
                logger.info('Return %s', response.encode("utf-8"))
                
                if different_language:
                    context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=responses['language_hint'])

                #Send the response to the user
                context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=response)


        #We got some weird input which we cannot perform
        except:
            logger.info("Could not perform /iv request")
            response = responses['iv_error']
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=response)

"""
This method converts a given IV in a number in the range 0..15.
It accepts standard numbers (no operation is done), hexadecimal representation, or the circled
numbers (white background/black background) that is used in apps such as CalcyIV.
"""    
def normalize_iv(iv):
    if(isinstance(iv, str) and iv.isdecimal()):
        # Note: we're not checking if the value is in the range 0..15.
        iv = max(0, int(iv))
        iv = min(15, int(iv))
        return iv
    else:
        # Try to convert from common app representations.
        # Hexadecimal:
        val = "0123456789ABCDEF".find(iv)
        if (val != -1):
            return val
        # Rounded white numbers
        if (iv == "⓪" or iv == "⓿"):
            return 0
        elif (iv == "①" or iv == "❶"):
            return 1
        elif (iv == "②" or  iv == "❷"):
            return 2
        elif (iv == "③" or iv == "❸"):
            return 3
        elif (iv == "④" or iv == "❹"):
            return 4
        elif (iv == "⑤" or iv == "❺"):
            return 5
        elif (iv == "⑥" or iv == "❻"):
            return 6
        elif (iv == "⑦" or iv == "❼"):
            return 7
        elif (iv == "⑧" or iv == "❽"):
            return 8
        elif (iv == "⑨" or iv == "❾"):
            return 9
        elif (iv == "⑩" or iv == "❿"):
            return 10
        elif (iv == "⑪" or iv == "⓫"):
            return 11
        elif (iv == "⑫" or iv == "⓬"):
            return 12
        elif (iv == "⑬" or iv == "⓭"):
            return 13
        elif (iv == "⑭" or iv == "⓮"):
            return 14
        elif (iv == "⑮" or iv == "⓯"):
            return 15
        else:
            return iv

"""
Button markup for IV response customisation
"""
def iv_keyboard(chat_id):
    # X \u274c
    # check \u2705
    #Load the IV_Config for the current chat id (i.e. which attributes should be returned)
    #ChatID, IV, CP, Level, Stat Product, Percent, Percent minimum, IV-percent, FastMoves, ChargeMoves    
    iv_config = database.get_iv_config(chat_id)
    keyboard = [[InlineKeyboardButton('IV {}'.format("\u2705" if iv_config[1] == 1 else "\u274c"), callback_data='IV')],
                [InlineKeyboardButton("IV Percent {}".format("\u2705" if iv_config[7] == 1 else "\u274c"), callback_data='IV Percent')],
                [InlineKeyboardButton("CP {}".format("\u2705" if iv_config[2] == 1 else "\u274c"), callback_data='CP')], 
                [InlineKeyboardButton('Level {}'.format("\u2705" if iv_config[3] == 1 else "\u274c"), callback_data='Level')], 
                [InlineKeyboardButton('Stat Product {}'.format("\u2705" if iv_config[4] == 1 else "\u274c"), callback_data='Stat Product')], 
                [InlineKeyboardButton('Percent {}'.format("\u2705" if iv_config[5] == 1 else "\u274c"), callback_data='Percent')], 
                [InlineKeyboardButton('Percent minimum {}'.format("\u2705" if iv_config[6] == 1 else "\u274c"), callback_data='Percent minimum')],
                [InlineKeyboardButton('Confirm', callback_data='Confirm')]]
    return InlineKeyboardMarkup(keyboard)

def confirm_config(update, context):
    try:
        query = update.callback_query
        context.bot.delete_message(chat_id=query.message.chat_id, message_id=update.effective_message.message_id)    
    except:
        logger.info("Cannot delete message Chat:%s MessageID:%s", update.message.chat_id, update.message.message_id)
    return

def update_response(update, context):
    if update._effective_message.chat_id < 0:
        admins = (admin.user.id for admin in context.bot.get_chat_administrators(update._effective_message.chat.id))     
        if update._effective_user.id in admins:
            database.configure_iv_response(update._effective_chat.id, context.matches[0].string)
    else:
        database.configure_iv_response(update._effective_chat.id, context.matches[0].string)        
    #Update the check boxes on the markup menu
    language = database.get_language(update._effective_chat.id)
    responses = jsonresponse[language]
    response = responses['iv_menu']
    context.bot.edit_message_text(chat_id=update._effective_chat.id, message_id=update._effective_message.message_id, text=response, reply_markup=iv_keyboard(update._effective_message.chat.id))
    return
