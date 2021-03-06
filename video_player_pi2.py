from config import LOGNAME, LOGFILE, LOGSIZE, FILE_LOG_LEVEL, CONSOLE_LOG_LEVEL, DB
import logging
import logging.handlers
logger = logging.getLogger(LOGNAME)

# Add the log message handler to the logger
file_handler = logging.handlers.RotatingFileHandler(LOGFILE,
                                               maxBytes=LOGSIZE,
                                               backupCount=5,
                                               )

formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
console_handler.setLevel(CONSOLE_LOG_LEVEL)
logger.addHandler(console_handler)


logger.addHandler(file_handler)
logger.setLevel(FILE_LOG_LEVEL)
logger.info('hello')


import pygame as pg
import os
import json
import time
import random
import glob
from os.path import basename





import librarian


pg.init()
pg.joystick.init()
joystick = None

## initialize font

pg.font.init()
font = pg.font.SysFont(None, 12)
title_font = pg.font.SysFont(None, 36)
words_font = pg.font.SysFont(None, 28)

## set config file name and define config load/save functions

from config_file import config, load_config, save_config

lib = librarian.librarian(media_dirs = config['dir'], extensions = config['ext'], database=DB)

## capture additional config options not saved before
for dk in default:
    if dk not in config:
        config[dk] = default[dk]

## resave possibily changed config
save_config(config)


## initial settings for screen size/refresh rate

pg.display.set_mode(config['size'])
FPS = config['FPS']
VISIBLE_MOUSE = config['VISIBLE_MOUSE']
MESSAGE_LENGTH = config['MESSAGE_LENGTH']
WIDTH = config['size'][0]
HEIGHT = config['size'][1]
FONT_HEIGHT = font.size('X')[1]

MODE_DEFINE_CONTROLS = 'DEFINE_CONTROLS'
MODE_MAIN = 'MAIN'
PLAYING = 'PLAYING'
GAME_MODE = {}
GAME_MODE['GAME_MODES'] = [MODE_DEFINE_CONTROLS, MODE_MAIN, PLAYING]
GAME_MODE['CURRENT_MODE'] = GAME_MODE['GAME_MODES'][0]

logger.debug(GAME_MODE)

import omxplayer_controller

