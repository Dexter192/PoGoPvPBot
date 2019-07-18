# -*- coding: utf-8 -*-
import logging
import json 
"""
Just a file which allows easier access to the language json file
"""
with open('responses.json', encoding='utf-8') as json_config_file:
    responses = json.load(json_config_file)
supported_languages = responses['supported_languages']
