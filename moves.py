# -*- coding: utf-8 -*-
import logging
logging.basicConfig(filename='log.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('Info')
import json
import database
import language_support
import iv_check

#The json file of currently supported language responses
jsonresponse = language_support.responses
    
def get_moves(en_name, initial_language, responses):
    with open('pokemon_info/move_stats.json', encoding='utf-8') as json_config_file:
        poke_info = json.load(json_config_file)
    response = responses['moves_start'].format(en_name)
    fast_moves = poke_info['pokemon'][en_name]['fastMoves']
    charge_moves = poke_info['pokemon'][en_name]['chargeMoves']
    
    response += responses['moves_fast_header']
    for fast in fast_moves:
        move_stats = poke_info['moves'][fast]
        response += build_fast_move(move_stats, fast_moves, responses, initial_language)        
        response += '\n'

    response += responses['moves_charge_header']
    for charge in charge_moves:
        move_stats = poke_info['moves'][charge]
        response += build_charge_move(move_stats, fast_moves, responses, initial_language)
        response += '\n'
    return response
    
def build_fast_move(move_stats, fast_move, responses, initial_language):        
    language = initial_language if initial_language in move_stats['names'].keys() else "en"
    response = responses['moves_name'].format(move_stats['names'][language])
    response += responses['moves_type'].format(move_stats['type'].capitalize())
    response += responses['moves_damage'].format(move_stats['power'])
    response += responses['moves_fast_energygain'].format(move_stats['energyGain'])
    response += responses['moves_fast_duration'].format(move_stats['cooldown']/1000)
    return response

def build_charge_move(move_stats, fast_move, responses,  initial_language):        
    language = initial_language if initial_language in move_stats['names'].keys() else "en"
    response = responses['moves_name'].format(move_stats['names'][language])
    response += responses['moves_type'].format(move_stats['type'].capitalize())
    response += responses['moves_damage'].format(move_stats['power'])
    response += responses['moves_charge_energycost'].format(move_stats['energy'])
    return response

    
def moves(update, context):
    try:
        language = database.get_language(update.message.chat_id)
        responses = jsonresponse[language]
        logger.info('Move query %s with query %s', update._effective_user.username, context.args)
        
        #Check, if move queries should be en-/disabled in this group
        if len(context.args) == 1 and (context.args[0] == 'enable' or context.args[0] == 'disable'):
            logger.info("/Move %s by %s", context.args[0] , update._effective_user.username)
            #En-/disable IV queries for this group
            database.toggle_groups(update, context, 'Moves')
            return
        #If we are in a group and dont want ivs queries are disabled we just delete the request and return
        if update.message.chat_id < 0 and not database.group_enabled(update.message.chat_id, 'Moves'):
            logger.info("Disabled /moves request attempted by (%s)", update._effective_user.username)
            return
        
        if(len(context.args) != 1):
            response = responses['iv_no_argument']
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=response)
        else: 
            en_name, initial_language, different_language = iv_check.get_english_name(context.args[0], language)
            response = get_moves(en_name.lower(), initial_language, responses)
            
            #Send the response to the user
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=response)


    #We got some weird input which we cannot perform
    except:
        logger.info("Could not perform /iv request")
        response = responses['iv_error']
        context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=response)
