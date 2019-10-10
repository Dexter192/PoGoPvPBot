# -*- coding: utf-8 -*-
import logging
from numpy.distutils.fcompiler import none
logging.basicConfig(filename='log.log', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('Info')
import json 
import requests
import sched, time
import datetime
import language_support as lan

api_url = "https://silph.gg/api/cup/{}/stats"
minutes_per_hour = 60
s = sched.scheduler(time.time, time.sleep)
index = 0

""" Load the responses by our bot for each languages """
responses = lan.responses
""" Load the currently supported languages """
supported_languages = lan.supported_languages
  
def update_data(context):
    cup = context.job.context[1]
    cup_url = api_url.format(cup)
    print(cup_url)
    
    """ Get the json information about the partners """
    request = requests.get(cup_url)
    cup_info = request.json()
    
    with open('cup_data/'+cup+'.json', 'w') as outfile:
        json.dump(cup_info, outfile, indent=4, sort_keys=True)
    
    print("Next")
    #Schedule the next api update
    schedule_next_update(context.job_queue)


def schedule_next_update(job):
    """ Load available silph cups"""
    with open('cup_data/cups.json') as json_config_file:
        cups_json = json.load(json_config_file)
    cups = cups_json['cups']    
    global index
    index = (index+1) % len(cups)
    #Cycle through all cups within one hour - Update interval depends on the number of cups that we have e.g. with 2 cups, we update a cup every 30 minutes
    next_update = datetime.datetime.now() + datetime.timedelta(minutes = minutes_per_hour/len(cups)) 
    logger.info('Next api scheduled for %s', next_update)
    job.run_once(update_data, next_update, context=(job, cups[index]))
