


from config import LOGNAME, exe_avprobe, exe_avconv
import logging
logger = logging.getLogger(LOGNAME)
logger.info('importing avconv/ffmpeg controller')


from subprocess import Popen, PIPE, STDOUT
import re

avconv_process = None

#for s in $(seq 1 250 20000)
#avconv -y -ss $s -i "$1" -vcodec png -frames 1 "$thumbnails/$file/$(printf "%06d" $s).png" > /dev/null 2>&1



def duration(file):
    try:
        logger.debug('determine duration of {0}'.format(file))
        avprobe_process = Popen(
            ['{exe_avprobe}'.format(exe_avprobe=exe_avprobe),'{file}'.format(file=file)],
               stdout=PIPE, stdin=PIPE, stderr=STDOUT
               # 2>&1 | grep -Eo "Duration: [0-9:\.]*" | sed "s/Duration: //"'
        )
        result,err = avprobe_process.communicate()
        #logger.debug('results {0}'.format(result))
        result = str(result)
        duration = re.search('Duration: [0-9]+:[0-9]+:[0-9]+\.[0-9]+',result).group(0)
        duration = duration.replace('Duration: ','')
        hh,mm,ss = [float(d) for d in duration.split(':')]
        logger.debug('duration {0}, {1}, {2}, {3}'.format(duration, hh, mm, ss))
        return int(hh*60*60+mm*60+ss)
    except Exception as e:
        logger.error('duration \'{0}\': {1}'.format(file,e))
        return 0
        
def thumbnail(position,file,thumbnail):
    try:
        logger.debug('generate thumbnails of {0}'.format(file))
        cmd = '{exe_avconv} -y -ss {position} -i'.format(exe_avconv=exe_avconv, position=position).split()+ \
            ['{file}'.format(file=file)]+ \
            '-vcodec png -frames 1'.split()+ \
            ['{thumbnail}'.format(thumbnail=thumbnail)]
        logger.debug('command {0}'.format(' '.join(cmd)))
        avconv_process = Popen(
             cmd, stdout=PIPE, stdin=PIPE, stderr=STDOUT
        )
        out,err = avconv_process.communicate()
        logger.debug(err)
        logger.debug('thumbnail at {0}'.format(position))
        return thumbnail
    except Exception as e:
        logger.error('thumbnail \'{0}\': {1}'.format(file,e))
        return None


def thumbnails(file, thumbnail_dir, start, end, interval):
    check_for_error = False
    results = []
    for pos in range(start,end,interval):
        result = thumbnail(pos, file, '{thumbnail_dir}/t{pos:05d}.png'
            .format(thumbnail_dir=thumbnail_dir, pos=pos))
        if result is None: check_for_error = True
        results.append(result)
    
    return { 'results': results, 'error': check_for_error }
