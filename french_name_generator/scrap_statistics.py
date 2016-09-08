#!python3
"""This script will scrap to get statistics on 1st names."""

import requests
from bs4 import BeautifulSoup
import json
from time import sleep
from random import randint
import logging
from constant import post_url

logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')


class NameStatistics():
    """A class to scrap name statistics."""

    def __init__(self, namesD):
        """Initialize NameStatistics."""
        self.s = requests.Session()
        self.counter = [0, 0]
        self.namesD = namesD
        self.totalNames = len(self.namesD)
        logging.debug('NameStatistics Class Initialized')

    def get_name_html(self, name):
        """Generate an html for a given name."""
        r = self.s.post(self.post_url, data={'prenom': name})
        sleep(randint(0, 10)/50 + 0.1)
        logging.debug('get_name_html HTML generated')
        return r.text

    def get_name_stats(self, name):
        """Parse the html to find the stats."""
        logging.debug('NameStatistics get_name_stats Started')
        soup = BeautifulSoup(self.get_name_html(name), 'html.parser')
        scripts = soup.find_all('script')
        try:
            s = str(
                [s for s in scripts if 'dataPopularitePrenom' in str(s)][0])
            self.counter[1] += 1
            sJson = json.loads(s[s.find('{"'):s.rfind(']}')+len(']}')])
            nameStats = sJson['data']
            nameStats = [(i['year'], i['value']) for i in nameStats]
            return nameStats

        except IndexError:
            return None

        finally:
            if self.counter[1] < 1:
                successes = 0
            else:
                successes = float(self.counter[1]) / self.totalNames
            if self.counter[0] < 1:
                progress = 0
            else:
                progress = float(self.counter[0]) / self.totalNames
            logging.debug('NameStatistics get_name_stats stats found. {:.2%} \
                successes, progress: {:.2%}'.format(successes, progress))

    def get_all_stats(self):
        """Get name stats from a list of names."""
        assert isinstance(self.namesD, dict), 'Error in loading first names.'
        logging.debug('NameStatistics get_all_stats Started')
        for name in self.namesD:
            self.counter[0] += 1
            try:
                if self.namesD[name]['stats'] is None:
                    self.namesD[name]['stats'] = self.get_name_stats(name)
                else:
                    pass
            except KeyError:
                self.namesD[name]['stats'] = self.get_name_stats(name)

        logging.debug('NameStatistics get_all_stats Finished')

        return self.namesD


if __name__ == '__main__':
    main = NameStatistics('First Names')
    names = main.get_all_stats()
