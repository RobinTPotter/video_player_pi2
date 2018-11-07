from config import LOGNAME, exe_avprobe, exe_avconv
import logging
logger = logging.getLogger(LOGNAME)
logger.info('importing avconv/ffmpeg controller')


from subprocess import Popen, PIPE, STDOUT
import json

avconv_process = None

#for s in $(seq 1 250 20000)
#avconv -y -ss $s -i "$1" -vcodec png -frames 1 "$thumbnails/$file/$(printf "%06d" $s).png" > /dev/null 2>&1



def duration(file):
    try:
        avprobe_process = Popen(
            '{exe_avprobe} -v quiet -of json "{file}"'
                .format(exe_avprobe=exe_avprobe,file=file).split(), stdout=PIPE, stdin=PIPE, stderr=STDOUT
        )
        result = json.loads(avprobe_process.stdout)
        print (result)
        return result['duration']
    except Exception as e:
        print ('duration calculation',e)
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
        print (e)
        return None


def thumbnails(file, thumbnail_dir, start, end, interval):
    check_for_error = False
    results = []
    for pos in range(start,end,interval):
        result = thumbnail(pos, file, '{thumbnail_dir}/t{pos:05d}.png'
            .format(thumbnail_dir=thumbnail_dir, pos=pos))
        if result is None: check_for_error = True
        results.append(result)
    
    return { 'results': results, error: check_for_error }
