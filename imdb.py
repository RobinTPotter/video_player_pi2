from config import LOGNAME, THUMBNAIL_INTERVAL, SSL_VERIFY, NOIMDB
import logging
logger = logging.getLogger(LOGNAME)

import requests
from bs4 import BeautifulSoup

def call_imdb(title):

    # incase of StupidCapsOnNames
    # title = re.sub('(.+)(\.avi|mp4|mkv)','\\1',title)
    # title = re.sub('([a-z])([A-Z])','\\1 \\2',title)
    # title = re.sub('([^\s0-9])([0-9])','\\1 \\2',title)

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

        description = description.strip()
        name = name.strip()

        logger.debug('{0} {1}'.format(description, name))

        # write out file
        title_image = requests.get(image_url, verify=False).content

        logger.debug('got title image')

        return { 'name': name, 'description': description, 'title_image':title_image }
        
    except Exception as e:
        logger.error('imdb image/title/descr results {0} on {1}'.format(e, self))
        return { 'name': title, 'description': 'no description', 'title_image': None }

