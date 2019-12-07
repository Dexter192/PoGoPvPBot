# -*- coding: utf-8 -*-
import logging
from pandas.core.frame import DataFrame
logging.basicConfig(filename='log.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('Info')
import pandas as pd
import database
import numpy as np
import language_support
import stringdist
import json
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

types = {"moves":"moves", "iv":"iv"}

#The json file of currently supported language responses
jsonresponse = language_support.responses
    
"""
Button markup for IV and move response customisation
"""
def custom_keyboard(chat_id, type):
    # X \u274c
    # check \u2705
    #Load the IV_Config for the current chat id (i.e. which attributes should be returned)
    #ChatID, IV, CP, Level, Stat Product, Percent, Percent minimum, IV-percent, FastMoves, ChargeMoves    
    if type == types["moves"]:
        current_config = database.get_iv_config(chat_id, "Moves")
    elif type == types["iv"]:
        current_config = database.get_iv_config(chat_id, "IV")
    
    keyboard = []
    
    for key in current_config.keys():
        if "Telegram" in key:
            continue
        button_text = key + "{}".format("\u2705" if current_config[key] == 1 else "\u274c")
        data = {"p":"conf", "type": type, "field" : key}
        data_string = json.dumps(data)
        keyboard.append([InlineKeyboardButton(button_text, callback_data=data_string)])
    keyboard.append([InlineKeyboardButton('Confirm', callback_data='Confirm')])
    return InlineKeyboardMarkup(keyboard)

""" 
Delete the config message if the user presses confirm
"""
def confirm_config(update, context):
    try:
        query = update.callback_query
        context.bot.delete_message(chat_id=query.message.chat_id, message_id=update.effective_message.message_id)    
    except:
        logger.info("Cannot delete message Chat:%s MessageID:%s", query.message.chat_id, update.message.message_id)
    return

"""
If the user presses a button we want to update the message such that he can see that the settings have been changed
This is for visual feedback
"""
def update_response(update, context):
    data = json.loads(update.callback_query.data)
    if data['type'] == types['moves']:
        table = "Moves"
    else:
        table = "IV"
    field = update.callback_query.data
    if update._effective_message.chat_id < 0:
        admins = (admin.user.id for admin in context.bot.get_chat_administrators(update._effective_message.chat.id))     
        if update._effective_user.id in admins:
            database.configure_iv_response(update._effective_chat.id, table, data["field"])
    else:
        database.configure_iv_response(update._effective_chat.id, table, data["field"])        
    #Update the check boxes on the markup menu
    language = database.get_language(update._effective_chat.id)
    responses = jsonresponse[language]
    response = responses['iv_menu']
    try:
        context.bot.edit_message_text(chat_id=update._effective_chat.id, message_id=update._effective_message.message_id, text=response, reply_markup=custom_keyboard(update._effective_message.chat.id, data['type']))
        logger.info("Updated IV output for group " + str(update._effective_chat.id))
    except:
        logger.info("Could not edit message in group " + str(update._effective_chat.id))
    return