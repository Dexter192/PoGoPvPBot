# -*- coding: utf-8 -*-
import logging
import json 

with open('responses.json', encoding='utf-8') as json_config_file:
    responses = json.load(json_config_file)
supported_languages = responses['supported_languages']
