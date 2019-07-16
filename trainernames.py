# -*- coding: utf-8 -*-
import logging
logging.basicConfig(filename='log.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('Info')
import json
import os, sys, sqlite3
import database

def add_trainername(update, context):
    if len(context.args) != 1 or len(context.args[0]) > 15 or len(context.args[0]) < 4:
        context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text="Your trainername has to be between 4 and 15 characters")
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
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text="Trainername set successfully")
        except:
            logger.warn("Could not set Trainername")
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text="Trainername could not be set")
        finally:
            if conn is not None:
                conn.close()

def add_trainercode(update, context):
    code = ' '.join(context.args)
    code = code.replace(" ", "")
    if len(code) != 12:
        context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text="Your trainercode must be 12 characters long!")
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
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text="Trainercode set successfully")
        except:
            logger.warn("Could not set Trainercode")
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text="Trainercode could not be set")
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