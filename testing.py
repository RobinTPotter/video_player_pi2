#for testing librarian

from config_file import config, load_config, save_config
from config import LOGNAME, LOGFILE, LOGSIZE, FILE_LOG_LEVEL, CONSOLE_LOG_LEVEL, DB
import librarian

lib = librarian.librarian(media_dirs = config['dir'], extensions = config['ext'], database=DB)