##https://learn.adafruit.com/pi-video-output-using-pygame/pointing-pygame-to-the-framebuffer
##stolen from here with grateful thanks
class main_screen :

    screen = None
    textsurface_counter = 0

    controls = None

    used_buttons = []
    used_keys = []

    control_index = 0
    thumb_index = 0
    film_index = -1
    last_index = -1

    def __init__(self, controls, controls_set):

        self.controls = controls
        if controls_set is False: GAME_MODE['CURRENT_MODE'] = MODE_DEFINE_CONTROLS
        else: GAME_MODE['CURRENT_MODE'] = MODE_MAIN

        '''
        [c for c in self.controls if c['name']=='up'][0]['callback']=self.up
        [c for c in self.controls if c['name']=='down'][0]['callback']=self.down
        [c for c in self.controls if c['name']=='left'][0]['callback']=self.left
        [c for c in self.controls if c['name']=='right'][0]['callback']=self.right
        [c for c in self.controls if c['name']=='fire'][0]['callback']=self.fire
        '''

        "Ininitializes a new pg screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            logger.debug("I'm running under X display = {0}".format(disp_no))

        # Check which frame buffer drivers are available
        # Start with fbcon since directfb hangs with composite output
        drivers = ['fbcon', 'directfb', 'svgalib']
        found = False
        for driver in drivers:
            # Make sure that SDL_VIDEODRIVER is set
            if not os.getenv('SDL_VIDEODRIVER'):
                os.putenv('SDL_VIDEODRIVER', driver)
            try:
                pg.display.init()
            except pg.error:
                logger.error('Driver: {0} failed.'.format(driver))
                continue
            found = True
            logger.info('Driver: {0} assigned.'.format(driver))
            break

        if not found:
            raise Exception('No suitable video driver found!')

        size = (pg.display.Info().current_w, pg.display.Info().current_h)
        logger.info("Framebuffer size: {0} x {1}".format(size[0], size[1]))
        self.screen = pg.display.set_mode(size) #, pg.FULLSCREEN)
        # Clear the screen to start
        self.screen.fill((0, 0, 0))
        # Initialise font support
        pg.font.init()
        # Render the screen
        pg.mouse.set_visible(VISIBLE_MOUSE)
        pg.display.update()

    def __del__(self):
        "Destructor to make sure pg shuts down, etc."

    def create_funky_panel(self,file):

        panel_width,panel_height = 600,500

        logger.debug('generating panel for {0}'.format(file))

        name = file.name
        if name is None:
            name = file.filename                
         
        #title_font
        #words_font
        #font.render(message, True, (0, 0, 0),(255,255,255))
        #render(text, antialias, color, background=None) -> Surface
        #font.size('kjsdvahsdfv') gets width, height

        panel = pg.Surface((panel_width,panel_height))

        yy = 0

        thing = title_font.render(name, True, (255,255,150))

        panel.blit(
            thing,
            (0, yy)
        )

        yy += thing.get_height()

        if file.description is None: desc = ['']
        else: desc = file.description.split()

        start_peg = 0
        end_peg = 1
        peg_trial = 1

        paragraph_done = False
        while not paragraph_done:
            ww,hh = words_font.size(' '.join(desc[start_peg:peg_trial]))
            if ww <= panel_width:
                end_peg = peg_trial
                peg_trial=peg_trial + 1
                if peg_trial > len(desc): paragraph_done = True
            if ww > panel_width or paragraph_done:
                if paragraph_done: end_peg = len(desc)+1
                thing = words_font.render(' '.join(desc[start_peg:end_peg]), True, (255,155,150))
                panel.blit(
                    thing,
                    (0, yy)
                )
                yy += thing.get_height()
                start_peg = end_peg
                peg_trial = end_peg = start_peg + 1
        
        if file.title_card is not None:
            panel.blit(
                file.title_card,
                (0, yy)
            )
        logger.debug('returning panel')
        return panel

    ##didn't steal this. attempt to read ast joystick from a config file
    def joystick_setup(self):
        try:
            for j in range(pg.joystick.get_count()):
                self.output("attemp connect to joysticks {0}".format(j))
                joystick = pg.joystick.Joystick(j)
                name = joystick.get_name()
                if 'last_joystick' not in config is None or config['last_joystick']==name:
                    joystick.init()
                    if 'last_joystick' not in config:
                        config['last_joystick'] = name
                        save_config(config)

                    self.output("{0} initialized".format(name))
        except:
            self.output("no joysticks")

    ##one line feed back to screen, setting a opacity/counter for fade out
    def output(self, message):
        logger.debug(message)
        self.textsurface = font.render(message, True, (0, 0, 0),(255,255,255))
        self.textsurface_counter = MESSAGE_LENGTH

    def back_to_menu(self):
        GAME_MODE['CURRENT_MODE'] = MODE_MAIN


    ##start function for main loop
    def start(self,clock):

        prev_m = None
        self.tick=0
        self.current_movie = ''

        done = False
        try:
            while done==False:

                self.tick+=1

                if self.tick%100==0: logger.debug('tick {0}'.format(GAME_MODE['CURRENT_MODE']))

                red = (0, 0, 0)
                self.screen.fill(red)

                key_number = None
                button_number = None

                # EVENT PROCESSING STEP
                # heavily doctored from Adafruit example
                for event in pg.event.get(): # User did something
                    if event.type == pg.QUIT or ( event.type == pg.KEYDOWN and event.key == 27 ): # If user clicked close
                        omxplayer_controller.send_command('kill')
                        logger.info('quit detected')
                        done=True # Flag that we are done so we exit this loop
                        logger.info('done set True')

                    # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
                    if event.type == pg.JOYBUTTONDOWN or ( event.type == pg.KEYDOWN ):
                        if 'button' in event.dict:
                            self.output("Joystick button {0} pressed".format(event.button))
                            logger.debug(self.used_buttons)
                            button_number = event.button

                        if 'key' in event.dict:
                            self.output("Key {0} pressed".format(event.key))
                            logger.debug(self.used_keys)
                            key_number = event.key

                    if event.type == pg.JOYBUTTONUP or ( event.type == pg.KEYUP ):
                        if 'button' in event.dict:
                            self.output("Joystick button {0} released".format(event.button))

                        if 'key' in event.dict:
                            self.output("Key {0} released".format(event.key))

                if GAME_MODE['CURRENT_MODE'] is MODE_DEFINE_CONTROLS:

                    ## noddy bit for define controls

                    #define start position (y) for list of controls
                    yy = ( HEIGHT / 2 ) - (len(self.controls) * (FONT_HEIGHT+2)) /2

                    # go through list of control and high light the current one
                    for p in range(len(self.controls)):
                        if p==self.control_index: colour = (255,255,128)
                        else: colour = (128,128,128)
                        thing = self.controls[p]['name']
                        panel = font.render(thing, True, (0, 0, 0), colour)
                        self.screen.blit(panel, ((WIDTH / 2) - panel.get_width() / 2 , yy))
                        yy += FONT_HEIGHT + 2

                    # if a button is pressed and not already assigned to a control ...
                    if button_number is not None and button_number not in self.used_buttons:
                        self.controls[self.control_index]['button'] = button_number
                        self.used_buttons = [c['button'] for c in self.controls]
                        self.control_index += 1

                    # if a key is pressed and not already assigned to a control ...
                    if key_number is not None and key_number not in self.used_keys:
                        self.controls[self.control_index]['key'] = key_number
                        self.control_index += 1
                        self.used_keys = [c['key'] for c in self.controls]

                    # if the list of controls is exhasusted, move on
                    if self.control_index == len(self.controls):
                        GAME_MODE['CURRENT_MODE'] = MODE_MAIN
                        config['controls_set'] = True
                        save_config(config)

                    pass

                if GAME_MODE['CURRENT_MODE'] is MODE_MAIN:
                    
                    if self.film_index == -1 or self.last_index is not self.film_index:
                        self.film_index = 0
                        lib_files = lib.get_files()
                        
                    # update logic for this mode
                    if key_number is not None:
                        c = [c for c in self.controls if key_number == c['key']]
                        #print ('pressed', key_number, c, self.controls)
                        if len(c)>0:
                            logger.debug ((key_number, c[0]))
                            
                            if c[0]['name'] == 'left':
                                self.thumb_index -= 1
                                if self.thumb_index<0: self.thumb_index = 0
                                
                            if c[0]['name'] == 'right':
                                self.thumb_index += 1
                                if self.thumb_index >= len(lib_files[self.film_index].thumbnails): self.thumb_index = 0
                            
                            if c[0]['name'] == 'up':
                                self.output('left')
                                self.film_index -= 1
                                self.thumb_index = 0 
                                if self.film_index<0: self.film_index = len(lib_files)-1
                            if c[0]['name'] == 'down':
                                self.film_index += 1
                                self.thumb_index = 0 
                                if self.film_index>=len(lib_files): self.film_index = 0

                            if c[0]['name'] == 'fire':
                                self.output('fire')
                                omxplayer_controller.play(lib_files[self.film_index].filename, lib_files[self.film_index].thumbnails_positions[self.thumb_index])
                                logger.debug('back in the room')
                                GAME_MODE['CURRENT_MODE'] = PLAYING
                                

                    #logger.debug('file_index {0}, last_index {1}'.format(self.film_index,self.last_index))
                    
                    if self.film_index == -1 or self.last_index is not self.film_index:
                        logger.debug('index {0}'.format(self.film_index))
                        lib_files[self.film_index].thumbnail()
                        panel = self.create_funky_panel(lib_files[self.film_index])
                        
                    self.screen.blit(panel,(10,10))
                    
                    if self.thumb_index is not -1:
                        thumbnails = lib_files[self.film_index].thumbnails
                        offsetx = 0
                        #logger.debug('thumb index {0}'.format(self.thumb_index))
                        start = self.thumb_index-1
                        for t in range(start,len(thumbnails)):
                            if t>=0: self.screen.blit(thumbnails[t],(offsetx,400))
                            offsetx += 240
                    
                    self.last_index = self.film_index

                elif GAME_MODE['CURRENT_MODE'] is PLAYING:
                    # update logic for this other mode
                    if key_number is not None:
                        c = [c for c in self.controls if key_number == c['key']]
                        #print ('pressed', key_number, c, self.controls)
                        if len(c)>0:
                            logger.debug ((key_number, c[0]))
                            
                            if c[0]['name'] == 'left':
                                omxplayer_controller.send_command('left')
                                
                            if c[0]['name'] == 'right':
                                omxplayer_controller.send_command('right')
                                
                            if c[0]['name'] == 'fire':
                                omxplayer_controller.send_command('kill', callback=self.back_to_menu)
                    pass

                if self.textsurface_counter > 0:
                    self.screen.blit(self.textsurface,(0,0))
                    self.textsurface.set_alpha(self.textsurface_counter)
                    self.textsurface_counter -= 10

                ## added a clock to control FPS
                clock.tick(FPS)

                ## update screen
                pg.display.flip()


        except Exception as al:
            logger.error("{0}".format(al))
            pass

        logger.info('quit pygame')
        pg.quit()


if __name__ == "__main__":
    # Create an instance of the class
    clock = pg.time.Clock()
    player = main_screen(config['controls'], config['controls_set'])
    player.joystick_setup()
    player.start(clock)
