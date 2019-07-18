# -*- coding: utf-8 -*-
import logging
logging.basicConfig(filename='log.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('Info')
from telegram.ext import Updater, MessageHandler, JobQueue
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
import trainernames
import database
import language_support

#A list of currently open pvp requests
pvprequests = {}
#All competitors for each request
competitors = {}
#The language strings
jsonresponse = language_support.responses

"""
This method transforms /pvp into a request with clickable buttons
"""
def pvp(update, context):
    #Load the language settings for this group
    language = database.get_language(update.message.chat_id)
    responses = jsonresponse[language]
    #Try to delete the /pvp command
    try:
        context.bot.delete_message(chat_id=update.message.chat_id,
                          message_id=update._effective_message['message_id'])
    #If we cannot delete the command, the bot probably doesn't have admin rights
    except:
        context.bot.send_message(chat_id=update.message.chat_id, text=responses['pvp_cant_delete'])
        logger.info('Cannot delete message Chat:%s MessageID:%s', update.message.chat_id, update._effective_message['message_id'])
    #Check, if we have a name for this telegram user
    name = trainernames.get_trainername(update.effective_user.id)
    #Format the name properly if we have a user. Otherwise, we just take the users telegram name
    if name is not None:
        response = "[" + name + "](tg://user?id=" + str(update.effective_user.id) + ")" + responses['poll']
    else:
        response = update.effective_user.name + responses['poll']
    #Does the poll provide any arguments such as league
    if len(context.args) > 0:
        #Did the user specify a league that he wants to play in? - If so, we format it
        if context.args[0].lower() == responses['greatleague'] or context.args[0].lower() == responses['ultraleague'] or context.args[0].lower() == responses['masterleague']:
            response += responses['league'] + context.args[0]
            #Did he specify more information? We just ass "Info:" infront of it and return the same query
            if len(context.args) > 1:
                response += responses['pollinfo'] + ' '.join(context.args[1:])
        #Did the user provide information without specifying the league
        else:
            response += responses['pollinfo'] + ' '.join(context.args)
    #Send the poll and add the buttons to it
    bot_message = context.bot.send_message(parse_mode='Markdown', chat_id=update.message.chat_id, text=response, reply_markup=pvp_keyboard(responses))
    logger.info('PvP request by %s (MessageID: %s, ChatID: %s) with arguments %s', update._effective_user.username, bot_message.message_id, bot_message.chat_id, context.args)
    #Store the message and create a list for the competitors
    pvprequests[bot_message.message_id, bot_message.chat_id] = {'user' : update.effective_user.id, 'date' : datetime.now(), 'text' : response}
    competitors[bot_message.message_id, bot_message.chat_id] = []

"""
If a user clicks on the fight button, we will either add or revoke him from the poll
"""
def add_competitor(update, context):
    #Get the info about the message that was clicked
    query = update.callback_query
    #remove user from competitor list
    if update.effective_user in competitors[query.message.message_id, update._effective_chat.id]:
        logger.info('%s revokes the PvP request from %s', update.effective_user.username, pvprequests[update.effective_message.message_id, update.effective_chat.id]['text'].split()[0])
        competitors[query.message.message_id, update._effective_chat.id].remove(update.effective_user)
        
    #add user too competitor list
    else:
        logger.info('%s joins from the PvP request from %s', update.effective_user.username, pvprequests[update.effective_message.message_id, update.effective_chat.id]['text'].split()[0])
        competitors[query.message.message_id, update._effective_chat.id].append(update.effective_user)
        #Retrieve the user object and his name, if he has one defined
        user = update.effective_user
        name = trainernames.get_trainername(user.id)
        #Format the users name
        if name is not None:
            direct_message = "[" + name + "](tg://user?id=" + str(user.id) + ")"
        else:
            direct_message = '@' + user.username
        #Get the current language and load the direct message to notifiy the creator
        language = database.get_language(update._effective_chat.id)
        direct_message += jsonresponse[language]['accepted']
        #Try to send a private notification to the creator of the poll
        try:
            context.bot.send_message(parse_mode='Markdown', chat_id=pvprequests[update.effective_message.message_id, update.effective_chat.id]['user'], text=direct_message)
            logger.info("Sent a private notification to %s", pvprequests[update.effective_message.message_id, update.effective_chat.id]['text'].split()[0])
        #If the creator doesn't have a private chat with the bot we cannot send him a private notification
        except:
            logger.info("Cannot initiate private conversation with %s", pvprequests[update.effective_message.message_id, update.effective_chat.id]['text'].split()[0])
    
    """ Edit the pvp request and add the competitor"""
    #Get the initial request
    response = pvprequests[update.effective_message.message_id, update.effective_chat.id]['text']
    #Add the name of each user to the request
    for user in competitors[query.message.message_id, update._effective_chat.id]:
        name = trainernames.get_trainername(user.id)
        if name is not None:
            response += "\n- [" + name + "](tg://user?id=" + str(update.effective_user.id) + ")"
        else:
            response += '\n- ' + user.name    
    #Update the message
    context.bot.edit_message_text(parse_mode='Markdown', chat_id=query.message.chat_id,
                          message_id=query.message.message_id,
                          text=response,
                          reply_markup=pvp_keyboard(jsonresponse[language]))

""" If a user clicks on delete, we want to delete this poll and all the information that we held with it"""
def delete_poll(update, context):
    #Try to remove the request
    try:
        req = pvprequests.pop((update.effective_message.message_id,update.effective_chat.id))
        comp = competitors.pop((update.effective_message.message_id, update.effective_chat.id))
    #If we don't have a request with the message id and the chat id, we just throw an error
    except:
        logger.info('No PVP-request stored by %s, %s', update.effective_user.username, update.effective_user.id)
        logger.warn('(MessageID: %s, ChatID: %s)\nOpen requests:', update.effective_message.message_id, update.effective_chat.id)
        for pvp in pvprequests:
            logger.info(pvp)
        return
    #Checks, if the user is indeed the creator of the message
    if req['user'] != update.effective_user.id:
        #The user did not create the request - add it back to the open requests
        logger.info('%s (%s) has no permission to delete the pvp request (MessageID: %s, ChatID: %s)', update.effective_user.username, update.effective_user.id, update.effective_message.message_id, update.effective_chat.id)
        pvprequests[update.effective_message.message_id, update.effective_chat.id] = req
        competitors[update.effective_message.message_id, update.effective_chat.id] = comp
        return
    #The user is the owner of the message. Try to delete it
    query = update.callback_query
    logger.info('%s deleted his PvP request (MessageID: %s, ChatID: %s)', update.effective_user.username, update.effective_message.message_id, update.effective_chat.id)
    try:
        context.bot.delete_message(chat_id=query.message.chat_id, message_id=update.effective_message.message_id)    
    except:    
        logger.info('Cannot delete message Chat:%s MessageID:%s', update.message.chat_id, update._effective_message['message_id'])

"""
Just the button markup for fight and delete
"""
def pvp_keyboard(response):
    keyboard = [[InlineKeyboardButton(response['fight'], callback_data='fight')],
                [InlineKeyboardButton(response['delete'], callback_data='delete')]]
    return InlineKeyboardMarkup(keyboard)

"""
This looks like dead code
"""
def get_user_name(telegramid):
    cursor.execute("SELECT Name FROM Names WHERE TelegramID = " + str(telegramid))

"""
We want to make sure, that messages will be deleted if they exist for over an hour
This is executed every ~15 minutes
"""    
def auto_delete(context):
    now = datetime.now()
    copy = dict(pvprequests)
    #Iterate over each open request and see how old it is
    for pvp in copy:
        diff = (now - pvprequests[pvp]['date']).seconds
        #If the message was posted more than an hour ago, we want to delete it
        if diff > 3600:
            pvprequests.pop(pvp)
            competitors.pop((pvp[0], pvp[1]))
            try:
                context.bot.delete_message(chat_id=pvp[1], message_id=pvp[0])
                logger.info("Auto delete pvp request: %s", pvp)
            except:
                logger.info("PvP request was already deleted (by an admin?): %s", pvp)