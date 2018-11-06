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

omxplayer_process = None

def send_command(command, callback):
    '''
    send command to the process 
    
    '''
    showMenu = False
    if command in [x['letter'] for x in commands]: 
        commando = [c for c in commands if c['letter']==command][0]
        if 'alt' in commando.keys(): command = commando['alt']
        try:
            #print('sending >'+ command +'<')
            #stdo, stde = omxplayer_process.communicate(command+'\0')
            #print('stdo: '+str(stdo))
            #print('stde: '+str(stde))
            print('why dyour force it')
            if not command=='kill':
                omxplayer_process.stdin.write(command)
            else:
                getproc = Popen('pgrep omxplayer'.split(),stdin=PIPE,stdout=PIPE)
                processes = ' '.join(getproc.communicate()[0].split('\n')).rstrip()
                Popen(('kill -9 '+processes).split(' '), stdout=PIPE, stdin=PIPE, stderr=STDOUT).communiate()

            ## 
            if command=='q' or command=='kill': callback()
            
        except Exception as e:
            print('communicate exception in command {0}\n{1}'.format(str(command),e))
    

def play(thing,pos):
    file = [f['directory']+'/'+f['file'] for f in files if f['number']==thing][0]
    global omxplayer_process
    omxplayer_process = Popen(['omxplayer', '-b',file,'--pos',pos], stdout=PIPE, stdin=PIPE, stderr=STDOUT)    
    print(omxplayer_process)
