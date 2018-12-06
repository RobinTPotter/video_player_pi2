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

sql_create_main = """CREATE TABLE IF NOT EXISTS videos (
 file text PRIMARY KEY,
 length integer,
 name text,
 description text,
 last_position integer,
 title blob,
 tries_left_imdb integer
);"""

sql_create_thumbnails = """CREATE TABLE IF NOT EXISTS thumbnails (
 file text PRIMARY KEY,
 pos integer,
 thumbnail blob
);"""

sql_select_file_name = 'SELECT name FROM videos WHERE file = :file;'

sql_select_file_record = 'SELECT file, length, name, description, last_position, title, tries_left_imdb FROM videos WHERE file = :file;'

sql_insert_fresh_file = """insert into videos(
    file, length, name, description, last_position, title, tries_left_imdb
)
values (
    :file, :length, :name, :description, :last_position, :title, :tries_left_imdb
)"""
             
class librarian:

    def __init__(self, **kwargs):

        self.media_dirs = kwargs.get('media_dirs', ['.'])
        self.extensions = kwargs.get('extensions', ['mp4'])
        self.database = kwargs.get('database', ['temp.db'])

        self.initialize()

    def initialize(self):

        self.connection = sqlite3.connect(self.database)
        cursor = self.connection.cursor()
        cursor.execute(sql_create_main)
        cursor.execute(sql_create_thumbnails)
        

        self.files = []
        for dir in self.media_dirs:
            logger.info ('checking {0}'.format(dir))
            for ext in self.extensions:
                logger.info ('checking for {1} in {0}'.format(dir, ext))
                self.files = self.files + [str(f) for f in sorted(find_files(dir, '*.' + ext))]


        logger.debug(str(self.files))
        untracked = []

        for file in self.files:
            cursor.execute(sql_select_file_name, {'file': file})
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
        
        for untracked_file in untracked:
            from imdb import call_imdb
            result = call_imdb(Path(untracked_file).name)
            name = result['name']
            description = result['description']
            image = result['title_image']
            length = avconv_controller.duration(untracked_file)

            cursor.execute(sql_insert_fresh_file, {'file':untracked_file,'length':length, 'name':name, 'description':description, 'tries_left_imdb':0 , 'title':image, 'last_position':0 })

        self.connection.commit()
            
    def get_file(self, num):
    
        if num >= len(self.files):
            num = len(self.files)-1
        elif num < 0: num = 0
        
        name = self.files[num]
        logger.debug('get file {0} is {1}'.format(num, name))
        
        cursor = self.connection.cursor()
        cursor.execute(sql_select_file_record, {'file': name})
        record = cursor.fetchone()
        
        labels = ['file', 'length', 'name', 'description', 'last_position', 'title', 'tries_left_imdb']
        object = dict(zip(labels,record)) 
        
        return object
      


    def get_files(self):
        logger.debug('called for the library {0} titles'.format(len(self.files)))
        return self.files
