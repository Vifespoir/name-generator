#!python3
"""This module gets a list of French first names.

Only one source for the moment: wikipedia.
"""

from bs4 import BeautifulSoup
from french_name_generator.request_handling import html_fr_source
from french_name_generator.log_methods import ItemLogger
import logging
from french_name_generator.scrap_statistics import NameStatistics
# soup = BeautifulSoup(html_source, 'html.parser')


logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

FIRST_NAMES_WIKIPEDIA_URL = 'https://fr.wikipedia.org/wiki/\
                     Liste_de_pr%C3%A9noms_fran%C3%A7ais_et_de_la_francophonie'


def names_fr_wikipedia(html):
    """Get names from html."""
    logging.debug('names_fr_wikipedia Started')
    soup = BeautifulSoup(html, 'html.parser')
    namesDict = {}
    for item in soup.find_all('dd'):
        item = BeautifulSoup(str(item), 'html.parser')
        print(item)
        try:
            name = item.a.string
            gender = item.span.string
            desc = item.get_text()
            if name not in [k for k in namesDict.keys()]:
                namesDict[name] = {
                    'gender': gender,
                    'description': desc}
            else:
                pass
        except AttributeError as e:
            logging.debug('names_fr_wikipedia AttributeError: "%s"' % e)

    logging.debug('names_fr_wikipedia Finished')
    return namesDict

if __name__ == '__main__':
    namesLog = ItemLogger('First Names')
    logging.debug('Last update: {}\nDays since last update: {}'.format(
        namesLog.previous_time.strftime('%Y-%m-%d %H:%M:%S'),
        namesLog.daydelta))
    logging.debug('Looking for "{}", need for update: {}'.format(
                  namesLog.name, namesLog.need_update))

    # check_if_test_need_for_update_works(namesLog)

    if namesLog.need_update is True:
        wikipedia_html = html_fr_source(FIRST_NAMES_WIKIPEDIA_URL)
        namesDict = names_fr_wikipedia(wikipedia_html)
        stats = NameStatistics(namesDict)
        namesDict = stats.get_all_stats()
        namesLog.store_log(namesDict)
    else:
        namesDict = namesLog.load_log()
        stats = NameStatistics(namesDict)
        namesDict = stats.get_all_stats()
        namesLog.store_log(namesDict)

    names = [k for k in namesDict.keys()]
