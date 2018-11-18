from config import LOGNAME
import logging
logger = logging.getLogger(LOGNAME)
logger.info('importing omxplayer controller')

from subprocess import Popen, PIPE, STDOUT

commands = [
    {'letter': 'q', 'name': 'quit'},
    {'letter': 'space', 'name': 'pause', 'alt':' ' },
    {'letter': '+', 'name': 'vol up' },
    {'letter': '-', 'name': 'vol down' },
    {'letter': 'o', 'name': 'on 10 mins' },
    {'letter': 'i', 'name': 'back 10 mins' },
    {'letter': 'right', 'name': 'on 30 secs' , 'alt':'\027[C'},
    {'letter': 'left', 'name': 'back 30 secs' , 'alt':'\027[D'},
    {'letter': 'kill', 'name': 'killall' },
]

logger.info('So should this')

omxplayer_process = None

def send_command(command, callback=None):
    '''
    send command to the process, command being literally the key pressed
    '''
    logger.info('command pressed {0}'.format(command))    
    if command in [com['letter'] for com in commands]: 
        commando = [c for c in commands if c['letter']==command][0]
        if 'alt' in commando.keys(): command = commando['alt']
        
        try:

            if not command=='kill':
                global omxplayer_process
                logger.info('about to send command {0} to {1}'.format(command,omxplayer_process))
                omxplayer_process.stdin.write(command.encode('ascii'))
                logger.info('written command')

            else:
                getproc = Popen('pgrep omxplayer'.split(),stdin=PIPE,stdout=PIPE)
                out, err = getproc.communicate()
                out = str(out.decode('utf-8'))
                processes = ' '.join(out.split('\n')).rstrip()
                logger.info('processes {0}'.format(processes))
                Popen(('kill -9 {0}'.format(processes)).split(' '), stdout=PIPE, stdin=PIPE, stderr=STDOUT).communicate()
                logger.info('kill sent')
            ## 
            if callback is not None: callback()
            
        except Exception as e:
            logger.error('communicate exception in command {0}\n{1}'.format(str(command),e))
    

def play(file,pos):
    global omxplayer_process
    logger.info('attempt to play {0} from {1}'.format(file,pos))
    omxplayer_process = Popen(['omxplayer', '-b',str(file),'--pos',str(pos)], stdout=PIPE, stdin=PIPE, stderr=STDOUT)    
    logger.info('got process {0}'.format(omxplayer_process))

