#!python3
"""This module will contain log methods shared by the different modules.

Current methods:
ItemLogger
UpdateLogs
"""

import shelve
import os
import logging
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')


# make sure log dir exists
cwd = os.getcwd()
logDir = os.path.join(cwd, 'french_name_generator/logs/')
if not os.path.exists(logDir):
    os.makedirs(logDir)
    logging.info('Log directory created at: "%s"' % logDir)


class ItemLogger():
    """Help to store names into database files."""

    log_file_name = 'Names'
    log_update = 'Update'
    year_in_s = 365*24*60*60

    def __init__(self, name, skip_update=False):
        """Initialize NameLogger."""
        logging.info('NameLogger class Initialized.')
        assert isinstance(name, str) is True,\
            'NameLogger name must be a string.'
        self.name = name
        self.shelf = shelve.open(logDir + self.log_file_name)
        self.update_shelf = shelve.open(logDir + self.log_update)
        self.current_time = datetime.today()

        try:
            self.previous_time = datetime.fromtimestamp(
                self.load_log(update=True)['time'])
        except KeyError:
            self.previous_time = self.current_time

        self.daydelta = (self.current_time-self.previous_time).days

        if self.daydelta > 366/2 or self.current_time == self.previous_time:
            self.need_update = True
            self.store_log(
                {'time': self.current_time.timestamp()}, update=True)
            logging.info('Log need update, \
                         last update time set to current time: %s'
                         % self.current_time.ctime())
        elif skip_update is True:
            self.need_update = True
        else:
            self.need_update = False
            logging.info('Last log update too recent: %s'
                         % self.previous_time.ctime())

    def store_log(self, dictionary, update=False):
        """Store the given dictionary."""
        logging.info('NameLogger dictionary.')
        if update:
            self.update_shelf[self.name] = dictionary
        else:
            self.shelf[self.name] = dictionary

    def load_log(self, update=False):
        """Load data from given name as a dictionary."""
        try:
            if update:
                dictionary = self.update_shelf[self.name]
            else:
                dictionary = self.shelf[self.name]
            assert isinstance(dictionary, dict)
            logging.info('Data "%s" successfully loaded.' % self.name)
        except Exception as e:
            logging.warning('Error during data loading: "{}"\nLog Name: "{}"'
                            .format(e, self.name))
            dictionary = {}
        except AssertionError as e:
            logging.warning('Error during data loading: "{}"\
                            \nLog "{}" do not exist'
                            .format(e, self.name))
            dictionary = {}

        return dictionary

    def print_log(self):
        """Print data from a given name."""
        import pprint
        pp = pprint.PrettyPrinter(indent=4)
        dictionary = self.load_log()
        pp.pprint(dictionary)


def check_if_test_need_for_update_works(namesLog):
    """Test function to see if the update mechanism works."""
    namesLog.previous_time = (
        datetime.today() - timedelta(days=365)).timestamp()
    namesLog.store_log({'time': namesLog.previous_time}, update=True)
