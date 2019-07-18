# -*- coding: utf-8 -*-
import logging
logging.basicConfig(filename='log.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('Info')
import json
import os, sys, sqlite3
import database
import language_support
jsonresponse = language_support.responses

def add_trainername(update, context):
    language = database.get_language(update.message.chat_id)
    responses = jsonresponse[language]
    if len(context.args) != 1 or len(context.args[0]) > 15 or len(context.args[0]) < 4:
        context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=responses['trainername_length'])
    else:
        logger.info("Setting Trainername")
        try:
            conn = database.connect()
            cursor = conn.cursor()
            query = "INSERT INTO `Names` (TelegramID, Trainername) VALUES (?,?)" 
            try:
                cursor.execute(query, (update._effective_user.id, context.args[0],))
                logger.info("Insert new entry %s (%s, %s)", query, update._effective_user.id, context.args[0])
            except:
                query = "UPDATE `Names` SET Trainername=? WHERE TelegramID=?;";
                cursor.execute(query, (context.args[0], update._effective_user.id, ))
                logger.info("Update entry %s (%s, %s)", query, context.args[0], update._effective_user.id)
            conn.commit()
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=responses['trainername_success'])
        except:
            logger.warn("Could not set Trainername")
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=responses['trainername_fail'])
        finally:
            if conn is not None:
                conn.close()

def add_trainercode(update, context):
    language = database.get_language(update.message.chat_id)
    responses = jsonresponse[language]
    code = ' '.join(context.args)
    code = code.replace(" ", "")
    if len(code) != 12:
        context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=responses['trainercode_length'])
    else:
        conn = database.connect()
        try:
            cursor = conn.cursor()
            query = "INSERT INTO `Names` (TelegramID, Trainercode) VALUES (?,?)" 
            try:
                cursor.execute(query, (update._effective_user.id,code,))
                logger.info("Update entry %s (%s, %s)", query, update._effective_user.id, code)
            except:
                query = "UPDATE `Names` SET Trainercode=? WHERE TelegramID=?;";
                cursor.execute(query, (code, update._effective_user.id,))
                logger.info("Update entry %s (%s, %s)", query, code, update._effective_user.id)
            conn.commit()
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=responses['trainercode_success'])
        except:
            logger.warn("Could not set Trainercode")
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=responses['trainername_fail'])
        finally:
            conn.close()
    
    
def get_trainername(telegramid):
    conn = database.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT Trainername FROM Names WHERE TelegramID = " + str(telegramid))
    rows = cursor.fetchall()
    conn.close()
    try:
        return rows[0][0]
    except:
        return None