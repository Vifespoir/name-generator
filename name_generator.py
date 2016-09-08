"""Flask tutorial."""

# all the imports
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from french_name_generator.main import generate_name_combo
import logging
from secret import SECRET_KEY

logging.basicConfig(
    level=logging.DEBUG, format=' %(asctime)s - %(levelname)s - %(message)s')


# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'name_generator.db'),
    SECRET_KEY=SECRET_KEY,
    static_folder='/static'
))
app.config.from_envvar('NAME_GENERATOR_SETTINGS', silent=True)


def connect_db():
    """Connect to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initialize the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initialize the database."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Open a new database connection.

    Check if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def init_names():
    """Open a new database connection.

    Check if there is none yet for the
    current application context.
    """
    db = get_db()
    with app.open_resource('names.sql', mode='r') as f:
        db.cursor().executescript(f.read())
        db.commit()


@app.teardown_appcontext
def close_db(error):
    """Close the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def reroute():
    logging.debug('Rerouting...')
    return redirect(url_for('show_names'))


@app.route('/fr/names', methods=['GET', 'POST'])
def show_names():
    """Display generated names."""
    logging.debug('Fetching names from db...')
    db = get_db()
    names = []
    errors = []
    try:
        cur = db.execute('select firstname, lastname from query order by id desc')
        namesDB = cur.fetchall()
        logging.debug('Names fetched')
    except sqlite3.OperationalError as e:
        errors.append(e)
        logging.debug('Error in name fetching: %s' % e)

    if namesDB:
        for name in namesDB:
            name = (name['firstname'], name['lastname'])
            names.append(name)

    logging.debug('Fetching info from db...')
    try:
        cur = db.execute('select nb_names, ageL, ageH, caps from info')
        infoDB = cur.fetchall()
        logging.debug('Info fetched: %s' % infoDB)
    except sqlite3.OperationalError as e:
        errors.append(e)
        infoDB = []
        logging.debug('Error in info fetching %s' % e)

    if infoDB:
        for info in infoDB:
            number, ageL, ageH = info['nb_names'], info['ageL'], info['ageH']
            logging.debug('Info row: %s' % [x for x in info])

        session.update(dict(names=names, number=number, ageL=ageL, ageH=ageH))
        flash('Last request generated {} names from {} to {} years-old'.format(number, ageL, ageH))
        logging.debug('Former request found, rendering show_names.html')

        return render_template('show_names.html')

    else:
        logging.debug('No former request found, rendering request.html')

        return render_template('request.html')


@app.route('/fr/names/generate', methods=['GET', 'POST'])
def generate_names():
    """Generate French names."""
    init_names()

    logging.debug('Generating names...')
    if request.method == 'POST':
        logging.debug("Generate_names POST form: %s" % request.form)

        age = request.form['range'].split(' - ')
        ageL, ageH = int(age[0]), int(age[1])

        logging.debug("Generate_names ages: {} - {}".format(ageL, ageH))

        try:
            request.form['lastUPPER']
            lastUPPER = True
        except Exception as e:
            logging.debug("generate_names lastUPPER error: %s" % e)
            lastUPPER = False

        logging.debug("generate_names last name upper: %s" % lastUPPER)

        if request.form['amount']:
            amount = int(request.form['amount'])
            names = generate_name_combo(amount=amount, ageL=ageL, ageH=ageH,
                                        lastUPPER=lastUPPER)
            logging.debug('generate_names amount: %s' % amount)

            logging.debug('Writing in db...')
            db = get_db()
            for name in names:
                db.execute('insert into query (firstname, lastname) values (?, ?)',
                           [name[0], name[1]])
                db.commit()
            logging.debug('Names written')

            db.execute('insert into info (nb_names, ageL, ageH, caps) values (?, ?, ?, ?)',
                       [amount, ageL, ageH, lastUPPER])
            db.commit()
            logging.debug('Info written')

            flash('Generated {} names from {} to {} years-old'.format(amount, ageL, ageH))

            session.update(dict(number=amount, ageL=ageL, ageH=ageH, names=names))

            return redirect(url_for('show_names'))

    else:
        return render_template('request.html')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
