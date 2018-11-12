from config import LOGNAME, exe_avprobe, exe_avconv
import logging
logger = logging.getLogger(LOGNAME)
logger.info('importing avconv/ffmpeg controller')


from subprocess import Popen, PIPE, STDOUT
import json

avconv_process = None

def duration(file):
    try:
        avprobe_process = Popen(
            '{exe_avprobe} "{file}"'
                .format(exe_avprobe=exe_avprobe,file=file).split(), stdout=PIPE, stdin=PIPE, stderr=STDOUT
        )
        result = avprobe_process.stdout.read()
        hh,mm,ss=[float(n) for n in re.search('Duration: [0-9]*:[0-9]*:[0-9]*\.[0-9]*',result).group(0).replace('Duration: ','').split(':')]
        duration = ss + mm*60 + hh*60*60
        logger.debug('values return {0} {1} {2} is {3}'.format(hh,mm,ss,duration))
        return int(duration)
    except Exception as e:
        logger.error('duration \'{0}\': {1}'.format(file,e))
        return 0
        
def thumbnail(position,file,thumbnail):
    try:
        avconv_process = Popen(
            '{exe_avconv} -y -ss {position} -i "{file}" -vcodec png -frames 1 "{thumbnail}"'
                .format(exe_avconv=exe_avconv, position=position,file=file,thumbnail=thumbnail)
                .split(), stdout=PIPE, stdin=PIPE, stderr=STDOUT
        )
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
