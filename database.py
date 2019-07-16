# -*- coding: utf-8 -*-
import logging
logging.basicConfig(filename='log.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('Info')
import json
import os, sys, sqlite3
import main

def create_db():
    connection = sqlite3.connect("www/names.db")
    cursor = connection.cursor()
    sql = "CREATE TABLE `Names` (`TelegramID` INT PRIMARY KEY NOT NULL, `Trainername` TEXT, `Trainercode` INT(12))"
    cursor.execute(sql)
    sql = "CREATE TABLE `Silph` (`Username` TEXT, `SilphID` INT PRIMARY KEY NOT NULL)"
    cursor.execute(sql)
    sql = "CREATE TABLE `Groups` (`GroupID` INT PRIMARY KEY NOT NULL, `Rank` BOOLEAN, `IV` BOOLEAN)"
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

def add_silph_id(name, id):
    conn = connect()
    cursor = conn.cursor()
    query = "INSERT INTO `Silph` (Username, SilphID) VALUES (?,?);"             
    cursor.execute(query, (name, id,))
    conn.commit()
    conn.close()

def get_silph_id(name):
    conn = connect()
    cursor = conn.cursor()
    sql = "SELECT SilphID FROM Silph WHERE Username=?"
    logger.info("Get SilphID: %s, %s", sql, name)
    cursor.execute(sql, (name,))
    rows = cursor.fetchall()
    conn.close()
    try:
        id = rows[0][0]
        logger.info("Return SilphID %s from user %s", id, name)
        return id
    except:
        logger.info("No SilphID for user %s", name)
        return None

def toggle_groups(update, context, type):
    #Check, if chat_id is negative. Otherwise return false
    if update.message.chat_id > 0:
        logger.info("/%s in private chat", type)
        response = "Das kann nur in Gruppen eingestellt werden"
        context.bot.send_message(chat_id=update.message.chat_id, text=response)
        return
    
    #Only continue, if the user is an admin
    admins = (admin.user.id for admin in context.bot.get_chat_administrators(update.message.chat.id))     
    if update._effective_user.id in admins:
        conn = connect()
        cursor = conn.cursor()
        insert = "INSERT INTO `Groups` (GroupID," + type + ") VALUES (?,?);"             
        change = "UPDATE `Groups` SET " + type + "=? WHERE GroupID=?;";
        try:
            cursor.execute(insert, (update.message.chat_id, context.args[0] == 'enable',))
            logger.info("Insert new entry %s (%s, %s)", insert, update.message.chat_id, (context.args[0] == 'enable'))
        except:
            cursor.execute(change, (context.args[0] == 'enable', update.message.chat_id,))
            logger.info("Update entry %s (%s, %s)", change, (context.args[0] == 'enable'), update.message.chat_id)

        conn.commit()
        conn.close()
        logger.info("/%s by a admin %s changed to %s", type, update._effective_chat.username, context.args[0] == 'enable')
        response = "Settings updated"
        context.bot.send_message(chat_id=update.message.chat_id, text=response)
    else:
        logger.info("/%s by a non-admin %s", type, update._effective_user.username)
        context.bot.delete_message(chat_id=update.message.chat_id,message_id=update.message.message_id)

def group_enabled(group_id, type):
    conn = connect()
    cursor = conn.cursor()
    query = "SELECT " + type + " FROM Groups WHERE GroupID="+str(group_id)
    try:
        cursor.execute(query)
        conn.commit()
    except:
        logger.warn("Could not get group!" + query)
    rows = cursor.fetchall()
    conn.close()
    try:
        enabled = bool(rows[0][0])
        logger.info("%s is on state %s for group %s", type, enabled, group_id)
        return enabled
    except:
        return True