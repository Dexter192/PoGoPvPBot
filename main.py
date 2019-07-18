# -*- coding: utf-8 -*-
import logging
logging.basicConfig(filename='log.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('Info')
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import json 
import iv_check
import silph
import pvp_poll
import re
import database
import requests
import trainernames
import language_support as lan
pvprequests = {}
competitors = {}

with open('config.json') as json_config_file:
    config = json.load(json_config_file)
responses = lan.responses
supported_languages = lan.supported_languages
    
updater = Updater(config['token'], use_context=True)
job = updater.job_queue
dispatcher = updater.dispatcher

def get_dog():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url

def get_cat():
    contents = requests.get('http://aws.random.cat/meow').json()
    url = contents['file']
    return url

def get_image_url(pic):
    allowed_extension = ['jpg','jpeg','png']
    file_extension = ''
    while file_extension not in allowed_extension:
        if pic == 'cat':
            url = get_cat()
        else:
            url = get_dog()
        file_extension = re.search("([^.]*)$",url).group(1).lower()
    return url

def meow(update, context):
    url = get_image_url('cat')
    context.bot.send_photo(chat_id=update.message.chat_id, photo=url)    

def bop(update, context):
    url = get_image_url('dog')
    context.bot.send_photo(chat_id=update.message.chat_id, photo=url)    

def start(update, context):
    language = database.get_language(update.message.chat_id)
    response = ''
    response = response.join(responses[language]['start'])
    context.bot.send_message(parse_mode='Markdown', chat_id=update.message.chat_id, text=response)    

def language(update, context):
    if len(context.args) == 1 and context.args[0].lower() in supported_languages:
        database.toggle_groups(update, context, 'Language')
    else:
        try:
               context.bot.delete_message(chat_id=update.message.chat_id,message_id=update.message.message_id)
        except:
            logger.info("Cannot delete message Chat:%s MessageID:%s", update.message.chat_id, update.message.message_id)
        language = database.get_language(update.message.chat_id)
        response = responses[language]['language_not_supported']
        response = response.format(supported_languages)
        bot_message = context.bot.send_message(parse_mode='Markdown', chat_id=update.message.chat_id, text=response)
        
def silph_rank(update, context):
    try:
        context.bot.delete_message(chat_id=update.message.chat_id,message_id=update.message.message_id)
    except:
        logger.info("Cannot delete message Chat:%s MessageID:%s", update.message.chat_id, update.message.message_id)
    bot_message = context.bot.send_message(chat_id=update.message.chat_id, text=responses['de']['poll'])#text="This feature is disabled until a public API is released by TSA")
    job.run_once(delete_message, 30, context=(bot_message.chat_id, bot_message.message_id))

def delete_message(context):
    try:
        context.bot.delete_message(chat_id=context.job.context[0], message_id=context.job.context[1])
        logger.info("Deleted message %s %s", context.job.context[0], context.job.context[1])
    except:
        logger.info("Cannot delete message %s %s", context.job.context[0], context.job.context[1])
        
def unknown(update, context):
    try:
        context.bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
    except:
        logger.info("Cannot delete message Chat:%s MessageID:%s", update.message.chat_id, update.message.message_id)
    bot_message = context.bot.send_message(chat_id=update.message.chat_id, text="I'm sorry! I don't understand that command. You can get a list of commands with /help.")
    job.run_once(delete_message, 30, context=(bot_message.chat_id, bot_message.message_id))


def main():
    logger.info('Started bot')
    
    dispatcher.add_handler(CommandHandler('pbp',bop))
    dispatcher.add_handler(CommandHandler('pcp',meow))
    
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", start))

    updater.dispatcher.add_handler(CommandHandler('pvp', pvp_poll.pvp))
    updater.dispatcher.add_handler(CallbackQueryHandler(pvp_poll.add_competitor, pattern='fight'))
    updater.dispatcher.add_handler(CallbackQueryHandler(pvp_poll.delete_poll, pattern='delete'))
    auto_del = job.run_repeating(pvp_poll.auto_delete, interval=900, first=0)
    
    dispatcher.add_handler(CommandHandler("iv", iv_check.iv_rank))    
    
    dispatcher.add_handler(CommandHandler("language", language))    

    dispatcher.add_handler(CommandHandler("rank", silph_rank))

    dispatcher.add_handler(CommandHandler("trainername", trainernames.add_trainername))
    dispatcher.add_handler(CommandHandler("trainercode", trainernames.add_trainercode))


    #This is the last methon and should be used to refer to info
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()