# -*- coding: utf-8 -*-
import logging
logging.basicConfig(filename='log.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('Info')
import json
import database
import language_support
import iv_check
import response_menu

#The json file of currently supported language responses
jsonresponse = language_support.responses
#The types of moves that are in Pokemon
movetype_fast = 'fast'
movetype_charge = 'charge'
movetype_legacy = 'legacy'
    
"""
    Find move statistics for the given pokemon and build the bot's response
    @param en_name: The english pokemon name
    @param initial_language: The chat language with the bot
    @param responses: The responses in the respective language for the chat 
    @param type: The type of move (fast, charge, legacy) 
"""    
def get_moves(en_name, initial_language, responses, type, move_config):
    with open('pokemon_info/move_stats.json', encoding='utf-8') as json_config_file:
        poke_info = json.load(json_config_file)
    local_name = iv_check. get_local_name(en_name, initial_language)
    response = ''
    
    if type == movetype_fast and move_config['Fast moves']:
        fast_moves = poke_info['pokemon'][en_name]['fastMoves']
        response = responses['moves_fast_header'].format(local_name)
        for fast in fast_moves:
            move_stats = poke_info['moves'][fast]
            response += create_move_string(move_stats, responses, initial_language, move_config)        
            response += '\n'
        return response

    if type == movetype_charge and move_config['Charge moves']:
        charge_moves = poke_info['pokemon'][en_name]['chargeMoves']
        response = responses['moves_charge_header'].format(local_name)
        for charge in charge_moves:
            move_stats = poke_info['moves'][charge]
            response += create_move_string(move_stats, responses, initial_language, move_config)
            response += '\n'
    
    if type == movetype_legacy and move_config['Legacy moves']:
        legacy_moves = poke_info['pokemon'][en_name]['legacyMoves']
        if len(legacy_moves) == 0:
            response = responses['no_legacy_moves'].format(local_name)
        else:
            response = responses['moves_legacy_header'].format(local_name)
        for legacy in legacy_moves:
            move_stats = poke_info['moves'][legacy]
            response += create_move_string(move_stats, responses, initial_language, move_config)
            response += '\n'
        
    return response
    
"""
    Create the info string of a move 
    For all moves it includes the name, the type, and the damage 
    If the move is a charge move we add the required energy for that move
    If the move is a fast move we get the energy that we build per turn and the duration of the move
    @param move_stats: The stats of the moves (from pvpoke)
    @param responses: The responses for the respective category
    @param initial_language: The language of the user such that we can return the proper move names in the respective language   
"""
def create_move_string(move_stats, responses,  initial_language, move_config):        
    language = initial_language if initial_language in move_stats['names'].keys() else "en"
    response = responses['moves_name'].format(move_stats['names'][language])
    if move_config['Type']:
        response += responses['moves_type'].format(move_stats['type'].capitalize())
    if move_config['Damage']:
        response += responses['moves_damage'].format(move_stats['power'])
    """ Charge moves if the energy gain is 0 """
    if move_stats['energyGain'] == 0:
        if move_config['Energy']:
            response += responses['moves_charge_energycost'].format(move_stats['energy'])    
    else: 
        if move_config['Duration']:
            response += responses['moves_fast_duration'].format(move_stats['cooldown']/1000)
        if move_config['Energy']:
            response += responses['moves_fast_energygain'].format(move_stats['energyGain'])
        if move_config['EPS']:
            response += responses['moves_fast_eps'].format(move_stats['energyGain']/(move_stats['cooldown']/1000))
        if move_config['DPS']:
            response += responses['moves_fast_dps'].format(move_stats['power']/(move_stats['cooldown']/1000))
    return response

""" If the user wants to know only the fast moves of a Pokemon (i.e. /fast)"""
def fast(update, context):
    build_move_response(update, context, movetype_fast)

""" If the user wants to know only the charge moves of a Pokemon (i.e. /charge)"""
def charge(update, context):
    build_move_response(update, context, movetype_charge)

""" If the user wants to know only the legacy moves of a Pokemon (i.e. /legacy)"""
def legacy(update, context):
    build_move_response(update, context, movetype_legacy)

""" 
    If the user wants to know only all moves of a Pokemon (i.e. /moves)
    We then iterate over fast, charge and legacy and return all moves
"""    
def moves(update, context):
    try:
        #We do not want to send unneccesary messages if we encountered an error/updated the settings
        proper_answer = build_move_response(update, context, movetype_fast)
        if not proper_answer:
            return
        proper_answer = build_move_response(update, context, movetype_charge)
        if not proper_answer:
            return
        build_move_response(update, context, movetype_legacy)
    except:
        return
    
"""
    Check settings (are queries enabled in a group) or if we want to change the settings in a group
    If we want to query the moves of a Pokemon we look for the english name of that pokemon and then
    build the response for that pokemon and the type of moves
    @param type: The type of moves (fast, charge, legacy) 
"""
def build_move_response(update, context, type):    
    try:
        language = database.get_language(update.message.chat_id)
        responses = jsonresponse[language]
        logger.info('Move query %s with query %s', update._effective_user.username, context.args)
        
        #The user wants to edit the response customisation
        if(len(context.args) == 0):
            if update.message.chat_id < 0:
                admins = (admin.user.id for admin in context.bot.get_chat_administrators(update.message.chat.id))     
                if update._effective_user.id in admins:
                    response = responses['moves_menu']
                    context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=response, reply_markup=response_menu.custom_keyboard(update.message.chat_id, response_menu.types["moves"]))
                else:
                    response = responses['only_for_admins']
                    bot_message = context.bot.send_message(parse_mode='Markdown', chat_id=update.message.chat_id, text=response)
                    return 
            else:    
                logger.info("Invalid pokemon")
                response = responses['moves_menu']
                context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=response, reply_markup=response_menu.custom_keyboard(update.message.chat_id, response_menu.types["moves"]))
                return
        
        #Check, if move queries should be en-/disabled in this group
        if len(context.args) == 1 and (context.args[0] == 'enable' or context.args[0] == 'disable'):
            logger.info("/Move %s by %s", context.args[0] , update._effective_user.username)
            #En-/disable IV queries for this group
            database.toggle_groups(update, context, 'Moves')
            return False
        #If we are in a group and dont want ivs queries are disabled we just delete the request and return
        if update.message.chat_id < 0 and not database.group_enabled(update.message.chat_id, 'Moves'):
            logger.info("Disabled /moves request attempted by (%s)", update._effective_user.username)
            return False
        
        #If the user did not specify a Pokemon
        if(len(context.args) != 1):
            response = responses['iv_no_argument']
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=response)
            return False
        #Look for the moves of that pokemon
        else: 
            #Load the IV_Config for the current chat id (i.e. which attributes should be returned)
            move_config = database.get_iv_config(update.message.chat_id, "Moves")
            
            en_name, initial_language, different_language = iv_check.get_english_name(context.args[0], language)
            response = get_moves(en_name.lower(), language, responses, type, move_config)
            
            #Send the response to the user
            char_limit = 4096
            for i in range(0, int(len(response)/4096)+1):
                if len(response) > 0:
                    splitted_response = response[i*char_limit:(i+1)*char_limit]
                    context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=splitted_response)
        return True

    #We got some weird input which we cannot perform
    except:
        logger.info("Could not perform /move request")
        response = responses['iv_error']
        context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=response)
        return False