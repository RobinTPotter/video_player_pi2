from config import LOGNAME, THUMBNAIL_INTERVAL, SSL_VERIFY
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

def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename

DEFAULT_THUMBNAIL_PATH = '~/thumnails'

import avconv_controller

class file:

    filename = None
    thumbnail_dir = None
    name = None
    description = None
    length = 0
    last_pos = 0
    title_card = None
    thumbnails = []

    def __init__(self, filename, thumbnail_dir):
        self.filename = filename
        self.thumbnail_dir = thumbnail_dir+'/'+ntpath.basename(filename)
        if not os.path.exists(self.thumbnail_dir): os.makedirs(self.thumbnail_dir)
        self.length = avconv_controller.duration(filename)
        self.thumbnail()

    def __repr__(self):
        return '{0} ({1}): {2} min;{3} thumbs'.format(self.name,self.filename,int(self.length/60),len(self.thumbnails))

    def thumbnail(self):
    
        # load the title.jpg if it exists
        if 'title.jpg' in os.listdir(self.thumbnail_dir):
            imagelocation = self.thumbnail_dir + '/title.jpg'
            self.title_card = pg.image.load(imagelocation)
            logger.info('title card {0}'.format(self.title_card))
        else:
            logger.warn('no title found')
            
        # load the name.txt if it exists
        if 'name.txt' in os.listdir(self.thumbnail_dir):
            with open(self.thumbnail_dir+'/name.txt','r') as fl:
                self.name = fl.read()                
            logger.debug('name read, {0} for {1}'.format(self.name,self.filename))
        else:
            logger.warn('no name found')
            
        # load the description.txt if it exists
        if 'description.txt' in os.listdir(self.thumbnail_dir):
            with open(self.thumbnail_dir+'/description.txt','r') as fl:
                self.description = fl.read()              
            logger.debug('description read, {0} for {1}'.format(self.description,self.filename))
        else:
            logger.warn('no description found')
            
        # check for thumbnails
        if len([f for f in find_files(self.thumbnail_dir,'*.png')])==0:
            logger.info('generating thumbnails')
            results = avconv_controller.thumbnails(self.filename, self.thumbnail_dir, 0, self.length, THUMBNAIL_INTERVAL)
            logger.info('ran thumbnail conversion')
            
        if len([f for f in find_files(self.thumbnail_dir,'*.png')])>0:
            logger.info('found thumbnail images')
            self.thumbnails = []         
            countload = 0 
            for r in [f for f in find_files(self.thumbnail_dir,'*.png')]:
                self.thumbnails.append(pg.image.load(r))
                countload += 1
                logger.debug('loaded {0}'.format(r))
                
            logger.info('loaded {0} thumbnails for {1}'.format(countload, self.filename))
        
        # check if the imdb elements are missing and attemt to get
        if self.title_card is None \
            or self.name is None \
            or self.description is None:
            title = self.filename = ntpath.basename(self.filename).replace('_',' ').replace('.',' ')
            self.call_imdb(title)


    def call_imdb(self, title):
    
        # incase of StupidCapsOnNames        
        title = re.sub('([a-z])([A-Z])','\\1 \\2',title)
        title = re.sub('([^\s0-9])([0-9])','\\1 \\2',title)
        
        logger.info('calling imdb for {0}'.format(title))
        
        # remove spaces and _ and change to + for search
        search = title.lower().replace(' ','+')
        
        # make request to imdb
        response = requests.get('https://www.imdb.com/find?q={0}&s=all'.format(search),verify=SSL_VERIFY).content

        # load doc into bs4
        soup = BeautifulSoup(response, 'html.parser')
        
        try:
            # get the table of results and first result
            first_result = soup.find_all('table', attrs={'class': 'findList'})[0].find_all('tr')[0]
            
            # get imdb id and image
            tiny_image_url = first_result.img['src']
            imdb_id = re.search('tt[0-9]*/',first_result.a['href']).group(0).replace('/','')
            
            # get main image from imdb title page
            main_page_response = requests.get('https://www.imdb.com/title/{0}/?ref_=tt_mv'.format(imdb_id),verify=SSL_VERIFY).content
            main_page_soup = BeautifulSoup(main_page_response, 'html.parser')
        
            image_url = main_page_soup.find_all('div', attrs={'class': 'poster'})[0].a.img['src']
            description = main_page_soup.find_all('div', attrs={'class': 'summary_text'})[0].text
            name = main_page_soup.find_all('div', attrs={'class': 'title_wrapper'})[0].h1.text
            
            logger.debug('parsed pages')
            
            description = ''.join([c if ord(c) < 128 else ' ' for c in description])
            name = ''.join([c if ord(c) < 128 else ' ' for c in name])
            
            self.description = description.strip()
            self.name = name.strip()
            
            logger.debug('{0} {1}'.format(self.description, self.name))
            
            # write out file
            with open(self.thumbnail_dir + '/title.jpg','wb') as output_image_file:
                stuff = requests.get(image_url, verify=False).content
                output_image_file.write(stuff)                
            
            logger.debug('written title')
                
            # write out file
            with open(self.thumbnail_dir + '/name.txt','w') as output_name_file:
                output_name_file.write('{0}'.format(self.name))
                
            logger.debug('written name')    
                
            # write out file
            with open(self.thumbnail_dir + '/description.txt','w') as output_desc_file:
                output_desc_file.write('{0}'.format(self.description))
                
            logger.debug('written description')
                
        except Exception as e:
            logger.error('imdb image/title/descr results {0}'.format(e))
        


class librarian:

    files = []


    def __init__(self, **kwargs):

        self.media_dirs = kwargs.get('media_dirs', ['.'])
        self.thumbnails = kwargs.get('thumbnails', DEFAULT_THUMBNAIL_PATH)
        self.extensions = kwargs.get('extensions', ['mp4'])

        self.initialize()

    def initialize(self):

        files = []
        for dir in self.media_dirs:
            logger.info ('checking {0}'.format(dir))
            for ext in self.extensions:
                logger.info ('checking for {1} in {0}'.format(dir, ext))
                files = files + [file(f,self.thumbnails) for f in find_files(dir, '*.' + ext)]

        logger.debug(str(files))


