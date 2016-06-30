#!python3
"""Main module for generating fake french people."""
from french_name_generator.log_methods import ItemLogger
from random import choice
from datetime import date, timedelta
from copy import deepcopy
import logging

logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')


def loading_names(name_type):
    """Load names."""
    logging.debug("loading_names Started")
    assert name_type == 'Last Names' or name_type == 'First Names',\
        'Name Type must be: "Last Names" or "First Names"'

    names = ItemLogger(name_type)
    return names


def filtering_names(names, ageL, ageH, threshold=500):
    """Filter names based on a timeframe and a popularity threshold."""
    logging.debug("filtering_names Started")
    yDelta = date(year=2013, month=12, day=31) - date.today()
    yDelta = int(yDelta.days / 365)
    namesCopy = deepcopy(names)
    for name in names:
        popular = False
        if names[name]['stats'] is None:
            namesCopy.pop(name)
        else:
            for stat in names[name]['stats'][-(ageH+yDelta):-(ageL+yDelta)]:
                if int(stat[1]) > threshold:
                    popular = True

            if not popular:
                namesCopy.pop(name)
    logging.debug("filtering_names Finished")

    return namesCopy


def generate_name_combo(amount, ageL, ageH, lastUPPER=True,
                        gender_equality=False):
    """Generate pseudo random name combos."""
    logging.debug("generate_name_combo Started")
    firstNamesD = loading_names('First Names').load_log()
    firstNamesD = filtering_names(firstNamesD, ageL, ageH)
    lastNamesD = loading_names('Last Names').load_log()

    assert isinstance(firstNamesD, dict) and isinstance(lastNamesD, dict),\
        'logs must be dicts'
    assert isinstance(amount, int), 'amount must be an integer'
    assert amount < 500, 'amount must be below "500"'

    firstNamesL = name_picker(amount, firstNamesD)
    lastNamesL = name_picker(amount, lastNamesD)

    fullNamesL = dict(zip(lastNamesL, firstNamesL))
    lastNamesOrdered = [k for k in fullNamesL]
    lastNamesOrdered.sort()

    finalList = []
    for lastName in lastNamesOrdered:
        if lastUPPER is True:
            finalList.append((fullNamesL[lastName], lastName.upper()))
        else:
            finalList.append((fullNamesL[lastName], lastName))
    logging.debug("generate_name_combo Finished")

    return finalList


def name_picker(amount, namesD):
    """Pick randomly 'amount' of names in namesD."""
    logging.debug("name_picker Started")
    namesL = []
    while True:
        namesL.append(choice([k for k in namesD.keys()]))

        if len(set(namesL)) == len(range(amount)):
            break
        else:
            namesL = [n for n in set(namesL)]

    return namesL


if __name__ == '__main__':
    while True:
        amount = input('How many names do you wan to generate?   ')
        try:
            amount = int(amount)
            break
        except ValueError:
            pass

    while True:
        lastUPPER = input('Do you want the last name all caps? ("y" or "n")  ')
        if lastUPPER == 'y' or lastUPPER == 'Y':
            lastUPPER = True
            break
        elif lastUPPER == 'n' or lastUPPER == 'N':
            lastUPPER = False
            break

    while True:
        ageRange = input('In which age range do you want names? (yy-yy)   ')
        try:
            ageRange = [int(i) for i in ageRange.split('-')]
            assert len(ageRange) == 2, 'Please give only two numbers.'
            ageL = min(ageRange)
            ageH = max(ageRange)
            break
        except ValueError:
            print('Please write two numbers separated with "-" like: "40-50"')

    gender_equality = True
    names = generate_name_combo(amount, ageL, ageH, gender_equality, lastUPPER)

    for name in names: print(name)
