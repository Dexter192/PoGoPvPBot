# -*- coding: utf-8 -*-
import logging
logging.basicConfig(filename='log.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('Info')
from telegram.ext import Updater, MessageHandler, JobQueue
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
import trainernames

pvprequests = {}
competitors = {}

def pvp(update, context):
    context.bot.delete_message(chat_id=update.message.chat_id,
                          message_id=update._effective_message['message_id'])
    name = trainernames.get_trainername(update.effective_user.id)
    if name is not None:
        response = "[" + name + "](tg://user?id=" + str(update.effective_user.id) + ") wants to fight! Are you ready to battle?"
    else:
        response = update.effective_user.name + " wants to fight! Are you ready to battle?"
    if len(context.args) > 0:
        if context.args[0].lower() == 'great' or context.args[0].lower() == 'ultra' or context.args[0].lower() == 'master':
            response += "\n*League: *" + context.args[0]
            if len(context.args) > 1:
                response += "\n*Info:* " + ' '.join(context.args[1:])
        else:
            response += "\n*Info: *" + ' '.join(context.args)
    bot_message = context.bot.send_message(parse_mode='Markdown', chat_id=update.message.chat_id, text=response, reply_markup=pvp_keyboard())
    logger.info('PvP request by %s (MessageID: %s, ChatID: %s) with arguments %s', update._effective_user.username, bot_message.message_id, bot_message.chat_id, context.args)
    pvprequests[bot_message.message_id, bot_message.chat_id] = {'user' : update.effective_user.id, 'date' : datetime.now(), 'text' : response}
    competitors[bot_message.message_id, bot_message.chat_id] = []

def add_competitor(update, context):
    query = update.callback_query
    #remove user from competitor list
    if update.effective_user in competitors[query.message.message_id, update._effective_chat.id]:
        logger.info('%s revokes the PvP request from %s', update.effective_user.username, pvprequests[update.effective_message.message_id, update.effective_chat.id]['text'].split()[0])
        competitors[query.message.message_id, update._effective_chat.id].remove(update.effective_user)
        
    #add user too competitor list
    else:
        logger.info('%s joins from the PvP request from %s', update.effective_user.username, pvprequests[update.effective_message.message_id, update.effective_chat.id]['text'].split()[0])
        competitors[query.message.message_id, update._effective_chat.id].append(update.effective_user)
        user = update.effective_user
        name = trainernames.get_trainername(user.id)
        if name is not None:
            direct_message = "[" + name + "](tg://user?id=" + str(user.id) + ")"
        else:
            direct_message = '@' + user.username
        direct_message += " has accepted your PvP-request!"
        try:
            context.bot.send_message(parse_mode='Markdown', chat_id=pvprequests[update.effective_message.message_id, update.effective_chat.id]['user'], text=direct_message)
            logger.info("Sent a private notification to %s", pvprequests[update.effective_message.message_id, update.effective_chat.id]['text'].split()[0])
        except:
            logger.info("Cannot initiate private conversation with %s", pvprequests[update.effective_message.message_id, update.effective_chat.id]['text'].split()[0])
    
    response = pvprequests[update.effective_message.message_id, update.effective_chat.id]['text']
    for user in competitors[query.message.message_id, update._effective_chat.id]:
        name = trainernames.get_trainername(user.id)
        if name is not None:
            response += "\n- [" + name + "](tg://user?id=" + str(update.effective_user.id) + ")"
        else:
            response += '\n- ' + user.name    
    context.bot.edit_message_text(parse_mode='Markdown', chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          text=response,
                          reply_markup=pvp_keyboard())

def delete_poll(update, context):
    try:
        req = pvprequests.pop((update.effective_message.message_id,update.effective_chat.id))
        comp = competitors.pop((update.effective_message.message_id, update.effective_chat.id))
    except:
        logger.info('No PVP-request stored by %s, %s', update.effective_user.username, update.effective_user.id)
        logger.warn('(MessageID: %s, ChatID: %s)\nOpen requests:', update.effective_message.message_id, update.effective_chat.id)
        for pvp in pvprequests:
            logger.info(pvp)
        return
    if req['user'] != update.effective_user.id:
        logger.info('%s (%s) has no permission to delete the pvp request (MessageID: %s, ChatID: %s)', update.effective_user.username, update.effective_user.id, update.effective_message.message_id, update.effective_chat.id)
        pvprequests[update.effective_message.message_id, update.effective_chat.id] = req
        competitors[update.effective_message.message_id, update.effective_chat.id] = comp
        return
    query = update.callback_query
    logger.info('%s deleted his PvP request (MessageID: %s, ChatID: %s)', update.effective_user.username, update.effective_message.message_id, update.effective_chat.id)
    context.bot.delete_message(chat_id=query.message.chat_id,
                          message_id=update.effective_message.message_id)    

def pvp_keyboard():
    keyboard = [[InlineKeyboardButton('Fight', callback_data='fight')],
                [InlineKeyboardButton('Delete', callback_data='delete')]]
    return InlineKeyboardMarkup(keyboard)

def get_user_name(telegramid):
    cursor.execute("SELECT Name FROM Names WHERE TelegramID = " + str(telegramid))
    
def auto_delete(context):
    now = datetime.now()
    copy = dict(pvprequests)
    for pvp in copy:
        diff = (now - pvprequests[pvp]['date']).seconds
        if diff > 3600:
            logger.info("Auto delete pvp request: %s", pvp)
            pvprequests.pop(pvp)
            competitors.pop((pvp[0], pvp[1]))
            context.bot.delete_message(chat_id=pvp[1], message_id=pvp[0])   