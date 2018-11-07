from config import LOGNAME
import logging
logger = logging.getLogger(LOGNAME)
logger.info('importing the librarian')

import os
import glob
import fnmatch
import threading



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

    def __init__(self, filename):
        self.filename = filename
        self.length = avconv_controller.duration(filename)

    def __str__(self):
        return '{0} ({1}): {2}min'.format(self.name,self.filename,int(self.length/60))

    def thumbnail(self,thumbnail_dir):
        self.thumbnail_dir = thumbnail_dir


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
                files = files + [file(f) for f in find_files(dir, '*.' + ext)]

        logger.debug(str((files, files[0])))


