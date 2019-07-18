# -*- coding: utf-8 -*-
import logging
logging.basicConfig(filename='log.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('Info')
import json
import os, sys, sqlite3
import database
import language_support
jsonresponse = language_support.responses

"""
Store the trainername associated with a telegramid in the database
"""
def add_trainername(update, context):
    #Load the language of the user
    language = database.get_language(update.message.chat_id)
    responses = jsonresponse[language]
    #The trainername is not within the Pokemon Go boundaries - Inform the user and return
    if len(context.args) != 1 or len(context.args[0]) > 15 or len(context.args[0]) < 4:
        context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=responses['trainername_length'])
    #Set the trainername
    else:
        logger.info("Setting Trainername")
        #Connect to the database
        try:
            conn = database.connect()
            cursor = conn.cursor()
            query = "INSERT INTO `Names` (TelegramID, Trainername) VALUES (?,?)" 
            #Try to insert the trainername
            try:
                cursor.execute(query, (update._effective_user.id, context.args[0],))
                logger.info("Insert new entry %s (%s, %s)", query, update._effective_user.id, context.args[0])
            #Update the trainername if the user already exists and wants to update their trainername
            except:
                query = "UPDATE `Names` SET Trainername=? WHERE TelegramID=?;";
                cursor.execute(query, (context.args[0], update._effective_user.id, ))
                logger.info("Update entry %s (%s, %s)", query, context.args[0], update._effective_user.id)
            conn.commit()
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=responses['trainername_success'])
        #We cannot connect to the database
        except:
            logger.warn("Could not set Trainername")
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=responses['trainername_fail'])
        #Make sure the connection gets closed
        finally:
            if conn is not None:
                conn.close()

"""
Store the trainercode associated with a telegramid in the database
Essentially the same as trainername - I see potential improvement :D
"""
def add_trainercode(update, context):
    #Load the language
    language = database.get_language(update.message.chat_id)
    responses = jsonresponse[language]
    #Trim spaces from the code
    code = ' '.join(context.args)
    code = code.replace(" ", "")
    #If the code is not 12 characters long it is malformed
    if len(code) != 12:
        context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=responses['trainercode_length'])
        return
    #If we have a valid code store it in the db
    else:
        conn = database.connect()
        #Insert the code
        try:
            cursor = conn.cursor()
            query = "INSERT INTO `Names` (TelegramID, Trainercode) VALUES (?,?)" 
            try:
                cursor.execute(query, (update._effective_user.id,code,))
                logger.info("Update entry %s (%s, %s)", query, update._effective_user.id, code)
            #If the user already has a trinercode or name we want to update this entry
            except:
                query = "UPDATE `Names` SET Trainercode=? WHERE TelegramID=?;";
                cursor.execute(query, (code, update._effective_user.id,))
                logger.info("Update entry %s (%s, %s)", query, code, update._effective_user.id)
            conn.commit()
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=responses['trainercode_success'])
        #We couln't connect to the db
        except:
            logger.warn("Could not set Trainercode")
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text=responses['trainername_fail'])
        #Close the connection
        finally:
            conn.close()
    
"""
Returns the trainername of a telegram user - if there is one, null if there is none
"""    
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