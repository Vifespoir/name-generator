#!python3
"""This module gets a list of French last names.

Only one source for the moment: genealogie.com.
"""

from bs4 import BeautifulSoup
from french_name_generator.request_handling import html_fr_source
from french_name_generator.log_methods import ItemLogger
import logging
# soup = BeautifulSoup(html_source, 'html.parser')


logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')

LAST_NAME_GENEALOGIE_URL =\
    'http://www.genealogie.com/nom-de-famille/classement-general-0-{}'


def htmls_fr_genealogie(url, nb_of_pg=5):
    """Generate htmls from multiple page."""
    logging.debug('htmls_fr_genealogie Started')
    htmls = []
    for x in range(1, nb_of_pg+1):
        url = LAST_NAME_GENEALOGIE_URL.format(x)
        htmls.append(html_fr_source(url))

    logging.debug('htmls_fr_genealogie Finished')
    return htmls


def names_fr_genealogie(html):
    """Get names from html."""
    logging.debug('names_fr_genealogie Started')
    soup = BeautifulSoup(html, 'html.parser')
    namesDict = {}
    for item in soup.find_all('tr'):
        item = BeautifulSoup(str(item), 'html.parser')
        try:
            name = BeautifulSoup(
                str(item.select('td.nameCell')), 'html.parser')
            name = str(name.get_text()[1:-1]).strip().title()
            freq = BeautifulSoup(
                str(item.select('td.numberCell')), 'html.parser')
            freq = str(freq.get_text()[1:-1]).strip().replace(' ', '')
            namesDict[name] = {'frequency': freq}
        except AttributeError as e:
            logging.debug('names_fr_genealogie AttributeError: %s' % e)
    namesDict.pop('Nom')

    logging.debug('names_fr_genealogie Finished')
    return namesDict


if __name__ == '__main__':
    namesDict = {}
    namesLog = ItemLogger('Last Names')
    logging.debug('Last update: {}\nDays since last update: {}'.format(
        namesLog.previous_time.strftime('%Y-%m-%d %H:%M:%S'),
        namesLog.daydelta))
    logging.debug('Looking for "{}", need for update: {}'.format(
                  namesLog.name, namesLog.need_update))

    # check_if_test_need_for_update_works(namesLog)

    if namesLog.need_update is True:
        genealogie_htmls = htmls_fr_genealogie(LAST_NAME_GENEALOGIE_URL)
        for html in genealogie_htmls:
            partialNamesDict = names_fr_genealogie(html)
            for k in partialNamesDict.keys():
                namesDict[k] = partialNamesDict[k]

        namesLog.store_log(namesDict)
    else:
        namesDict = namesLog.load_log()

    names = [k for k in namesDict.keys()]

    cntr = 0
    for name in names:
        cntr += int(namesDict[name]['frequency'])
    print('{:,} names for a total of: {:,} persons'.format(len(names), cntr))
