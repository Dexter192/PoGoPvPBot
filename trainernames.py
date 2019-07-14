# -*- coding: utf-8 -*-
import logging
logging.basicConfig(filename='log.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('Info')
import json
import os, sys, sqlite3


def create_db():
    connection = sqlite3.connect("www/names.db")
    cursor = connection.cursor()
    sql = "CREATE TABLE `Names` (`TelegramID` INT PRIMARY KEY NOT NULL, Trainername TEXT, `Trainercode` INT(12))"
    cursor.execute(sql)
    connection.commit()
    connection.close()

def connect():
    # Existenz der Datenbank überprüfen und ggf. diese anlegen
    if not os.path.exists("www/names.db"):
        logger.info("Datenbank names.db nicht vorhanden - Datenbank wird anglegt.")
        create_db()
    """ Connect to MySQL database """
    try:
        conn = sqlite3.connect("www/names.db")
        return conn
    except:
        logger.info("Error while connecting to database")

def add_trainername(update, context):
    if len(context.args) != 1 or len(context.args[0]) > 15 or len(context.args[0]) < 4:
        context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text="Your trainername has to be between 4 and 15 characters")
    else:
        logger.info("Setting Trainername")
        try:
            conn = connect()
            cursor = conn.cursor()
            query = "INSERT INTO `Names` (TelegramID, Trainername) VALUES ('" + str(update._effective_user.id) + "','" + str(context.args[0]) + "') " 
            try:
                cursor.execute(query)
                logger.info("Insert new entry" + query)
            except:
                query = "UPDATE `Names` SET Trainername='" + str(context.args[0]) + "' WHERE TelegramID='" + str(update._effective_user.id) + "';";
                cursor.execute(query)
                logger.info("Update entry" + query)
            conn.commit()
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text="Trainername set successfully")
        except:
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text="Trainername could not be set")
        finally:
            if conn is not None:
                conn.close()

def add_trainercode(update, context):
    code = ' '.join(context.args)
    code = code.replace(" ", "")
    if len(context.args) != 1 or len(context.args[0]) != 12:
        context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text="Your trainercode must be 12 characters long!")
    else:
        conn = connect()
        try:
            cursor = conn.cursor()
            query = "INSERT INTO `Names` (TelegramID, Trainercode) VALUES ('" + str(update._effective_user.id) + "','" + str(context.args[0]) + "') " 
            try:
                cursor.execute(query)
                logger.info("Insert new entry" + query)
            except:
                query = "UPDATE `Names` SET Trainercode='" + str(context.args[0]) + "' WHERE TelegramID='" + str(update._effective_user.id) + "';";
                cursor.execute(query)
                logger.info("Update entry" + query)
            conn.commit()
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text="Trainercode set successfully")
        except:
            context.bot.send_message(parse_mode='HTML', chat_id=update.message.chat_id, text="Trainercode could not be set")
        finally:
            conn.close()
    
    
def get_trainername(telegramid):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT Trainername FROM Names WHERE TelegramID = " + str(telegramid))
    rows = cursor.fetchall()
    conn.close()
    try:
        return rows[0][0]
    except:
        return None