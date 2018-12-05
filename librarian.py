from config import LOGNAME, THUMBNAIL_INTERVAL, SSL_VERIFY, NOIMDB
import logging
logger = logging.getLogger(LOGNAME)

import os
import glob
import fnmatch
import threading
import requests
from bs4 import BeautifulSoup
import re
import pygame as pg
import ntpath
import sqlite3
from pathlib import Path 

import avconv_controller

def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = Path(root, basename)
                yield filename

#cursor.execute('insert into File (id, name, bin) values (?,?,?)', (id, name, sqlite3.Binary(file.read())))
#file = cursor.execute('select bin from File where id=?', (id,)).fetchone()

class librarian:

    def __init__(self, **kwargs):

        self.media_dirs = kwargs.get('media_dirs', ['.'])
        self.extensions = kwargs.get('extensions', ['mp4'])
        self.database = kwargs.get('database', ['temp.db'])

        self.initialize()

    def initialize(self):

        self.connection = sqlite3.connect(self.database)
        cursor = self.connection.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS videos (
 file text PRIMARY KEY,
 length integer,
 name text,
 description text,
 last_position integer,
 title blob,
 tries_left_imdb integer
        );""")
        

        self.files = []
        for dir in self.media_dirs:
            logger.info ('checking {0}'.format(dir))
            for ext in self.extensions:
                logger.info ('checking for {1} in {0}'.format(dir, ext))
                self.files = self.files + [str(f) for f in sorted(find_files(dir, '*.' + ext))]


        logger.debug(str(self.files))
        untracked = []

        for file in self.files:
            cursor.execute('SELECT name FROM videos WHERE file = ?;', (file,))
            record = cursor.fetchone()
            
            if record is None:
                untracked = untracked + [file]
                print ('untracked {0}'.format(file))
            else:
                print ('found {0}'.format(file))

        # do something clever to match up new names
        #
        # give up, remove from untracked and update table
        #
        
        cursor.executemany("insert into videos(file, length, name) values (?)", [(u,) for u in untracked])
        self.connection.commit()
            




    def get_files(self):
        logger.debug('called for the library {0} titles'.format(len(self.files)))
        return self.files
