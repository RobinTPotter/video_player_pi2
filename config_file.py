from config import LOGNAME
import logging
logger = logging.getLogger(LOGNAME)
logger.info('importing config_file')

import os 
import json

config_file = 'config.file.txt'

default = {'size': [720,576], \
    'FPS': 25, \
    'VISIBLE_MOUSE': False, \
    'MESSAGE_LENGTH': 255, \
    'thumbnails': 'thumbnails', \
    'ext': ['mp4'], \
    'dir': ['~'], \
    'controls_set': False, \
    'controls': [
        {'name': 'up', 'button': None, 'key': None, 'callback': None},
        {'name': 'down', 'button': None, 'key': None, 'callback': None},
        {'name': 'left', 'button': None, 'key': None, 'callback': None},
        {'name': 'right', 'button': None, 'key': None, 'callback': None},
        {'name': 'fire', 'button': None, 'key': None, 'callback': None}
    ]
}



def save_config(config):
    with open(config_file,'w') as fp:
        fp.write(json.dumps(config, indent=4))
        logger.debug('saving')
        logger.debug(config)

def load_config():
    if config_file in os.listdir('.'):
        with open(config_file,'r') as fp:
            logger.debug('loading from {cf}'.format(cf=config_file))
            return json.loads(fp.read())
    else:
        logger.warning("no config found: {0}".format(config_file))
        return default

config = load_config()
