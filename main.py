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
import requests
import trainernames

pvprequests = {}
competitors = {}

with open('config.json') as json_config_file:
    config = json.load(json_config_file)
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
    context.bot.send_message(parse_mode='Markdown', chat_id=update.message.chat_id, text="""
Hello! 

With me you can create PvP-Polls for Pokémon Go in your Telegram group, check PvP-IV-ranks of your Pokémon and check the Silph Arena ranks of trainers!

I do respond to the following commands:

/trainername - Sets your trainername. This is useful for players who have a different username in Telegram and will replace your Telegram name with the name you set.
Example: /trainername Dexter

/pvp - Creates a PvP-poll. Polls will be deleted automatically after approximately one hour. Additionally you can add some more information to your request such as the league or specific rules.
Example: /pvp Great Mirror Cup

/iv - Retrieve the optimal IVs for a Pokémon in the great league or check where your Pokémon ranks according to [Go Stadium](https://gostadium.club/pvp/iv).
You can check alolan forms by appending +Alolan to the Pokémon
Example: /iv Pidgey ; /iv Geodude+alolan 12 12 12

/rank - Check the current Silph Arena rank of a player 
Example: /rank ValorAsh

If you want to host the bot yourself, feel free to clone this [Github repository](https://github.com/Dexter192/PoGoPvPBot).

Feedback, Suggestions or Problems can be posted in this [Telegram Group](https://t.me/joinchat/ET9xmhO2jGHqZ1adIeeFRQ).

I hope the bot enhances the PvP experience in your community!
""")    

def delete_message(context):
    logger.info("Deleted message %s %s", context.job.context[0], context.job.context[1])
    context.bot.delete_message(chat_id=context.job.context[0], message_id=context.job.context[1])

def unknown(update, context):
    context.bot.delete_message(chat_id=update.message.chat_id,message_id=update.message.message_id)
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

    dispatcher.add_handler(CommandHandler("rank", silph.silph_rank))

    dispatcher.add_handler(CommandHandler("trainername", trainernames.add_trainername))
    dispatcher.add_handler(CommandHandler("trainercode", trainernames.add_trainercode))


    #This is the last methon and should be used to refer to info
    unknown_handler = MessageHandler(Filters.command, unknown)
    dispatcher.add_handler(unknown_handler)    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()